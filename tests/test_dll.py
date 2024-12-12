from pathlib import Path
import subprocess
import pytest

from cadet import Cadet


# %% Utility methods

# Use this to specify custom cadet_roots if you require it.
cadet_root = None


def setup_model(
        cadet_root,
        use_dll=True,
        model='GENERAL_RATE_MODEL',
        n_partypes=1,
        ncol=10,
        npar=4,
        include_sensitivity=False,
        file_name='LWE.h5',
        n_components=4
        ):
    """
    Set up and initialize a CADET model template.

    This function prepares a CADET model template by invoking the `createLWE` executable
    with specified parameters. It supports the configuration of the model type, number
    of particle types, inclusion of sensitivity analysis, and the name of the output
    file. Depending on the operating system, it adjusts the executable name accordingly.
    After creating the model, it initializes a Cadet instance with the specified or
    default CADET binary and the created model file.

    Parameters
    ----------
    cadet_root : str or Path
        The root directory where the CADET software is located.
    use_dll : bool, optional
        If True, use the in-memory interface for CADET. Otherwise, use the CLI.
        The default is True.
    model : str, optional
        The model type to set up. The default is 'GENERAL_RATE_MODEL'.
    n_partypes : int, optional
        The number of particle types. The default is 1.
    ncol : int, optional
        The number of axial cells in the unit operation. The default is 10.
    npar : int, optional
        The number of particle cells in the unit operation. The default is 4.
    include_sensitivity : bool, optional
        If True, included parameter sensitivities in template. The default is False.
    file_name : str, optional
        The name of the file to which the CADET model is written.
        The default is 'LWE.h5'.
    n_components : int, optional
         Number of components for the simulation. The default is 4.

    Returns
    -------
    Cadet
        An initialized Cadet instance with the model loaded.

    Raises
    ------
    Exception
        If the creation of the test simulation encounters problems,
        detailed in the subprocess's stdout and stderr.
    FileNotFoundError
        If the CADET executable or DLL file cannot be found at the specified paths.

    Notes
    -----
    The function assumes the presence of `createLWE` executable within the `bin`
    directory of the `cadet_root` path. The sensitivity analysis, if included, is
    configured for column porosity.

    See Also
    --------
    Cadet : The class representing a CADET simulation model.

    Examples
    --------
    >>> cadet_model = setup_model(
        '/path/to/cadet',
        use_dll=False,
        model='GENERAL_RATE_MODEL',
        n_partypes=2,
        include_sensitivity=True,
        file_name='my_model.h5'
    )
    This example sets up a GENERAL_RATE_MODEL with 2 particle types, includes
    sensitivity analysis, and writes the model to 'my_model.h5', using the command-line
    interface.
    """

    cadet_model = Cadet(install_path=cadet_root, use_dll=use_dll)

    args = [
        cadet_model.cadet_create_lwe_path,
        f'--out {file_name}',
        f'--unit {model}',
        f'--parTypes {n_partypes}',
        f'--col {ncol}',
        f'--par {npar}',
    ]

    if include_sensitivity:
        args.append('--sens COL_POROSITY/-1/-1/-1/-1/-1/-1/0')

    ret = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd='./'
    )

    if ret.returncode != 0:
        if ret.stdout:
            print('Output', ret.stdout.decode('utf-8'))
        if ret.stderr:
            print('Errors', ret.stderr.decode('utf-8'))
        raise Exception(
            "Failure: Creation of test simulation ran into problems"
        )

    cadet_model.filename = file_name
    cadet_model.load()
    if n_components < 4:
        unit_000 = cadet_model.root.input.model.unit_000
        unit_000.update({
            'adsorption_model': 'LINEAR',
            'col_dispersion': 5.75e-08,
            'col_length': 0.014,
            'col_porosity': 0.37,
            'cross_section_area': 0.0003141592653589793,
            'film_diffusion': [6.9e-06, ] * n_components,
            'film_diffusion_multiplex': 0,
            'init_c': [0., ] * n_components,
            'init_q': [0., ] * n_components,
            'nbound': [1, ] * n_components,
            'ncomp': 1,
            'npartype': 1,
            'par_coreradius': 0.0,
            'par_diffusion': [7.00e-10, ] * n_components,
            'par_geom': 'SPHERE',
            'par_porosity': 0.75,
            'par_radius': 4.5e-05,
            'par_surfdiffusion': [0., ] * n_components,
            'unit_type': 'GENERAL_RATE_MODEL',
            'velocity': 1.0,
            'adsorption': {
                'is_kinetic': 0,
                'lin_ka': [0.] * n_components,
                'lin_kd': [1.] * n_components
            },
        })
        cadet_model.root.input.model.unit_001.update({
             'inlet_type': b'PIECEWISE_CUBIC_POLY',
             'ncomp': 1, 'unit_type': b'INLET',
             'sec_000': {
                 'const_coeff': [50., ],
                 'cube_coeff': [0., ],
                 'lin_coeff': [0., ],
                 'quad_coeff': [0., ]
             },
             'sec_001': {
                 'const_coeff': [50., ],
                 'cube_coeff': [0., ],
                 'lin_coeff': [0., ],
                 'quad_coeff': [0., ]
             },
             'sec_002': {
                 'const_coeff': [100., ],
                 'cube_coeff': [0.2, ],
                 'lin_coeff': [0., ],
                 'quad_coeff': [0., ]
             }
         }
        )
        # if we don't save and re-load the model we get windows access violations.
        # Interesting case for future tests, not what I want to test now.
        cadet_model.save()
        cadet_model = Cadet(install_path=cadet_root, use_dll=use_dll)
        cadet_model.filename = file_name
        cadet_model.load()

    return cadet_model


