import os
from pathlib import Path
import platform
import shutil
import subprocess
from typing import Optional
import warnings

from cadet.h5 import H5
from cadet.runner import CadetRunnerBase, CadetFileRunner
from cadet.cadet_dll import CadetDLLRunner


def is_dll(path: os.PathLike) -> bool:
    """
    Determine if the given path points to a shared library.

    Parameters
    ----------
    path : os.PathLike
        Path to the file.

    Returns
    -------
    bool
        True if the file has a shared library extension (.so, .dll), False otherwise.
    """
    suffix = Path(path).suffix
    return suffix in {'.so', '.dll'}


class CadetMeta(type):
    """
    Meta class for the CADET interface.

    This meta class allows setting the `cadet_path` attribute for all instances of the
    `Cadet` class. The `cadet_path` determines whether to use a DLL or file-based CADET
    runner.
    """

    @property
    def is_file(cls) -> bool:
        """
        Check if the current runner is file-based.

        Returns
        -------
        bool
            True if the current runner is file-based, False otherwise.
        """
        return bool(cls._is_file_class)

    @property
    def cadet_path(cls) -> Optional[Path]:
        """
        Get the current CADET path.

        Returns
        -------
        Optional[Path]
            The current CADET path if set, otherwise None.
        """
        if cls._cadet_runner_class is not None:
            return cls._cadet_runner_class.cadet_path
        return None

    @cadet_path.setter
    def cadet_path(cls, cadet_path: os.PathLike) -> None:
        """
        Set the CADET path and initialize the appropriate runner.

        Parameters
        ----------
        cadet_path : os.PathLike
            Path to the CADET executable or library.

        Notes
        -----
        If the path is a DLL, a `CadetDLLRunner` runner is used.
        Otherwise, a `CadetFileRunner` runner is used.
        """
        cadet_path = Path(cadet_path)
        if (
                cls._cadet_runner_class is not None
                and
                cls._cadet_runner_class.cadet_path != cadet_path
                ):
            del cls._cadet_runner_class

        if is_dll(cadet_path):
            cls._cadet_runner_class = CadetDLLRunner(cadet_path)
            cls._is_file_class = False
        else:
            cls._cadet_runner_class = CadetFileRunner(cadet_path)
            cls._is_file_class = True

    @cadet_path.deleter
    def cadet_path(cls) -> None:
        """
        Delete the current CADET runner instance.
        """
        del cls._cadet_runner_class


