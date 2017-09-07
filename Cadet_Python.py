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

#location of the cadet binary
cadet_location = "C:\\Users\\kosh_000\\cadet_build\\cadet_31\\cadet\\MS_SMKL_RELEASE\\bin\\cadet-cli.exe"

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
    filename = "LWE.h5"
    createSimulation(filename)
    runSimulation(filename)
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
    set_int(model, 'NUNITS', 3)

    # Part of CADET 3.1
    set_int(model, 'GS_TYPE', 1)
    set_int(model, 'MAX_KRYLOV', 0)
    set_int(model, 'MAX_RESTARTS', 0)
    set_double(model, 'SCHUR_SAFETY', 1.0e-8)

    createConnections(model)
    createInlet(model)
    createColumn(model)
    createOutlet(model)

def createConnections(model):
    connections = model.create_group("connections")
    set_int(connections, 'NSWITCHES', 1)
    createSwitch(connections)

def createSwitch(connections):
    """Create a switch in the system. In 3.0 these are very limited but in 3.1 they allow arbitrary connections between unit operations.
    The format is a set of 4 numbers (Source Unit Operation ID, Destination Unit Operation ID, Source Component ID, Destination Component ID. If the
    Source and Destination Component IDs are set to -1 that means connect all to all and this is the most common setup."""

    # CADET uses 0 based numbers and 3 digits to identify anything there are multiples of like unit operations, sections, switches etc
    switch_000 = connections.create_group("switch_000")

    #Connect all of Inlet [0] to Column [1] and Column [1] to Outlet [2]
    set_int(switch_000, 'CONNECTIONS', [0, 1, -1, -1, 1, 2, -1, -1])
    set_int(switch_000, 'SECTION', 0)

def createInlet(model):
    inlet = model.create_group("unit_000")

    set_string(inlet, 'INLET_TYPE', 'PIECEWISE_CUBIC_POLY')
    set_int(inlet, 'NCOMP', 4)
    set_string(inlet, 'UNIT_TYPE', 'INLET')

    # CADET 3.1
    set_double(inlet, 'FLOW', 1.0)
    
    createLoad(inlet)
    createWash(inlet)
    createElute(inlet)

def createLoad(inlet):
    sec = inlet.create_group('sec_000')

    set_double(sec, 'CONST_COEFF', [50.0, 1.0, 1.0, 1.0])
    set_double(sec, 'LIN_COEFF', [0.0, 0.0, 0.0, 0.0])
    set_double(sec, 'QUAD_COEFF', [0.0, 0.0, 0.0, 0.0])
    set_double(sec, 'CUBE_COEFF', [0.0, 0.0, 0.0, 0.0])

def createWash(inlet):
    sec = inlet.create_group('sec_001')

    set_double(sec, 'CONST_COEFF', [50.0, 0.0, 0.0, 0.0])
    set_double(sec, 'LIN_COEFF', [0.0, 0.0, 0.0, 0.0])
    set_double(sec, 'QUAD_COEFF', [0.0, 0.0, 0.0, 0.0])
    set_double(sec, 'CUBE_COEFF', [0.0, 0.0, 0.0, 0.0])

def createElute(inlet):
    sec = inlet.create_group('sec_002')

    set_double(sec, 'CONST_COEFF', [100.0, 0.0, 0.0, 0.0])
    set_double(sec, 'LIN_COEFF', [0.2, 0.0, 0.0, 0.0])
    set_double(sec, 'QUAD_COEFF', [0.0, 0.0, 0.0, 0.0])
    set_double(sec, 'CUBE_COEFF', [0.0, 0.0, 0.0, 0.0])

def createColumn(model):
    column = model.create_group('unit_001')

    set_string(column, 'ADSORPTION_MODEL', 'STERIC_MASS_ACTION')
    set_double(column, 'COL_DISPERSION', 5.75e-8)
    set_double(column, 'COL_LENGTH', 0.014)
    set_double(column, 'COL_POROSITY', 0.37)
    set_double(column, 'FILM_DIFFUSION', [6.9e-6, 6.9e-6, 6.9e-6, 6.9e-6])
    set_double(column, 'INIT_C', [50.0, 0.0, 0.0, 0.0])
    set_double(column, 'INIT_Q', [1200.0, 0.0, 0.0, 0.0])
    set_int(column, 'NCOMP', 4)
    set_double(column, 'PAR_DIFFUSION', [7e-10, 6.07e-11, 6.07e-11, 6.07e-11])
    set_double(column, 'PAR_POROSITY', 0.75)
    set_double(column, 'PAR_RADIUS', 4.5e-5)
    set_double(column, 'PAR_SURFDIFFUSION', [0.0, 0.0, 0.0, 0.0])
    set_string(column, 'UNIT_TYPE', 'GENERAL_RATE_MODEL')
    set_double(column, 'VELOCITY', 5.75e-4)
    
    # CADET 3.1
    set_double(column, 'FLOW', 1.0)

    createAdsorption(column)
    createDiscretization(column)

def createAdsorption(column):
    ads = column.create_group('adsorption')

    set_int(ads, 'IS_KINETIC', 0)
    set_double(ads, 'SMA_KA', [0.0, 35.5, 1.59, 7.7])
    set_double(ads, 'SMA_KD', [0, 1000, 1000, 1000])
    set_double(ads, 'SMA_LAMBDA', 1200)
    set_double(ads, 'SMA_NU', [0.0, 4.7, 5.29, 3.7])
    set_double(ads, 'SMA_SIGMA', [0, 11.83, 10.6, 10.0])

