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

import numpy

#use to render results
import matplotlib.pyplot as plt

from cadet import Cadet
Cadet.cadet_path = "C:/Users/kosh_000/cadet_build/CADET/MS_SMKL_RELEASE/bin/cadet-cli.exe"

import common

def main():
    simulation = Cadet(common.common.root)
    simulation.filename = "MSSMA.h5"
    createSimulation(simulation)
    simulation.save()
    simulation.run()
    simulation.load()
    plotSimulation(simulation)

def createSimulation(simulation):
    root = simulation.root

    root.input.model.nunits = 3

    root.input.model.connections.nswitches = 1
    root.input.model.connections.switch_000.section = 0
    root.input.model.connections.switch_000.connections = [0, 1, -1, -1, 1.0,
                                                           1, 2, -1, -1, 1.0]
    root.input.model.unit_000.inlet_type = 'PIECEWISE_CUBIC_POLY'
    root.input.model.unit_000.unit_type = 'INLET'
    root.input.model.unit_000.ncomp = 2

    root.input.model.unit_000.sec_000.const_coeff = [92.0, 0.10631294584377825]
    root.input.model.unit_000.sec_000.lin_coeff = [0.0, 0.0]
    root.input.model.unit_000.sec_000.quad_coeff = [0.0, 0.0]
    root.input.model.unit_000.sec_000.cube_coeff = [0.0, 0.0]

    root.input.model.unit_000.sec_001.const_coeff = [69.97439960989882, 0.0]
    root.input.model.unit_000.sec_001.lin_coeff = [0.0, 0.0]
    root.input.model.unit_000.sec_001.quad_coeff = [0.0, 0.0]
    root.input.model.unit_000.sec_001.cube_coeff = [0.0, 0.0]

    root.input.model.unit_000.sec_002.const_coeff = [69.97439960989882, 0.0]
    root.input.model.unit_000.sec_002.lin_coeff = [0.053, 0.0]
    root.input.model.unit_000.sec_002.quad_coeff = [0.0, 0.0]
    root.input.model.unit_000.sec_002.cube_coeff = [0.0, 0.0]

    root.input.model.unit_001.adsorption_model = 'MULTISTATE_STERIC_MASS_ACTION'
    root.input.model.unit_001.col_dispersion = 1.5E-7
    root.input.model.unit_001.col_length = 0.215
    root.input.model.unit_001.col_porosity = 0.33999999999999997
    root.input.model.unit_001.film_diffusion = [2.14E-4, 2.1e-5]
    root.input.model.unit_001.init_c = [69.9743996098988, 0.0]
    root.input.model.unit_001.init_q = [223.547, 0.0, 0.0]
    root.input.model.unit_001.ncomp = 2
    root.input.model.unit_001.par_diffusion = [4.08E-10, 9.0E-12]
    root.input.model.unit_001.par_porosity = 0.39
    root.input.model.unit_001.par_radius = 3.25E-5
    root.input.model.unit_001.par_surfdiffusion = [0.0, 0.0, 0.0]
    root.input.model.unit_001.unit_type = 'GENERAL_RATE_MODEL'
    root.input.model.unit_001.velocity = 0.0011437908496732027

    root.input.model.unit_001.adsorption.is_kinetic = 1
    root.input.model.unit_001.adsorption.mssma_ka = [0.0, 1.0652004307518004E31, 7.724553149425915E26]
    root.input.model.unit_001.adsorption.mssma_kd = [0.0, 5.88452172578919E31, 1.955092026422206E36]
    root.input.model.unit_001.adsorption.mssma_lambda = 223.547
    root.input.model.unit_001.adsorption.mssma_nu = [0.0, 9.618977853171593, 24.75290977103934]
    root.input.model.unit_001.adsorption.mssma_sigma = [0.0, 47.82861669713074, 65.93967947378826]
    root.input.model.unit_001.adsorption.mssma_refq = 223.547
    root.input.model.unit_001.adsorption.mssma_refc0 = 520.0
    root.input.model.unit_001.adsorption.mssma_rates = [0.0, 0.0, 9.39710359947847E39, 9.503195767335168, 0.0]

    root.input.model.unit_001.discretization.nbound = [1, 2]
    root.input.model.unit_001.discretization.ncol = 50
    root.input.model.unit_001.discretization.npar = 5

    root.input.model.unit_002.ncomp = 2
    root.input.model.unit_002.unit_type = 'OUTLET'

    root.input.solver.user_solution_times = numpy.linspace(0, 14731.2, 1000)
    root.input.solver.sections.nsec = 3
    root.input.solver.sections.section_continuity = [0, 0]
    root.input.solver.sections.section_times = [0.0, 4445.422740524782, 6103.9941690962105, 14731.2]

    root.input.solver.consistent_init_mode = 3

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
