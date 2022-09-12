import cadet.cadet
import cadet.cadet_dll
import time
import matplotlib.pyplot as plt

print('here')

cadet.Cadet.cadet_path = r"C:\Users\kosh\cadet_build\CADET\VCPKG_42_dll\bin\cadet.dll"

sim = cadet.Cadet()
sim.filename = r"C:\Users\kosh\cadet_build\CADET\VCPKG_42_dll\bin\LWE.h5"
sim.load()

sim.root.input['return'].unit_000.write_solution_inlet = 1
sim.root.input['return'].unit_000.write_solution_bulk = 1
sim.root.input['return'].unit_001.write_solution_bulk = 0

print('before run')

sim.run_load()

print('after run')

plt.figure(figsize=[15,15])
plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_000.solution_outlet_comp_001)
plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_000.solution_outlet_comp_002)
plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_000.solution_outlet_comp_003)
plt.show()


plt.figure(figsize=[15,15])
plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_000.solution_inlet_comp_001)
plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_000.solution_inlet_comp_002)
plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_000.solution_inlet_comp_003)
plt.show()

print(sim.root.output.solution.unit_000.solution_bulk.shape)

a = None
