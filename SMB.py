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
import math

#used to run CADET
import subprocess
import io

#use to render results
import matplotlib.pyplot as plt

#location of the cadet binary
#cadet_location = "C:\\Users\\kosh_000\\cadet_build\\CADET-dev\\MS_MKL_RELEASE\\bin\\cadet-cli.exe"
cadet_location = "C:\\Users\\kosh_000\\cadet_build\\CADET-dev\\MS_SMKL_DEBUG\\bin\\cadet-cli.exe"

# Helper functions that make it easier to set the values in the HDF5 file
# In the CADET pdf file each value in the hdf5 file has a type. The functions
# below match those types.

#number of columns in a cycle
cycle_size = 4

#number of cycles
cycles = 17

#number of times flows have to be expanded for a 4-zone model
repeat_size = int(cycle_size/4)

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
    filename = "SMB.h5"
    createSimulation(filename)
    print("Simulated Created")
    runSimulation(filename)
    print("Simulation Run")
    plotSimulation(filename)

def createSimulation(filename):
    with h5py.File(filename, 'w') as f:
        createInput(f)

def createInput(f):
    input = f.create_group("input")
    createModel(input)
    createReturn(input)
    createSolver(input)

def createModel(input):
    model = input.create_group("model")
    set_int(model, 'NUNITS', 8)

    # Part of CADET 3.1
    solver = model.create_group('solver')
    set_int(solver, 'GS_TYPE', 1)
    set_int(solver, 'MAX_KRYLOV', 0)
    set_int(solver, 'MAX_RESTARTS', 0)
    set_double(solver, 'SCHUR_SAFETY', 1.0e-8)

    createConnections(model)
    createInlet(model)
    createOutlet(model)
    createColumn(model)
    

def createConnections(model):
    connections = model.create_group("connections")
    set_int(connections, 'NSWITCHES', 4)
    createSwitch(connections)

def gen_connections(units, step, flows, flows_static):
    temp = []
    connections = zip(units, np.roll(units,-1), flows)
    io = np.roll(units, step)[[0, repeat_size*2, repeat_size-1, repeat_size*3-1]]
    ios = list(zip([0, 1, 2, 3], io))

    for connection in connections:
        temp.append([connection[0], connection[1], -1, -1, connection[2]])
    #inputs
    idx = 0
    for io in ios[:2]:
        temp.append([io[0], io[1], -1, -1, flows_static[idx]])
        idx+=1;
    #outputs
    for io in ios[2:]:
        temp.append([io[1], io[0], -1, -1, flows_static[idx]])
        idx+=1;
    return temp

def createSwitch(connections):
    """Create SMB switches. We only need to create the switches needed for one cycle. CADET will cycle the switches on its own as needed"""
    flows = [7.66E-07, 7.66E-07, 8.08E-07, 8.08E-07]
    flows_static = np.array([0.98e-7, 1.96e-7, 1.4e-7, 1.54e-7])

    units = range(4, 4+cycle_size)

    for i in range(cycle_size):
        switch_000 = connections.create_group("switch_%03d" % i)

        #Connect all of Inlet [0] to Column [1] and Column [1] to Outlet [2]
        set_double(switch_000, 'CONNECTIONS', gen_connections(units, -i, np.array(list(np.roll(flows, i))), flows_static ))
        set_int(switch_000, 'SECTION', i)

def createInlet(model):
    inlet = model.create_group("unit_000")

    set_string(inlet, 'INLET_TYPE', 'PIECEWISE_CUBIC_POLY')
    set_int(inlet, 'NCOMP', 2)
    set_string(inlet, 'UNIT_TYPE', 'INLET')

    for i in range(cycle_size):
        #section
        section = inlet.create_group("sec_%03d" % i)

        set_double(section, 'CONST_COEFF', [0.55/180.16, 0.55/180.16])
        #set_double(section, 'CONST_COEFF', [0.00305284191829485, 0.00305284191829485])
        set_double(section, 'CUBE_COEFF', [0, 0])
        set_double(section, 'LIN_COEFF', [0, 0])
        set_double(section, 'QUAD_COEFF', [0, 0])

    inlet = model.create_group("unit_001")

    set_string(inlet, 'INLET_TYPE', 'PIECEWISE_CUBIC_POLY')
    set_int(inlet, 'NCOMP', 2)
    set_string(inlet, 'UNIT_TYPE', 'INLET')

    for i in range(cycle_size):
        #section
        section = inlet.create_group("sec_%03d" % i)

        set_double(section, 'CONST_COEFF', [0, 0])
        set_double(section, 'CUBE_COEFF', [0, 0])
        set_double(section, 'LIN_COEFF', [0, 0])
        set_double(section, 'QUAD_COEFF', [0, 0])

