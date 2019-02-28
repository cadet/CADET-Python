import cadet_library

data = cadet_library.Cadet()
data.filename = r"C:\Users\kosh_000\Documents\Visual Studio 2017\Projects\CADETMatch\Examples\Example1\Dextran\dextran_pulse.h5"
data.cadet_library_path = r"C:\Users\kosh_000\cadet_build\CADET-dev\MS_SMKL_RELEASE\bin\cadet.dll"
data.load()

data.save_memory()


data.run_memory()