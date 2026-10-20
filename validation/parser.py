#!/usr/bin/env python

# fanoCavity portal parser: metadata() reads the macro, parse() the captured stdout.
#
# Ported from geant-config-generator/tests/geant4/fanoCavity/parser.py (which
# targeted the old gts.BaseParser queue API) to the module-level metadata()/parse()
# API expected by ci-workflows/validation/export.py.
import os

from geantval import getJSON, one_command, single_run

# Particle (gamma) and energy (1.25 MeV, Co-60-like) are hardcoded in
# PrimaryGeneratorAction.cc, not configurable from the macro.
BEAM_PARTICLE = "gamma"
BEAM_ENERGY_MEV = 1.25


def extract_ratio(filename):
    with open(filename) as f:
        for line in f:
            if "(Dose/EnergyFluence)/Mass_energy_transfer" in line:
                fields = line.split()
                return float(fields[-3]), float(fields[-1])
    raise ValueError("No '(Dose/EnergyFluence)/Mass_energy_transfer' line found in " + filename)


def model_name(physlist):
    name = "em" + physlist
    if "WVI" in name or "GS" in name:
        name = name.replace("_", "")
    return name


def metadata(commands):
    single_run(commands)
    physlist = one_command(commands, "/testem/phys/addPhysics")
    step_function = one_command(commands, "/process/eLoss/StepFunction")
    rover = float(step_function.split()[0])
    return {"TEST": "fanoCavity", "PHYSLIST": physlist, "ROVER": rover}


def parse(job):
    filepath = os.path.join(job["path"], "test_stdout.txt")
    ratio, error = extract_ratio(filepath)

    rjson = getJSON(job, "chart",
                     mctool_name="GEANT4",
                     mctool_model=model_name(job["PHYSLIST"]),
                     observableName="dose ratio (sim/theor)",
                     targetName="Water",
                     beamParticle=BEAM_PARTICLE,
                     beamEnergies=[BEAM_ENERGY_MEV],
                     title="dose ratio (sim/theor)",
                     xAxisName="dRoverRange",
                     yAxisName="dose ratio (sim/theory)",
                     xValues=[job["ROVER"]],
                     yValues=[ratio],
                     yStatErrorsPlus=[error],
                     yStatErrorsMinus=[error])
    yield rjson
