
import matplotlib.pyplot as plt

import numpy

import pandas

from cadet import Cadet
Cadet.cadet_path = "C:/Users/kosh_000/cadet_build/CADET-dev/MS_SMKL_RELEASE/bin/cadet-cli.exe"

common = Cadet()
root = common.root

root.input.model.unit_001.discretization.par_disc_type = 'EQUIDISTANT_PAR'
root.input.model.unit_001.discretization.schur_safety = 1.0e-8
root.input.model.unit_001.discretization.use_analytic_jacobian = 1
root.input.model.unit_001.discretization.weno.boundary_model = 0
root.input.model.unit_001.discretization.weno.weno_eps = 1e-10
root.input.model.unit_001.discretization.weno.weno_order = 3
root.input.model.unit_001.discretization.gs_type = 1
root.input.model.unit_001.discretization.max_krylov = 0
root.input.model.unit_001.discretization.max_restarts = 10

root.input.solver.time_integrator.abstol = 1e-8
root.input.solver.time_integrator.algtol = 1e-12
root.input.solver.time_integrator.init_step_size = 1e-6
root.input.solver.time_integrator.max_steps = 1000000
root.input.solver.time_integrator.reltol = 1e-6

root.input.model.solver.gs_type = 1
root.input.model.solver.max_krylov = 0
root.input.model.solver.max_restarts = 10
root.input.model.solver.schur_safety  = 1e-8

#CADET 3.1 and CADET-dev flags are in here so that it works with both
#CADET-dev removed column from the name on the inputs and outputs since for many
#operations it no longer makes sense
root.input['return'].write_solution_times = 1
root.input['return'].split_components_data = 1
root.input['return'].unit_000.write_sens_bulk = 0
root.input['return'].unit_000.write_sens_flux = 0
root.input['return'].unit_000.write_sens_inlet = 0
root.input['return'].unit_000.write_sens_outlet = 0
root.input['return'].unit_000.write_sens_particle = 0
root.input['return'].unit_000.write_solution_bulk = 0
root.input['return'].unit_000.write_solution_flux = 0
root.input['return'].unit_000.write_solution_inlet = 1
root.input['return'].unit_000.write_solution_outlet = 1
root.input['return'].unit_000.write_solution_particle = 0
root.input['return'].unit_000.write_sens_column = 0
root.input['return'].unit_000.write_sens_column_inlet = 0
root.input['return'].unit_000.write_sens_column_outlet = 0
root.input['return'].unit_000.write_solution_column = 0
root.input['return'].unit_000.write_solution_column_inlet = 1
root.input['return'].unit_000.write_solution_column_outlet = 1

root.input['return'].unit_001 = root.input['return'].unit_000
root.input['return'].unit_002 = root.input['return'].unit_000
root.input['return'].unit_003 = root.input['return'].unit_000

root.input.solver.nthreads = 1


cstr = Cadet()
root = cstr.root

root.input.model.unit_002.unit_type = 'CSTR'
root.input.model.unit_002.ncomp = 1
root.input.model.unit_002.nbound =[0]
root.input.model.unit_002.init_c = [0]
root.input.model.unit_002.porosity = 1.0
root.input.model.unit_002.init_volume = 5e-6
root.input.model.unit_002.flowrate_filter = 0.0

dpfr = Cadet()
root = dpfr.root

root.input.model.unit_001.unit_type = 'LUMPED_RATE_MODEL_WITHOUT_PORES'
root.input.model.unit_001.ncomp = 1
root.input.model.unit_001.adsorption_model= 'NONE'
root.input.model.unit_001.init_c = [0]
root.input.model.unit_001.init_q = []
root.input.model.unit_001.col_dispersion =  4e-8
root.input.model.unit_001.col_length = 1.0
root.input.model.unit_001.total_porosity = 1.0
root.input.model.unit_001.velocity = 1.0
root.input.model.unit_001.cross_section_area = ((3.75e-5)**2)*numpy.pi 

root.input.model.unit_001.discretization.nbound = [0]
root.input.model.unit_001.discretization.ncol = 50
root.input.model.unit_001.discretization.use_analytic_jacobian = 1
root.input.model.unit_001.discretization.reconstruction = 'WENO'


io = Cadet()
root = io.root

root.input.model.unit_000.inlet_type = 'PIECEWISE_CUBIC_POLY'
root.input.model.unit_000.unit_type = 'INLET'
root.input.model.unit_000.ncomp = 1

