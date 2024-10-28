# CADET-Python

**CADET-Python** provides a file-based Python interface for **CADET-Core**, which must be installed separately. For this, please refer to the [installation instructions](https://cadet.github.io/master/getting_started/installation.html) and the [CADET-Core repository](https://github.com/cadet/CADET-Core).

The CADET-Python package simplifies access by mapping to the [CADET interface](https://cadet.github.io/master/interface/index.html#), **with all dataset names in lowercase**.

## Installation

To install CADET-Python, use:

```
pip install cadet-python
```

## Usage Example

The package includes two primary classes:

- **`CADET`**: The main class to configure and run simulations.
- **`H5`**: A general-purpose HDF5 interface.

### Setting Up a Simulation

To set a simulation parameter, such as the column porosity for column 1.

Referring to this path in the CADET interface:
```
/input/model/unit_001/COL_POROSITY
```
In CADET-Python, this is now set as:
```
from cadet import Cadet

# Initialize simulation
sim = Cadet()

# Set column porosity for unit 001
sim.root.input.model.unit_001.col_porosity = 0.33
```
### Saving the Simulation File

Before running, save the simulation configuration to a file:
```
sim.filename = "/path/to/your/file.hdf5"
sim.save()
```
### Setting the Path to CADET

To execute the simulation, specify the path to **CADET-Core**. On Windows, set the path to `cadet-cli.exe`:
```
sim.cadet_path = '/path/to/cadet-cli'
```
### Running the Simulation and Loading Data

Run the simulation and load the output data with:
```
print(sim.run())
sim.load()
```
### Reading Data from a Pre-Simulated File

If you have a pre-simulated file, you can read it directly:
```
# Initialize a new simulation object
sim = Cadet()

# Set the filename for the existing simulation data
sim.filename = "/path/to/your/file.hdf5"
sim.load()
```
At this point, any data in the file can be accessed.
