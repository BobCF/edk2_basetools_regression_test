import pytest
from py._xmlgen import html
import os

@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(2, html.th("Full Time"))
    cells.insert(3, html.th("Incremental Time"))
    cells.insert(4, html.th("Test Case Location"))
    cells.pop()
    cells.pop()
@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    cells.insert(2, html.td(report.fulltime))
    cells.insert(3, html.td(report.inctime))
    cells.insert(4, html.td(report.description))
    cells.pop()
    cells.pop()

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    desc = report.nodeid[report.nodeid.index("[")+1:report.nodeid.index("]")]
    case_desc = desc
    case_location = ''
    if "|" in desc:
        case_desc, case_location =  desc.split("|")
        case_location = os.path.dirname(case_location)
    report.nodeid = case_desc

    case = item._pyfuncitem.funcargs.get('setup_cases')
    if case:
        fulltime = case.fullbuildtime
        inctime = case.incbuildtime
    else:
        fulltime, inctime = 0,0
    report.description = os.path.normpath(case_location)
    setattr(report,"fulltime",str(fulltime) + "s")
    setattr(report,"inctime",str(inctime) + "s")


@pytest.mark.optionalhook
def pytest_html_report_title(report):
    report.title = "EDK2 Incremental Build Test Report"



def pytest_configure(config):

    config._metadata["Project"] = "Edk2"
    config._metadata['ToolChain'] = 'VS2015'
    config._metadata['Target'] = 'RELEASE'

    config._metadata.pop("Packages")
    config._metadata.pop("Platform")
    config._metadata.pop("Plugins")
    config._metadata.pop("Python")
    if "JAVA_HOME" in config._metadata:
        config._metadata.pop("JAVA_HOME")

    
