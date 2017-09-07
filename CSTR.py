#!/usr/bin/env python3.6

# Everything in here is based on CADET3.pdf in the same directory
# 

# Basic Python CADET file based interface compatible with CADET 3.0 and 3.1
# Some additional fields have been added so that the generated simulations will also
# work in 3.1 and where those differences are I have noted them.
# This whole file follows the CADET pdf documentation. I have broken the system up into many
# functions in order to make it simpler and to make code reuse easier.

# Normally the main function is placed at the bottom of the file but I have placed it at the top so that
# This interface is more like a tutorial and can be read from the top down and any given function
# can be drilled into to learn more about it.

# The core part of python with CADET is HDF5 and numpy
import h5py
import numpy as np

#used to run CADET
import subprocess
import io

#use to render results
import matplotlib.pyplot as plt

import types

#location of the cadet binary
cadet_location = "C:/Users/kosh_000/cadet_build/CADET-dev/MS_SMKL_RELEASE/bin/cadet-cli.exe"

# Helper functions that make it easier to set the values in the HDF5 file
# In the CADET pdf file each value in the hdf5 file has a type. The functions
# below match those types.

def set_int(node, nameH5, value):
    "set one or more integers in the hdf5 file"
    data = np.array(value, dtype="i4")
    if node.get(nameH5, None) is not None:
        del node[nameH5]
    node.create_dataset(nameH5, data=data, maxshape=tuple(None for i in range(data.ndim)), fillvalue=[0])

def set_double(node, nameH5, value):
    "set one or more doubles in the hdf5 file"
    data = np.array(value, dtype="f8")
    if node.get(nameH5, None) is not None:
        del node[nameH5]
    node.create_dataset(nameH5, data=data, maxshape=tuple(None for i in range(data.ndim)), fillvalue=[0])

def set_string(node, nameH5, value):
    "set a string value in the hdf5 file"
    if isinstance(value, list):
        dtype = 'S' + str(len(value[0])+1)
    else:
        dtype = 'S' + str(len(value)+1)
    data = np.array(value, dtype=dtype)
    if node.get(nameH5, None) is not None:
        del node[nameH5]
    node.create_dataset(nameH5, data=data)


