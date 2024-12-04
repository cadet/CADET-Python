import os
from pathlib import Path
import platform
import shutil
import subprocess
from typing import Optional
import warnings

from addict import Dict

from cadet.h5 import H5
from cadet.runner import CadetRunnerBase, CadetCLIRunner, ReturnInformation
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


def install_path_to_cadet_paths(
        install_path: Optional[os.PathLike],
        ) -> tuple[Optional[Path], Optional[Path], Optional[Path], Optional[Path]]:
    """
    Get the correct paths (root_path, cadet_cli_path, cadet_dll_path, cadet_create_lwe_path)
     from the installation path of CADET. This is extracted into a function to be used
     in both the meta class and the cadet class itself.

    Parameters
    ----------
    install_path : Optional[os.PathLike]
        Path to the root of the CADET installation or the executable file 'cadet-cli'.
        If a file path is provided, the root directory will be inferred.

    Returns
    -------
    tuple[Optional[Path], Optional[Path], Optional[Path], Optional[Path]]
        Tuple with CADET installation paths
        (root_path, cadet_cli_path, cadet_dll_path, cadet_create_lwe_path)
    """
    if install_path is None:
        return None, None, None, None

    install_path = Path(install_path)

    if install_path.is_file():
        cadet_root = install_path.parent.parent
        warnings.warn(
            "The specified install_path is not the root of the CADET installation. "
            "It has been inferred from the file path."
        )
    else:
        cadet_root = install_path

    root_path = cadet_root

    cli_executable = 'cadet-cli'
    lwe_executable = 'createLWE'

    if platform.system() == 'Windows':
        cli_executable += '.exe'
        lwe_executable += '.exe'

    cadet_cli_path = cadet_root / 'bin' / cli_executable
    if cadet_cli_path.is_file():
        cadet_cli_path = cadet_cli_path
    else:
        raise FileNotFoundError(
            "CADET could not be found. Please check the path."
        )

    cadet_create_lwe_path = cadet_root / 'bin' / lwe_executable
    if cadet_create_lwe_path.is_file():
        cadet_create_lwe_path = cadet_create_lwe_path.as_posix()

    if platform.system() == 'Windows':
        dll_path = cadet_root / 'bin' / 'cadet.dll'
        dll_debug_path = cadet_root / 'bin' / 'cadet_d.dll'
    else:
        dll_path = cadet_root / 'lib' / 'libcadet.so'
        dll_debug_path = cadet_root / 'lib' / 'libcadet_d.so'

    # Look for debug dll if dll is not found.
    if not dll_path.is_file() and dll_debug_path.is_file():
        dll_path = dll_debug_path

    if dll_path.is_file():
        cadet_dll_path = dll_path
    else:
        cadet_dll_path = None

    return root_path, cadet_cli_path, cadet_dll_path, cadet_create_lwe_path


