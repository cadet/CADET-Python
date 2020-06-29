import cadet

sim = cadet.Cadet()
sim.filename = r"C:\Users\kosh_000\Documents\Visual Studio 2017\Projects\CADETMatch\Examples\Example1\Dextran\dextran_pulse.h5"
sim.load()

sim.save_json(r"C:\Users\kosh_000\Documents\Visual Studio 2017\Projects\CADETMatch\Examples\Example1\Dextran\dextran_pulse.json")

sim.load_json(r"C:\Users\kosh_000\Documents\Visual Studio 2017\Projects\CADETMatch\Examples\Example1\Dextran\dextran_pulse.json")
