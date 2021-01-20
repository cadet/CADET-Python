import cadet.cadet
import cadet.cadet_dll
import time
import matplotlib.pyplot as plt

#cadet.Cadet.cadet_path = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\cadet.dll"

#sim = cadet.Cadet()
#sim.filename = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\LWE.h5"
#sim.load()
#sim.run()
#sim.load_results()
#print(sim)

cadet.cadet.Cadet.class_cadet_path(r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\cadet.dll")

sim = cadet.cadet.Cadet()

sim.filename = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\LWE.h5"
#sim.filename = r"F:\match_examples\transforms\auto\dextran.h5"
sim.load()

print("isFile", sim.is_file)

sim.filename = "L:/temp.h5"


#sim.cadet_path = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\cadet-cli.exe"

#sim.save()
sim.run()
sim.load_results()

plt.figure(figsize=[15,15])
plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_000.solution_outlet_comp_001)
plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_000.solution_outlet_comp_002)
plt.plot(sim.root.output.solution.solution_times, sim.root.output.solution.unit_000.solution_outlet_comp_003)
plt.show()

#size = 100

#start = time.time()
#for i in range(size):
#    sim.clear()
#    sim.run()
#    sim.load_results()
#elapsed_dll = time.time() - start

#print("Finished dll", elapsed_dll)


#sim.cadet_path = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\cadet-cli.exe"

#start = time.time()
#for i in range(size):
#    sim.save()
#    sim.run()
#    sim.load_results()
#elapsed_memory = time.time() - start

#print("Finished RamDrive", elapsed_memory)

#sim.filename = "F:/temp.h5"

#start = time.time()
#for i in range(size):
#    sim.save()
#    sim.run()
#    sim.load_results()
#elapsed_ssd = time.time() - start

#print("Finished SSD", elapsed_ssd)


#print("DLL", elapsed_dll, 
#      "RamDrive", elapsed_memory,
#      "SSD", elapsed_ssd)


#res = sim.run()

#a = None

#c = cadet.cadet_dll.CadetDLL("C:/Users/kosh_000/cadet_build/CADET/VCPKG_4/bin/cadet.dll")
#print(c.cadet_version)
#print(c.cadet_branch)

#inp = sim.root.input

#res = c.run(simulation=sim.root.input)

#t, out = res.outlet(0)
#print(t)
#print(out)

#import matplotlib.pyplot as plt

#plt.plot(t, out[:,0,1:])
#plt.show()
