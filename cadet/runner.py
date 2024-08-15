from abc import ABC, abstractmethod
import ctypes
import os
from pathlib import Path
import subprocess
from typing import Optional, Any


class CadetRunnerBase(ABC):
    """
    Abstract base class for CADET runners.

    Subclasses must implement the `run`, `clear`, and `load_results` methods.
    """

    @abstractmethod
    def run(
            self,
            simulation: "Cadet",
            timeout: Optional[int] = None,
            ) -> bool:
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
        bool
            True, if simulation ran successfully, False otherwise.
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


class CadetFileRunner(CadetRunnerBase):
    """
    File-based CADET runner.

    This class runs CADET simulations using a command-line interface (CLI) executable.
    """

    def __init__(self, cadet_path: str) -> None:
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
            ) -> bool:
        """
        Run a CADET simulation using the CLI executable.

        Parameters
        ----------
        simulation : Cadet
            Not used in this runner.
        timeout : Optional[int]
            Maximum time allowed for the simulation to run, in seconds.

        Returns
        -------
        bool
            True if the simulation ran successfully, False otherwise.

        Raises
        ------
        RuntimeError
            If the simulation process returns a non-zero exit code.
        """
        if simulation.filename is None:
            raise ValueError("Filename must be set before run can be used")

        data = subprocess.run(
            [self.cadet_path, str(simulation.filename)],
            timeout=timeout,
            capture_output=True
        )

        if data.returncode != 0:
            raise RuntimeError(
                f"Simulation failed with error: {data.stderr.decode('utf-8')}"
            )

        return True

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
