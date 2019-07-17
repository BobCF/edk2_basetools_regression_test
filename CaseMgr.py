import toml
import os
import collections

class Case():
    def __init__(self,name,desc,patches,hash_value,case_cate):
        self.name = name
        self.desc = desc
        self.patches = patches
        self.hash = hash_value
        self.case_cate = case_cate

class CaseMgr():
    '''
    This class require the case have the following orgnization and format.
    1. case patch is in the folder whose name is the test case name.
    2. case patch commit message format: the description of this cases.
    3. .hash file exists in each case folder.
    
    This class will collect the cases information by walk the case directory and generate the
    case bom list file whose format is toml.

    If the case bom list exist, will check and update this file.
    '''
    
    def __init__(self):
        self._case_list = []
        self.case_dir = r".\CasePatches"
    def update_case_bom(self):
        ''' update bom list based on file '''
    
    def create_case_bom(self):
        ''' create case bom list file '''
        for root, _, files in os.walk(self.case_dir):
            patches = []
            for file in files:
                if file.endswith(".patch"):
                    patch_info = self.ReadPatch(os.path.join(root,file))
                    patches.append(patch_info)
            if patches:
                dir_s = os.path.split(root)
                case_name= dir_s[1]
                case_cate = os.path.split(dir_s[0])[1]
                case = Case(case_name,r"\n".join([patch['Description'] for patch in patches]),patches,"",case_cate)
                self._case_list.append(case)
        case_toml = collections.OrderedDict()
        case_toml['Case_Num'] = len(self._case_list)
        for case in self._case_list:
            try:
                case_toml[case.case_cate]['Case'].append({
                "name" : ".".join((case_cate,case.name)),
                "desc" : case.desc,
                "repo" : [patch["Repo"] for patch in case.patches],
                "patch" : [patch["path"] for patch in case.patches],
                "hash" : ''
                })
            except:
                case_toml[case.case_cate]={'Case':[{
                "name" : case.name,
                "desc" : case.desc,
                "repo" : [patch["Repo"] for patch in case.patches],
                "patch" : [patch["path"] for patch in case.patches],
                "hash" : ''
                }]}

        with open(os.path.join(self.case_dir, "Bom.toml"),"w") as fw:
            toml.dump(case_toml,fw)
        
    def check_case_bom(self):
        ''' check if bom list file need update based on hash value '''

    @property
    def CaseSuite(self):
        ''' return case set '''
        self.create_case_bom()
        return self._case_list

    def ReadPatch(self,patch_file):
        PatchInfo = {}
        desc_start = False
        with open(patch_file,"r") as fd:
            lines = fd.readlines()
            for line in lines:
                if line == "---":
                    break
                if line.startswith("Subject:"):
                    PatchInfo['Description'] = line[len("Subject:"):].lstrip(" [Patch]").strip()
                    desc_start = True
                    continue
                if line.startswith("Repo:"):
                    PatchInfo['Repo'] = line[len("Repo:"):].strip()
                    continue
                if desc_start and ":" in line:
                    desc_start = False
                if desc_start:
                    PatchInfo['Description'] += line
        PatchInfo['path'] = os.path.abspath(patch_file)
        return PatchInfo


case_mgr = CaseMgr()