class CadetMeta(type):
    """
    Meta class for the CADET interface.

    This meta class allows setting the `cadet_path` attribute for all instances of the
    `Cadet` class.
    """
    use_dll = False
    cadet_cli_path = None
    cadet_dll_path = None
    cadet_create_lwe_path = None

    @property
    def cadet_path(cls) -> Optional[Path]:
        """
        Get the current CADET path.

        Returns
        -------
        Optional[Path]
            The current CADET path if set, otherwise None.
        """
        if cls.use_dll and cls.cadet_dll_path is not None:
            return cls.cadet_dll_path
        elif cls.cadet_cli_path is not None:
            return cls.cadet_cli_path
        else:
            return None

    @cadet_path.setter
    def cadet_path(cls, cadet_path: Optional[os.PathLike]) -> None:
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
        warnings.warn(
            "Support for setting Cadet.cadet_path will be removed in a future version. "
            "Please set the `install_path` on instance level.",
            DeprecationWarning
        )
        if cadet_path is None:
            cls.use_dll = False
            cls._install_path = None
            cls.cadet_cli_path = None
            cls.cadet_dll_path = None
            cls.cadet_create_lwe_path = None
            return

        cadet_path = Path(cadet_path)

        cls.use_dll = cadet_path.suffix in [".dll", ".so"]

        _install_path, cadet_cli_path, cadet_dll_path, cadet_create_lwe_path = install_path_to_cadet_paths(cadet_path)

        cls._install_path = _install_path
        cls.cadet_create_lwe_path = cadet_create_lwe_path
        cls.cadet_cli_path = cadet_cli_path
        cls.cadet_dll_path = cadet_dll_path


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

    def __init__(self, install_path: Optional[Path] = None, use_dll: bool = False, *data):
        """
        Initialize a new instance of the Cadet class.
        Priority order of install_paths is:
        1. install_path set in __init__ args
        2. install_path set in CadetMeta
        3. auto-detected install_path

        Parameters
        ----------
        *data : tuple
            Additional data to be passed to the H5 base class initialization.
        """
        super().__init__(*data)

        self.cadet_create_lwe_path: Optional[Path] = None
        self.return_information: Optional[dict] = None

        self._cadet_cli_runner: Optional[CadetCLIRunner] = None
        self._cadet_dll_runner: Optional[CadetDLLRunner] = None

        # Regardless of settings in the Meta Class, if we get an install_path, we respect the install_path
        if install_path is not None:
            self.use_dll = use_dll
            self.install_path = install_path  # This will set _cadet_dll_runner and _cadet_cli_runner
            return

        # If _cadet_cli_runner_class has been set in the Meta Class, use them, else instantiate Nones
        if hasattr(self, "cadet_cli_path") and self.cadet_cli_path is not None:
            self._cadet_cli_runner: Optional[CadetCLIRunner] = CadetCLIRunner(
                self.cadet_cli_path
            )
        else:
            self._cadet_cli_runner: Optional[CadetCLIRunner] = None
            self.use_dll = use_dll

        if hasattr(self, "cadet_dll_path") and self.cadet_dll_path is not None:
            try:
                self._cadet_dll_runner: Optional[CadetDLLRunner] = CadetDLLRunner(
                    self.cadet_dll_path
                )
            except ValueError:
                self.cadet_dll_path = None
                self._cadet_dll_runner: Optional[CadetCLIRunner] = None
                self.use_dll = False
        else:
            self._cadet_dll_runner: Optional[CadetCLIRunner] = None
            self.use_dll = use_dll

        # If any runner has been set in the Meta Class, don't auto-detect Cadet, just return
        if self._cadet_cli_runner is not None or self._cadet_dll_runner is not None:
            return

        # If neither Meta Class nor install_path are given: auto-detect Cadet
        self.install_path = self.autodetect_cadet()

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
        install_path : Optional[os.PathLike]
            Path to the root of the CADET installation or the executable file 'cadet-cli'.
            If a file path is provided, the root directory will be inferred.
        """
        if install_path is None:
            self._install_path = None
            self.cadet_cli_path = None
            self.cadet_dll_path = None
            self.cadet_create_lwe_path = None
            return

        root_path, cadet_cli_path, cadet_dll_path, create_lwe_path = install_path_to_cadet_paths(install_path)

        self._install_path = root_path
        self.cadet_create_lwe_path = create_lwe_path

        if cadet_cli_path is not None:
            self._cadet_cli_runner = CadetCLIRunner(cadet_cli_path)
            self.cadet_cli_path = cadet_cli_path

        self.cadet_dll_path = cadet_dll_path
        if cadet_dll_path is not None:
            try:
                self._cadet_dll_runner = CadetDLLRunner(cadet_dll_path)
            except ValueError:
                pass

    @property
    def cadet_path(self) -> Optional[Path]:
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
        warnings.warn(
            "Deprecation warning: Support for setting cadet.cadet_path will be removed "
            " in a future version. Use `install_path` instead.",
            FutureWarning
        )
        self.install_path = cadet_path

    @staticmethod
    def autodetect_cadet() -> Optional[Path]:
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

        return cadet_root

    @property
    def cadet_runner(self) -> CadetRunnerBase:
        """
        Get the current CADET runner instance.

        Returns
        -------
        Optional[CadetRunnerBase]
            The current runner instance, either a DLL or file-based runner.
        """

        if self.use_dll and self.found_dll:
            return self._cadet_dll_runner

        if self.use_dll and not self.found_dll:
            raise ValueError("Set Cadet to use_dll but no dll interface found.")

        return self._cadet_cli_runner

    def create_lwe(self, file_path=None):
        """Create basic LWE example and loads the configuration into self.

        Parameters
        ----------
        file_path : Path, optional
            Path to store HDF5 file. If None, temporary file will be created and
            deleted after simulation.

        """
        file_path_input = file_path
        if file_path is None:
            file_name = "LWE.h5"
            cwd = os.getcwd()
            file_path = Path(cwd) / file_name
        else:
            file_path = Path(file_path).absolute()
            file_name = file_path.name
            cwd = file_path.parent.as_posix()

        ret = subprocess.run(
            [self.cadet_create_lwe_path, '-o', file_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
        )
        if ret.returncode != 0:
            if ret.stdout:
                print('Output', ret.stdout.decode('utf-8'))
            if ret.stderr:
                print('Errors', ret.stderr.decode('utf-8'))
            raise RuntimeError(
                "Failure: Creation of test simulation ran into problems"
            )

        self.filename = file_path

        self.load()

        if file_path_input is None:
            os.remove(file_path)

        return self

    @property
    def found_dll(self):
        """
        Check if a DLL interface was found.

        Returns
        -------
        bool
            True if a cadet DLL interface was found.
            False otherwise.
        """
        return self.cadet_dll_path is not None

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
    ) -> ReturnInformation:
        """
        Run the CADET simulation.

        Parameters
        ----------
        timeout : Optional[int]
            Maximum time allowed for the simulation to run, in seconds.

        Returns
        -------
        ReturnInformation
            Information about the simulation run.
        """
        return_information = self.cadet_runner.run(
            self,
            timeout=timeout,
        )

        return return_information

    def run_load(
            self,
            timeout: Optional[int] = None,
            clear: bool = True
    ) -> ReturnInformation:
        """
        Run the CADET simulation and load the results.

        Parameters
        ----------
        timeout : Optional[int]
            Maximum time allowed for the simulation to run, in seconds.
        clear : bool
            If True, clear previous results after loading new ones.

        Returns
        -------
        ReturnInformation
            Information about the simulation run.
        """
        return_information = self.run(timeout)
        self.load_results()

        if clear:
            self.clear()
        return return_information

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

    def delete_file(self) -> None:
        if self.filename is not None:
            try:
                os.remove(self.filename)
            except FileNotFoundError:
                pass

    def __del__(self):
        self.clear()
        del self._cadet_dll_runner
        del self._cadet_cli_runner

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        # Restore the state and cast to addict.Dict() to add __frozen attributes
        state = Dict(state)
        self.__dict__.update(state)
