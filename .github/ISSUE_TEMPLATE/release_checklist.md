---
name: Release checklist
about: Checklist to make a release
title: ''
labels: 'maintenance'
assignees: ''

---

# CADET-Python Release Checklist

CADET-Python follows the semantic versioning system described at [semver.org](https://semver.org/).

CADET-Python is released direcntly from the master branch and deployed to PyPi via a GitHub workflow automatically, and to conda-forge semi-automatically.

The following checklist describes the steps to execute sequentially for creating a new release.

---

## Preparation

- [ ] Create a version bump commit `Bump version to vX.X.X`:
  - Update the version number in 
  - `__init__.py`
  - `zenodo.json` (two places)

---

## Creating the release on GitHub

- [ ] Go to [GitHub Releases](https://github.com/cadet/CADET-Core/releases/new):
  - Set the release branch as the target
  - Specify the tag `vX.X.X` according to semantic versioning
  - Add release notes with sections for Added, Fixed, Changed, and Updated
  - Publish the release.
- [ ] Check deployment on PyPi via the CI and the [PyPi CADET-Python website](https://pypi.org/project/CADET-Python/)
- [ ] Verify Zenodo archiving:
  - Confirm that a version-specific DOI was created
  - Ensure that the source code and associated files are archived
  - Note that the [concept DOI](https://doi.org/10.5281/zenodo.14132721) remains constant

## Deployment on pypi

- [ ] Check if the GitHub action with workflow file `python-publish.yml` ran successfully, fix if required.

## Deployment on conda-forge

- [ ] Go to your fork of [cadet-feedstock](https://github.com/conda-forge/cadet-python-feedstock) or create one if it does not exist
- [ ] Create a new branch on your fork and change the file `recipe/meta.yaml`:
  - install openSSL
  - Generate the SHA256 key (replace `{{ version }}` with the semantic version number):  
    ```bash
    curl -sL https://github.com/cadet/CADET-Python/archive/refs/tags/v{{ version }}.tar.gz | openssl sha256
    ```
  - Update the version number and SHA256 key
  - Set the build number to zero (`build: number: 0`)
- [ ] Open a PR onto the `main` branch of `conda-forge/cadet-feedstock`, and complete the automatically generated checklist
  - Note: to check if the license file is included, check the tarball (`https://github.com/cadet/CADET-Python/archive/refs/tags/v{{ version }}.tar.gz`) if the License file is in the location specified in the meta.yml in the variable `license_file`
- [ ] Wait for the automatic checks to pass
- [ ] Merge the pull request to trigger the conda-forge release
- [ ] Double check if the new version of cadet-python is on conda-forge

---

## Follow-up
- [ ] If this release checklist was updated, add these changes to the corresponding issue template
