#!/usr/bin/env python

# class for sc test parsing
import os
from decimal import Decimal
import shutil
from gts.utils import getJSON
from gts.BaseParser import BaseParser, PRECISE

XAXIS_MAP = {
    "Elastic(b)": 'E (MeV)',
    "Inelastic(b)": 'E (MeV)',
    "Total(b)": 'E (MeV)',
    "Capture(b)": "capture cross section",
    "Fission(b)": "fission cross section"
}

YAXIS_MAP = {
    "Elastic(b)": 'cross section, barn',
    "Inelastic(b)": 'cross section, barn',
    "Total(b)": 'cross section, barn',
}

OBSERVABLE_MAP = {
    "Elastic(b)": 'elastic cross section',
    "Inelastic(b)": 'inelastic cross section',
    "Total(b)": 'total cross section',
}


def extractObservable(filename):
    r_value = 0
    re_value = 0
    with open(filename) as myfile:
        for line in myfile:
            if '(Dose/EnergyFluence)/Mass_energy_transfer' in line:
                print(line)
                line = line.split()
                r_value = round(Decimal(line[-3]), PRECISE)
                re_value = round(Decimal(line[-1]), PRECISE)
                break
    return r_value, re_value


class Test (BaseParser):
    TEST = "fanoCavity"
    IGNOREKEYS = ["ROVER"]

    def parse(self, jobs):
        job = jobs[0]
        print(job)
        rover_values = set([x["ROVER"] for x in jobs])
        print(rover_values)
        common_data = []
        for rover in rover_values:
            rover_jobs = [x for x in jobs if x["ROVER"] == rover]
            r_value_mean = 0.
            re_value_mean = 0.
            njobs = 0.
            for rover_job in rover_jobs:
                filepath = os.path.join(rover_job["path"], "test_stdout.txt")
                print(filepath)
                r_value, re_value = extractObservable(filepath)
                r_value_mean += r_value
                re_value_mean += re_value
                njobs += 1.
            common_data.append(("ratio", (float(rover), r_value_mean/njobs, re_value_mean/(njobs*njobs))))
        print("common_data", common_data)
        data = [x[1] for x in common_data if x[0] == "ratio"]
        valueslist = sorted([(x[0], x[1], x[2]) for x in data], key=lambda x: x[0])
        xvalues = [x[0] for x in valueslist]
        yvalues = [x[1] for x in valueslist]
        err_yvalues = [x[2] for x in valueslist] 
        print(xvalues)
        print(yvalues)
        print(err_yvalues)

#       fixing model names
        model_name = "em" + job["PHYSLIST"];
        if 'WVI' in model_name or 'GS' in model_name:
            print("here")
            model_name = model_name.replace('_','')
            print(model_name)
        rjson = getJSON(job, "chart",
                            mctool_name="GEANT4",
                            mctool_model=model_name,
                            observableName="dose ratio (sim/theor)",
                            targetName="Water",
                            beamParticle=job["PARTICLE"],
                            beamEnergies=[float(job["ENERGY"])],
                            title="dose ratio (sim/theor)",
                            xAxisName="dRoverRange",
                            yAxisName="dose ratio (sim/theory)",
                            xValues=xvalues,
                            yValues=yvalues,
                            yStatErrorsPlus=err_yvalues,
                            yStatErrorsMinus=err_yvalues
        )

        yield rjson
