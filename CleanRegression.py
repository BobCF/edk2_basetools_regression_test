from Regression import RegressionTest
from UnifiedBuild.BuildPlatform import BuildPlatform
class Test_PlatformRegression(RegressionTest):
    def test_run(self,setup_cases):
        build_steps = self.manifest.BuildCate.get(self.build_cate)
        working_dir = self.manifest.Defines.get("workdir")
        BuildPlatform(working_dir,build_steps)
        assert self.CompareAutoGen()