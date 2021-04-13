import pytest

import importlib
import os
import sys


def import_path(path):
    module_name = os.path.basename(path).replace("-", "_")
    spec = importlib.util.spec_from_loader(
        module_name, importlib.machinery.SourceFileLoader(module_name, path)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module


qcost = import_path("qcost")


def test_qcost():

    assert qcost.qcost("normal", 4, "4GB", "1:00:00") == 4 * 2
    assert qcost.qcost("normal", 8, "4GB", "1:00:00") == 8 * 2
    assert qcost.qcost("normal", 4, "32GB", "1:00:00") == 8 * 2
    assert qcost.qcost("normal", 4, "32GB", "2:30:00") == 8 * 2 * 2.5
    assert qcost.qcost("normal", 1, "8192MB", "1:00:00") == 2 * 2

    assert qcost.qcost("express", 4, "4GB", "1:00:00") == 4 * 6

    assert qcost.qcost("normalbw", 4, "4GB", "1:00:00") == 4 * 1.25
    assert qcost.qcost("normalbw", 4, "32GB", "1:00:00") == 4 * 1.25
    assert qcost.qcost("normalbw", 4, "256GB", "1:00:00") == 28 * 1.25

    assert qcost.qcost("normalsl", 4, "4GB", "1:00:00") == 4 * 1.5
    assert qcost.qcost("normalsl", 4, "30GB", "1:00:00") == 5 * 1.5
