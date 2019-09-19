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

#use to render results
import matplotlib.pyplot as plt

import numpy

from cadet import Cadet
import common

#Cadet.cadet_path = r"C:\Users\kosh_000\cadet_build\CADET-fran\MS_SMKL_DEBUG\bin\cadet-cli.exe"
Cadet.cadet_path = r"C:\Users\kosh_000\cadet_build\CADET-fran\MS_SMKL_RELEASE\bin\cadet-cli.exe"


# Helper functions that make it easier to set the values in the HDF5 file
# In the CADET pdf file each value in the hdf5 file has a type. The functions
# below match those types.

def main():
    simulation = Cadet(common.common.root)
    simulation.filename = "F:/temp/HICWang.h5"
    createSimulation(simulation)
    simulation.save()
    simulation.run()
    simulation.load()

    plotSimulation(simulation)

def createSimulation(simulation):
    root = simulation.root

    root.input.model.nunits = 3

    root.input.solver.time_integrator.abstol = 1e-6
    root.input.solver.time_integrator.reltol = 0.0

    root.input.model.connections.nswitches = 1
    root.input.model.connections.switch_000.section = 0
    root.input.model.connections.switch_000.connections = [0, 1, -1, -1, 1.0,
                                                           1, 2, -1, -1, 1.0]
    root.input.model.unit_000.inlet_type = 'PIECEWISE_CUBIC_POLY'
    root.input.model.unit_000.unit_type = 'INLET'
    root.input.model.unit_000.ncomp = 2

    root.input.model.unit_000.sec_000.const_coeff = [4000.0, 1.0]
    root.input.model.unit_000.sec_000.lin_coeff = [0.0, 0.0]
    root.input.model.unit_000.sec_000.quad_coeff = [0.0, 0.0]
    root.input.model.unit_000.sec_000.cube_coeff = [0.0, 0.0]

    root.input.model.unit_000.sec_001.const_coeff = [4000.0, 0.0]
    root.input.model.unit_000.sec_001.lin_coeff = [-4000/15000, 0.0]
    root.input.model.unit_000.sec_001.quad_coeff = [0.0, 0.0]
    root.input.model.unit_000.sec_001.cube_coeff = [0.0, 0.0]

    root.input.model.unit_001.adsorption_model = 'HICWANG'
    root.input.model.unit_001.col_dispersion = 5.6e-8
    root.input.model.unit_001.col_length = 0.014
    root.input.model.unit_001.col_porosity = 0.4
    root.input.model.unit_001.film_diffusion = [1.4e-7, 1.4e-7]
    root.input.model.unit_001.init_c = [4000.0, 0.0]
    root.input.model.unit_001.init_q = [0.0]
    root.input.model.unit_001.ncomp = 2
    root.input.model.unit_001.par_diffusion = [4e-12, 4e-12]
    root.input.model.unit_001.par_porosity = 0.98
    root.input.model.unit_001.par_radius = 4.5e-5
    root.input.model.unit_001.par_surfdiffusion = [0.0]
    root.input.model.unit_001.unit_type = 'GENERAL_RATE_MODEL'

    #root.input.model.unit_001.velocity = 1
    #root.input.model.unit_001.cross_section_area = 4700.352526439483
    root.input.model.unit_001.velocity = 60/(3600*100)


    root.input.model.unit_001.adsorption.is_kinetic = 1
    root.input.model.unit_001.adsorption.hicwang_kkin = [1e2, 1.0/0.16]
    root.input.model.unit_001.adsorption.hicwang_keq = [0.0, 34]
    root.input.model.unit_001.adsorption.hicwang_nu = [1.0, 9.5]
    root.input.model.unit_001.adsorption.hicwang_qmax = [1.0, 1.3e-2*1000]
    root.input.model.unit_001.adsorption.hicwang_beta0 = 3.6e-2
    root.input.model.unit_001.adsorption.hicwang_beta1 = 1.0/1e3

    root.input.model.unit_001.discretization.nbound = [0, 1]
    root.input.model.unit_001.discretization.ncol = 3
    root.input.model.unit_001.discretization.npar = 1
    root.input.model.unit_001.discretization.use_analytic_jacobian = 0


    root.input.model.unit_002.ncomp = 2
    root.input.model.unit_002.unit_type = 'OUTLET'

    root.input.solver.user_solution_times = numpy.linspace(0, 15000, 15000)
    root.input.solver.sections.nsec = 2
    root.input.solver.sections.section_continuity = [0]
    root.input.solver.sections.section_times = [0.0, 10.0, 15000.0]

    root.input.solver.time_integrator.init_step_size = 1e-2
    
def plotSimulation(simulation):
    f, (ax1, ax2) = plt.subplots(1, 2, figsize=[16, 8])
    plotInlet(ax1, simulation)
    plotOutlet(ax2, simulation)
    f.tight_layout()
    plt.show()

def plotInlet(axis, simulation):
    solution_times = simulation.root.output.solution.solution_times

    inlet_salt = simulation.root.output.solution.unit_000.solution_column_inlet_comp_000
    inlet_p1 = simulation.root.output.solution.unit_000.solution_column_inlet_comp_001

    axis.set_title("Inlet")
    axis.plot(solution_times, inlet_salt, 'b-', label="Salt")
    axis.set_xlabel('time (s)')
        
    # Make the y-axis label, ticks and tick labels match the line color.
    axis.set_ylabel('mMol Salt', color='b')
    axis.tick_params('y', colors='b')

    axis2 = axis.twinx()
    axis2.plot(solution_times, inlet_p1, 'r-', label="P1")
    axis2.set_ylabel('mMol Protein', color='r')
    axis2.tick_params('y', colors='r')


    lines, labels = axis.get_legend_handles_labels()
    lines2, labels2 = axis2.get_legend_handles_labels()
    axis2.legend(lines + lines2, labels + labels2, loc=0)


def plotOutlet(axis, simulation):
    solution_times = simulation.root.output.solution.solution_times

    outlet_salt = simulation.root.output.solution.unit_002.solution_column_outlet_comp_000
    outlet_p1 = simulation.root.output.solution.unit_002.solution_column_outlet_comp_001
    
    axis.set_title("Output")
    axis.plot(solution_times, outlet_salt, 'b-', label="Salt")
    axis.set_xlabel('time (s)')
        
    # Make the y-axis label, ticks and tick labels match the line color.
    axis.set_ylabel('mMol Salt', color='b')
    axis.tick_params('y', colors='b')

    axis2 = axis.twinx()
    axis2.plot(solution_times, outlet_p1, 'r-', label="P1")
    axis2.set_ylabel('mMol Protein', color='r')
    axis2.tick_params('y', colors='r')


    lines, labels = axis.get_legend_handles_labels()
    lines2, labels2 = axis2.get_legend_handles_labels()
    axis2.legend(lines + lines2, labels + labels2, loc=0)


if __name__ == "__main__":
    import sys
    print(sys.version)
    main()

