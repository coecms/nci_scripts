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


import typing as T
import pandas
import re
import subprocess
import json

def decode_bytes(s):
    """
    Convert a formatted size to number of bytes
    """
    if pandas.isnull(s):
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


def qstat(jobids: T.List[str], show_finished: bool=False):
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