root.input.model.unit_000.sec_000.const_coeff = [5.0]
root.input.model.unit_000.sec_000.lin_coeff = [0]
root.input.model.unit_000.sec_000.quad_coeff = [0]
root.input.model.unit_000.sec_000.cube_coeff = [0]

root.input.model.unit_000.sec_001.const_coeff = [1000.0]
root.input.model.unit_000.sec_001.lin_coeff = [0]
root.input.model.unit_000.sec_001.quad_coeff = [0]
root.input.model.unit_000.sec_001.cube_coeff = [0]

root.input.model.unit_000.sec_002.const_coeff = [0]
root.input.model.unit_000.sec_002.lin_coeff = [0]
root.input.model.unit_000.sec_002.quad_coeff = [0]
root.input.model.unit_000.sec_002.cube_coeff = [0]

root.input.model.unit_003.unit_type = 'OUTLET'
root.input.model.unit_003.ncomp = 1

connectivity = Cadet()
root = connectivity.root

root.input.model.nunits = 4
    
root.input.model.connections.nswitches = 1
root.input.model.connections.switch_000.section = 0
root.input.model.connections.switch_000.connections = [0, 2, -1, -1, (100/(60*1e6)),
                                                        2, 1, -1, -1, (100/(60*1e6)),
                                                        1, 3, -1, -1, (100/(60*1e6))]

root.input.solver.user_solution_times = numpy.linspace(0, 153.87, 1000)
root.input.solver.sections.nsec = 3
root.input.solver.sections.section_continuity = [0]
root.input.solver.sections.section_times = [0.0, 15.006, 100.0, 153.87]


def main():
    sim = Cadet(common.root, dpfr.root, io.root, cstr.root, connectivity.root)
    sim.filename = r"F:\jurgen\Pilot_test.h5"
    #createSimulation(sim)
    sim.save()
    sim.run()
    sim.load()
    plotSimulation(sim)

    #sim = Cadet(common.root, cstr.root, io.root, connectivity.root)
    #sim.root.input['return'].unit_001.write_solution_volume = 1
    #sim.root.input.model.connections.switch_000.connections = [0, 1, -1, -1, 1.5,
    #                                                    1, 2, -1, -1, 1.0]
    #sim.filename = r"C:\Users\Kohl\Desktop\Cadet\test_file_cstr.h5"
    #sim.save()
    #sim.run()
    #sim.load()
    #plotSimulation(sim)
    #plotVolume(sim)
    
    writer = pandas.ExcelWriter(r'F:\jurgen\test_file_cstr.xlsx')

    inputs = pandas.DataFrame.from_items([('Time', sim.root.output.solution.solution_times), ('Concentration', sim.root.output.solution.unit_000.solution_inlet_comp_000)])
    outputs = pandas.DataFrame.from_items([('Time', sim.root.output.solution.solution_times), ('Concentration', sim.root.output.solution.unit_002.solution_outlet_comp_000)])
    #volumes = pandas.DataFrame.from_items([('Time', sim.root.output.solution.solution_times), ('Volume', numpy.squeeze(sim.root.output.solution.unit_001.solution_volume))])
    
    inputs.to_excel(writer, 'Input', index=False)
    outputs.to_excel(writer, 'Output', index=False)
    #volumes.to_excel(writer, 'Volume', index=False)

    writer.save()


def plotSimulation(sim):
    plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_002.solution_outlet_comp_000)
    plt.show()

def plotVolume(sim):
    plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_001.solution_volume)
    plt.show()

def createSimulation(sim):
    root = sim.root
    
    #SMA Model
    root.input.model.unit_001.adsorption_model= 'STERIC_MASS_ACTION'
    root.input.model.unit_001.adsorption.is_kinetic = 1
    root.input.model.unit_001.adsorption.sma_ka = [0,35.5]
    root.input.model.unit_001.adsorption.sma_kd = [0,1000.0]
    root.input.model.unit_001.adsorption.sma_lambda = 800.0
    root.input.model.unit_001.adsorption.sma_nu = [1,7.0]
    root.input.model.unit_001.adsorption.sma_sigma = [0,10.0]

    #Linear isotherm
   # root.input.model.unit_001.adsorption_model = 'LINEAR'

    #root.input.model.unit_001.adsorption.is_kinetic = 1
    #root.input.model.unit_001.adsorption.lin_ka = [5e-3]
    #root.input.model.unit_001.adsorption.lin_kd = [1e-3]
        
if __name__ == "__main__":
    main()
