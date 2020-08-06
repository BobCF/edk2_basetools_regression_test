import toml
from collections import OrderedDict

DEFINES ="Defines"
REPOSITORY = "Repo"
RESERVE_KEY = (DEFINES,REPOSITORY)

class Manifest():
    def __init__(self, manifest_file):
        self.manifest_file = manifest_file
        self.repos = {}
        self.build_cate = {}
        self.defines = OrderedDict()

    @property
    def RepoConf(self):
        if not self.repos:
            try:
                self.ReadConf()
            except:
                self.repos = {}
        return self.repos

    @property
    def BuildCate(self):
        if not self.build_cate:
            try:
                self.ReadConf()
            except:
                self.build_cate = {}
        return self.build_cate

    @property
    def Defines(self):
        if not self.defines:
            try:
                self.ReadConf()
            except:
                self.defines = {}
        return self.defines

    def ReadConf(self):

        proj_conf = toml.load(self.manifest_file)
        self.repos = proj_conf.get("Repo",{})
        self.defines = proj_conf.get('Defines',{})
        for key in proj_conf:
            if key not in RESERVE_KEY:
                self.build_cate[key] = proj_conf[key]            

if __name__ == "__main__":
    target_platform = r".\ProjectManifest\MinKabylake.toml"
    manifest = Manifest(target_platform)
    print(manifest.RepoConf)
    print(manifest.Defines)
    print(manifest.BuildCate)
    print(manifest.BuildCate.get("Basic"))
    for step in manifest.BuildCate.get("Basic").get('step'):
        print(step)