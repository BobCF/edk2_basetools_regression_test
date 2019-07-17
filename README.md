# Edk2 BaseTools Regression Test Framework
This framework is to do the BaseTools regression test. Now it's only for AutoGen phase regression testing. The basic idea is to run the build twice and compare all the autogen files. It's expected that all the autogen files are the same.

## Required python library
* toml.  `pip install toml`
* pytest. `pip install pytest`
## Usage
1. clone this repository.

`git clone https://github.com/BobCF/edk2_basetools_regression_test.git`

2. Copy basetools patches to BaseToolsPatches folder

3. Run the pytest

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