def setup_solution_recorder(
        model,
        split_components=0,
        split_ports=0,
        single_as_multi_port=0,
        ):
    """
    Configure the solution recorder for the simulation.

    This function adjusts the model's settings to specify what simulation data should
    be recorded, including solutions at various points (inlet, outlet, bulk, etc.),
    sensitivities, and their derivatives. It allows for the configuration of how
    components and ports are treated in the output data, potentially splitting them for
    individual analysis or aggregating them for a more holistic view.

    Parameters
    ----------
    model : Cadet
        The model instance to be configured for solution recording.
    split_components : int, optional
        If 1, split component data in the output. The default is 0.
    split_ports : int, optional
        If 1, split port data in the output. The default is 0.
    single_as_multi_port : int, optional
        If 1, treat single ports as multiple ports in the output. The default is 0.

    Examples
    --------
    >>> model = Cadet()
    >>> setup_solution_recorder(model, split_components=1, split_ports=1, single_as_multi_port=1)
    This example demonstrates configuring a Cadet model instance for detailed solution
    recording, with component and port data split, and single ports treated as multiple
    ports.

    """

    model.root.input['return'].write_solution_times = 1
    model.root.input['return'].write_solution_last = 1
    model.root.input['return'].write_sens_last = 1

    model.root.input['return'].split_components_data = split_components
    model.root.input['return'].split_ports_data = split_ports
    model.root.input['return'].single_as_multi_port = single_as_multi_port

    model.root.input['return'].unit_000.write_coordinates = 1

    model.root.input['return'].unit_000.write_solution_inlet = 1
    model.root.input['return'].unit_000.write_solution_outlet = 1
    model.root.input['return'].unit_000.write_solution_bulk = 1
    model.root.input['return'].unit_000.write_solution_particle = 1
    model.root.input['return'].unit_000.write_solution_solid = 1
    model.root.input['return'].unit_000.write_solution_flux = 1
    model.root.input['return'].unit_000.write_solution_volume = 1

    model.root.input['return'].unit_000.write_soldot_inlet = 1
    model.root.input['return'].unit_000.write_soldot_outlet = 1
    model.root.input['return'].unit_000.write_soldot_bulk = 1
    model.root.input['return'].unit_000.write_soldot_particle = 1
    model.root.input['return'].unit_000.write_soldot_solid = 1
    model.root.input['return'].unit_000.write_soldot_flux = 1
    model.root.input['return'].unit_000.write_soldot_volume = 1

    model.root.input['return'].unit_000.write_sens_inlet = 1
    model.root.input['return'].unit_000.write_sens_outlet = 1
    model.root.input['return'].unit_000.write_sens_bulk = 1
    model.root.input['return'].unit_000.write_sens_particle = 1
    model.root.input['return'].unit_000.write_sens_solid = 1
    model.root.input['return'].unit_000.write_sens_flux = 1
    model.root.input['return'].unit_000.write_sens_volume = 1

    model.root.input['return'].unit_000.write_sensdot_inlet = 1
    model.root.input['return'].unit_000.write_sensdot_outlet = 1
    model.root.input['return'].unit_000.write_sensdot_bulk = 1
    model.root.input['return'].unit_000.write_sensdot_particle = 1
    model.root.input['return'].unit_000.write_sensdot_solid = 1
    model.root.input['return'].unit_000.write_sensdot_flux = 1
    model.root.input['return'].unit_000.write_sensdot_volume = 1

    model.root.input['return'].unit_000.write_solution_last_unit = 1
    model.root.input['return'].unit_000.write_soldot_last_unit = 1

    for unit in range(model.root.input.model['nunits']):
        model.root.input['return']['unit_{0:03d}'.format(unit)] = model.root.input['return'].unit_000

    if model.filename is not None:
        model.save()


def run_simulation_with_options(use_dll, model_options, solution_recorder_options):
    """Run a simulation with specified options for the model and solution recorder.

    Initializes and configures a simulation model with given options, sets up the
    solution recording parameters, and executes the simulation. This function leverages
    `setup_model` to create and initialize the model and `setup_solution_recorder` to
    configure how the simulation results should be recorded based on the specified
    options.

    Parameters
    ----------
    use_dll : bool, optional
        If True, use the in-memory interface for CADET. Otherwise, use the CLI.
        The default is True.
    model_options : dict
        A dictionary of options to pass to `setup_model` for initializing the model.
        Keys should match the parameter names of `setup_model`, excluding `use_dll`.
    solution_recorder_options : dict
        A dictionary of options to pass to `setup_solution_recorder` for configuring the
        solution recorder. Keys should match the parameter names of
        `setup_solution_recorder`.

    Returns
    -------
    Cadet
        An instance of the Cadet class with the model simulated and loaded.

    Examples
    --------
    >>> use_dll = True
    >>> model_options = {
    ...     'model': 'GENERAL_RATE_MODEL',
    ...     'n_partypes': 2,
    ...     'include_sensitivity': True,
    ...     'file_name': 'model_output.h5'
    ... }
    >>> solution_recorder_options = {
    ...     'split_components': 1,
    ...     'split_ports': 1,
    ...     'single_as_multi_port': True
    ... }
    >>> model = run_simulation_with_options(use_dll, model_options, solution_recorder_options)
    This example configures and runs a GENERAL_RATE_MODEL with sensitivity analysis
    and two particle types, records the solution with specific options, and loads the
    simulation results for further analysis.
    """
    model = setup_model(cadet_root, use_dll, **model_options)
    setup_solution_recorder(model, **solution_recorder_options)

    return_info = model.run_load()

    if return_info.return_code != 0:
        raise RuntimeError(return_info)

    return model


