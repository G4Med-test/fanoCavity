#!/usr/bin/env
import sys
import os
import subprocess
import collections
import hashlib
import json
import itertools

PLATFORM = ""

# alias to print to stderr
def eprint(s):
    sys.stderr.write(s + "\n");

def safeInt(value):
    try:
        return int(value)
    except ValueError:
        return None


def getTestPath(initialPath, version=None):
    if not os.path.exists(initialPath):
        eprint ("Directory {0} does not exists.".format(initialPath))
        sys.exit()
    indent = 2
    versions = [x for x in os.listdir(
        initialPath) if os.path.isdir(os.path.join(initialPath, x))]
    if not versions:
        eprint ("No versions found in {0}".format(initialPath))
        sys.exit()
    if len(versions) > 1:
        if version is None:
            eprint("More than one version found. Please select version or number: ")
        answer_version = version
        while True and answer_version is None:
            for v in versions:
                eprint (" " * indent + \
                    "{1}) {0}".format(v, versions.index(v) + 1))
            eprint("Please select version: ")
            answer_version = input()
            if answer_version in versions:
                version = answer_version
                break
            elif safeInt(answer_version) < len(versions) + 1:
                version = versions[safeInt(answer_version) - 1]
                break
            else:
                eprint ("Unexpected answer. Try again.")
    else:
        version = versions[0]
    versionpath = os.path.join(initialPath, version)
    if not os.path.exists(versionpath):
        eprint ("Path '{0}' does not exists".format(versionpath))
        sys.exit()
    platforms = [x for x in os.listdir(
        versionpath) if os.path.isdir(os.path.join(versionpath, x))]
    if not platforms:
        eprint ("No platforms found in {0}".format(initialPath))
        sys.exit()
    if len(platforms) > 1:
        eprint ("More than one platform found. Please select: ")
        answer_platform = None
        while True:
            for p in platforms:
                eprint (" " * indent + \
                    "{1}) {0}".format(p, platforms.index(p) + 1))
            eprint("Please select platform: ")
            answer_platform = input()
            if answer_platform in platforms:
                platform = answer_platform
                break
            elif safeInt(answer_platform) < len(platforms) + 1:
                platform = platforms[safeInt(answer_platform) - 1]
                break
            else:
                eprint ("Unexpected answer. Try again.")
    else:
        platform = platforms[0]
    return os.path.join(initialPath, version, platform)


def get_available_test_configurations(project, path="."):
    testdirpath = os.path.join(path, "tests", project)
    if not os.path.exists(testdirpath):
        return []
    tests = [x for x in os.listdir(testdirpath) if os.path.exists(
        os.path.join(testdirpath, x, "template.conf"))]
    return tests

# pylint: disable=global-statement