def main():
    obj = types.SimpleNamespace()
    obj.filename = "CSTR_V1_C1.h5"
    obj.volume = 1
    obj.conc = 1
    obj.linear = 0
    obj.flowIn = 1
    obj.flowOut = 1
    obj.porosity = 1
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_V1_C2.h5"
    obj.volume = 1
    obj.conc = 2
    obj.flowIn = 1
    obj.flowOut = 1
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_V1_C2_F2_F1.h5"
    obj.volume = 1
    obj.conc = 2
    obj.flowIn = 2
    obj.flowOut = 1
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_V10_C1_F2_F1.h5"
    obj.volume = 10
    obj.conc = 1
    obj.flowIn = 2
    obj.flowOut = 1
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_V10_C2.h5"
    obj.volume = 10
    obj.conc = 2
    obj.flowIn = 1
    obj.flowOut = 1
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_V100_C1_F2_F2.h5"
    obj.volume = 100
    obj.conc = 1
    obj.flowIn = 2
    obj.flowOut = 2
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_V100_C2.h5"
    obj.volume = 100
    obj.conc = 2
    obj.flowIn = 1
    obj.flowOut = 1
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_V100_C2_F2_F1.h5"
    obj.volume = 100
    obj.conc = 2
    obj.flowIn = 2
    obj.flowOut = 1
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_sens.h5"
    obj.porosity = 0.5
    obj.volume = 1
    obj.conc = 2
    obj.linear = 0.01
    obj.flowIn = 2
    obj.flowOut = 1
    obj.filter = 0.01
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_con_down.h5"
    obj.porosity = 0.5
    obj.volume = 1
    obj.conc = 2 - 1e-6
    obj.linear = 0.01
    obj.flowIn = 2
    obj.flowOut = 1
    obj.filter = 0.01
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_con_up.h5"
    obj.porosity = 0.5
    obj.volume = 1
    obj.conc = 2 + 1e-6
    obj.linear = 0.01
    obj.flowIn = 2
    obj.flowOut = 1
    obj.filter = 0.01
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_lin_down.h5"
    obj.porosity = 0.5
    obj.volume = 1
    obj.conc = 2
    obj.linear = 0.01 - 1e-6
    obj.flowIn = 2
    obj.flowOut = 1
    obj.filter = 0.01
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_lin_up.h5"
    obj.porosity = 0.5
    obj.volume = 1
    obj.conc = 2
    obj.linear = 0.01 + 1e-6
    obj.flowIn = 2
    obj.flowOut = 1
    obj.filter = 0.01
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_por_up.h5"
    obj.volume = 1
    obj.conc = 2
    obj.linear = 0.01
    obj.porosity = 0.5 + 1e-6
    obj.flowIn = 2
    obj.flowOut = 1
    obj.filter = 0.01
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_por_down.h5"
    obj.volume = 1
    obj.conc = 2
    obj.linear = 0.01
    obj.porosity = 0.5 - 1e-6
    obj.flowIn = 2
    obj.flowOut = 1
    obj.filter = 0.01
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_filter_up.h5"
    obj.volume = 1
    obj.conc = 2
    obj.linear = 0.01
    obj.porosity = 0.5
    obj.flowIn = 2
    obj.flowOut = 1
    obj.filter = 0.01 + 1e-6
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

    obj.filename = "CSTR_filter_down.h5"
    obj.volume = 1
    obj.conc = 2
    obj.linear = 0.01
    obj.porosity = 0.5
    obj.flowIn = 2
    obj.flowOut = 1
    obj.filter = 0.01 - 1e-6
    createSimulation(obj)
    runSimulation(obj)
    plotSimulation(obj)

def createSimulation(obj):
    with h5py.File(obj.filename, 'w') as f:
        createInput(f, obj)

def createInput(f, obj):
    input = f.create_group("input")
    createModel(input, obj)
    createReturn(input)
    createSolver(input)
    createSensitivity(input)

def createModel(input, obj):
    model = input.create_group("model")
    set_int(model, 'NUNITS', 3)

    # Part of CADET 3.1
    solver = model.create_group('solver')
    set_int(solver, 'GS_TYPE', 1)
    set_int(solver, 'MAX_KRYLOV', 0)
    set_int(solver, 'MAX_RESTARTS', 0)
    set_double(solver, 'SCHUR_SAFETY', 1.0e-8)

    createConnections(model, obj)
    createInlet(model, obj)
    createColumn(model, obj)
    createOutlet(model)

def createConnections(model, obj):
    connections = model.create_group("connections")
    set_int(connections, 'NSWITCHES', 1)
    createSwitch(connections, obj)

def createSwitch(connections, obj):
    """Create a switch in the system. In 3.0 these are very limited but in 3.1 they allow arbitrary connections between unit operations.
    The format is a set of 4 numbers (Source Unit Operation ID, Destination Unit Operation ID, Source Component ID, Destination Component ID. If the
    Source and Destination Component IDs are set to -1 that means connect all to all and this is the most common setup."""

    # CADET uses 0 based numbers and 3 digits to identify anything there are multiples of like unit operations, sections, switches etc
    switch_000 = connections.create_group("switch_000")

    #Connect all of Inlet [0] to Column [1] and Column [1] to Outlet [2]
    set_int(switch_000, 'CONNECTIONS', [0, 1, -1, -1, obj.flowIn,
                                        1, 2, -1, -1, obj.flowOut])
    set_int(switch_000, 'SECTION', 0)