def createColumn(model):

    for unit in range(4, 4 + cycle_size):

        column = model.create_group("unit_%03d" % unit)

        set_string(column, 'UNIT_TYPE', 'GENERAL_RATE_MODEL')
        set_int(column, 'NCOMP', 2)
        set_double(column, 'CROSS_SECTION_AREA', math.pi * (0.02**2)/4.0)
        set_double(column, 'COL_DISPERSION', 3.8148e-20)
        set_double(column, 'COL_LENGTH', 0.25)
        set_double(column, 'COL_POROSITY', 0.83)
        #set_double(column, 'FILM_DIFFUSION', [1.6e4, 1.6e4])
        set_double(column, 'INIT_C', [0.0, 0.0])
        set_double(column, 'INIT_Q', [0.0, 0.0])
        #set_double(column, 'PAR_DIFFUSION', [5e-5, 5e-5])
        set_double(column, 'FILM_DIFFUSION', [100, 100])
        set_double(column, 'PAR_DIFFUSION', [1.6e4, 1.6e4])

        set_double(column, 'PAR_RADIUS', 0.0005)
        set_double(column, 'PAR_POROSITY', 0.000001)
        set_double(column, 'PAR_SURFDIFFUSION', [0.0, 0.0])
        set_string(column, 'ADSORPTION_MODEL', 'LINEAR')
        set_double(column, "VELOCITY", 1.0)

        createAdsorption(column)
        createDiscretization(column)

def createAdsorption(column):
    ads = column.create_group('adsorption')

    set_int(ads, 'IS_KINETIC', 0)
    set_double(ads, 'LIN_KA', [5.72, 7.7])
    set_double(ads, 'LIN_KD', [1, 1])

def createDiscretization(column):
    disc = column.create_group('discretization')

    set_int(disc, 'GS_TYPE', 1)
    set_int(disc, 'MAX_KRYLOV', 0)
    set_int(disc, 'MAX_RESTARTS', 0)
    set_int(disc, 'NBOUND', [1, 1])
    set_int(disc, 'NCOL', 40)
    set_int(disc, 'NPAR', 1)
    set_string(disc, 'PAR_DISC_TYPE', 'EQUIDISTANT_PAR')
    set_double(disc, 'SCHUR_SAFETY', 1.0e-8)
    set_int(disc, 'USE_ANALYTIC_JACOBIAN',  1)

    createWENO(disc)

def createWENO(disc):
    weno = disc.create_group("weno")
    set_int(weno, 'BOUNDARY_MODEL', 0)
    set_double(weno, 'WENO_EPS', 1e-12)
    set_int(weno, 'WENO_ORDER', 3)

def createOutlet(model):
    outlet = model.create_group('unit_002')
    set_int(outlet, 'NCOMP', 2)
    set_string(outlet, 'UNIT_TYPE', 'OUTLET')

    outlet = model.create_group('unit_003')
    set_int(outlet, 'NCOMP', 2)
    set_string(outlet, 'UNIT_TYPE', 'OUTLET')

def createReturn(input):
    ret = input.create_group('return')

    set_int(ret, 'WRITE_SOLUTION_TIMES', 1)
    set_int(ret, 'WRITE_SOLUTION_LAST', 1)

    createColumnOutput(ret)