# %% Model templates

cstr_template = {
    'model': 'CSTR',
    'n_partypes': 1,
    'include_sensitivity': False,
}

lrm_template = {
    'model': 'LUMPED_RATE_MODEL_WITHOUT_PORES',
    'ncol': 10,
    'n_partypes': 1,
    'include_sensitivity': False,
}

lrmp_template = {
    'model': 'LUMPED_RATE_MODEL_WITH_PORES',
    'ncol': 10,
    'n_partypes': 1,
    'include_sensitivity': False,
}

grm_template = {
    'model': 'GENERAL_RATE_MODEL',
    'ncol': 10,
    'npar': 5,
    'n_partypes': 1,
    'include_sensitivity': False,
}

grm_template_1_comp = {
    'model': 'GENERAL_RATE_MODEL',
    'n_partypes': 1,
    'ncol': 10,
    'npar': 5,
    'include_sensitivity': False,
    'n_components': 1,
}

grm_template_sens = {
    'model': 'GENERAL_RATE_MODEL',
    'n_partypes': 1,
    'ncol': 10,
    'npar': 5,
    'include_sensitivity': True,
}

grm_template_partypes = {
    'model': 'GENERAL_RATE_MODEL',
    'n_partypes': 2,
    'ncol': 10,
    'npar': 5,
    'include_sensitivity': False,
}

_2dgrm_template = {
    'model': 'GENERAL_RATE_MODEL_2D',
    'n_partypes': 1,
    'ncol': 10,
    'npar': 5,
    'include_sensitivity': False,
}


# %% Solution recorder templates

no_split = {
    'split_components': 0,
    'split_ports': 0,
    'single_as_multi_port': 0,
}

split_components = {
    'split_components': 1,
    'split_ports': 0,
    'single_as_multi_port': 0,
}

split_ports = {
    'split_components': 0,
    'split_ports': 1,
    'single_as_multi_port': 0,
}

split_ports_single_as_multi = {
    'split_components': 0,
    'split_ports': 1,
    'single_as_multi_port': 1,
}

split_all = {
    'split_components': 1,
    'split_ports': 1,
    'single_as_multi_port': 1,
}


# %% Test cases

class Case():
    def __init__(self, name, model_options, solution_recorder_options, expected_results):
        self.name = name
        self.model_options = model_options
        self.solution_recorder_options = solution_recorder_options
        self.expected_results = expected_results

    def __str__(self):
        return self.name

    def __repr__(self):
        return \
            f"Case('{self.name}', {self.model_options}, " \
            f"{self.solution_recorder_options}, {self.expected_results})"


# %% CSTR

cstr = Case(
    name='cstr',
    model_options=cstr_template,
    solution_recorder_options=no_split,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (21,),
        'last_state_ydot': (21,),
        'coordinates_unit_000': {},
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (13,),
            'last_state_ydot': (13,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),
            'solution_bulk': (1501, 4),
            'solution_solid': (1501, 4),
            'solution_volume': (1501,),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
            'soldot_bulk': (1501, 4),
            'soldot_solid': (1501, 4),
            'soldot_volume': (1501,),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
        },
    },
)


# %% LRM

lrm = Case(
    name='lrm',
    model_options=lrm_template,
    solution_recorder_options=no_split,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (92,),
        'last_state_ydot': (92,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (84,),
            'last_state_ydot': (84,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),
            'solution_bulk': (1501, 10, 4),
            'solution_solid': (1501, 10, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
            'soldot_bulk': (1501, 10, 4),
            'soldot_solid': (1501, 10, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),

        },
    },
)


# %% LRMP

