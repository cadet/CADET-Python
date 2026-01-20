---
name: Release checklist
about: Checklist to make a release
title: ''
labels: 'maintenance'
assignees: ''

---

# CADET-Python Release Checklist

CADET-Python follows the semantic versioning system described at [semver.org](https://semver.org/).

CADET-Python is released direcntly from the master branch and deployed to PyPi via a GitHub workflow atuomatically.

The following checklist describes the steps to execute sequentially for creating a new release.

---

## Preparation

- [ ] Create a version bump commit `Bump version to vX.X.X`:
  - Update the version number in 
  - `__init__.py`
  - `zenodo.json` (two places), `cadet.hpp` and 

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

---

## Follow-up
- [ ] If this release checklist was updated, add these changes to the corresponding issue template
