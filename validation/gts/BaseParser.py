#!/usr/bin/env python
import os
import json
import sys
import subprocess

# Main interface to all parsing classes

PRECISE = 30


class BaseParser(object):
    TEST = ""
    IGNOREKEYS = []

    def __init__(self, path):
        if not self.TEST:
            print("Please set TEST in parser class")
            sys.exit()
        self._path = os.path.abspath(os.path.join(path, self.TEST))
        self._jobs = []

    def getJobs(self):
        if not self._jobs:
            allj = []
            _list = [os.path.join(self._path, x) for x in os.listdir(
                self._path) if not x.startswith('.')]
            _list_len = len(_list)
            _idx = 0
            for hdir in _list:
                if os.path.exists(os.path.join(hdir, self.TEST + '.json')):
                    sys.stdout.write(
                        "Fetched {0}/{1}".format(_idx + 1, _list_len))
                    sys.stdout.flush()
                    sys.stdout.write("\r")
                    _idx += 1
                    with open(os.path.join(hdir, self.TEST + '.json'), 'r') as fh:
                        tmp = json.load(fh)
                    tmp["path"] = hdir
                    tmp["TEST"] = self.TEST
                    for key in tmp:
                        if "include" in tmp[key]:
                            tmp[key] = tmp[key].split()[1]
                    allj.append(tmp)
                else:
                    _list_len -= 1
            self._jobs = allj
            sys.stdout.write("\n")
        return self._jobs

    def getJobsList(self):
        # returns list of jobs
        # where Job is dict with parameters and 'path' corresponds to job path
        # the function should group all Jobs to list
        joblist = []
        allJobs = self.getJobs()[:]
        donejobs = []
        while allJobs:
            job = allJobs[0]
            jobstojoblist = [x for x in allJobs if self.isJobMatches(job, x)]
            for j in jobstojoblist:
                donejobs.append(j)
                allJobs.remove(j)
            joblist.append(jobstojoblist)
        return joblist

    # pylint: disable=no-self-use
    def parse(self, jobs):
        # should return generator of JSONs
        raise RuntimeError(
            "You should implement your own parse() functino in parser class!")

    def isJobMatches(self, job1, job2):
        keywords_to_ignore = ["N", "RANDOMSEED",
                              "NEVENTS", "TEST", "path"] + self.IGNOREKEYS
        for k in job1:
            if k in keywords_to_ignore:
                continue
            if k not in job2:
                return False
            if job1[k] != job2[k]:
                return False
        return True


def execCmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = p.communicate()
    return (p.returncode, stdout.strip(), stderr.strip())


def mktemp(template="XXXXXXX.tmp", isDir=False):
    r = execCmd(['mktemp'] + ([], ["-d"])[isDir] + [template])
    if r[0] == 0:
        return r[1]
    raise RuntimeError("Cannot create tmpdir")


def mktempdir():
    return mktemp(isDir=True)


def mergeROOT(inputfiles, outfile):
    r = execCmd(['hadd', '-f', outfile] + inputfiles)
    # print r[1]
    return r