lrmp = Case(
    name='lrmp',
    model_options=lrmp_template,
    solution_recorder_options=no_split,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (172,),
        'last_state_ydot': (172,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (164,),
            'last_state_ydot': (164,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),
            'solution_bulk': (1501, 10, 4),
            'solution_particle': (1501, 10, 4),
            'solution_solid': (1501, 10, 4),
            'solution_flux': (1501, 1, 10, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
            'soldot_bulk': (1501, 10, 4),
            'soldot_particle': (1501, 10, 4),
            'soldot_solid': (1501, 10, 4),
            'soldot_flux': (1501, 1, 10, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
        },
    },
)


# %% GRM (no_split)

grm = Case(
    name='grm',
    model_options=grm_template,
    solution_recorder_options=no_split,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (492,),
        'last_state_ydot': (492,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (484,),
            'last_state_ydot': (484,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),
            'solution_bulk': (1501, 10, 4),
            'solution_particle': (1501, 10, 5, 4),
            'solution_solid': (1501, 10, 5, 4),
            'solution_flux': (1501, 1, 10, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
            'soldot_bulk': (1501, 10, 4),
            'soldot_particle': (1501, 10, 5, 4),
            'soldot_solid': (1501, 10, 5, 4),
            'soldot_flux': (1501, 1, 10, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
        },
    },
)


# %% GRM (split_components)

grm_split_components = Case(
    name='grm_split_components',
    model_options=grm_template,
    solution_recorder_options=split_components,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (492,),
        'last_state_ydot': (492,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (484,),
            'last_state_ydot': (484,),

            'solution_inlet_comp_000': (1501,),
            'solution_inlet_comp_001': (1501,),
            'solution_inlet_comp_002': (1501,),
            'solution_inlet_comp_003': (1501,),
            'solution_outlet_comp_000': (1501,),
            'solution_outlet_comp_001': (1501,),
            'solution_outlet_comp_002': (1501,),
            'solution_outlet_comp_003': (1501,),
            'solution_bulk': (1501, 10, 4),
            'solution_particle': (1501, 10, 5, 4),
            'solution_solid': (1501, 10, 5, 4),
            'solution_flux': (1501, 1, 10, 4),

            'soldot_inlet_comp_000': (1501,),
            'soldot_inlet_comp_001': (1501,),
            'soldot_inlet_comp_002': (1501,),
            'soldot_inlet_comp_003': (1501,),
            'soldot_outlet_comp_000': (1501,),
            'soldot_outlet_comp_001': (1501,),
            'soldot_outlet_comp_002': (1501,),
            'soldot_outlet_comp_003': (1501,),
            'soldot_bulk': (1501, 10, 4),
            'soldot_particle': (1501, 10, 5, 4),
            'soldot_solid': (1501, 10, 5, 4),
            'soldot_flux': (1501, 1, 10, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet_comp_000': (1501,),
            'solution_inlet_comp_001': (1501,),
            'solution_inlet_comp_002': (1501,),
            'solution_inlet_comp_003': (1501,),
            'solution_outlet_comp_000': (1501,),
            'solution_outlet_comp_001': (1501,),
            'solution_outlet_comp_002': (1501,),
            'solution_outlet_comp_003': (1501,),

            'soldot_inlet_comp_000': (1501,),
            'soldot_inlet_comp_001': (1501,),
            'soldot_inlet_comp_002': (1501,),
            'soldot_inlet_comp_003': (1501,),
            'soldot_outlet_comp_000': (1501,),
            'soldot_outlet_comp_001': (1501,),
            'soldot_outlet_comp_002': (1501,),
            'soldot_outlet_comp_003': (1501,),
        },
    },
)


# %% GRM (split_ports)

grm_split_ports = Case(
    name='grm_split_ports',
    model_options=grm_template,
    solution_recorder_options=split_ports,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (492,),
        'last_state_ydot': (492,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (484,),
            'last_state_ydot': (484,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),
            'solution_bulk': (1501, 10, 4),
            'solution_particle': (1501, 10, 5, 4),
            'solution_solid': (1501, 10, 5, 4),
            'solution_flux': (1501, 1, 10, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
            'soldot_bulk': (1501, 10, 4),
            'soldot_particle': (1501, 10, 5, 4),
            'soldot_solid': (1501, 10, 5, 4),
            'soldot_flux': (1501, 1, 10, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
        },
    },
)

# %% GRM (split_ports_single_as_multi)

grm_split_ports_single_as_multi = Case(
    name='grm_split_ports_single_as_multi',
    model_options=grm_template,
    solution_recorder_options=split_ports_single_as_multi,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (492,),
        'last_state_ydot': (492,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (484,),
            'last_state_ydot': (484,),

            'solution_inlet_port_000': (1501, 4),
            'solution_outlet_port_000': (1501, 4),
            'solution_bulk': (1501, 10, 4),
            'solution_particle': (1501, 10, 5, 4),
            'solution_solid': (1501, 10, 5, 4),
            'solution_flux': (1501, 1, 10, 4),

            'soldot_inlet_port_000': (1501, 4),
            'soldot_outlet_port_000': (1501, 4),
            'soldot_bulk': (1501, 10, 4),
            'soldot_particle': (1501, 10, 5, 4),
            'soldot_solid': (1501, 10, 5, 4),
            'soldot_flux': (1501, 1, 10, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet_port_000': (1501, 4),
            'solution_outlet_port_000': (1501, 4),

            'soldot_inlet_port_000': (1501, 4),
            'soldot_outlet_port_000': (1501, 4),
        },
    },
)


# %% GRM (split_all)

grm_split_all = Case(
    name='grm_split_all',
    model_options=grm_template,
    solution_recorder_options=split_all,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (492,),
        'last_state_ydot': (492,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (484,),
            'last_state_ydot': (484,),

            'solution_inlet_port_000_comp_000': (1501,),
            'solution_inlet_port_000_comp_001': (1501,),
            'solution_inlet_port_000_comp_002': (1501,),
            'solution_inlet_port_000_comp_003': (1501,),
            'solution_outlet_port_000_comp_000': (1501,),
            'solution_outlet_port_000_comp_001': (1501,),
            'solution_outlet_port_000_comp_002': (1501,),
            'solution_outlet_port_000_comp_003': (1501,),
            'solution_bulk': (1501, 10, 4),
            'solution_particle': (1501, 10, 5, 4),
            'solution_solid': (1501, 10, 5, 4),
            'solution_flux': (1501, 1, 10, 4),

            'soldot_inlet_port_000_comp_000': (1501,),
            'soldot_inlet_port_000_comp_001': (1501,),
            'soldot_inlet_port_000_comp_002': (1501,),
            'soldot_inlet_port_000_comp_003': (1501,),
            'soldot_outlet_port_000_comp_000': (1501,),
            'soldot_outlet_port_000_comp_001': (1501,),
            'soldot_outlet_port_000_comp_002': (1501,),
            'soldot_outlet_port_000_comp_003': (1501,),
            'soldot_bulk': (1501, 10, 4),
            'soldot_particle': (1501, 10, 5, 4),
            'soldot_solid': (1501, 10, 5, 4),
            'soldot_flux': (1501, 1, 10, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet_port_000_comp_000': (1501,),
            'solution_inlet_port_000_comp_001': (1501,),
            'solution_inlet_port_000_comp_002': (1501,),
            'solution_inlet_port_000_comp_003': (1501,),
            'solution_outlet_port_000_comp_000': (1501,),
            'solution_outlet_port_000_comp_001': (1501,),
            'solution_outlet_port_000_comp_002': (1501,),
            'solution_outlet_port_000_comp_003': (1501,),

            'soldot_inlet_port_000_comp_000': (1501,),
            'soldot_inlet_port_000_comp_001': (1501,),
            'soldot_inlet_port_000_comp_002': (1501,),
            'soldot_inlet_port_000_comp_003': (1501,),
            'soldot_outlet_port_000_comp_000': (1501,),
            'soldot_outlet_port_000_comp_001': (1501,),
            'soldot_outlet_port_000_comp_002': (1501,),
            'soldot_outlet_port_000_comp_003': (1501,),
        },
    },
)


# %% GRM 1 Comp

grm_1_comp = Case(
    name='grm_1_comp',
    model_options=grm_template_1_comp,
    solution_recorder_options=no_split,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (123,),
        'last_state_ydot': (123,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (121,),
            'last_state_ydot': (121,),

            'solution_inlet': (1501, 1),
            'solution_outlet': (1501, 1),
            'solution_bulk': (1501, 10, 1),
            'solution_particle': (1501, 10, 5, 1),
            'solution_solid': (1501, 10, 5, 1),
            'solution_flux': (1501, 1, 10, 1),

            'soldot_inlet': (1501, 1),
            'soldot_outlet': (1501, 1),
            'soldot_bulk': (1501, 10, 1),
            'soldot_particle': (1501, 10, 5, 1),
            'soldot_solid': (1501, 10, 5, 1),
            'soldot_flux': (1501, 1, 10, 1),
        },
        'solution_unit_001': {
            'last_state_y': (1,),
            'last_state_ydot': (1,),

            'solution_inlet': (1501, 1),
            'solution_outlet': (1501, 1),
            'soldot_inlet': (1501, 1),
            'soldot_outlet': (1501, 1),
        },
    },
)


# %% GRM Sens

grm_sens = Case(
    name='grm_sens',
    model_options=grm_template_sens,
    solution_recorder_options=no_split,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (492,),
        'last_state_ydot': (492,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (484,),
            'last_state_ydot': (484,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),
            'solution_bulk': (1501, 10, 4),
            'solution_particle': (1501, 10, 5, 4),
            'solution_solid': (1501, 10, 5, 4),
            'solution_flux': (1501, 1, 10, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
            'soldot_bulk': (1501, 10, 4),
            'soldot_particle': (1501, 10, 5, 4),
            'soldot_solid': (1501, 10, 5, 4),
            'soldot_flux': (1501, 1, 10, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
        },
        'sens_param_000_unit_000': {
            'sens_inlet': (1501, 4),
            'sens_outlet': (1501, 4),
            'sens_bulk': (1501, 10, 4),
            'sens_particle': (1501, 10, 5, 4),
            'sens_solid': (1501, 10, 5, 4),
            'sens_flux': (1501, 1, 10, 4),

            'sensdot_inlet': (1501, 4),
            'sensdot_outlet': (1501, 4),
            'sensdot_bulk': (1501, 10, 4),
            'sensdot_particle': (1501, 10, 5, 4),
            'sensdot_solid': (1501, 10, 5, 4),
            'sensdot_flux': (1501, 1, 10, 4),
        },
        'sens_param_000_unit_001': {
            'sens_inlet': (1501, 4),
            'sens_outlet': (1501, 4),

            'sensdot_inlet': (1501, 4),
            'sensdot_outlet': (1501, 4),
        },
    },
)

# %% GRM ParTypes

grm_par_types = Case(
    name='grm_par_types',
    model_options=grm_template_partypes,
    solution_recorder_options=no_split,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (932,),
        'last_state_ydot': (932,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
            'particle_coordinates_001': (5,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (924,),
            'last_state_ydot': (924,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),
            'solution_bulk': (1501, 10, 4),
            'solution_particle_partype_000': (1501, 10, 5, 4),
            'solution_particle_partype_001': (1501, 10, 5, 4),
            'solution_solid_partype_000': (1501, 10, 5, 4),
            'solution_solid_partype_001': (1501, 10, 5, 4),
            'solution_flux': (1501, 2, 10, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
            'soldot_bulk': (1501, 10, 4),
            'soldot_particle_partype_000': (1501, 10, 5, 4),
            'soldot_particle_partype_001': (1501, 10, 5, 4),
            'soldot_solid_partype_000': (1501, 10, 5, 4),
            'soldot_solid_partype_001': (1501, 10, 5, 4),
            'soldot_flux': (1501, 2, 10, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
        },
    },
)

# %% 2D GRM
_2dgrm = Case(
    name='_2dgrm',
    model_options=_2dgrm_template,
    solution_recorder_options=no_split,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (1468,),
        'last_state_ydot': (1468,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
            'radial_coordinates': (3,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (1452,),
            'last_state_ydot': (1452,),

            'solution_inlet': (1501, 3, 4),
            'solution_outlet': (1501, 3, 4),
            'solution_bulk': (1501, 10, 3, 4),
            'solution_particle': (1501, 10, 3, 5, 4),
            'solution_solid': (1501, 10, 3, 5, 4),
            'solution_flux': (1501, 1, 10, 3, 4),

            'soldot_inlet': (1501, 3, 4),
            'soldot_outlet': (1501, 3, 4),
            'soldot_bulk': (1501, 10, 3, 4),
            'soldot_particle': (1501, 10, 3, 5, 4),
            'soldot_solid': (1501, 10, 3, 5, 4),
            'soldot_flux': (1501, 1, 10, 3, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
        },
    },
)

# %% 2D GRM Split Ports (single_as_multi_port=False)

_2dgrm_split_ports = Case(
    name='_2dgrm_split_ports',
    model_options=_2dgrm_template,
    solution_recorder_options=split_ports,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (1468,),
        'last_state_ydot': (1468,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
            'radial_coordinates': (3,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (1452,),
            'last_state_ydot': (1452,),

            'solution_inlet_port_000': (1501, 4),
            'solution_inlet_port_001': (1501, 4),
            'solution_inlet_port_002': (1501, 4),
            'solution_outlet_port_000': (1501, 4),
            'solution_outlet_port_001': (1501, 4),
            'solution_outlet_port_002': (1501, 4),
            'solution_bulk': (1501, 10, 3, 4),
            'solution_particle': (1501, 10, 3, 5, 4),
            'solution_solid': (1501, 10, 3, 5, 4),
            'solution_flux': (1501, 1, 10, 3, 4),

            'soldot_inlet_port_000': (1501, 4),
            'soldot_inlet_port_001': (1501, 4),
            'soldot_inlet_port_002': (1501, 4),
            'soldot_outlet_port_000': (1501, 4),
            'soldot_outlet_port_001': (1501, 4),
            'soldot_outlet_port_002': (1501, 4),
            'soldot_bulk': (1501, 10, 3, 4),
            'soldot_particle': (1501, 10, 3, 5, 4),
            'soldot_solid': (1501, 10, 3, 5, 4),
            'soldot_flux': (1501, 1, 10, 3, 4),

        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),

            'solution_inlet': (1501, 4),
            'solution_outlet': (1501, 4),

            'soldot_inlet': (1501, 4),
            'soldot_outlet': (1501, 4),
        },
    },
)

# %% 2D GRM Split All

_2dgrm_split_all = Case(
    name='_2dgrm_split_all',
    model_options=_2dgrm_template,
    solution_recorder_options=split_all,
    expected_results={
        'solution_times': (1501,),
        'last_state_y': (1468,),
        'last_state_ydot': (1468,),
        'coordinates_unit_000': {
            'axial_coordinates': (10,),
            'particle_coordinates_000': (5,),
            'radial_coordinates': (3,),
        },
        'coordinates_unit_001': {},
        'solution_unit_000': {
            'last_state_y': (1452,),
            'last_state_ydot': (1452,),

            'solution_inlet_port_000_comp_000': (1501,),
            'solution_inlet_port_000_comp_001': (1501,),
            'solution_inlet_port_000_comp_002': (1501,),
            'solution_inlet_port_000_comp_003': (1501,),
            'solution_inlet_port_001_comp_000': (1501,),
            'solution_inlet_port_001_comp_001': (1501,),
            'solution_inlet_port_001_comp_002': (1501,),
            'solution_inlet_port_001_comp_003': (1501,),
            'solution_inlet_port_002_comp_000': (1501,),
            'solution_inlet_port_002_comp_001': (1501,),
            'solution_inlet_port_002_comp_002': (1501,),
            'solution_inlet_port_002_comp_003': (1501,),
            'solution_outlet_port_000_comp_000': (1501,),
            'solution_outlet_port_000_comp_001': (1501,),
            'solution_outlet_port_000_comp_002': (1501,),
            'solution_outlet_port_000_comp_003': (1501,),
            'solution_outlet_port_001_comp_000': (1501,),
            'solution_outlet_port_001_comp_001': (1501,),
            'solution_outlet_port_001_comp_002': (1501,),
            'solution_outlet_port_001_comp_003': (1501,),
            'solution_outlet_port_002_comp_000': (1501,),
            'solution_outlet_port_002_comp_001': (1501,),
            'solution_outlet_port_002_comp_002': (1501,),
            'solution_outlet_port_002_comp_003': (1501,),
            'solution_bulk': (1501, 10, 3, 4),
            'solution_particle': (1501, 10, 3, 5, 4),
            'solution_solid': (1501, 10, 3, 5, 4),
            'solution_flux': (1501, 1, 10, 3, 4),

            'soldot_inlet_port_000_comp_000': (1501,),
            'soldot_inlet_port_000_comp_001': (1501,),
            'soldot_inlet_port_000_comp_002': (1501,),
            'soldot_inlet_port_000_comp_003': (1501,),
            'soldot_inlet_port_001_comp_000': (1501,),
            'soldot_inlet_port_001_comp_001': (1501,),
            'soldot_inlet_port_001_comp_002': (1501,),
            'soldot_inlet_port_001_comp_003': (1501,),
            'soldot_inlet_port_002_comp_000': (1501,),
            'soldot_inlet_port_002_comp_001': (1501,),
            'soldot_inlet_port_002_comp_002': (1501,),
            'soldot_inlet_port_002_comp_003': (1501,),
            'soldot_outlet_port_000_comp_000': (1501,),
            'soldot_outlet_port_000_comp_001': (1501,),
            'soldot_outlet_port_000_comp_002': (1501,),
            'soldot_outlet_port_000_comp_003': (1501,),
            'soldot_outlet_port_001_comp_000': (1501,),
            'soldot_outlet_port_001_comp_001': (1501,),
            'soldot_outlet_port_001_comp_002': (1501,),
            'soldot_outlet_port_001_comp_003': (1501,),
            'soldot_outlet_port_002_comp_000': (1501,),
            'soldot_outlet_port_002_comp_001': (1501,),
            'soldot_outlet_port_002_comp_002': (1501,),
            'soldot_outlet_port_002_comp_003': (1501,),
            'soldot_bulk': (1501, 10, 3, 4),
            'soldot_particle': (1501, 10, 3, 5, 4),
            'soldot_solid': (1501, 10, 3, 5, 4),
            'soldot_flux': (1501, 1, 10, 3, 4),
        },
        'solution_unit_001': {
            'last_state_y': (4,),
            'last_state_ydot': (4,),
            'solution_inlet_port_000_comp_000': (1501,),
            'solution_inlet_port_000_comp_001': (1501,),
            'solution_inlet_port_000_comp_002': (1501,),
            'solution_inlet_port_000_comp_003': (1501,),
            'solution_outlet_port_000_comp_000': (1501,),
            'solution_outlet_port_000_comp_001': (1501,),
            'solution_outlet_port_000_comp_002': (1501,),
            'solution_outlet_port_000_comp_003': (1501,),

            'soldot_inlet_port_000_comp_000': (1501,),
            'soldot_inlet_port_000_comp_001': (1501,),
            'soldot_inlet_port_000_comp_002': (1501,),
            'soldot_inlet_port_000_comp_003': (1501,),
            'soldot_outlet_port_000_comp_000': (1501,),
            'soldot_outlet_port_000_comp_001': (1501,),
            'soldot_outlet_port_000_comp_002': (1501,),
            'soldot_outlet_port_000_comp_003': (1501,),
        },
    },
)



# %% Testing utils

def assert_keys(model_dict: dict, expected_dict: dict):
    """
    Assert that the keys of two dictionaries are identical.

    Parameters
    ----------
    model_dict : dict
        The dictionary whose keys are to be compared.
    expected_dict : dict
        The dictionary containing the expected set of keys.

    Raises
    ------
    AssertionError
        If the keys of `model_dict` and `expected_dict` do not match.

    Examples
    --------
    >>> assert_keys({"a": 1, "b": 2}, {"b": 3, "a": 4})
    True
    >>> assert_keys({"a": 1, "b": 2}, {"b": 3, "c": 4})
    Traceback (most recent call last):
    ...
    AssertionError: Key mismatch. Expected {'b', 'c'}, but got {'b', 'a'}.
    """
    model_keys = set(model_dict.keys())
    expected_keys = set(expected_dict.keys())
    assert model_keys == expected_keys, (
        f"Key mismatch. Expected {expected_keys}, but got {model_keys}."
    )


def assert_shape(array_shape, expected_shape, context, key, unit_id=None):
    """
    Assert that the shape of an array matches the expected shape.

    Parameters
    ----------
    array_shape : tuple
        The shape of the actual array to validate.
    expected_shape : tuple
        The expected shape to compare against.
    context : str
        High-level context for the assertion,
        e.g., 'last_state', 'coordinates', 'solution'.
    key : str
        Specific key or identifier within the context.
    unit_id : str, optional
        Unit identifier, e.g., 'unit_000'. If not provided, it is assumed the context
        does not require unit-specific validation.

    Raises
    ------
    AssertionError
        If the actual shape does not match the expected shape, including detailed context.

    """
    unit_info = f"in unit '{unit_id}'" if unit_id else ""
    assert array_shape == expected_shape, (
        f"Shape mismatch {unit_info} for {context}[{key}]. "
        f"Expected {expected_shape}, but got {array_shape}."
    )


# %% Actual tests

use_dll = [False, True]

test_cases = [
    cstr,
    lrm,
    lrmp,
    grm,
    grm_split_components,
    grm_split_ports,
    grm_split_ports_single_as_multi,
    grm_split_all,
    grm_1_comp,
    grm_sens,
    grm_par_types,
    _2dgrm,
    _2dgrm_split_ports,
    _2dgrm_split_all
]


@pytest.mark.parametrize("use_dll", use_dll, ids=[f"{case}" for case in use_dll])
@pytest.mark.parametrize("test_case", test_cases, ids=[case.name for case in test_cases])
def test_simulator_options(use_dll, test_case):
    model_options = test_case.model_options
    solution_recorder_options = test_case.solution_recorder_options
    expected_results = test_case.expected_results

    model = run_simulation_with_options(
        use_dll, model_options, solution_recorder_options
    )

    # Assert solution_times shape
    assert_shape(
        model.root.output.solution.solution_times.shape,
        expected_results['solution_times'],
        context="solution",
        key="solution_times"
    )

    # Assert last_state shapes
    assert_shape(
        model.root.output.last_state_y.shape,
        expected_results['last_state_y'],
        context="last_state",
        key="y"
    )
    assert_shape(
        model.root.output.last_state_ydot.shape,
        expected_results['last_state_ydot'],
        context="last_state",
        key="ydot"
    )

    # Check coordinates
    unit = "unit_000"
    excpected_coordinates = expected_results[f'coordinates_{unit}']
    coordinates_unit = model.root.output.coordinates[unit]
    assert_keys(coordinates_unit, excpected_coordinates)

    for key, value in excpected_coordinates.items():
        coordinates_shape = coordinates_unit[key].shape
        assert_shape(
            coordinates_shape,
            value,
            context="coordinates",
            key=key,
            unit_id=unit,
        )

    unit = "unit_001"
    excpected_coordinates = expected_results[f'coordinates_{unit}']
    coordinates_unit = model.root.output.coordinates[unit]
    assert_keys(coordinates_unit, excpected_coordinates)

    for key, value in excpected_coordinates.items():
        coordinates_shape = coordinates_unit[key].shape
        assert_shape(
            coordinates_shape,
            value,
            context="coordinates",
            key=key,
            unit_id=unit,
        )

    # Check solution
    unit = "unit_000"
    excpected_solution = expected_results[f'solution_{unit}']
    solution_unit = model.root.output.solution[unit]
    assert_keys(excpected_solution, solution_unit)

    for key, value in excpected_solution.items():
        shape = solution_unit[key].shape
        assert_shape(
            shape,
            value,
            context="solution",
            key=key,
            unit_id=unit,
        )

    unit = "unit_001"
    excpected_solution = expected_results[f'solution_{unit}']
    solution_unit = model.root.output.solution[unit]
    assert_keys(excpected_solution, solution_unit)

    for key, value in excpected_solution.items():
        shape = solution_unit[key].shape
        assert_shape(
            shape,
            value,
            context="solution",
            key=key,
            unit_id=unit,
        )

    # Check sensitivity
    if model_options['include_sensitivity']:
        unit = "unit_000"
        excpected_sensitivity = expected_results[f'sens_param_000_{unit}']
        sensitivity_unit = model.root.output.sensitivity.param_000[unit]
        assert_keys(excpected_sensitivity, sensitivity_unit)

        for key, value in excpected_sensitivity.items():
            shape = sensitivity_unit[key].shape
            assert_shape(
                shape,
                value,
                context="sensitivity",
                key=key,
                unit_id=unit,
            )

        unit = "unit_001"
        excpected_sensitivity = expected_results[f'sens_param_000_{unit}']
        sensitivity_unit = model.root.output.sensitivity.param_000[unit]
        assert_keys(excpected_sensitivity, sensitivity_unit)

        for key, value in excpected_sensitivity.items():
            shape = sensitivity_unit[key].shape
            assert_shape(
                shape,
                value,
                context="sensitivity",
                key=key,
                unit_id=unit,
            )


@pytest.mark.parametrize("use_dll", use_dll)
@pytest.mark.parametrize("test_case", [grm])
def test_meta(use_dll, test_case):
    model_options = test_case.model_options
    solution_recorder_options = test_case.solution_recorder_options
    expected_results = test_case.expected_results

    model = run_simulation_with_options(
        use_dll, model_options, solution_recorder_options
    )

    meta_information = {
        'cadet_branch': str,
        'cadet_commit': str,
        'cadet_version': str,
        'file_format': int,
        'time_sim': float,
    }

    assert model.root.meta.keys() == meta_information.keys()

    for meta_key, meta_type in meta_information.items():
        assert isinstance(model.root.meta[meta_key], meta_type)


if __name__ == "__main__":
    pytest.main(["test_dll.py"])
