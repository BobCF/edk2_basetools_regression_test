from Regression import RegressionTest,get_basetools_patches
from UnifiedBuild.BuildPlatform import BuildPlatform
import pytest
from CaseMgr import case_mgr
import shutil
class Test_PlatformRegression(RegressionTest):
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
        repo_mgr.clean_all()
        repo_mgr.reset_all()
        try:
            print(self.BaseLine_dir)
            shutil.rmtree(self.tmp_dir)
        except:
            print("rm folder failed")
    def test_run(self,setup_cases):
        build_steps = self.manifest.BuildCate.get(self.build_cate)
        working_dir = self.manifest.Defines.get("workdir")
        BuildPlatform(working_dir,build_steps)

        assert(self.CompareAutoGen())