def createInlet(model, obj):
    inlet = model.create_group("unit_000")

    set_string(inlet, 'INLET_TYPE', 'PIECEWISE_CUBIC_POLY')
    set_int(inlet, 'NCOMP', 1)
    set_string(inlet, 'UNIT_TYPE', 'INLET')

    sec = inlet.create_group('sec_000')

    set_double(sec, 'CONST_COEFF', [obj.conc,])
    set_double(sec, 'LIN_COEFF', [obj.linear,])
    set_double(sec, 'QUAD_COEFF', [0.0,])
    set_double(sec, 'CUBE_COEFF', [0.0,])

def createColumn(model, obj):
    column = model.create_group('unit_001')

    set_double(column, 'INIT_C', [1.0,])
    set_double(column, 'INIT_VOLUME', obj.volume)
    set_double(column, 'FLOWRATE_FILTER', [0.0,])
    set_int(column, 'NCOMP', 1)
    set_string(column, 'UNIT_TYPE', 'CSTR')

def createOutlet(model):
    outlet = model.create_group('unit_002')
    set_int(outlet, 'NCOMP', 1)
    set_string(outlet, 'UNIT_TYPE', 'OUTLET')

def createReturn(input):
    ret = input.create_group('return')

    set_int(ret, 'WRITE_SOLUTION_TIMES', 1)

    createColumnOutput(ret)

def createColumnOutput(ret):
    column = ret.create_group('unit_001')

    set_int(column, 'WRITE_SENS_BULK', 0)
    set_int(column, 'WRITE_SENS_INLET', 1)
    set_int(column, 'WRITE_SENS_OUTLET', 1)
    set_int(column, 'WRITE_SENS_FLUX', 0)
    set_int(column, 'WRITE_SENS_PARTICLE', 0)

    set_int(column, 'WRITE_SOLUTION_BULK', 0)
    set_int(column, 'WRITE_SOLUTION_INLET', 1)
    set_int(column, 'WRITE_SOLUTION_OUTLET', 1)
    set_int(column, 'WRITE_SOLUTION_FLUX', 0)
    set_int(column, 'WRITE_SOLUTION_PARTICLE', 0)


    column = ret.create_group('unit_002')

    set_int(column, 'WRITE_SENS_BULK', 0)
    set_int(column, 'WRITE_SENS_INLET', 1)
    set_int(column, 'WRITE_SENS_OUTLET', 1)
    set_int(column, 'WRITE_SENS_FLUX', 0)
    set_int(column, 'WRITE_SENS_PARTICLE', 0)

    set_int(column, 'WRITE_SOLUTION_BULK', 0)
    set_int(column, 'WRITE_SOLUTION_INLET', 1)
    set_int(column, 'WRITE_SOLUTION_OUTLET', 1)
    set_int(column, 'WRITE_SOLUTION_FLUX', 0)
    set_int(column, 'WRITE_SOLUTION_PARTICLE', 0)
    
def createSolver(input):
    solver = input.create_group("solver")
    set_int(solver, 'NTHREADS', 1)
    set_double(solver, 'USER_SOLUTION_TIMES', range(0, 101))
    set_int(solver, 'CONSISTENT_INIT_MODE', 1)

    createSections(solver)
    createTimeIntegrator(solver)

def createSections(solver):
    sections = solver.create_group("sections")
    set_int(sections, 'NSEC', 1)
    set_int(sections, 'SECTION_CONTINUITY', [0,0])
    set_double(sections, 'SECTION_TIMES', [0, 100.0])

def createTimeIntegrator(solver):
    time_integrator = solver.create_group("time_integrator")
    set_double(time_integrator, 'ABSTOL', 1e-8)
    set_double(time_integrator, 'ALGTOL', 1e-12)
    set_double(time_integrator, 'INIT_STEP_SIZE', 1e-6)
    set_int(time_integrator, 'MAX_STEPS', 10000)
    set_double(time_integrator, 'RELTOL', 1e-6)

