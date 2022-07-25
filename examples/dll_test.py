import cadet.cadet
import cadet.cadet_dll
import time
import matplotlib.pyplot as plt

cadet.Cadet.cadet_path = r"C:\Users\kosh\cadet_build\CADET\VCPKG_42_dll\bin\cadet.dll"

sim = cadet.Cadet()
sim.filename = r"C:\Users\kosh\cadet_build\CADET\VCPKG_42_dll\bin\LWE.h5"
sim.load()
sim.run_load()

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
