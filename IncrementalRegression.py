from TestCommon.BuildPlatform import BuildPlatform
import pytest
from TestCommon.CaseMgr import CaseMgr
import shutil
import os
from TestCommon.RepoMgr import RepoMgr
import tempfile
from filehash import FileHash
import collections

EXCLUDE_FILELIST_TYPE = ["",".obj", ".map", ".lib", ".dll", ".bin"]
FileHashResult = collections.namedtuple("FileHashResult", ["filename", "hash"])
case_mgr = CaseMgr(r".\CasePatches")

def gen_tmp_dir():
    print (tempfile.tempdir)
    tempfile.tempdir = os.path.abspath(r"Temp")
    tmpdir = tempfile.mkdtemp("basetool_reg")
    return tmpdir

def get_basetools_patches():
    try:
        return [patch for patch in os.listdir("./BaseToolsPatches") if patch.endswith(".patch")]
    except:
        return []

def get_hash(build_dir):
    """Compute hash of directory."""
    sha256 = FileHash('sha256')
    build_files = get_buildfiles(build_dir)
    return sha256.cathash_files(build_files)


def get_buildfiles(build_dir):
    """Return file list from a build folder."""
    build_file_list = []
    for root,_,files in os.walk(build_dir):
        for file_name in files:
            name, ext = os.path.splitext(file_name)
            if ext not in EXCLUDE_FILELIST_TYPE:
                build_file_list.append(os.path.join(root,file_name))
    return build_file_list

class Test_PlatformRegression():
    tmp_dir = gen_tmp_dir()
    BaseLine_dir = os.path.join(tmp_dir,".BaseLine")
    target_platform = ""
    manifest = None
    build_cate = ''

    @pytest.fixture(scope='session')
    def setup_repository(self):
        workspace = self.manifest.Defines.get("workspace",".")
        if not workspace:
            assert 0, "workspace is not defined"
        repo_conf = self.manifest.RepoConf
        if not repo_conf:
            assert 0, "Repo is not defined"
        repo_mgr = RepoMgr(workspace, repo_conf)
        repo_mgr.setup_repo()
        return repo_mgr

    @pytest.fixture(scope='session',
                    params = case_mgr.CaseSuite)
    def setup_cases(self,setup_repository,request):
        repo_mgr = setup_repository
        patch = request.param
        repo_mgr.reset((patch[0]))
        repo_mgr.apply_cases(patch)
        print(self.build_cate)
        build_steps = self.manifest.BuildCate.get(self.build_cate)
        if not build_steps:
            assert 0
        working_dir = self.manifest.Defines.get("workdir")
        if not working_dir:
            assert 0
        try:
            build_dir = os.path.join(working_dir,"Build")
            shutil.rmtree(build_dir)
        except:
            print("no Build Folder")
        # First time build with patch
        BuildPlatform(working_dir,build_steps)
        self.PrepareBaseLine()
        repo_mgr.reset((patch[0]))

        #fist time build without patch
        BuildPlatform(working_dir,build_steps)
        repo_mgr.apply_cases(patch)

        yield
        repo_mgr.clean_all()
        repo_mgr.reset((patch[0]))
        try:
            print(self.BaseLine_dir)
            shutil.rmtree(self.tmp_dir)
        except:
            print("rm folder failed")

    def PrepareBaseLine(self):
        platform_workspace = self.manifest.Defines.get("workspace")
        if not platform_workspace:
            assert 0
        build_dir = os.path.join(platform_workspace,"Build")
        if not os.path.exists(build_dir):
            assert 0
        try:
            print (self.BaseLine_dir)
            shutil.move(build_dir,self.BaseLine_dir)
        except:
            assert 0
    def test_run(self,setup_cases):
        build_steps = self.manifest.BuildCate.get(self.build_cate)
        working_dir = self.manifest.Defines.get("workdir")
        build_dir = os.path.join(working_dir,"Build")
        # Incremental build
        BuildPlatform(working_dir,build_steps)
        assert(get_hash(self.BaseLine_dir) == get_hash(build_dir))
