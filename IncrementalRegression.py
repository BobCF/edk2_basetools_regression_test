from UnifiedBuild.BuildPlatform import BuildPlatform
import pytest
from CaseMgr import case_mgr
import shutil
import os
from UnifiedBuild.RepoMgr import RepoMgr
import tempfile
def gen_tmp_dir():
    print (tempfile.tempdir)
    tempfile.tempdir = r"C:\Temp"
    tmpdir = tempfile.mkdtemp("basetool_reg")
    return tmpdir
def get_basetools_patches():
    try:
        return [patch for patch in os.listdir("./BaseToolsPatches") if patch.endswith(".patch")]
    except:
        return []
class Test_PlatformRegression():
    tmp_dir = gen_tmp_dir()
    diff_dir =  os.path.join(tmp_dir,".Diff")
    BaseLine_dir = os.path.join(tmp_dir,".BaseLine")
    target_platform = ""
    manifest = None
    build_cate = ''

    @pytest.fixture(scope='session')
    def setup_repository(self):
        print(self.manifest.Defines)
        workspace = self.manifest.Defines.get("workspace",".")
        if not workspace:
            assert 0
        repo_conf = self.manifest.RepoConf
        if not repo_conf:
            assert 0
        repo_mgr = RepoMgr(workspace, repo_conf)
        repo_mgr.setup_repo()
        return repo_mgr

    @pytest.fixture(scope='session',
                    params = case_mgr.CaseSuite)
    def setup_cases(self,setup_repository,request):
        repo_mgr = setup_repository
        patch = request.param
        repo_mgr.revert_patch(patch)
        repo_mgr.apply_cases(patch)
        print(self.build_cate)
        build_steps = self.manifest.BuildCate.get(self.build_cate)
        if not build_steps:
            assert 0
        working_dir = self.manifest.Defines.get("workdir")
        if not working_dir:
            assert 0
        input()
        try:
            build_dir = os.path.join(working_dir,"Build")
            shutil.rmtree(build_dir)
        except:
            print("no Build Folder")
        BuildPlatform(working_dir,build_steps)
        self.PrepareBaseLine()
        input()
        repo_mgr.revert_patch(patch)
        input()
        BuildPlatform(working_dir,build_steps)
        repo_mgr.apply_cases(patch)
        
        yield
        repo_mgr.clean_all()
        repo_mgr.revert_patch(patch)
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
        BuildPlatform(working_dir,build_steps)
        #assert(self.CompareAutoGen())