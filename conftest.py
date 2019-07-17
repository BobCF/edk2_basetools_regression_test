from Manifest import Manifest
from CaseMgr import case_mgr

def pytest_addoption(parser):
    parser.addoption(
        "--platform",
        action="store", 
        dest="platform",
        default=r"./ProjectManifest/Ovmf.toml",
        help="The Platform name",
    )
    parser.addoption(
        "--build-cate",
        action="store", 
        dest="build_cate",
        type="string",
        default="Basic",
        help="How many commit number patch will be generated",
    )

def pytest_generate_tests(metafunc):
    metafunc.cls.target_platform = metafunc.config.getoption("platform")
    metafunc.cls.manifest = Manifest(metafunc.config.getoption("platform"))
    metafunc.cls.build_cate = metafunc.config.getoption("build_cate")
