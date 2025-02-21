import os
import docker
import pytest

from cadet import Cadet
from cadet.runner import CadetDockerRunner
from tests.test_dll import setup_model

os.chdir("docker_resources")


@pytest.fixture
def my_docker_image_tag():
    client = docker.from_env()

    image, logs = client.images.build(
        path=".",
        tag="cadet-docker-test",
        quiet=False,
    )

    # for log in logs:
    #     print(log)

    return_info = client.containers.run(
        image=image,
        command="cadet-cli --version"
    )

    if len(return_info.decode()[:10000]) < 1:
        raise RuntimeError("Docker build went wrong.")
    return image.tags[0]


@pytest.mark.local
@pytest.mark.docker
def test_docker_version(my_docker_image_tag):
    runner = CadetDockerRunner(my_docker_image_tag)
    assert len(runner.cadet_version) > 0
    assert len(runner.cadet_branch) > 0
    assert len(runner.cadet_build_type) > 0
    assert len(runner.cadet_commit_hash) > 0

@pytest.mark.local
@pytest.mark.docker
def test_docker_runner(my_docker_image_tag):
    model = setup_model(Cadet.autodetect_cadet(), file_name=f"LWE_docker.h5")
    runner = CadetDockerRunner(my_docker_image_tag)
    runner.run(model)
    model.load()
    assert hasattr(model.root, "output")
    assert hasattr(model.root.output, "solution")
    assert hasattr(model.root.output.solution, "unit_000")


@pytest.mark.local
@pytest.mark.docker
def test_docker_run(my_docker_image_tag):
    simulator = Cadet(docker_container=my_docker_image_tag)
    simulator.filename = "LWE_docker.h5"
    simulator.save()
    model = setup_model(Cadet.autodetect_cadet(), file_name=f"LWE_docker.h5")
    simulator.root.input.update(model.root.input)
    simulator.run_load()
    assert hasattr(simulator.root, "output")
    assert hasattr(simulator.root.output, "solution")
    assert hasattr(simulator.root.output.solution, "unit_000")