def get_platform(project, version):
    global PLATFORM
    if not PLATFORM:
        versionfile = os.path.join("configs", project, version + ".sh")
        proc = subprocess.Popen(["bash", "-c", "source {0}; echo $PLATFORM".format(versionfile)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        PLATFORM = proc.communicate()[0].strip().split("\n")[-1]
    return PLATFORM


def convert(value, f, t):
    # value, from, to
    if f == t:
        return value
    # const scale
    scale = {
        "m": 1e-3,
        "c": 1e-2,
        "d": 1e-1,
        "K": 1e3,
        "M": 1e6,
        "G": 1e9,
        "T": 1e12
    }
    # find max common part
    rev_f = "".join(reversed(f))
    rev_t = "".join(reversed(t))
    max_ft = "".join(reversed(sorted([f, t], key=len)[0]))
    s = "".join([max_ft[x]
                 for x in range(len(max_ft)) if rev_f[x] == rev_t[x]])
    rev_f = rev_f.replace(s, "", 1)
    rev_t = rev_t.replace(s, "", 1)
    if rev_f and rev_f not in scale:
        raise RuntimeError(
            "Coefficient '{0}' not found in constant coefficients".format(rev_f))
    if rev_t and rev_t not in scale:
        raise RuntimeError(
            "Coefficient '{0}' not found in constant coefficients".format(rev_t))
    f_c = 1 if not rev_f else scale[rev_f]
    t_c = 1 if not rev_t else scale[rev_t]
    return float(value) * f_c / t_c


def get_ordered_dict(obj):
    return collections.OrderedDict(sorted(obj.items()))


def get_hashed_path(obj):
    return hashlib.md5(json.dumps(get_ordered_dict(obj)).encode()).hexdigest()


def getcombinations(cdict):
    alllist = []
    for key in cdict.keys():
        tmp = []
        for val in cdict[key]:
            tmp.append("{0}={1}".format(key, val))
        alllist.append(tmp)
    clist = list(itertools.product(*alllist))
    rlist = []
    for clistitem in clist:
        obj = {}
        for item in clistitem:
            key = item.split("=")[0].strip()
            val = item.split("=")[1].strip()
            obj[key] = val
        rlist.append(obj)
    return rlist


def getJSON(job, charttype="chart", **kwargs):
    if job is None:
        job = {}
    j = {
        "article": {
            "inspireId": kwargs.get("inspireId", -1)
        },
        "mctool": {
            "name":  kwargs.get("mctool_name"),
            "version": kwargs.get("mctool_version", '' if 'VERSION' not in job else job['VERSION']),
            "model": kwargs.get("mctool_model")
        },
        "testName":  kwargs.get("testName", '' if 'TEST' not in job else job['TEST']),
        "metadata": {
            "observableName": kwargs.get("observableName"),
            "reaction": kwargs.get("reaction", "reaction name"),
            "targetName": kwargs.get("targetName"),
            "beamParticle": kwargs.get('beamParticle'),
            "beamEnergies": kwargs.get("beamEnergies"),
            "secondaryParticle": kwargs.get("secondaryParticle", "None"),
            "parameters": kwargs.get("parameters", [])
        },
        "plotType": "SCATTER2D" if charttype == "chart" else "TH1"
    }
    if charttype == "chart":
        j["chart"] = {
            "nPoints": len(kwargs.get("xValues")),
            "title": kwargs.get("title", "title"),
            "xAxisName": kwargs.get("xAxisName", "x axis"),
            "yAxisName": kwargs.get("yAxisName", "y axis"),
            "xValues": kwargs.get("xValues"),
            "yValues": kwargs.get("yValues"),
            "xStatErrorsPlus": kwargs.get("xStatErrorsPlus", []),
            "xStatErrorsMinus": kwargs.get("xStatErrorsMinus", []),
            "yStatErrorsPlus": kwargs.get("yStatErrorsPlus", []),
            "yStatErrorsMinus": kwargs.get("yStatErrorsMinus", []),
            "xSysErrorsPlus": kwargs.get("xSysErrorsPlus", []),
            "xSysErrorsMinus": kwargs.get("xSysErrorsMinus", []),
            "ySysErrorsPlus": kwargs.get("ySysErrorsPlus", []),
            "ySysErrorsMinus": kwargs.get("ySysErrorsMinus", [])
        }
    if charttype == "histogram":
        j["histogram"] = {
            "nBins": [len(kwargs.get("binContent"))],
            "title": kwargs.get("title", "title"),
            "xAxisName": kwargs.get("xAxisName", "x axis"),
            "yAxisName": kwargs.get("yAxisName", "y axis"),
            "binEdgeLow": kwargs.get("binEdgeLow"),
            "binEdgeHigh": kwargs.get("binEdgeHigh"),
            "binContent": kwargs.get("binContent"),
            "yStatErrorsPlus": kwargs.get("yStatErrorsPlus", []),
            "yStatErrorsMinus": kwargs.get("yStatErrorsMinus", []),
            "ySysErrorsPlus": kwargs.get("ySysErrorsPlus", []),
            "ySysErrorsMinus": kwargs.get("ySysErrorsMinus", []),
            "binLabel": kwargs.get("binLabel", [])
        }
    if charttype not in ("chart", "histogram"):
        raise RuntimeError("Undefined type {}".format(charttype))
    return j
