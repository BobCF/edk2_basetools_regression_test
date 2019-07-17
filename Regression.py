import pytest
import os
from UnifiedBuild.RepoMgr import RepoMgr
from UnifiedBuild.BuildPlatform import BuildPlatform
from FileCompare import CompareFile
from CaseMgr import case_mgr
import shutil
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

class RegressionTest():
    AutoGenFileList = ['AutoGen.c','AutoGen.h',"Makefile"]
    tmp_dir = gen_tmp_dir()
    diff_dir =  os.path.join(tmp_dir,".Diff")
    BaseLine_dir = os.path.join(tmp_dir,".BaseLine")
    target_platform = ""
    manifest = None
    build_cate = ''

    @pytest.fixture(scope='module')
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

    @pytest.fixture(scope='module',
                    params = case_mgr.CaseSuite)
    def setup_cases(self,setup_repository,request):
        repo_mgr = setup_repository
        repo_mgr.apply_cases(request.param)
        print(self.build_cate)
        build_steps = self.manifest.BuildCate.get(self.build_cate)
        if not build_steps:
            assert 0
        working_dir = self.manifest.Defines.get("workdir")
        if not working_dir:
            assert 0
        BuildPlatform(working_dir,build_steps)
        self.PrepareBaseLine()
        edk2 = repo_mgr.get_repo('edk2')
        edk2.apply_patches(get_basetools_patches())
        yield
        repo_mgr.reset_all()
    
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

    def GetAutoGenFileList(self,BuildDir):
        autogen_list = []
        for root,_,files in os.walk(BuildDir):
            for file_name in files:
                if file_name in self.AutoGenFileList:
                    autogen_list.append(os.path.relpath(os.path.join(root,file_name),BuildDir))
        autogen_list.sort()
        return autogen_list
                    
    def CompareAutoGen(self):
        platform_workspace = self.manifest.Defines.get("workspace")
        build_dir = os.path.join(platform_workspace,"Build")
        if not os.path.exists(self.diff_dir):
            os.makedirs(self.diff_dir)
        
        baseline_filelist = self.GetAutoGenFileList(self.BaseLine_dir)
        build_filelist = self.GetAutoGenFileList(build_dir)
        
        if build_filelist != baseline_filelist:
            print (set(build_filelist) - set(baseline_filelist))
            return 0
        diff = False
        for i in range(len(build_filelist)):
            if not CompareFile(os.path.join(build_dir,build_filelist[i]),os.path.join(self.BaseLine_dir,baseline_filelist[i]),self.diff_dir):
                print(os.path.join(build_dir,build_filelist[i]),os.path.join(self.BaseLine_dir,baseline_filelist[i]))
                diff = True
        return 0 if diff else 1