def createSensitivity(input):
    sensitivity = input.create_group('sensitivity')
    set_int(sensitivity, 'NSENS', 4)
    set_string(sensitivity, 'SENS_METHOD', 'ad1')

    param = sensitivity.create_group('param_000')
    set_int(param, 'SENS_UNIT', 0)    
    set_string(param, 'SENS_NAME', 'CONST_COEFF')
    set_int(param, 'SENS_COMP', 0)
    set_int(param, 'SENS_REACTION', -1)
    set_int(param, 'SENS_BOUNDPHASE', -1)
    set_int(param, 'SENS_SECTION', 0)

    set_double(param, 'SENS_ABSTOL', 1e-6)
    set_double(param, 'SENS_FACTOR', 1)

    param = sensitivity.create_group('param_001')
    set_int(param, 'SENS_UNIT', 0)    
    set_string(param, 'SENS_NAME', 'LIN_COEFF')
    set_int(param, 'SENS_COMP', 0)
    set_int(param, 'SENS_REACTION', -1)
    set_int(param, 'SENS_BOUNDPHASE', -1)
    set_int(param, 'SENS_SECTION', 0)

    set_double(param, 'SENS_ABSTOL', 1e-6)
    set_double(param, 'SENS_FACTOR', 1)

    param = sensitivity.create_group('param_002')
    set_int(param, 'SENS_UNIT', 1)    
    set_string(param, 'SENS_NAME', 'POROSITY')
    set_int(param, 'SENS_COMP', -1)
    set_int(param, 'SENS_REACTION', -1)
    set_int(param, 'SENS_BOUNDPHASE', -1)
    set_int(param, 'SENS_SECTION', -1)

    set_double(param, 'SENS_ABSTOL', 1e-6)
    set_double(param, 'SENS_FACTOR', 1)

    param = sensitivity.create_group('param_003')
    set_int(param, 'SENS_UNIT', 1)    
    set_string(param, 'SENS_NAME', 'FLOWRATE_FILTER')
    set_int(param, 'SENS_COMP', -1)
    set_int(param, 'SENS_REACTION', -1)
    set_int(param, 'SENS_BOUNDPHASE', -1)
    set_int(param, 'SENS_SECTION', -1)

    set_double(param, 'SENS_ABSTOL', 1e-6)
    set_double(param, 'SENS_FACTOR', 1)

def runSimulation(obj):
    proc = subprocess.Popen([cadet_location, obj.filename], bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    proc.wait()
    print("CADET Output")
    print(stdout)
    print("CADET Errors")
    print(stderr)

def plotSimulation(obj):
    with h5py.File(obj.filename, 'r') as h5:
        f, (ax1, ax2) = plt.subplots(1, 2, figsize=[16, 8])
        plotInlet(ax1, h5)
        plotOutlet(ax2, h5)
        f.tight_layout()
        plt.show()

def plotInlet(axis, h5):
    solution_times = np.array(h5['/output/solution/SOLUTION_TIMES'].value)
        
    inlet = np.array(h5['/output/solution/unit_001/SOLUTION_INLET_COMP_000'].value)
   

    axis.set_title("Inlet")
    axis.plot(solution_times, inlet, 'b-', label="Product")
    axis.set_xlabel('time (s)')
        
    # Make the y-axis label, ticks and tick labels match the line color.
    axis.set_ylabel('mMol', color='b')
    axis.tick_params('y', colors='b')

    lines, labels = axis.get_legend_handles_labels()
    axis.legend(lines, labels, loc=0)


def plotOutlet(axis, h5):
    solution_times = np.array(h5['/output/solution/SOLUTION_TIMES'].value)
        
    outlet = np.array(h5['/output/solution/unit_001/SOLUTION_OUTLET_COMP_000'].value)

    axis.set_title("Output")
    axis.plot(solution_times, outlet, 'b-', label="Product")
    axis.set_xlabel('time (s)')
        
    # Make the y-axis label, ticks and tick labels match the line color.
    axis.set_ylabel('mMol', color='b')
    axis.tick_params('y', colors='b')

    lines, labels = axis.get_legend_handles_labels()
    axis.legend(lines, labels, loc=0)


if __name__ == "__main__":
    import sys
    print(sys.version)
    main()