class Cadet(H5, metaclass=CadetMeta):
    """
    CADET interface class.

    This class manages the CADET runner, whether it's based on a CLI executable or a DLL,
    and provides methods for running simulations and loading results.

    Attributes
    ----------
    install_path : Optional[Path]
        The root directory of the CADET installation.
    cadet_cli_path : Optional[Path]
        Path to the 'cadet-cli' executable.
    cadet_dll_path : Optional[Path]
        Path to the 'cadet.dll' or equivalent shared library.
    cadet_create_lwe_path : Optional[Path]
        Path to the 'createLWE' executable.
    return_information : Optional[dict]
        Stores the information returned after a simulation run.
    """

    def __init__(self, *data):
        """
        Initialize a new instance of the Cadet class.

        Parameters
        ----------
        *data : tuple
            Additional data to be passed to the base class.
        """
        super().__init__(*data)
        self._cadet_runner: Optional[CadetRunnerBase] = None
        self._is_file: Optional[bool] = None
        self.install_path: Optional[Path] = None
        self.cadet_cli_path: Optional[Path] = None
        self.cadet_dll_path: Optional[Path] = None
        self.cadet_create_lwe_path: Optional[Path] = None
        self.return_information: Optional[dict] = None

    @property
    def is_file(self) -> Optional[bool]:
        """
        Check if the current runner is file-based.

        Returns
        -------
        Optional[bool]
            True if the runner is file-based, False otherwise. None if undetermined.
        """
        if self._is_file is not None:
            return bool(self._is_file)
        if self._is_file_class is not None:
            return bool(self._is_file_class)
        return None

    @property
    def cadet_runner(self) -> CadetRunnerBase:
        """
        Get the current CADET runner instance.

        Returns
        -------
        CadetRunnerBase
            The current runner instance, either a DLL or file-based runner.
        """
        if self._cadet_runner is not None:
            return self._cadet_runner
        if hasattr(self, "_cadet_runner_class") and self._cadet_runner_class is not None:
            return self._cadet_runner_class

        self.autodetect_cadet()

        return self._cadet_runner

    @property
    def cadet_path(self) -> Path:
        """
        Get the path to the current CADET executable or library.

        Returns
        -------
        Path
            The path to the current CADET executable or library if set, otherwise None.
        """
        runner = self.cadet_runner
        if runner is not None:
            return runner.cadet_path
        return None

    @cadet_path.setter
    def cadet_path(self, cadet_path: os.PathLike) -> None:
        """
        Set the CADET path and initialize the appropriate runner.

        Parameters
        ----------
        cadet_path : os.PathLike
            Path to the CADET executable or library.

        Notes
        -----
        If the path is a DLL, a `CadetDLLRunner` runner is used.
        Otherwise, a `CadetFileRunner` runner is used.
        """
        cadet_path = Path(cadet_path)

        if self._cadet_runner is not None and self._cadet_runner.cadet_path != cadet_path:
            del self._cadet_runner

        if is_dll(cadet_path):
            self._cadet_runner = CadetDLLRunner(cadet_path)
            self._is_file = False
        else:
            self._cadet_runner = CadetFileRunner(cadet_path)
            self._is_file = True

    @cadet_path.deleter
    def cadet_path(self) -> None:
        """
        Delete the current CADET runner instance.
        """
        del self._cadet_runner

    def autodetect_cadet(self) -> Optional[Path]:
        """
        Autodetect the CADET installation path.

        Returns
        -------
        Optional[Path]
            The root directory of the CADET installation.

        Raises
        ------
        FileNotFoundError
            If CADET cannot be found in the system path.
        """
        executable = 'cadet-cli'
        if platform.system() == 'Windows':
            executable += '.exe'

        path = shutil.which(executable)

        if path is None:
            raise FileNotFoundError(
                "Could not autodetect CADET installation. Please provide path."
            )

        cli_path = Path(path)
        cadet_root = cli_path.parent.parent if cli_path else None
        if cadet_root:
            self.install_path = cadet_root

        return cadet_root

    @property
    def install_path(self) -> Optional[Path]:
        """
        Path to the installation of CADET.

        Returns
        -------
        Optional[Path]
            The root directory of the CADET installation or the path to 'cadet-cli'.
        """
        return self._install_path

    @install_path.setter
    def install_path(self, install_path: Optional[os.PathLike]) -> None:
        """
        Set the installation path of CADET.

        Parameters
        ----------
        install_path : Path | os.PathLike | None
            Path to the root of the CADET installation or the executable file 'cadet-cli'.
            If a file path is provided, the root directory will be inferred.
        """
        if install_path is None:
            self._install_path = None
            self.cadet_cli_path = None
            self.cadet_dll_path = None
            self.cadet_create_lwe_path = None
            return

        install_path = Path(install_path)

        if install_path.is_file():
            cadet_root = install_path.parent.parent
            warnings.warn(
                "The specified install_path is not the root of the CADET installation. "
                "It has been inferred from the file path."
            )
        else:
            cadet_root = install_path

        self._install_path = cadet_root

        cli_executable = 'cadet-cli'
        lwe_executable = 'createLWE'

        if platform.system() == 'Windows':
            cli_executable += '.exe'
            lwe_executable += '.exe'

        cadet_cli_path = cadet_root / 'bin' / cli_executable
        if cadet_cli_path.is_file():
            self.cadet_cli_path = cadet_cli_path
            self.cadet_path = cadet_cli_path
        else:
            raise FileNotFoundError(
                "CADET could not be found. Please check the path."
            )

        cadet_create_lwe_path = cadet_root / 'bin' / lwe_executable
        if cadet_create_lwe_path.is_file():
            self.cadet_create_lwe_path = cadet_create_lwe_path.as_posix()

        if platform.system() == 'Windows':
            dll_path = cadet_root / 'bin' / 'cadet.dll'
            dll_debug_path = cadet_root / 'bin' / 'cadet_d.dll'
        else:
            dll_path = cadet_root / 'lib' / 'lib_cadet.so'
            dll_debug_path = cadet_root / 'lib' / 'lib_cadet_d.so'

        if not dll_path.is_file() and dll_debug_path.is_file():
            dll_path = dll_debug_path

        if dll_path.is_file():
            self.cadet_dll_path = dll_path.as_posix()

    def transform(self, x: str) -> str:
        """
        Transform the input string to uppercase.

        Parameters
        ----------
        x : str
            Input string.

        Returns
        -------
        str
            Transformed string in uppercase.
        """
        return str.upper(x)

    def inverse_transform(self, x: str) -> str:
        """
        Transform the input string to lowercase.

        Parameters
        ----------
        x : str
            Input string.

        Returns
        -------
        str
            Transformed string in lowercase.
        """
        return str.lower(x)

    def run(
            self,
            timeout: Optional[int] = None,
            ) -> None:
        """
        Run the CADET simulation.

        Parameters
        ----------
        timeout : Optional[int]
            Maximum time allowed for the simulation to run, in seconds.
        """
        self.cadet_runner.run(
            self,
            timeout=timeout,
        )

    def run_load(
            self,
            timeout: Optional[int] = None,
            clear: bool = True
            ) -> None:
        """
        Run the CADET simulation and load the results.

        Parameters
        ----------
        timeout : Optional[int]
            Maximum time allowed for the simulation to run, in seconds.
        clear : bool
            If True, clear previous results after loading new ones.
        """
        self.run(timeout)
        self.load_results()

        if clear:
            self.clear()

    def load_results(self) -> None:
        """Load the results of the last simulation run into the current instance."""
        runner = self.cadet_runner
        if runner is not None:
            runner.load_results(self)

    def clear(self) -> None:
        """Clear the loaded results from the current instance."""
        runner = self.cadet_runner
        if runner is not None:
            runner.clear()