def createColumnOutput(ret):
    column = ret.create_group('unit_002')

    set_int(column, 'WRITE_SENS_COLUMN', 0)
    set_int(column, 'WRITE_SENS_COLUMN_INLET', 0)
    set_int(column, 'WRITE_SENS_COLUMN_OUTLET', 0)
    set_int(column, 'WRITE_SENS_FLUX', 0)
    set_int(column, 'WRITE_SENS_PARTICLE', 0)

    set_int(column, 'WRITE_SOLUTION_COLUMN', 0)
    set_int(column, 'WRITE_SOLUTION_COLUMN_INLET', 1)
    set_int(column, 'WRITE_SOLUTION_COLUMN_OUTLET', 1)
    set_int(column, 'WRITE_SOLUTION_FLUX', 0)
    set_int(column, 'WRITE_SOLUTION_PARTICLE', 0)

    column = ret.create_group('unit_003')

    set_int(column, 'WRITE_SENS_COLUMN', 0)
    set_int(column, 'WRITE_SENS_COLUMN_INLET', 0)
    set_int(column, 'WRITE_SENS_COLUMN_OUTLET', 0)
    set_int(column, 'WRITE_SENS_FLUX', 0)
    set_int(column, 'WRITE_SENS_PARTICLE', 0)

    set_int(column, 'WRITE_SOLUTION_COLUMN', 0)
    set_int(column, 'WRITE_SOLUTION_COLUMN_INLET', 1)
    set_int(column, 'WRITE_SOLUTION_COLUMN_OUTLET', 1)
    set_int(column, 'WRITE_SOLUTION_FLUX', 0)
    set_int(column, 'WRITE_SOLUTION_PARTICLE', 0)
    
def createSolver(input):
    solver = input.create_group("solver")
    set_int(solver, 'NTHREADS', 0)
    set_double(solver, 'USER_SOLUTION_TIMES', np.linspace(0, cycles*180*4, 1000*cycle_size*cycles))

    createSections(solver)
    createTimeIntegrator(solver)

def createSections(solver):
    sections = solver.create_group("sections")
    set_int(sections, 'NSEC', cycle_size*cycles)
    set_int(sections, 'SECTION_CONTINUITY', [0] * (cycle_size*cycles -1))
    set_double(sections, 'SECTION_TIMES', [float(i) * 180*4.0/cycle_size for i in range(cycle_size*cycles+1)])

def createTimeIntegrator(solver):
    time_integrator = solver.create_group("time_integrator")
    set_double(time_integrator, 'ABSTOL', 1e-10)
    set_double(time_integrator, 'ALGTOL', 1e-10)
    set_double(time_integrator, 'INIT_STEP_SIZE', 1e-14)
    set_int(time_integrator, 'MAX_STEPS', 5e6)
    set_double(time_integrator, 'RELTOL', 1e-6)

def runSimulation(filename):
    proc = subprocess.Popen([cadet_location, filename], bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    proc.wait()
    print("CADET Output")
    print(stdout)
    print("CADET Errors")
    print(stderr)

def plotSimulation(filename):
    with h5py.File(filename, 'r') as h5:
        plotOutlet(h5)

def plotOutlet(h5):
    solution_times = np.array(h5['/output/solution/SOLUTION_TIMES'].value)
        
    e_0 = np.array(h5['/output/solution/unit_002/SOLUTION_COLUMN_OUTLET_COMP_000'].value)
    e_1 = np.array(h5['/output/solution/unit_002/SOLUTION_COLUMN_OUTLET_COMP_001'].value)
    
    r_0 = np.array(h5['/output/solution/unit_003/SOLUTION_COLUMN_OUTLET_COMP_000'].value)
    r_1 = np.array(h5['/output/solution/unit_003/SOLUTION_COLUMN_OUTLET_COMP_001'].value)

    fig = plt.figure(figsize=[10, 2*10])

    graph = fig.add_subplot(2, 1, 1)
    graph.set_title("Extract")

    graph.plot(solution_times, e_0, 'r', label='1')
    graph.plot(solution_times, e_1, 'g', label='2')
    graph.legend()
        
    graph = fig.add_subplot(2, 1, 2)
    graph.set_title("Raffinate")

    graph.plot(solution_times, r_0, 'r', label='1')
    graph.plot(solution_times, r_1, 'g', label='2')
    graph.legend()
    plt.show()


if __name__ == "__main__":
    import sys
    print(sys.version)
    main()
