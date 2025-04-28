#!/g/data/hh5/public/apps/nci_scripts/python-analysis3
# Copyright 2020 Scott Wales
# author: Scott Wales <scott.wales@unimelb.edu.au>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re
import subprocess
import json
import sys
import pymunge
import requests
### Hopefully speed up initialisation
from pandas import isnull
from math import floor,pow,log

from typing import List, Dict, Union

def format_size(val: float,suffix: str="iB",base: float=1024.0,dp: int=2) -> str:
    prefixes=( "", "K", "M", "G", "T", "P", "E", "Z", "Y")
    multiplier=1.0
    if val < 0:
        multiplier=-1.0
        val = -val
    i=0
    if ( val < base ):
        if suffix == 'iB': suffix='B'
    else:
        i = int(floor(log(val,base)))
    p = pow(base,i)
    s = round(val/p,dp)
    return f"{multiplier*s:.{dp}f}{prefixes[i]}{suffix}"

def node_to_queue(node: str) -> str:

    if node.startswith('gadi-cpu-clx-'): return 'normal-exec'
    if node.startswith('gadi-dm-'): return 'copyq-exec'
    if node.startswith('gadi-hmem-clx-'): return 'hugemem-exec'
    if node.startswith('gadi-gpu-v100-'): return 'gpuvolta-exec'
    if node.startswith('gadi-hmem-bdw-'): return 'hugemembw-exec'
    if node.startswith('gadi-mmem-clx-'): return 'megamem-exec'
    if node.startswith('gadi-mmem-bdw-'): return 'megamembw-exec'
    if node.startswith('gadi-cpu-bdw-'): return 'normalbw-exec'
    if node.startswith('gadi-cpu-skl'): return 'normalsl-exec'
    if node.startswith('gadi-dgx-a100'): return 'dgxa100-exec'
    if node.startswith('gadi-analysis-'): return 'analysis-exec'
    return '???'

def decode_bytes(s):
    """
    Convert a formatted size to number of bytes
    """
    if isnull(s):
        return s

    scales = {
        'k': 1024,
        }
    if not s.endswith('b'):
        raise Exception(f"{s} doesn't look like a size")

    scale = 1
    s = s[:-1]

    if not s[-1].isdigit():
        scale = scales[s[-1]]
        s = s[:-1]

    return int(s) * scale


def clean_qstat_json(stream):
    """
    Clean up the improperly escaped JSON returned by qstat
    """
    string_entry_re = re.compile(r'^\s*"(?P<key>.+)":"(?P<value>.+)"(?P<comma>,?)$')

    lines = []

    for line in stream.splitlines():
        match = string_entry_re.match(line)
        if match is not None:
            fixed_value = json.dumps(match.group('value'))
            line = f'"{match.group("key")}":{fixed_value}{match.group("comma")}'

        lines.append(line)

    return json.loads(''.join(lines))


def qstat(jobids: List[str], show_finished: bool=False):
    """
    Returns the information from qstat
    """

    extra_args = []
    if show_finished:
        extra_args.append('-x')

    subp = subprocess.run(
        ["/opt/pbs/default/bin/qstat", *extra_args, "-f", "-F", "json", *jobids],
        text=True,
        check=True,
        stdout=subprocess.PIPE,
    )

    jobs = clean_qstat_json(subp.stdout)["Jobs"]

    return jobs

nqstat_size_keys=('resources_used.mem', 'resources_used.vmem','resources_used.jobfs', 
                  'Resource_List.mem', 'Resource_List.jobfs')

def nqstat(project: str) -> Dict[str,Dict[str,Union[str,int]]]:
    
    url = 'http://gadi-pbs-01.gadi.nci.org.au:8812/qstat'
    headers = { 'Authorization': f"MUNGE {pymunge.encode().decode(sys.getdefaultencoding())}" }
    params = {'project': project}
    
    response = requests.get(url, params=params, headers=headers, timeout=120.0)
    response.raise_for_status()

    if response.status_code == 200:
        ### This function outputs a list - transform it so it looks like 
        ### qstat json output
        d = {}
        for job in response.json()['qstat']:
            d[job['Job_ID']] = { k:v for k,v in job.items() if k not in [ 'Job_ID', 'Submit_arguments']  }
            d[job['Job_ID']]['Submit_arguments'] = job['Submit_arguments'].replace('<jsdl-hpcpa:Argument>','').replace('</jsdl-hpcpa:Argument>',' ')
            for k in nqstat_size_keys:
                if k in d[job['Job_ID']]:
                    d[job['Job_ID']][k] = decode_bytes(d[job['Job_ID']][k])
        return d
    else:
        return {}

