import cadet.cadet
import cadet.cadet_dll

#cadet.Cadet.cadet_path = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\cadet.dll"

#sim = cadet.Cadet()
#sim.filename = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\LWE.h5"
#sim.load()
#sim.run()
#sim.load_results()
#print(sim)

sim = cadet.cadet.Cadet()
sim.filename = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\LWE.h5"
sim.load()

#sim.cadet_path = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\cadet-cli.exe"
#sim.cadet_path = r"C:\Users\kosh_000\cadet_build\CADET\VCPKG_4\bin\cadet.dll"

#res = sim.run()

#a = None

c = cadet.cadet_dll.CadetDLL("C:/Users/kosh_000/cadet_build/CADET/VCPKG_4/bin/cadet.dll")
print(c.cadet_version)
print(c.cadet_branch)

inp = sim.root.input

res = c.run(simulation=sim.root.input)

t, out = res.outlet(0)
print(t)
print(out)

import matplotlib.pyplot as plt

plt.plot(t, out[:,0,1:])
plt.show()
