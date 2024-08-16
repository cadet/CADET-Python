import os
import pathlib
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ReturnInformation:
    """
    Class to store information about a CADET run return status.

    Parameters
    ----------
    return_code : int
        An integer representing the return code. 0 indicates success, non-zero values indicate errors.
    error_message : str
        A string containing the error message if an error occurred. Empty if no error.
    log : str
        A string containing log information.
    """
    return_code: int
    error_message: str
    log: str


class CadetRunnerBase(ABC):
    """
    Abstract base class for CADET runners.

    Subclasses must implement the `run`, `clear`, and `load_results` methods.
    """
    cadet_path: Optional[pathlib.Path] = None

    @abstractmethod
    def run(
            self,
            simulation: "Cadet",
            timeout: Optional[int] = None,
    ) -> ReturnInformation:
        """
        Run a CADET simulation.

        Parameters
        ----------
        simulation : Cadet
            The simulation object.
        timeout : Optional[int]
            Maximum time allowed for the simulation to run, in seconds.

        Returns
        -------
        ReturnInformation
            Information about the simulation run.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the simulation data.
        """
        pass

    @abstractmethod
    def load_results(self, sim: "Cadet") -> None:
        """
        Load the results of the simulation into the provided object.

        Parameters
        ----------
        sim : Cadet
            The simulation object where results will be loaded.
        """
        pass


class CadetCLIRunner(CadetRunnerBase):
    """
    File-based CADET runner.

    This class runs CADET simulations using a command-line interface (CLI) executable.
    """

    def __init__(self, cadet_path: str | os.PathLike) -> None:
        """
        Initialize the CadetFileRunner.

        Parameters
        ----------
        cadet_path : os.PathLike
            Path to the CADET CLI executable.
        """
        cadet_path = Path(cadet_path)

        self.cadet_path = cadet_path

    def run(
            self,
            simulation: "Cadet",
            timeout: Optional[int] = None,
    ) -> ReturnInformation:
        """
        Run a CADET simulation using the CLI executable.

        Parameters
        ----------
        simulation : Cadet
            Not used in this runner.
        timeout : Optional[int]
            Maximum time allowed for the simulation to run, in seconds.

        Raises
        ------
        RuntimeError
            If the simulation process returns a non-zero exit code.

        Returns
        -------
        ReturnInformation
            Information about the simulation run.
        """
        if simulation.filename is None:
            raise ValueError("Filename must be set before run can be used")

        data = subprocess.run(
            [self.cadet_path, str(simulation.filename)],
            timeout=timeout,
            capture_output=True
        )

        return_info = ReturnInformation(
            return_code=data.returncode,
            error_message=data.stderr.decode('utf-8'),
            log=data.stdout.decode('utf-8')
        )

        return return_info

    def clear(self) -> None:
        """
        Clear the simulation data.

        This method can be extended if any cleanup is required.
        """
        pass

    def load_results(self, sim: "Cadet") -> None:
        """
        Load the results of the simulation into the provided object.

        Parameters
        ----------
        sim : Cadet
            The simulation object where results will be loaded.
        """
        sim.load(paths=["/meta", "/output"], update=True)