def pbsnodes(json: bool = False) -> Dict[str,Dict[str,str]]:

    cmd=["pbsnodes","-a"]
    if json:
        cmd.extend(["-F","json"])

    try:
        p = subprocess.run(cmd,text=True,check=True,capture_output=True)
    except subprocess.CalledProcessError:
        exit("Unable to call pbsnodes")
    
    if json:
        d = json.dumps(p.stdout["nodes"])
    else:
        d={}
        lines=[ l.strip() for l in p.stdout.split('\n') ]
        ##startline=0
        ##endline=0
        innodeblock=False
        for l in lines:
            if '=' not in l:
                if innodeblock:
                    ### Found the end of the nodeblock
                    ##endline=i+1
                    innodeblock=False
                else:
                    if l.startswith('gadi-'):
                        ##startline=i+1
                        innodeblock=True
                        node=l
                        d[node]={}
                        continue
            if innodeblock:
                line=l.split(' ')
                if line[0] == 'jobs':
                    d[node]['jobs'] = [ job.split('/')[0] for job in line[2:] ]
                elif line[0].startswith('resources_available') or line[0].startswith("resources_assigned"):
                    dname,dkey = line[0].split('.')
                    try:
                        d[node][dname].update({dkey:' '.join(line[2:])})
                    except KeyError:
                        d[node][dname] = { dkey:' '.join(line[2:]) }
                else:
                    d[node][line[0]] = ' '.join(line[2:])

        return d

def job_data_from_pbsnodes(jobids: List[str] = []) -> Dict[str,Dict[str,Union[str,int]]]:

    nodes={}
    for i,node in pbsnodes().items():
        if 'jobs' in node:
            nodes[i] = []
            tmp = list(dict.fromkeys(node['jobs']))
            for j in tmp:
                nodes[i].append( ( j, node['jobs'].count(j), decode_bytes(node['resources_assigned']['mem'])//len(tmp) ) )

    ### Create dict objects that sort of match nqstat output
    if jobids:
        data=dict.fromkeys([ j if j.endswith('.gadi-pbs') else j + '.gadi-pbs' for j in jobids ])
    else:
        data=dict.fromkeys([ j[0] for n in nodes.values() for j in n ])
    for d in data:
        data[d] = {'Resource_List.ncpus':0,'resources_used.mem':0,'exec_host':''}

    for host,node in nodes.items():
        if jobids:
            for jobid in data.keys():
                for i in node:
                    if i[0] == jobid:
                        data[jobid]['Resource_List.ncpus'] += i[1]
                        data[jobid]['resources_used.mem'] += i[2]
                        data[jobid]['queue'] = node_to_queue(host)
                        if data[jobid]['exec_host']:
                            data[jobid]['exec_host'] = data[jobid]['exec_host'] + '+' + host
                        else:
                            data[jobid]['exec_host'] = host
        else:
            for i in node:
                data[i[0]]['Resource_List.ncpus'] += i[1]
                data[i[0]]['resources_used.mem'] += i[2]
                data[i[0]]['queue'] = node_to_queue(host)
                data[i[0]]['job_state']='R'
                ### Create an exec_host string that, when split on '+' creates
                ### a list corresponding to the nodes, just like nqstat does
                if data[i[0]]['exec_host']:
                    data[i[0]]['exec_host'] = data[i[0]]['exec_host'] + '+' + host
                else:
                    data[i[0]]['exec_host'] = host

    if jobids:
        ### Clear out dict keys for non-existent jobs
        for k,v in data.copy().items():
            if v['Resource_List.ncpus'] == 0 and v['resources_used.mem'] == 0:
                del(data[k])

    return data
            
