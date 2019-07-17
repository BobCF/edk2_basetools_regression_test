from Regression import RegressionTest
from UnifiedBuild.BuildPlatform import BuildPlatform
import pytest
class Test_PlatformRegression(RegressionTest):
    @pytest.fixture(scope='module')
    def setup_cases(self,setup_repository,request):
        repo_mgr = setup_repository
        print(self.build_cate)
        build_steps = self.manifest.BuildCate.get(self.build_cate)
        if not build_steps:
            assert 0
        working_dir = self.manifest.Defines.get("workdir")
        if not working_dir:
            assert 0
        yield
        repo_mgr.clean_all()
        repo_mgr.reset_all()

    def test_run(self,setup_cases,benchmark):
        
        build_steps = self.manifest.BuildCate.get(self.build_cate)
        working_dir = self.manifest.Defines.get("workdir")
        print(build_steps)
        benchmark(BuildPlatform,PlatformWorkingPath= working_dir,BuildSteps=build_steps)
        assert 1