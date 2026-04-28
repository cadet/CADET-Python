from pathlib import Path
import subprocess
import pytest
import numpy as np
from packaging.version import Version
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
        '--out', file_name,
        '--unit', model,
        '--parTypes', str(n_partypes),
        '--ncol', str(ncol),
        '--npar', str(npar),
    ]

    if include_sensitivity:
        args.extend(['-S', 'COL_POROSITY/-1/-1/-1/-1/-1/-1/0'])

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
    cadet_model.load_from_file()
    if n_components < 4:
        unit_000 = cadet_model.root.input.model.unit_000
        unit_000.update({
            'adsorption_model': 'LINEAR',
            'col_dispersion': 5.75e-08,
            'col_length': 0.014,
            'col_porosity': 0.37,
            'cross_section_area': 0.0003141592653589793,
            'init_c': [0., ] * n_components,
            'ncomp': 1,
            'npartype': 1,
            'unit_type': 'GENERAL_RATE_MODEL',
            'velocity': 1.0
        })
        par = cadet_model.root.input.model.unit_000.particle_type_000
        par.update({
            'par_coreradius': 0.0,
            'par_diffusion': [7.00e-10, ] * n_components,
            'par_geom': 'SPHERE',
            'par_porosity': 0.75,
            'par_radius': 4.5e-05,
            'par_surfdiffusion': [0., ] * n_components,
            'nbound': [1, ] * n_components,
            'init_cs': [0., ] * n_components,
            'film_diffusion': [6.9e-06, ] * n_components,
            'film_diffusion_multiplex': 0,
            'adsorption': {
                            'is_kinetic': 0,
                            'lin_ka': [0.] * n_components,
                            'lin_kd': [1.] * n_components
                        }
        })
        cadet_model.root.input.model.unit_001.update({
             'inlet_type': b'PIECEWISE_CUBIC_POLY',
             'ncomp': 1, 'unit_type': b'INLET',
             'sec_000': {
                 'const_coeff': [50., ],
                 'cube_coeff': [0., ],
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
        cadet_model.load_from_file()

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


def reduce_to_single_section(model):
    """Reduce a multi-section model to a single section.

    perform_simulation_step only supports models with exactly one section.
    This helper keeps only the first section and updates nsec, section_times,
    section_continuity, and user_solution_times accordingly.
    """
    sections = model.root.input.solver.sections
    end_time = float(sections.section_times[1])
    sections.section_times = [0.0, end_time]
    sections.nsec = 1
    sections.section_continuity = []

    # Trim user_solution_times to the new end time
    solver = model.root.input.solver
    if hasattr(solver, 'user_solution_times') and solver.user_solution_times is not None:
        ust = np.asarray(solver.user_solution_times)
        solver.user_solution_times = ust[ust <= end_time]

    if model.filename is not None:
        model.save()


# %% Model templates

cstr_template = {
    'model': 'CSTR',
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

# %% Test cases


class Case:
    def __init__(self, name, model_options):
        self.name = name
        self.model_options = model_options

    def __repr__(self):
        return f"Case('{self.name}', {self.model_options})"


# %% Test case instances

cstr = Case(name='cstr', model_options=cstr_template)
grm = Case(name='grm', model_options=grm_template)


# %% Tests for stepped simulation (CAPI >= 1.1.0a2)

_runner = Cadet(install_path=cadet_root, use_dll=True)._cadet_dll_runner
_has_step_api = _runner._cadet_capi_version >= Version("1.1.0a2")

requires_1_1_0a2_api = pytest.mark.skipif(
    not _has_step_api, reason="Requires CADET CAPI >= 1.1.0a2"
)


def _init_stepped_model(test_case, file_name='test_step.h5'):
    """Set up a model, configure recording, and initialize the simulation."""
    model = setup_model(
        cadet_root, use_dll=True, file_name=file_name, **test_case.model_options
    )
    setup_solution_recorder(model)
    reduce_to_single_section(model)
    return_info = model.initialize_simulation()
    assert return_info.return_code == 0
    assert return_info.error_message == ""
    assert isinstance(return_info.log, str)
    return model


@requires_1_1_0a2_api
@pytest.mark.parametrize("test_case", [cstr, grm])
def test_initialize_simulation(test_case):
    """Test that initialization succeeds and end_simulation cleans up."""
    model = _init_stepped_model(test_case, file_name='test_init.h5')
    model.end_simulation()
    model.delete_file()


@requires_1_1_0a2_api
@pytest.mark.parametrize("test_case", [cstr, grm])
def test_step_to_end(test_case):
    """Test stepping through the simulation in 10 increments."""
    model = _init_stepped_model(test_case, file_name='test_step_to_end.h5')

    section_times = model.root.input.solver.sections.section_times
    total_time = section_times[-1]
    step_size = total_time / 10
    t_current = 0.0

    while t_current < total_time:
        t_target = min(t_current + step_size, total_time)
        return_info, t_reached = model.perform_simulation_step(t_target)
        assert return_info.return_code == 0
        assert t_reached > t_current or t_reached == total_time
        t_current = t_reached

    model.end_simulation()
    model.delete_file()


@requires_1_1_0a2_api
@pytest.mark.parametrize("test_case", [cstr, grm])
def test_step_results_match_full_simulation(test_case):
    """Verify that a single step to end produces the same state as a full run."""
    # Full simulation
    model_full = setup_model(
        cadet_root, use_dll=True,
        file_name='test_results_full.h5', **test_case.model_options
    )
    setup_solution_recorder(model_full)
    reduce_to_single_section(model_full)
    assert model_full.run_simulation().return_code == 0

    last_state_y_full = model_full.root.output.last_state_y.copy()
    last_state_ydot_full = model_full.root.output.last_state_ydot.copy()

    # Stepped simulation (one step to end)
    model_step = _init_stepped_model(test_case, file_name='test_results_step.h5')
    total_time = model_step.root.input.solver.sections.section_times[-1]

    return_info, _ = model_step.perform_simulation_step(total_time)
    assert return_info.return_code == 0

    res = model_step.cadet_runner.res
    last_state_y_step = res.last_state_y()
    last_state_ydot_step = res.last_state_ydot()
    model_step.end_simulation()

    np.testing.assert_allclose(
        last_state_y_step, last_state_y_full, rtol=1e-8, atol=1e-10,
    )
    np.testing.assert_allclose(
        last_state_ydot_step, last_state_ydot_full, rtol=1e-8, atol=1e-10,
    )
    model_full.delete_file()
    model_step.delete_file()


@requires_1_1_0a2_api
@pytest.mark.parametrize("test_case", [cstr, grm])
def test_intermediate_state_access(test_case):
    """Test that intermediate states can be read and time progresses."""
    model = _init_stepped_model(test_case, file_name='test_step_state_access.h5')

    total_time = model.root.input.solver.sections.section_times[-1]
    fractions = [0.1, 0.25, 0.5, 0.75]

    prev_t = 0.0
    prev_shape = None
    for frac in fractions:
        return_info, t_reached = model.perform_simulation_step(total_time * frac)
        assert return_info.return_code == 0
        assert t_reached > prev_t

        state = model.cadet_runner.res.last_state_y()
        if prev_shape is not None:
            assert state.shape == prev_shape
        prev_shape = state.shape
        prev_t = t_reached

    model.end_simulation()
    model.delete_file()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

    
