# Edk2 BaseTools Regression Test Framework
This framework is to do the BaseTools regression test. Now it's only for AutoGen phase regression testing. The basic idea is to run the build twice and compare all the autogen files. It's expected that all the autogen files are the same.

This framework also supports BaseTools incremental build test. The incremental build test steps are as follows:
1. apply case patch and do a full build
2. Move Build folder to a temp directory
3. revert patch and do a full build
4. apply case patch and do an incremental build
5. compare the hash value of the incremental build Build folder and full build Build folder.

The incremental build test require the edk2 of https://github.com/BobCF/edk2.git, branch origin/IncrementalBuildTest.

## Required python library
* toml.  `pip install toml`
* pytest. `pip install pytest`
* filehash. `pip install filehash`

## Usage
- Incremental Build Test

  - Install tox

    `py -3 -m pip install tox`

  - clone edk2 for test 

    ` git clone https://github.com/BobCF/edk2.git`

    `git checkout IncrementalBuildTest`

  - set edk2 folder as z:\edk2

    `subst z: <path_2_edk2>`

  - execute test

    `py -3 -m tox`
- Common
  - clone this repository.

    `git clone https://github.com/BobCF/edk2_basetools_regression_test.git`

  - Copy basetools patches to BaseToolsPatches folder
  
  - Run the pytest

For clean build regression testing:

`pytest CleanRegression.py`

For incremental build regression testing:

`pytest IncrementalRegression.py`

For incremental build testing:

`pytest IncrementalTest.py`

For performance regression testing:

`pytest PerformanceRegression.py`

## File Structure
## Configuration file
## TODO list
* Test cases filter.
* The parameter of RegressionTest.py.
* Git commands wrapper.
* Test report generation.
* Windows and Linux support.
