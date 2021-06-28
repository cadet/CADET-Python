CADET-Python is a file based Python interface for CADET. CADET must be downloaded from:

https://github.com/modsim/CADET

CADET-Python almost exactly maps to the documented CADET interface except that all dataset names are lowercase. This simplifies useing the interface.

To install CADET-Python simply
------------------------------

pip install cadet-python

or

conda install -c immudzen cadet-python


This package includes the CADET class and H5 class. H5 can be used as a simple generic HDF5 interface.

As an example look at setting column porosity for column 1. From the CADET manual, the path for this is:

/input/model/unit_001/COL_POROSITY

In the Python interface this becomes:

sim = Cadet()
sim.root.input.model.unit_001.col_porosity = 0.33

Once the simulation has been created it must be saved before it can be run.

sim.filename = "/path/to/where/you/want/the/file.hdf5"
sim.save()

#next the path to CADET needs to be set before a simulation can be run. If running on Microsoft Windows you need the path to cadet-cli.exe

sim.cadet_path = '/path/to/cadet-cli'

#next run the simulation

print(sim.run())

#load the data
sim.load()


At this point any data can be read.

If you have a file you want to read that has already been simulated this is also easy to do.

sim = Cadet()
sim.filename = "/path/to/where/you/want/the/file.hdf5"
sim.load()
