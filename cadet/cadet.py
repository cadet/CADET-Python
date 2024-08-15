import platform
import shutil
import subprocess
import warnings
from pathlib import Path

from cadet.h5 import H5
from cadet.runner import CadetRunnerBase, CadetFileRunner
from cadet.cadet_dll import CadetDLLRunner


def is_dll(value):
    suffix = Path(value).suffix
    return suffix in {'.so', '.dll'}


class CadetMeta(type):
    """
    A meta class for the CADET interface. This allows calls to Cadet.cadet_path = "..." to set
    the cadet_path for all subsequent Cadet() instances.
    """
    _cadet_runner_class = None
    _is_file_class = None

    @property
    def is_file(cls):
        return bool(cls._is_file_class)

    @property
    def cadet_path(cls):
        if cls._cadet_runner_class is not None:
            return cls._cadet_runner_class.cadet_path

    @cadet_path.setter
    def cadet_path(cls, value):
        if cls._cadet_runner_class is not None and cls._cadet_runner_class.cadet_path != value:
            del cls._cadet_runner_class

        if is_dll(value):
            cls._cadet_runner_class = CadetDLLRunner(value)
            cls._is_file_class = False
        else:
            cls._cadet_runner_class = CadetFileRunner(value)
            cls._is_file_class = True

    @cadet_path.deleter
    def cadet_path(cls):
        del cls._cadet_runner_class


class Cadet(H5, metaclass=CadetMeta):
    # cadet_path must be set in order for simulations to run
    def __init__(self, *data):
        super().__init__(*data)
        self._cadet_runner = None

        self._is_file = None  # Is CLI or DLL
        # self.cadet_path  # from Bill, declared in meta class -> path to CLI-file or DLL-file

        self.install_path = None  # from Jo -> root of the CADET installation.

        self.cadet_cli_path = None
        self.cadet_dll_path = None
        self.cadet_create_lwe_path = None

        self.return_information = None

    @property
    def is_file(self):
        if self._is_file is not None:
            return bool(self._is_file)
        if self._is_file_class is not None:
            return bool(self._is_file_class)

    @property
    def cadet_runner(self):
        if self._cadet_runner is not None:
            return self._cadet_runner
        if hasattr(self, "_cadet_runner_class") and self._cadet_runner_class is not None:
            return self._cadet_runner_class
        self.autodetect_cadet()
        return self._cadet_runner

    @property
    def cadet_path(self):
        runner = self.cadet_runner
        if runner is not None:
            return runner.cadet_path

    @cadet_path.setter
    def cadet_path(self, value):
        if self._cadet_runner is not None and self._cadet_runner.cadet_path != value:
            del self._cadet_runner

        if is_dll(value):
            self._cadet_runner = CadetDLLRunner(value)
            self._is_file = False
        else:
            self._cadet_runner = CadetFileRunner(value)
            self._is_file = True

    @cadet_path.deleter
    def cadet_path(self):
        del self._cadet_runner

    def autodetect_cadet(self):
        """
        Autodetect installation CADET based on operating system and API usage.

        Returns
        -------
        cadet_root : Path
            Installation path of the CADET program.
        """
        executable = 'cadet-cli'
        if platform.system() == 'Windows':
            executable += '.exe'

        # Searching for the executable in system path
        path = shutil.which(executable)

        if path is None:
            raise FileNotFoundError(
                "Could not autodetect CADET installation. Please provide path."
            )

        cli_path = Path(path)

        cadet_root = None
        if cli_path is not None:
            cadet_root = cli_path.parent.parent
            self.install_path = cadet_root

        return cadet_root

    @property
    def install_path(self):
        """str: Path to the installation of CADET.

        This can either be the root directory of the installation or the path to the
        executable file 'cadet-cli'. If a file path is provided, the root directory will
        be inferred.

        Raises
        ------
        FileNotFoundError
            If CADET cannot be found at the specified path.

        Warnings
        --------
        If the specified install_path is not the root of the CADET installation, it will
        be inferred from the file path.

        See Also
        --------
        check_cadet
        """
        return self._install_path

    @install_path.setter
    def install_path(self, install_path):
        """
        Set the installation path of CADET.

        Parameters
        ----------
        install_path : str or Path
            Path to the root of the CADET installation.
            It should either be the root directory of the installation or the path
            to the executable file 'cadet-cli'.
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
                "CADET could not be found. Please check the path"
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

        # Look for debug dll if dll is not found.
        if not dll_path.is_file() and dll_debug_path.is_file():
            dll_path = dll_debug_path

        # Look for debug dll if dll is not found.
        if dll_path.is_file():
            self.cadet_dll_path = dll_path.as_posix()

    def transform(self, x):
        return str.upper(x)

    def inverse_transform(self, x):
        return str.lower(x)

    def load_results(self):
        runner = self.cadet_runner
        if runner is not None:
            runner.load_results(self)

    def run(self, timeout=None, check=None):
        data = self.cadet_runner.run(simulation=self.root.input, filename=self.filename, timeout=timeout, check=check)
        # TODO: Why is this commented out?
        # self.return_information = data
        return data

    def run_load(self, timeout = None, check=None, clear=True):
        data = self.cadet_runner.run(
            simulation=self.root.input,
            filename=self.filename,
            timeout=timeout,
            check=check
        )
        # TODO: Why is this commented out?
        # self.return_information = data
        self.load_results()
        if clear:
            self.clear()
        return data

    def clear(self):
        runner = self.cadet_runner
        if runner is not None:
            runner.clear()
