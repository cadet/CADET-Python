import ctypes
import io
import os
from pathlib import Path
from typing import Any, Optional

import addict
import numpy

from cadet.runner import CadetRunnerBase, ReturnInformation
import cadet.cadet_dll_parameterprovider as cadet_dll_parameterprovider


# Common types for ctypes function signatures
CadetDriver = ctypes.c_void_p
array_double = ctypes.POINTER(ctypes.POINTER(ctypes.c_double))
point_bool = ctypes.POINTER(ctypes.c_bool)
point_int = ctypes.POINTER(ctypes.c_int)
point_double = ctypes.POINTER(ctypes.c_double)

# Values of cdtResult
c_cadet_result = ctypes.c_int
_CDT_OK = 0
_CDT_ERROR = -1
_CDT_ERROR_INVALID_INPUTS = -2
_CDT_DATA_NOT_STORED = -3


class CADETAPIV010000_DATA:
    """
    Definition of CADET-C-API v1.0 function signatures and type mappings.

    Attributes
    ----------
    signatures : dict
        Signatures of exported API functions.
    lookup_prototype : dict
        Mapping of common ctypes parameters.
    lookup_output_argument_type : dict
        Mapping of ctypes output parameters for the API.
    """

    # API function signatures
    # Note, order is important, it has to match the cdtAPIv010000 struct of the C-API
    signatures = {}

    signatures['getFileFormat'] = ('return', 'fileFormat')

    signatures['createDriver'] = ('drv',)
    signatures['deleteDriver'] = (None, 'drv')
    signatures['runSimulation'] = ('return', 'drv', 'parameterProvider')

    signatures['getNumUnitOp'] = ('return', 'drv', 'nUnits')
    signatures['getNumParTypes'] = ('return', 'drv', 'unitOpId', 'nParTypes')
    signatures['getNumSensitivities'] = ('return', 'drv', 'nSens')

    signatures['getSolutionInlet'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime', 'nPort', 'nComp')
    signatures['getSolutionOutlet'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime', 'nPort', 'nComp')
    signatures['getSolutionBulk'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nComp', 'keepAxialSingletonDimension')
    signatures['getSolutionParticle'] = ('return', 'drv', 'unitOpId', 'parType', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParShells', 'nComp', 'keepAxialSingletonDimension', 'keepParticleSingletonDimension')
    signatures['getSolutionSolid'] = ('return', 'drv', 'unitOpId', 'parType', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParShells', 'nBound', 'keepAxialSingletonDimension', 'keepParticleSingletonDimension')
    signatures['getSolutionFlux'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParTypes', 'nComp', 'keepAxialSingletonDimension')
    signatures['getSolutionVolume'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime')

    signatures['getSolutionDerivativeInlet'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime', 'nPort', 'nComp')
    signatures['getSolutionDerivativeOutlet'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime', 'nPort', 'nComp')
    signatures['getSolutionDerivativeBulk'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nComp', 'keepAxialSingletonDimension')
    signatures['getSolutionDerivativeParticle'] = ('return', 'drv', 'unitOpId', 'parType', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParShells', 'nComp', 'keepAxialSingletonDimension', 'keepParticleSingletonDimension')
    signatures['getSolutionDerivativeSolid'] = ('return', 'drv', 'unitOpId', 'parType', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParShells', 'nBound', 'keepAxialSingletonDimension', 'keepParticleSingletonDimension')
    signatures['getSolutionDerivativeFlux'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParTypes', 'nComp', 'keepAxialSingletonDimension')
    signatures['getSolutionDerivativeVolume'] = ('return', 'drv', 'unitOpId', 'time', 'data', 'nTime')

    signatures['getSensitivityInlet'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime', 'nPort', 'nComp')
    signatures['getSensitivityOutlet'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime', 'nPort', 'nComp')
    signatures['getSensitivityBulk'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nComp', 'keepAxialSingletonDimension')
    signatures['getSensitivityParticle'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'parType', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParShells', 'nComp', 'keepAxialSingletonDimension', 'keepParticleSingletonDimension')
    signatures['getSensitivitySolid'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'parType', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParShells', 'nBound', 'keepAxialSingletonDimension', 'keepParticleSingletonDimension')
    signatures['getSensitivityFlux'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParTypes', 'nComp', 'keepAxialSingletonDimension')
    signatures['getSensitivityVolume'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime')

    signatures['getSensitivityDerivativeInlet'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime', 'nPort', 'nComp')
    signatures['getSensitivityDerivativeOutlet'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime', 'nPort', 'nComp')
    signatures['getSensitivityDerivativeBulk'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nComp', 'keepAxialSingletonDimension')
    signatures['getSensitivityDerivativeParticle'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'parType', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParShells', 'nComp', 'keepAxialSingletonDimension', 'keepParticleSingletonDimension')
    signatures['getSensitivityDerivativeSolid'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'parType', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParShells', 'nBound', 'keepAxialSingletonDimension', 'keepParticleSingletonDimension')
    signatures['getSensitivityDerivativeFlux'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime', 'nAxialCells', 'nRadialCells', 'nParTypes', 'nComp', 'keepAxialSingletonDimension')
    signatures['getSensitivityDerivativeVolume'] = ('return', 'drv', 'unitOpId', 'sensIdx', 'time', 'data', 'nTime')

    signatures['getLastState'] = ('return', 'drv', 'state', 'nStates')
    signatures['getLastStateTimeDerivative'] = ('return', 'drv', 'state', 'nStates')
    signatures['getLastUnitState'] = ('return', 'drv', 'unitOpId', 'state', 'nStates')
    signatures['getLastUnitStateTimeDerivative'] = ('return', 'drv', 'unitOpId', 'state', 'nStates')
    signatures['getLastSensitivityState'] = ('return', 'drv', 'sensIdx', 'state', 'nStates')
    signatures['getLastSensitivityStateTimeDerivative'] = ('return', 'drv', 'sensIdx', 'state', 'nStates')
    signatures['getLastSensitivityUnitState'] = ('return', 'drv', 'sensIdx', 'unitOpId', 'state', 'nStates')
    signatures['getLastSensitivityUnitStateTimeDerivative'] = ('return', 'drv', 'sensIdx', 'unitOpId', 'state', 'nStates')

    signatures['getPrimaryCoordinates'] = ('return', 'drv', 'unitOpId', 'coords', 'nCoords')
    signatures['getSecondaryCoordinates'] = ('return', 'drv', 'unitOpId', 'coords', 'nCoords')
    signatures['getParticleCoordinates'] = ('return', 'drv', 'unitOpId', 'parType', 'coords', 'nCoords')
    signatures['getSolutionTimes'] = ('return', 'drv', 'time', 'nTime')

    signatures['getTimeSim'] = ('return', 'drv', 'timeSim')

    # Mappings for common ctypes parameters
    lookup_prototype = {
        None: None,
        'return': c_cadet_result,
        'fileFormat': point_int,
        'drv': CadetDriver,
        'parameterProvider': ctypes.POINTER(cadet_dll_parameterprovider.PARAMETERPROVIDER),
        'nUnits': point_int,
        'nTime': point_int,
        'nCoords': point_int,
        'nPort': point_int,
        'nAxialCells': point_int,
        'nRadialCells': point_int,
        'nParTypes': point_int,
        'nSens': point_int,
        'nParShells': point_int,
        'nComp': point_int,
        'nBound': point_int,
        'nStates': point_int,
        'unitOpId': ctypes.c_int,
        'sensIdx': ctypes.c_int,
        'parType': ctypes.c_int,
        'time': array_double,
        'data': array_double,
        'state': array_double,
        'coords': array_double,
        'keepAxialSingletonDimension': point_bool,
        'keepParticleSingletonDimension': point_bool,
        'timeSim': point_double,
    }

    lookup_output_argument_type = {
        'fileFormat': ctypes.c_int,
        'nUnits': ctypes.c_int,
        'nTime': ctypes.c_int,
        'nCoords': ctypes.c_int,
        'nPort': ctypes.c_int,
        'nAxialCells': ctypes.c_int,
        'nRadialCells': ctypes.c_int,
        'nParTypes': ctypes.c_int,
        'nSens': ctypes.c_int,
        'nParShells': ctypes.c_int,
        'nComp': ctypes.c_int,
        'nBound': ctypes.c_int,
        'nStates': ctypes.c_int,
        'time': ctypes.POINTER(ctypes.c_double),
        'data': ctypes.POINTER(ctypes.c_double),
        'state': ctypes.POINTER(ctypes.c_double),
        'coords': ctypes.POINTER(ctypes.c_double),
        'keepAxialSingletonDimension': ctypes.c_bool,
        'keepParticleSingletonDimension': ctypes.c_bool,
        'timeSim': ctypes.c_double,
    }


def _setup_api() -> list[tuple[str, ctypes.CFUNCTYPE]]:
    """
    Set up the API function prototypes for CADETAPIV010000.

    Returns
    -------
    list of tuple
        List of function names and corresponding ctypes function prototypes.
    """
    _fields_ = []
    for key, value in CADETAPIV010000_DATA.signatures.items():
        args = tuple(CADETAPIV010000_DATA.lookup_prototype[key] for key in value)
        _fields_.append((key, ctypes.CFUNCTYPE(*args)))

    return _fields_


class CADETAPIV010000(ctypes.Structure):
    """Mimic cdtAPIv010000 struct of CADET C-API in ctypes."""
    _fields_ = _setup_api()


class SimulationResult:
    """
    Handles reading results from a CADET simulation.

    Parameters
    ----------
    api : CADETAPIV010000
        The CADET API instance.
    driver : CadetDriver
        The driver handle used for the simulation.

    """

    def __init__(self, api: CADETAPIV010000, driver: CadetDriver) -> None:
        self._api = api
        self._driver = driver

    def _load_data(
            self,
            get_solution_str: str,
            unitOpId: Optional[int] = None,
            sensIdx: Optional[int] = None,
            parType: Optional[int] = None
            ) -> Optional[dict[str, Any]]:
        """
        Load data from the CADET API.

        Parameters
        ----------
        get_solution_str : str
            The name of the API function to call.
        unitOpId : Optional[int], default=None
            The unit operation ID.
        sensIdx : Optional[int], default=None
            The sensitivity index.
        parType : Optional[int], default=None
            The particle type index.

        Returns
        -------
        Optional[dict[str, Any]]
            The output arguments mapped to their values, or None if data is not available.
        """
        get_solution = getattr(self._api, get_solution_str)

        # Collect actual values
        call_args = []
        call_outputs = {}

        # Construct API call function arguments
        for key in CADETAPIV010000_DATA.signatures[get_solution_str]:
            if key == 'return':
                # Skip, this is the actual return value of the API function
                continue
            elif key == 'drv':
                call_args.append(self._driver)
            elif key == 'unitOpId' and unitOpId is not None:
                call_args.append(unitOpId)
            elif key == 'sensIdx':
                call_args.append(sensIdx)
            elif key == 'parType':
                call_args.append(parType)
            else:
                _obj = CADETAPIV010000_DATA.lookup_output_argument_type[key]()
                call_outputs[key] = _obj
                call_args.append(ctypes.byref(_obj))

        result = get_solution(*call_args)

        if result == _CDT_DATA_NOT_STORED:
            # Call successful, but data is not available
            return
        elif result == _CDT_ERROR_INVALID_INPUTS:
            raise ValueError("Error reading data: Invalid call arguments")
        elif result != _CDT_OK:
            # Something else failed
            raise Exception("Error reading data.")

        return call_outputs

    def _process_array(
            self,
            call_outputs: dict[str, Any],
            data_key: str,
            len_key: str,
            own_data: bool = True,
            ) -> Optional[numpy.ndarray]:
        """
        Process array data from the API.

        Parameters
        ----------
        call_outputs : dict
            The output arguments returned from the API call.
        data_key : str
            The key for the data array in the output arguments.
        len_key : str
            The key for the length of the data array.
        own_data : bool, default=True
            Whether to create a copy of the data.

        Returns
        -------
        Optional[numpy.ndarray]
            The processed data array or None if the length is zero.
        """
        array_length = call_outputs[len_key].value
        if array_length == 0:
            return

        data = numpy.ctypeslib.as_array(call_outputs[data_key], shape=(array_length, ))
        if own_data:
            return data.copy()
        return data

    def _process_data(
            self,
            call_outputs: dict[str, Any],
            own_data: bool = True,
            ) -> Optional[tuple[numpy.ndarray, numpy.ndarray, list[str]]]:
        """
        Process multi-dimensional data from the API.

        Parameters
        ----------
        call_outputs : dict
            The output arguments returned from the API call.
        own_data : bool, default=True
            Whether to create a copy of the data.

        Returns
        -------
        Optional[tuple[numpy.ndarray, numpy.ndarray, list[str]]]
            A tuple of time, data, and dimensions, or None if no data is available.
        """
        shape = []
        dims = []
        drop_indices = []

        # Ordering of multi-dimensional arrays, all possible dimensions:
        # bulk: 'nTime', ('nAxialCells',) ('nRadialCells' / 'nPorts',) 'nComp'
        # particle_liquid: 'nTime', ('nParTypes',) ('nAxialCells',) ('nRadialCells' / 'nPorts',) ('nParShells',) 'nComp'
        # particle_solid: 'nTime', ('nParTypes',) ('nAxialCells',) ('nRadialCells' / 'nPorts',) ('nParShells',) 'nComp', 'nBound'
        # flux: 'nTime', ('nParTypes',) ('nAxialCells',) ('nRadialCells' / 'nPorts',) 'nComp'
        dimensions = [
            'nTime',
            'nParTypes',
            'nAxialCells',
            'nPort',
            'nRadialCells',
            'nParShells',
            'nComp',
            'nBound',
        ]
        for dim in dimensions:
            if dim in call_outputs and call_outputs[dim].value:
                shape.append(call_outputs[dim].value)
                dims.append(dim)

        if len(shape) == 0:
            return

        if 'data' in call_outputs:
            if 'nAxialCells' in dims:
                nAxialCells = call_outputs['nAxialCells'].value
                keep_axial_singleton_dim = call_outputs['keepAxialSingletonDimension'].value
                if nAxialCells == 1 and not keep_axial_singleton_dim:
                    drop_indices.append(dims.index('nAxialCells'))

            if 'nParShells' in dims:
                nParShells = call_outputs['nParShells'].value
                keep_particle_singleton_dim = call_outputs['keepParticleSingletonDimension'].value
                if nParShells == 1 and not keep_particle_singleton_dim:
                    drop_indices.append(dims.index('nParShells'))

            shape = numpy.delete(shape, drop_indices)

            data = numpy.ctypeslib.as_array(call_outputs['data'], shape=shape)
            if own_data:
                data = data.copy()

        if 'time' in call_outputs:
            n_time = call_outputs['nTime'].value
            time = numpy.ctypeslib.as_array(call_outputs['time'], shape=(n_time, ))
            if own_data:
                time = time.copy()

        return time, data, dims

    def _load_and_process(
            self,
            *args: Any,
            own_data: bool = True,
            **kwargs: Any
            ) -> Optional[tuple[numpy.ndarray, numpy.ndarray, list[str]]]:
        """
        Load and process data from the API in a single step.

        Parameters
        ----------
        own_data : bool, default=True
            Whether to create a copy of the data.

        Returns
        -------
        Optional[tuple[numpy.ndarray, numpy.ndarray, list[str]]]
            A tuple of time, data, and dimensions, or None if no data is available.
        """
        call_outputs = self._load_data(*args, **kwargs)

        if call_outputs is None:
            return

        processed_results = self._process_data(call_outputs, own_data)
        return processed_results

    def _load_and_process_array(
            self,
            data_key: str,
            len_key: str,
            *args: Any,
            own_data: bool = True,
            **kwargs: Any
            ) -> Optional[numpy.ndarray]:
        """
        Load and process a 1D array from the API.

        Parameters
        ----------
        data_key : str
            The key for the data array in the output arguments.
        len_key : str
            The key for the length of the data array.
        own_data : bool, default=True
            Whether to create a copy of the data.

        Returns
        -------
        Optional[numpy.ndarray]
            The processed data array or None if no data is available.
        """
        call_outputs = self._load_data(*args, **kwargs)

        if call_outputs is None:
            return None

        return self._process_array(call_outputs, data_key, len_key, own_data)

    def file_format(
            self,
            own_data: bool = True,
            ) -> float:
        """
        Load the file format used for the simulation config.

        Parameters
        ----------
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        int
            The file format.
        """
        call_outputs = self._load_data('getFileFormat')
        return int(call_outputs['fileFormat'].value)

    def nunits(self) -> int:
        """
        Get the number of unit operations in the system.

        Returns
        -------
        int
            The number of unit operations in the system.
        """
        call_outputs = self._load_data('getNumUnitOp')
        return int(call_outputs['nUnits'].value)

    def npartypes(self, unitOpId: int) -> int:
        """
        Get the number of particle types for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.

        Returns
        -------
        int
            The number of particle types.
        """
        call_outputs = self._load_data('getNumParTypes', unitOpId=unitOpId)
        return int(call_outputs['nParTypes'].value)

    def nsensitivities(self) -> int:
        """
        Get the number of sensitivities defined for the simulation.

        Returns
        -------
        int
            The number of sensitivities.
        """
        call_outputs = self._load_data('getNumSensitivities')
        return int(call_outputs['nSens'].value)

    def solution_inlet(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the inlet solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution.
        """
        return self._load_and_process(
            'getSolutionInlet', unitOpId=unitOpId, own_data=own_data
        )

    def solution_outlet(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the outlet solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution.
        """
        return self._load_and_process(
            'getSolutionOutlet', unitOpId=unitOpId, own_data=own_data
        )

    def solution_bulk(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the bulk solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution.
        """
        return self._load_and_process(
            'getSolutionBulk', unitOpId=unitOpId, own_data=own_data
        )

    def solution_particle(
            self,
            unitOpId: int,
            parType: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the particle-phase solution for a given unit operation and particle type.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        parType : int
            The particle type index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution.
        """
        return self._load_and_process(
            'getSolutionParticle', unitOpId=unitOpId, parType=parType, own_data=own_data
        )

    def solution_solid(
            self,
            unitOpId: int,
            parType: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the solid-phase solution for a given unit operation and particle type.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        parType : int
            The particle type index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution.
        """
        return self._load_and_process(
            'getSolutionSolid', unitOpId=unitOpId, parType=parType, own_data=own_data
        )

    def solution_flux(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the flux solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution.
        """
        return self._load_and_process(
            'getSolutionFlux', unitOpId=unitOpId, own_data=own_data
        )

    def solution_volume(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the volume solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution.
        """
        return self._load_and_process(
            'getSolutionVolume', unitOpId=unitOpId, own_data=own_data
        )

    def soldot_inlet(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the inlet solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution derivative.
        """
        return self._load_and_process(
            'getSolutionDerivativeInlet', unitOpId=unitOpId, own_data=own_data
        )

    def soldot_outlet(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the outlet solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution derivative.
        """
        return self._load_and_process(
            'getSolutionDerivativeOutlet', unitOpId=unitOpId, own_data=own_data
        )

    def soldot_bulk(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the bulk solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution derivative.
        """
        return self._load_and_process(
            'getSolutionDerivativeBulk', unitOpId=unitOpId, own_data=own_data
        )

    def soldot_particle(
            self,
            unitOpId: int,
            parType: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the particle-phase solution for a given unit operation and particle type.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        parType : int
            The particle type index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution derivative.
        """
        return self._load_and_process(
            'getSolutionDerivativeParticle',
            unitOpId=unitOpId,
            parType=parType,
            own_data=own_data
        )

    def soldot_solid(
            self,
            unitOpId: int,
            parType: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the solid-phase solution for a given unit operation and particle type.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        parType : int
            The particle type index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution derivative.
        """
        return self._load_and_process(
            'getSolutionDerivativeSolid',
            unitOpId=unitOpId,
            parType=parType,
            own_data=own_data
        )

    def soldot_flux(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the flux solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution derivative.
        """
        return self._load_and_process(
            'getSolutionDerivativeFlux', unitOpId=unitOpId, own_data=own_data
        )

    def soldot_volume(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the volume solution for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the solution derivative.
        """
        return self._load_and_process(
            'getSolutionDerivativeVolume', unitOpId=unitOpId, own_data=own_data
        )

    def sens_inlet(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the sensitivity data for the inlet of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity data.
        """
        return self._load_and_process(
            'getSensitivityInlet', unitOpId=unitOpId, sensIdx=sensIdx, own_data=own_data
        )

    def sens_outlet(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity data for the outlet of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity data.
        """
        return self._load_and_process(
            'getSensitivityOutlet',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            own_data=own_data
        )

    def sens_bulk(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity data for the bulk of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity data.
        """
        return self._load_and_process(
            'getSensitivityBulk', unitOpId=unitOpId, sensIdx=sensIdx, own_data=own_data
        )

    def sens_particle(
            self,
            unitOpId: int,
            sensIdx: int,
            parType: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity data for the particle phase of a given unit operation, sensitivity index, and particle type.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        parType : int
            The particle type index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity data.
        """
        return self._load_and_process(
            'getSensitivityParticle',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            parType=parType,
            own_data=own_data
        )

    def sens_solid(
            self,
            unitOpId: int,
            sensIdx: int,
            parType: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity data for the solid phase of a given unit operation, sensitivity index, and particle type.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        parType : int
            The particle type index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity data.
        """
        return self._load_and_process(
            'getSensitivitySolid',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            parType=parType,
            own_data=own_data
        )

    def sens_flux(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity data for the flux of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity data.
        """
        return self._load_and_process(
            'getSensitivityFlux', unitOpId=unitOpId, sensIdx=sensIdx, own_data=own_data
        )

    def sens_volume(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity data for the volume of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity data.
        """
        return self._load_and_process(
            'getSensitivityVolume',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            own_data=own_data
        )

    def sensdot_inlet(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity derivative data for the inlet of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity derivative data.
        """
        return self._load_and_process(
            'getSensitivityDerivativeInlet',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            own_data=own_data
        )

    def sensdot_outlet(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity derivative data for the outlet of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity derivative data.
        """
        return self._load_and_process(
            'getSensitivityDerivativeOutlet',
            unitOpId,
            sensIdx=sensIdx,
            own_data=own_data
        )

    def sensdot_bulk(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity derivative data for the bulk of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity derivative data.
        """
        return self._load_and_process(
            'getSensitivityDerivativeBulk',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            own_data=own_data
        )

    def sensdot_particle(
            self,
            unitOpId: int,
            sensIdx: int,
            parType: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity derivative data for the particle phase of a given unit operation, sensitivity index, and particle type.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        parType : int
            The particle type index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity derivative data.
        """
        return self._load_and_process(
            'getSensitivityDerivativeParticle',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            parType=parType,
            own_data=own_data
        )

    def sensdot_solid(
            self,
            unitOpId: int,
            sensIdx: int,
            parType: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity derivative data for the solid phase of a given unit operation, sensitivity index, and particle type.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        parType : int
            The particle type index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity derivative data.
        """
        return self._load_and_process(
            'getSensitivityDerivativeSolid',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            parType=parType,
            own_data=own_data
        )

    def sensdot_flux(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity derivative data for the flux of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity derivative data.
        """
        return self._load_and_process(
            'getSensitivityDerivativeFlux',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            own_data=own_data
        )

    def sensdot_volume(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load sensitivity derivative data for the volume of a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity derivative data.
        """
        return self._load_and_process(
            'getSensitivityDerivativeVolume',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            own_data=own_data
        )

    def last_state_y(
            self,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the last state of the system.

        Parameters
        ----------
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The state data.
        """
        return self._load_and_process_array(
            'state', 'nStates', 'getLastState', own_data=own_data
        )

    def last_state_ydot(
            self,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the last state of the system.

        Parameters
        ----------
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The time derivative data.
        """
        return self._load_and_process_array(
            'state', 'nStates', 'getLastStateTimeDerivative', own_data=own_data
        )

    def last_state_y_unit(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the last state of a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The state data.
        """
        return self._load_and_process_array(
            'state', 'nStates', 'getLastUnitState', unitOpId=unitOpId, own_data=own_data
        )

    def last_state_ydot_unit(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the last state of a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The time derivative data.
        """
        return self._load_and_process_array(
            'state',
            'nStates',
            'getLastUnitStateTimeDerivative',
            unitOpId=unitOpId,
            own_data=own_data
        )

    def last_state_sens(
            self,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the last sensitivity state for a given sensitivity index.

        Parameters
        ----------
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The sensitivity state data.
        """
        return self._load_and_process_array(
            'state',
            'nStates',
            'getLastSensitivityState',
            sensIdx=sensIdx,
            own_data=own_data
        )

    def last_state_sensdot(
            self,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the last sensitivity state for a given sensitivity index.

        Parameters
        ----------
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The sensitivity state time derivative data.
        """
        return self._load_and_process_array(
            'state',
            'nStates',
            'getLastSensitivityStateTimeDerivative',
            sensIdx=sensIdx,
            own_data=own_data
        )

    def last_state_sens_unit(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the last sensitivity state for a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity state.
        """
        return self._load_and_process(
            'getLastSensitivityUnitState',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            own_data=own_data
        )

    def last_state_sensdot_unit(
            self,
            unitOpId: int,
            sensIdx: int,
            own_data: bool = True,
            ) -> tuple[numpy.ndarray, numpy.ndarray, list[str]]:
        """
        Load the time derivative of the last sensitivity state for a given unit operation and sensitivity index.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        sensIdx : int
            The sensitivity index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray, list[str]]
            The time, data, and dimensions of the sensitivity state time derivative.
        """
        return self._load_and_process(
            'getLastSensitivityUnitStateTimeDerivative',
            unitOpId=unitOpId,
            sensIdx=sensIdx,
            own_data=own_data
        )

    def primary_coordinates(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> numpy.ndarray:
        """
        Load the primary coordinates for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The primary coordinates.
        """
        return self._load_and_process_array(
            'coords',
            'nCoords',
            'getPrimaryCoordinates',
            unitOpId=unitOpId,
            own_data=own_data
        )

    def secondary_coordinates(
            self,
            unitOpId: int,
            own_data: bool = True,
            ) -> numpy.ndarray:
        """
        Load the secondary coordinates for a given unit operation.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The secondary coordinates.
        """
        return self._load_and_process_array(
            'coords',
            'nCoords',
            'getSecondaryCoordinates',
            unitOpId=unitOpId,
            own_data=own_data
        )

    def particle_coordinates(
            self,
            unitOpId: int,
            parType: int,
            own_data: bool = True,
            ) -> numpy.ndarray:
        """
        Load the particle coordinates for a given unit operation and particle type.

        Parameters
        ----------
        unitOpId : int
            The unit operation ID.
        parType : int
            The particle type index.
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The particle coordinates.
        """
        return self._load_and_process_array(
            'coords',
            'nCoords',
            'getParticleCoordinates',
            unitOpId=unitOpId,
            parType=parType, own_data=own_data
        )

    def solution_times(
            self,
            own_data: bool = True,
            ) -> numpy.ndarray:
        """
        Load the solution times from the simulation.

        Parameters
        ----------
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        numpy.ndarray
            The solution times.
        """
        return self._load_and_process_array(
            'time', 'nTime', 'getSolutionTimes', own_data=own_data
        )

    def time_sim(
            self,
            own_data: bool = True,
            ) -> float:
        """
        Load the simulation run time.

        Parameters
        ----------
        own_data : bool, optional
            Whether to copy the data (default is True).

        Returns
        -------
        float
            The simulation run time.
        """
        call_outputs = self._load_data('getTimeSim')
        return float(call_outputs['timeSim'].value)


class CadetDLLRunner(CadetRunnerBase):
    """
    Runner for CADET simulations using a DLL-based interface.

    This class loads and interacts with the CADET DLL, providing methods for running
    simulations and loading results.
    """

    def __init__(self, dll_path: os.PathLike | str) -> None:
        """
        Initialize the CadetDLLRunner.

        Parameters
        ----------
        dll_path : os.PathLike or str
            Path to the CADET DLL.
        """
        self._cadet_path = Path(dll_path)
        self._initialize_dll()

    def _initialize_dll(self):
        self._lib = ctypes.cdll.LoadLibrary(self._cadet_path.as_posix())

        # Query meta information
        cdtGetLibraryVersion = self._lib.cdtGetLibraryVersion
        cdtGetLibraryVersion.restype = ctypes.c_char_p
        self._cadet_version = cdtGetLibraryVersion().decode('utf-8')

        cdtGetLibraryCommitHash = self._lib.cdtGetLibraryCommitHash
        cdtGetLibraryCommitHash.restype = ctypes.c_char_p
        self._cadet_commit_hash = cdtGetLibraryCommitHash().decode('utf-8')

        cdtGetLibraryBranchRefspec = self._lib.cdtGetLibraryBranchRefspec
        cdtGetLibraryBranchRefspec.restype = ctypes.c_char_p
        self._cadet_branch = cdtGetLibraryBranchRefspec().decode('utf-8')

        cdtGetLibraryBuildType = self._lib.cdtGetLibraryBuildType
        cdtGetLibraryBuildType.restype = ctypes.c_char_p
        self._cadet_build_type = cdtGetLibraryBuildType().decode('utf-8')

        # Define the log handler callback type
        self.LOG_HANDLER_CLBK = ctypes.CFUNCTYPE(
            None,
            ctypes.c_char_p,  # file
            ctypes.c_char_p,  # func
            ctypes.c_uint,    # line
            ctypes.c_int,     # level
            ctypes.c_char_p,  # level_name
            ctypes.c_char_p   # message
        )

        # Set up the C functions for setting the log handler and log level
        self._set_log_handler = self._lib.cdtSetLogReceiver
        self._set_log_handler.argtypes = [self.LOG_HANDLER_CLBK]
        self._set_log_handler.restype = None

        self._set_log_level = self._lib.cdtSetLogLevel
        self._set_log_level.argtypes = [ctypes.c_int]
        self._set_log_level.restype = None

        self._default_log_level = 2

        # Query API
        try:
            cdtGetLatestCAPIVersion = self._lib.cdtGetLatestCAPIVersion#
        except AttributeError:
            raise ValueError(
                "CADET-Python does not support CADET-CAPI at all."
            )
        cdtGetLatestCAPIVersion.restype = ctypes.c_char_p
        self._cadet_capi_version = cdtGetLatestCAPIVersion().decode('utf-8')

        # Check which C-API is provided by CADET (given the current install path)
        if self._cadet_capi_version == "1.0.0":
            cdtGetAPIv010000 = self._lib.cdtGetAPIv010000
            cdtGetAPIv010000.argtypes = [ctypes.POINTER(CADETAPIV010000)]
            cdtGetAPIv010000.restype = c_cadet_result
            self._api = CADETAPIV010000()
            cdtGetAPIv010000(ctypes.byref(self._api))
        else:
            raise ValueError(
                "CADET-Python does not support CADET-CAPI version "
                f"({self._cadet_capi_version})."
            )

        self._driver = self._api.createDriver()
        self.res: Optional[SimulationResult] = None

    def __getstate__(self):
        # Exclude all non-pickleable attributes and only keep _cadet_path
        state = self.__dict__.copy()
        pickleable_keys = ["_cadet_path"]
        state = {key: state[key] for key in pickleable_keys}
        return state

    def __setstate__(self, state):
        # Restore the state and reinitialize the DLL
        self.__dict__.update(state)
        self._initialize_dll()

    def clear(self) -> None:
        """
        Clear the current simulation state.

        This method deletes the current simulation results and resets the driver.
        """
        if hasattr(self, "res"):
            del self.res

        if hasattr(self, "_api") and hasattr(self, "_driver"):
            self._api.deleteDriver(self._driver)
        self._driver = self._api.createDriver()

    def __del__(self) -> None:
        """
        Clean up the CADET driver on object deletion.
        """
        if hasattr(self, "_api") and hasattr(self, "_driver"):
            self._api.deleteDriver(self._driver)

    def setup_log_buffer(self, log_level: int = None) -> io.StringIO:
        """
        Set up a new log buffer for capturing log output with the specified log level.

        Parameters
        ----------
        log_level : int, optional
            The desired log level. Defaults to the instance's default log level.

        Returns
        -------
        log_buffer : io.StringIO
            A new log buffer for capturing log output.
        """
        if log_level is None:
            log_level = self._default_log_level

        # Create a new log buffer
        log_buffer = io.StringIO()

        def log_handler(file, func, line, level, level_name, message):
            """Logging callback function."""
            msg = f"{level_name.decode('utf-8')} ({func.decode('utf-8')}:{line}) {message.decode('utf-8')}"
            log_buffer.write(msg + "\n")  # Write to the instance's buffer

        # Set up the logging callback
        self._log_handler = self.LOG_HANDLER_CLBK(log_handler)
        self._set_log_handler(self._log_handler)

        # Set the log level
        self._set_log_level(log_level)

        # Return the log buffer so it can be accessed after the run
        return log_buffer

    def run(
            self,
            simulation: Optional["Cadet"] = None,
            timeout: Optional[int] = None,
            ) -> ReturnInformation:
        """
        Run a CADET simulation using the DLL interface.

        Parameters
        ----------
        simulation : Optional[Cadet]
            Simulation object containing input data.
        timeout : Optional[int]
            Maximum time allowed for the simulation to run, in seconds.

        Raises
        ------
        RuntimeError
            If the simulation process returns a non-zero exit code.
        """
        pp = cadet_dll_parameterprovider.PARAMETERPROVIDER(simulation)

        log_buffer = self.setup_log_buffer()

        returncode = self._api.runSimulation(self._driver, ctypes.byref(pp))

        if returncode != 0:
            log = ""
            error_message = log_buffer.getvalue()
        else:
            log = log_buffer.getvalue()
            error_message = ""

        self.res = SimulationResult(self._api, self._driver)

        return_info = ReturnInformation(
            return_code=returncode,
            error_message=error_message,
            log=log
        )

        return return_info

    def load_results(self, sim: "Cadet") -> None:
        """
        Load the simulation results into the provided simulation object.

        Parameters
        ----------
        sim : Cadet
            The simulation object where results will be loaded.
        """
        if self.res is None:
            return

        self.load_solution_times(sim)
        self.load_coordinates(sim)
        self.load_solution(sim)
        self.load_sensitivity(sim)
        self.load_state(sim)

        self.load_meta(sim)

    def load_solution_times(self, sim: "Cadet") -> None:
        """Load solution times from simulation results."""
        write_solution_times = sim.root.input['return'].get('write_solution_times', 0)
        if write_solution_times:
            sim.root.output.solution.solution_times = self.res.solution_times()

    def load_coordinates(self, sim: "Cadet") -> None:
        """Load coordinates data from simulation results."""
        coordinates = addict.Dict()
        for unit in range(self.res.nunits()):
            unit_index = self._get_index_string('unit', unit)
            write_coordinates = sim.root.input['return'][unit_index].get('write_coordinates', 0)
            if write_coordinates:
                pc = self.res.primary_coordinates(unit)
                if pc is not None:
                    coordinates[unit_index]['axial_coordinates'] = pc

                sc = self.res.secondary_coordinates(unit)
                if sc is not None:
                    coordinates[unit_index]['radial_coordinates'] = sc

                num_par_types = self.res.npartypes(unit)
                for pt in range(num_par_types):
                    par_coords = self.res.particle_coordinates(unit, pt)
                    if par_coords is not None:
                        par_idx = self._get_index_string('particle_coordinates', pt)
                        coordinates[unit_index][par_idx] = par_coords

        if len(coordinates) > 0:
            sim.root.output.coordinates = coordinates

    def load_solution(self, sim: "Cadet") -> addict.Dict:
        """Load solution data from simulation results."""
        solution = addict.Dict()
        for unit in range(self.res.nunits()):
            unit_index = self._get_index_string('unit', unit)
            unit_solution = addict.Dict()

            unit_solution.update(self._load_solution_io(sim, unit, 'solution_inlet'))
            unit_solution.update(self._load_solution_io(sim, unit, 'solution_outlet'))
            unit_solution.update(self._load_solution_trivial(sim, unit, 'solution_bulk'))
            unit_solution.update(self._load_solution_particle(sim, unit, 'solution_particle'))
            unit_solution.update(self._load_solution_particle(sim, unit, 'solution_solid'))
            unit_solution.update(self._load_solution_trivial(sim, unit, 'solution_flux'))
            unit_solution.update(self._load_solution_trivial(sim, unit, 'solution_volume'))

            unit_solution.update(self._load_solution_io(sim, unit, 'soldot_inlet'))
            unit_solution.update(self._load_solution_io(sim, unit, 'soldot_outlet'))
            unit_solution.update(self._load_solution_trivial(sim, unit, 'soldot_bulk'))
            unit_solution.update(self._load_solution_particle(sim, unit, 'soldot_particle'))
            unit_solution.update(self._load_solution_particle(sim, unit, 'soldot_solid'))
            unit_solution.update(self._load_solution_trivial(sim, unit, 'soldot_flux'))
            unit_solution.update(self._load_solution_trivial(sim, unit, 'soldot_volume'))

            if len(unit_solution) > 0:
                solution[unit_index].update(unit_solution)

        if len(solution) > 0:
            sim.root.output.solution.update(solution)

        return solution

    def load_sensitivity(self, sim: "Cadet") -> None:
        """Load sensitivity data from simulation results."""
        sensitivity = addict.Dict()
        nsens = sim.root.input.sensitivity.get('nsens', 0)

        for sens in range(nsens):
            sens_index = self._get_index_string('param', sens)

            for unit in range(self.res.nunits()):
                unit_sensitivity = addict.Dict()
                unit_index = self._get_index_string('unit', unit)

                unit_sensitivity.update(
                    self._load_solution_io(sim, unit, 'sens_inlet', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_io(sim, unit, 'sens_outlet', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_trivial(sim, unit, 'sens_bulk', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_particle(sim, unit, 'sens_particle', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_particle(sim, unit, 'sens_solid', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_trivial(sim, unit, 'sens_flux', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_trivial(sim, unit, 'sens_volume', sens)
                )

                unit_sensitivity.update(
                    self._load_solution_io(sim, unit, 'sensdot_inlet', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_io(sim, unit, 'sensdot_outlet', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_trivial(sim, unit, 'sensdot_bulk', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_particle(sim, unit, 'sensdot_particle', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_particle(sim, unit, 'sensdot_solid', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_trivial(sim, unit, 'sensdot_flux', sens)
                )
                unit_sensitivity.update(
                    self._load_solution_trivial(sim, unit, 'sensdot_volume', sens)
                )

                if len(unit_sensitivity) > 0:
                    sensitivity[sens_index][unit_index] = unit_sensitivity

        if len(sensitivity) > 0:
            sim.root.output.sensitivity = sensitivity

    def load_state(self, sim: "Cadet") -> None:
        """Load last state from simulation results."""
        write_solution_last = sim.root.input['return'].get('write_solution_last', 0)
        if write_solution_last:
            sim.root.output['last_state_y'] = self.res.last_state_y()
            sim.root.output['last_state_ydot'] = self.res.last_state_ydot()

        write_sens_last = sim.root.input['return'].get('write_sens_last', 0)
        if write_sens_last:
            for idx in range(self.res.nsensitivities()):
                idx_str_y = self._get_index_string('last_state_sensy', idx)
                sim.root.output[idx_str_y] = self.res.last_state_sens(idx)
                idx_str_ydot = self._get_index_string('last_state_sensydot', idx)
                sim.root.output[idx_str_ydot] = self.res.last_state_sensdot(idx)

        solution = sim.root.output.solution
        for unit in range(self.res.nunits()):
            unit_index = self._get_index_string('unit', unit)
            write_solution_last = sim.root.input['return'][unit_index].get('write_solution_last_unit', 0)
            if write_solution_last:
                solution_last_unit = self.res.last_state_y_unit(unit)
                solution[unit_index]['last_state_y'] = solution_last_unit
                soldot_last_unit = self.res.last_state_ydot_unit(unit)
                solution[unit_index]['last_state_ydot'] = soldot_last_unit

    @staticmethod
    def _get_index_string(prefix: str, index: int) -> str:
        """Get a formatted string index (e.g., ('unit', 0) -> 'unit_000')."""
        return f'{prefix}_{index:03d}'

    def _checks_if_write_is_true(func):
        """Decorator to check if unit operation solution should be written out."""
        def wrapper(self, sim, unitOpId, solution_str, *args, **kwargs):
            unit_index = self._get_index_string('unit', unitOpId)
            write = sim.root.input['return'][unit_index].get(f'write_{solution_str}', 0)
            if not write:
                return {}
            solution = func(self, sim, unitOpId, solution_str, *args, **kwargs)
            if solution is None:
                return {}
            return solution
        return wrapper

    def _loads_data(func):
        """Decorator to load data from simulation results before processing further."""
        def wrapper(self, sim, unitOpId, solution_str, sensIdx=None, *args, **kwargs):
            solution_fun = getattr(self.res, solution_str)
            if sensIdx is None:
                data = solution_fun(unitOpId)
            else:
                data = solution_fun(unitOpId, sensIdx)
            if data is None:
                return
            solution = func(self, sim, data, unitOpId, solution_str, *args, **kwargs)
            return solution
        return wrapper

    @_checks_if_write_is_true
    @_loads_data
    def _load_solution_trivial(
            self,
            sim: "Cadet",
            data: tuple[numpy.ndarray, numpy.ndarray, list[int]],
            unitOpId: int,
            solution_str: str,
            sensIdx: Optional[int] = None
            ) -> addict.Dict:
        """Load trivial solution data from simulation results."""
        solution = addict.Dict()
        _, out, _ = data
        solution[solution_str] = out
        return solution

    @_checks_if_write_is_true
    @_loads_data
    def _load_solution_io(
            self,
            sim: "Cadet",
            data: tuple[numpy.ndarray, numpy.ndarray, list[int]],
            unitOpId: int,
            solution_str: str,
            sensIdx: Optional[int] = None
            ) -> addict.Dict:
        """Load IO-related solution data from simulation results."""
        solution = addict.Dict()
        _, out, dims = data

        split_components_data = sim.root.input['return'].get('split_components_data', 1)
        split_ports_data = sim.root.input['return'].get('split_ports_data', 1)
        single_as_multi_port = sim.root.input['return'].get('single_as_multi_port', 0)

        nComp_idx = dims.index('nComp')
        nComp = out.shape[nComp_idx]
        try:
            nPort_idx = dims.index('nPort')
            nPort = out.shape[nPort_idx]
        except ValueError:
            nPort_idx = None
            nPort = 1

        if split_components_data:
            if split_ports_data:
                if nPort == 1:
                    if single_as_multi_port:
                        for comp in range(nComp):
                            comp_out = out[..., 0, comp]
                            solution[f'{solution_str}_port_000_comp_{comp:03d}'] = comp_out
                    else:
                        for comp in range(nComp):
                            comp_out = out[..., comp]
                            solution[f'{solution_str}_comp_{comp:03d}'] = comp_out
                else:
                    for port in range(nPort):
                        for comp in range(nComp):
                            comp_out = out[..., port, comp]
                            solution[f'{solution_str}_port_{port:03d}_comp_{comp:03d}'] = comp_out
            else:
                for comp in range(nComp):
                    comp_out = out[..., comp]
                    solution[f'{solution_str}_comp_{comp:03d}'] = comp_out
        else:
            if split_ports_data:
                if nPort == 1:
                    if single_as_multi_port:
                        solution[f'{solution_str}_port_000'] = out
                    else:
                        solution[solution_str] = out[..., 0, :]
                else:
                    for port in range(nPort):
                        port_out = out[..., port, :]
                        solution[f'{solution_str}_port_{port:03d}'] = port_out
            else:
                if nPort == 1 and nPort_idx is not None:
                    solution[solution_str] = out[..., 0, :]
                else:
                    solution[solution_str] = out

        return solution

    @_checks_if_write_is_true
    def _load_solution_particle(
            self,
            sim: "Cadet",
            unitOpId: int,
            solution_str: str,
            sensIdx: Optional[int] = None
            ) -> addict.Dict:
        """Load particle-related solution data from simulation results."""
        solution = addict.Dict()
        solution_fun = getattr(self.res, solution_str)

        npartype = self.res.npartypes(unitOpId)

        for partype in range(npartype):
            if sensIdx is None:
                data = solution_fun(unitOpId, partype)
            else:
                data = solution_fun(unitOpId, sensIdx, partype)

            if data is None:
                continue

            _, out, dims = data

            if npartype == 1:
                solution[solution_str] = out
            else:
                par_index = self._get_index_string('partype', partype)
                solution[f'{solution_str}_{par_index}'] = out

        if len(solution) == 0:
            return addict.Dict()

        return solution

    @staticmethod
    def _get_index_string(prefix, index):
        """Helper method to get string indices (e.g. (unit, 0) -> 'unit_000')."""
        return f'{prefix}_{index:03d}'

    def load_meta(self, sim: "Cadet") -> None:
        """Load meta information about CADET."""

        sim.root.meta.cadet_branch = self.cadet_branch
        sim.root.meta.cadet_commit = self.cadet_commit_hash
        sim.root.meta.cadet_version = self.cadet_version
        sim.root.meta.file_format = self.res.file_format()
        sim.root.meta.time_sim = self.res.time_sim()

    @property
    def cadet_version(self) -> str:
        return self._cadet_version

    @property
    def cadet_branch(self) -> str:
        return self._cadet_branch

    @property
    def cadet_build_type(self) -> str:
        return self._cadet_build_type

    @property
    def cadet_commit_hash(self) -> str:
        return self._cadet_commit_hash

    @property
    def cadet_path(self) -> os.PathLike:
        return self._cadet_path