def createDiscretization(column):
    disc = column.create_group('discretization')

    set_int(disc, 'GS_TYPE', 1)
    set_int(disc, 'MAX_KRYLOV', 0)
    set_int(disc, 'MAX_RESTARTS', 10)
    set_int(disc, 'NBOUND', [1, 1, 1, 1])
    set_int(disc, 'NCOL', 50)
    set_int(disc, 'NPAR', 10)
    set_string(disc, 'PAR_DISC_TYPE', 'EQUIDISTANT_PAR')
    set_double(disc, 'SCHUR_SAFETY', 1.0e-8)
    set_int(disc, 'USE_ANALYTIC_JACOBIAN',  1)

    createWENO(disc)

def createWENO(disc):
    weno = disc.create_group("weno")
    set_int(weno, 'BOUNDARY_MODEL', 0)
    set_double(weno, 'WENO_EPS', 1e-10)
    set_int(weno, 'WENO_ORDER', 3)

def createOutlet(model):
    outlet = model.create_group('unit_002')
    set_int(outlet, 'NCOMP', 4)
    set_string(outlet, 'UNIT_TYPE', 'OUTLET')

    # CADET 3.1
    set_double(outlet, 'FLOW', 1.0)

def createReturn(input):
    ret = input.create_group('return')

    set_int(ret, 'WRITE_SOLUTION_TIMES', 1)

    createColumnOutput(ret)

def createColumnOutput(ret):
    column = ret.create_group('unit_001')

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
    set_int(solver, 'NTHREADS', 1)
    set_double(solver, 'USER_SOLUTION_TIMES', range(0, 1500+1))

    createSections(solver)
    createTimeIntegrator(solver)

def createSections(solver):
    sections = solver.create_group("sections")
    set_int(sections, 'NSEC', 3)
    set_int(sections, 'SECTION_CONTINUITY', [0,0])
    set_double(sections, 'SECTION_TIMES', [0, 10, 90, 1500])

def createTimeIntegrator(solver):
    time_integrator = solver.create_group("time_integrator")
    set_double(time_integrator, 'ABSTOL', 1e-8)
    set_double(time_integrator, 'ALGTOL', 1e-12)
    set_double(time_integrator, 'INIT_STEP_SIZE', 1e-6)
    set_int(time_integrator, 'MAX_STEPS', 10000)
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
        f, (ax1, ax2) = plt.subplots(1, 2, figsize=[16, 8])
        plotInlet(ax1, h5)
        plotOutlet(ax2, h5)
        f.tight_layout()
        plt.show()

def plotInlet(axis, h5):
    solution_times = np.array(h5['/output/solution/SOLUTION_TIMES'].value)
        
    inlet_salt = np.array(h5['/output/solution/unit_001/SOLUTION_COLUMN_INLET_COMP_000'].value)
    inlet_p1 = np.array(h5['/output/solution/unit_001/SOLUTION_COLUMN_INLET_COMP_001'].value)
    inlet_p2 = np.array(h5['/output/solution/unit_001/SOLUTION_COLUMN_INLET_COMP_002'].value)
    inlet_p3 = np.array(h5['/output/solution/unit_001/SOLUTION_COLUMN_INLET_COMP_003'].value)


    axis.set_title("Inlet")
    axis.plot(solution_times, inlet_salt, 'b-', label="Salt")
    axis.set_xlabel('time (s)')
        
    # Make the y-axis label, ticks and tick labels match the line color.
    axis.set_ylabel('mMol Salt', color='b')
    axis.tick_params('y', colors='b')

    axis2 = axis.twinx()
    axis2.plot(solution_times, inlet_p1, 'r-', label="P1")
    axis2.plot(solution_times, inlet_p2, 'g-', label="P2")
    axis2.plot(solution_times, inlet_p3, 'k-', label="P3")
    axis2.set_ylabel('mMol Protein', color='r')
    axis2.tick_params('y', colors='r')


    lines, labels = axis.get_legend_handles_labels()
    lines2, labels2 = axis2.get_legend_handles_labels()
    axis2.legend(lines + lines2, labels + labels2, loc=0)


def plotOutlet(axis, h5):
    solution_times = np.array(h5['/output/solution/SOLUTION_TIMES'].value)
        
    outlet_salt = np.array(h5['/output/solution/unit_001/SOLUTION_COLUMN_OUTLET_COMP_000'].value)
    outlet_p1 = np.array(h5['/output/solution/unit_001/SOLUTION_COLUMN_OUTLET_COMP_001'].value)
    outlet_p2 = np.array(h5['/output/solution/unit_001/SOLUTION_COLUMN_OUTLET_COMP_002'].value)
    outlet_p3 = np.array(h5['/output/solution/unit_001/SOLUTION_COLUMN_OUTLET_COMP_003'].value)

    axis.set_title("Output")
    axis.plot(solution_times, outlet_salt, 'b-', label="Salt")
    axis.set_xlabel('time (s)')
        
    # Make the y-axis label, ticks and tick labels match the line color.
    axis.set_ylabel('mMol Salt', color='b')
    axis.tick_params('y', colors='b')

    axis2 = axis.twinx()
    axis2.plot(solution_times, outlet_p1, 'r-', label="P1")
    axis2.plot(solution_times, outlet_p2, 'g-', label="P2")
    axis2.plot(solution_times, outlet_p3, 'k-', label="P3")
    axis2.set_ylabel('mMol Protein', color='r')
    axis2.tick_params('y', colors='r')


    lines, labels = axis.get_legend_handles_labels()
    lines2, labels2 = axis2.get_legend_handles_labels()
    axis2.legend(lines + lines2, labels + labels2, loc=0)


if __name__ == "__main__":
    import sys
    print(sys.version)
    main()
