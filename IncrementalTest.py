from Regression import RegressionTest
from UnifiedBuild.BuildPlatform import BuildPlatform
import os
import shutil

class Test_PlatformRegression(RegressionTest):

    def PrepareBaseLine(self):
        platform_workspace = self.manifest.Defines.get("workspace")
        if not platform_workspace:
            assert 0
        build_dir = os.path.join(platform_workspace,"Build")
        if not os.path.exists(build_dir):
            assert 0
        try:
            print (self.BaseLine_dir)
            shutil.copytree(build_dir,self.BaseLine_dir)
        except:
            assert 0

    def test_run(self,setup_cases):
        build_steps = self.manifest.BuildCate.get(self.build_cate)
        working_dir = self.manifest.Defines.get("workdir")
        BuildPlatform(working_dir,build_steps,['BuildClean'])
        assert(self.CompareAutoGen())