from cadet import Cadet
from joblib import Parallel, delayed
from .test_dll import setup_model

n_jobs = 2


def run_simulation(model):
    model.save()
    data = model.run_load()
    model.delete_file()

    return data


def test_parallelization_io():
    model1 = Cadet()
    model1.root.input = {'model': 1}
    model1.filename = "sim_1.h5"
    model2 = Cadet()
    model2.root.input = {'model': 2}
    model2.filename = "sim_2.h5"

    models = [model1, model2]

    results_sequential = [run_simulation(model) for model in models]

    results_parallel = Parallel(n_jobs=n_jobs, verbose=0)(
        delayed(run_simulation)(model, ) for model in models
    )
    assert results_sequential == results_parallel


def test_parallelization_simulation():
    models = [setup_model(Cadet.autodetect_cadet(), file_name=f"LWE_{i}.h5") for i in range(2)]

    results_sequential = [run_simulation(model) for model in models]

    results_parallel = Parallel(n_jobs=n_jobs, verbose=0)(
        delayed(run_simulation)(model, ) for model in models
    )
    assert results_sequential == results_parallel


if __name__ == "__main__":
    pytest.main([__file__])
