import collections
import pytest
import os
import tempfile
import yaml
from filehash import FileHash
import shutil
import subprocess
from string import Template
import logging
import platform
import glob
import time

LOGGER = logging.getLogger("IncTest")
edk2_proj_root = os.environ.get("EDK2_PROJ_ROOT",os.path.abspath(".")) 
FileHashResult = collections.namedtuple("FileHashResult", ["filename", "hash"])

# for class property
class cached_property(object):
    def __init__(self, function):
        self._function = function
    def __get__(self, obj, cls):
        Value = obj.__dict__[self._function.__name__] = self._function(obj)
        return Value

class INPUT():
    def __init__(self,source,dest):
        self.source = source
        self.dest = dest
        
def git_cmd(work_dir, *args):
    if not os.path.exists(work_dir):
        raise git_error(message = "work dir does not exist.")
    with cd(work_dir):
        error, lines = cli_cmd('git', *args)
        if error:
            raise git_error(message = get_giterror(['git']+list(args), error, lines))
        return lines

def cli_cmd(command, *args):
    """Run a shell command and return its error code and the lines it
    printed to stdout or stderr.
    """
    cmdline = [command] + list(args)
    p = subprocess.Popen(cmdline,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT,
                     shell=False,
                     universal_newlines=True,
                     encoding='ascii',
                     errors="ignore")

    lines = []
    for line in p.stdout:
        lines.append(line)
    return p.wait(), lines

def get_giterror(cmd, error_code, subprocess_lines):
    "Format and returns error message received from subprocess."
    git_command = " ".join([argument for argument in  cmd])
    error_message = " ".join([line for line in  subprocess_lines])
    return "\n Command:{} \n Code:{} \n Message:{}".format(git_command, error_code, error_message)

class git_error(Exception):
    """Error to raise when Git commands fail."""
    def __init__(self, message):
        super().__init__(message)
class cd:
    """Context manager for changing the current working directory.
    """
    def __init__(self, newPath):
        """
        with utilities.cd(targetDir):
            ...do something in the target directory
        """
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class IncTestEnv():
    def __init__(self,root,case_folder,build_workspace):
        '''
        root: root folder of the project
        case_folder: repository of test cases
        build_workspace: workspace
        '''
        self.root = root
        self.cases_folder = case_folder
        self.build_workspace = build_workspace
        self.case_list = []


    @property
    def collect_cases(self):
        '''
        update the directory to relevent directory from build_workspace
        '''
        LOGGER.info("collect test case %s" %self.cases_folder)
        if not self.case_list:
            for root, _, files in os.walk(self.cases_folder):
                for file in files:
                    if file.endswith(".yml"):
                        case = self.ReadCases(os.path.join(root,file))
                        newinputs = []
                        if case:
                            case.path = root
                            case.changes = [os.path.join(case.path,change) for change in case.changes]
                            case.outputs = [os.path.join(self.root,output) for output in case.outputs]
                            for item in case.inputs:
                                if item.source.endswith(".patch"):
                                    newinputs.append(INPUT(os.path.join(case.path,item.source),item.dest))
                                else:
                                    newinputs.append(INPUT(os.path.join(case.path,item.source),os.path.join(self.root,item.dest)))
                                
                            case.inputs = newinputs
                            self.case_list.append(case)
        return self.case_list
    def ReadCases(self,case_file):
        try:
            file_content = []
            with open(case_file,'r') as f:
                for line in f.readlines():
                    if line.strip().startswith("!include"):
                        _, included_file = line.strip().split(" ")
                        include_file = included_file.strip()
                        if os.path.exists(os.path.join(self.cases_folder,'common',include_file)):
                            with open(os.path.join(self.cases_folder,'common',include_file),'r') as inc:
                                for inc_line in inc.readlines():
                                    file_content.append(inc_line)
                    else:
                        file_content.append(line)
                case_content = "".join(file_content)
                src = Template( case_content )
                data = yaml.load(src.substitute(CaseRoot=self.cases_folder),Loader=yaml.FullLoader)
        except:
            LOGGER.info("Load case %s failed" % case_file)
            return None
        if data is None:
            LOGGER.info("Empty case description file %s" % case_file)
            return None
        case = self.__fillcase(data, case_file)
        return case
    def __fillcase(self,data,case_file):
        case = Case()
        case.name = os.path.basename(data.get('name',''))
        case.description = data.get('description','')
        case_init = data.get('init')
        case_input = data.get('input')
        case.type = data.get('type','Auto')

        pathes = case_file.split(os.sep)
        case.case_file = os.sep.join(pathes[pathes.index("TestCases")+1:])

        for item in case_init:
            if not item['src'] or item['src'].endswith(".patch"):
                repo_info = item['dest'].split("|")
                if len(repo_info) == 1:
                    version = ''
                    repo_name = repo_info[0].strip().lower()
                else:
                    version = repo_info[1].strip()
                    repo_name = repo_info[0].strip().lower()
                case.repo.add((repo_name,version))
        for item in case.repo:
            if case_input['repo'].lower() == item[0]:
                break
        else:
            case.repo.add((case_input['repo'].lower(),''))
        
        case.inputs = [INPUT(item['src'],item['dest']) for item in case_init if item['src']]
        case.changes = [item for item in data.get('change',[])]
        case.neg_changes = [item for item in data.get('neg_change',[])]
        case.outputs= data.get('output',[])
        case.command = data.get('command','')
        LOGGER.info(case.name)
        return case

class Edk2TestEnv(IncTestEnv):
    def __init__(self,root,case_folder,build_workspace):
        super(Edk2TestEnv,self).__init__(root,case_folder,build_workspace)

    def update_case(self):
        return self.case_list
    
    def set_env(self,case):
        return

        LOGGER.info("do edk2 set_env")
        cmds = ['edksetup.bat','Rebuild']
        env_dict = os.environ.copy()
        cmds.append(">nul")
        cmds.append("&")
        cmds.append("set")
        need_capture_output = True
        if 'WORKSPACE' in env_dict:
            env_dict['WORKSPACE'] = ''
        LOGGER.info(self.build_workspace)
        rt = subprocess.run(cmds,capture_output=need_capture_output,cwd=self.build_workspace,shell=True,text=True,env=env_dict)
        if rt.returncode != 0:
            LOGGER.info(rt.stderr)
            LOGGER.info(rt.stdout)
        envirmentvar = rt.stdout
        for envi in envirmentvar.split("\n"):
            try:
                name,value = envi.split("=")
                env_dict[name.strip()] = value.strip()
            except:
                continue
        case.env_dict = env_dict
        
class RepoEnv():

    repo_locations = {
        'Tiano':{
            'edk2': os.path.join(edk2_proj_root,"edk2")
            }
        }
    repo_version = {
        'Tiano':{
            'edk2': os.environ.get("TIANO_EDK2_VER")
            }
        }

    __cache__ = {}

    def __new__(cls,workspace, project,caseinit,repoes):
        key = (workspace,project)
        if key in cls.__cache__:
            return cls.__cache__[key]
        re = cls.__cache__[key] = super(RepoEnv,cls).__new__(cls)
        return re

    def __init__(self,workspace,project, caseinit, repoes):
        self.workspace = workspace
        self.project = project
        self.caseinit = caseinit
        self.repoes = repoes

    @cached_property
    def repo_components(self):
        proj_repos = self.repo_locations[self.project]
        component = {}
        user_version = {r[0].lower():r[1] for r in self.repoes}
        for r in proj_repos:
            if r in user_version and user_version[r]:
                component[proj_repos[r]] = user_version[r]
            else:
                component[proj_repos[r]] = self.repo_version[self.project][r]
        return component
    @property
    def init_sources(self):
        sources = collections.OrderedDict([(s.source,s.dest) for s in self.caseinit if s.source])
        return sources

    def apply(self,case,negative=False):
        if negative:
            changes = case.neg_changes
        else:
            changes = case.changes
        
        proj_repos = self.repo_locations[self.project]
        source_map = {os.path.basename(s):d for s,d in self.init_sources.items()}
        for ch in changes:
            LOGGER.info(ch)
            change_com = [item.strip() for item in ch.split("|")]
            if change_com[0].endswith(".patch"):
                
                if len(change_com) != 2:
                    LOGGER.error("Don't know how to apply change: %s" % change_com[0])
                    continue
                repo_localtion = proj_repos[change_com[1].lower()]
                try:
                    git_cmd(repo_localtion,"reset", "--hard")
                except git_error as ge:
                    LOGGER.info(str(ge))
                try:
                    git_cmd(repo_localtion,"am", "--3way", "--ignore-space-change", "--keep-cr", change_com[0])
                except git_error as ge:
                    LOGGER.info(str(ge))
                    git_cmd(repo_localtion,"am", "--abort")
            else:
                change = change_com[0]
                dest = source_map.get(os.path.basename(change))   
                if dest:
                    if os.path.isdir(change):
                        if os.path.exists(dest):
                            shutil.rmtree(dest)
                        shutil.copytree(change,dest)
                    else:
                        shutil.copy(change,dest)
                    LOGGER.info("copy %s" % change)
                else:
                    LOGGER.info("change error %s" % change)
    def clean(self):
        for comp in self.repo_components:
            version = self.repo_components[comp]

            try:
                git_cmd(comp,"reset",version,"--hard")
            except Exception as e:
                git_cmd(comp,"pull")
                try:
                    git_cmd(comp,"reset",version,"--hard")
                except Exception as se:
                    LOGGER.warning(str(se))

    def revert(self):
        for comp in self.repo_components:
            version = self.repo_components[comp]
            try:
                git_cmd(comp,"reset",version,"--hard")
            except Exception as e:
                git_cmd(comp,"pull")
                try:
                    git_cmd(comp,"reset",version,"--hard")
                except Exception as se:
                    LOGGER.warning(str(se))
        self.init()
    def init(self):
        proj_repos = self.repo_locations[self.project]
        for init_s in self.init_sources:
            init_d = self.init_sources[init_s]
            if init_s.endswith(".patch"):
                repo_localtion = proj_repos[init_d.lower()]
                try:
                    git_cmd(repo_localtion,"am", "--3way", "--ignore-space-change", "--keep-cr", init_s)
                except git_error as ge:
                    git_cmd(repo_localtion,"am", "--abort")
                    LOGGER.info(str(ge))
            else:
                if os.path.isdir(init_s):
                    if os.path.exists(init_d):
                        shutil.rmtree(init_d)
                    LOGGER.info("clean copy %s" % init_s)
                    shutil.copytree(init_s,init_d)
                else:
                    if not os.path.exists(os.path.dirname(init_d)):
                        os.makedirs(os.path.dirname(init_d))
                    LOGGER.info("clean copy %s" % init_s)
                    shutil.copy(init_s,init_d)

class Case():
    def __init__(self):
        self.command = ''
        self.type = ''
        self.repo = set()
        self.inputs = []
        self.changes = []
        self.neg_changes = []
        self.expected_outputs = []
        self.outputs = []
        self.name = ""
        self.description = ""
        self.BaseLine_dir = os.path.join(self.tmp_dir,".BaseLine")
        self.Results_dir = os.path.join(self.tmp_dir,".Results")
        self.OriLine_dir = os.path.join(self.tmp_dir,".OrnLine")
        self.path = ""
        self.env_dict = os.environ
        self.valid = True
        self.exclude_filelist_type = []
        self.case_file = ""
        self.incbuildtime = 0
        self.fullbuildtime = 0
        try:
            os.mkdir(self.BaseLine_dir)
            os.mkdir(self.Results_dir)
            os.mkdir(self.OriLine_dir)
        except:
            LOGGER.info("make dir failed")

    def compare(self):
        if self.type.lower() == "manual":
            return True
        return self.get_hash(self.BaseLine_dir) == self.get_hash(self.Results_dir)
    
    def __splitcommand(self,command_str):
        return [item.strip() for item in command_str.split(" ") if item.strip()]

    def execute(self,PlatformWorkingPath,capture_output=False):
        if self.type.lower() == "manual":
            return
        LOGGER.info(self.command)
        cmds = self.__splitcommand(self.command)
        LOGGER.info(cmds)
        begin = time.time()
        print(PlatformWorkingPath)
        rt = subprocess.run(cmds,cwd=PlatformWorkingPath,shell=True,text=True,env=self.env_dict)
        end = time.time()
        #rt = subprocess.run(cmds,cwd=PlatformWorkingPath,env=env_dict) # py36 on linux

        if rt.returncode !=0:
            LOGGER.info(rt.stderr)
            LOGGER.info(rt.stdout)
        elif capture_output:
            LOGGER.info(rt.stdout)

        return round(end-begin,2)

    def get_hash(self,build_dir):
        """Compute hash of directory."""
        sha256 = FileHash('sha256')

        build_files = self.get_buildfiles(build_dir)
        return sha256.cathash_files(build_files)


    def get_buildfiles(self,build_dir):
        """Return file list from a build folder."""
        build_file_list = []
        for root,_,files in os.walk(build_dir):
            for file_name in files:
                name, ext = os.path.splitext(file_name)
                if ext not in self.exclude_filelist_type:
                    build_file_list.append(self.covert_long_file_path(os.path.join(root, file_name)))
        return build_file_list
    
    def covert_long_file_path(self,filename):
        """
        support long file path
        :return: path
        """
        file_name = os.path.normpath(filename)
        if platform.system() == 'Windows':
            if file_name.startswith('\\\\?\\'):
                return file_name
            if file_name.startswith('\\\\'):
                return '\\\\?\\UNC\\' + file_name[2:]
            if os.path.isabs(file_name):
                return '\\\\?\\' + file_name
        return file_name

    
    @cached_property
    def tmp_dir(self):
        tempfile.tempdir = os.path.abspath(r"Temp")
        tmpdir = tempfile.mkdtemp("incre_reg")
        return tmpdir

    def verify(self):
        if self.type.lower() == "manual":
            return True
        LOGGER.info("compare %s and %s" % (self.BaseLine_dir,self.OriLine_dir))
        return self.get_hash(self.BaseLine_dir) != self.get_hash(self.OriLine_dir)

    def GetOutput(self,outputfile_list):
        '''Find the *file name under its parent folder'''
        outputfiles = set()
        for output in outputfile_list:
            filename = os.path.basename(output)
            if "*" in filename:
                for f in glob.glob(output):
                    outputfiles.add(f)
            else:
                outputfiles.add(output)
        return list(outputfiles)

    def create_baseline(self):
        print (self.BaseLine_dir)
        for f in self.GetOutput(self.outputs):
            try:
                LOGGER.info(f)
                shutil.move(f,self.BaseLine_dir)
            except Exception as e:
                LOGGER.info("bsackup baseline failed %s" % f)
                continue
        return True

    def create_original_line(self):
        print (self.OriLine_dir)
        for f in self.GetOutput(self.outputs):
            try:
                LOGGER.info(f)
                if os.path.isdir(f):
                    if f.endswith(os.sep):
                        foldername = os.path.basename(os.path.split(f)[0])
                    else:
                        foldername = os.path.basename(f)
                    shutil.copytree(f,os.path.join(self.OriLine_dir,foldername))
                else:
                    shutil.copy(f,self.OriLine_dir)
            except Exception as e:
                LOGGER.info("bsackup original failed %s" % f)
                continue
        return True
    
    def backup_result(self):
        print (self.Results_dir)
        for f in self.GetOutput(self.outputs):
            try:
                shutil.move(f,self.Results_dir)
            except:
                LOGGER.info("bsackup result failed %s" % f)
                continue
        return True

    def clean_temp(self):
        try:
            shutil.rmtree(self.tmp_dir)
        except:
            LOGGER.info("rm folder failed")
    def clean_env(self):
        ''' remove all build output '''
        for output in self.outputs:
            try:
                if os.path.isdir(output):
                    shutil.rmtree(output)
                else:
                    os.remove(output)
            except:
                LOGGER.info(output)
                continue



# -------------------------- Test ---------------------------#

edk2_testenv = Edk2TestEnv(edk2_proj_root,os.path.join(os.path.abspath("."),r"TestCases\pilot"),os.path.join(edk2_proj_root,"edk2"))

@pytest.mark.edk2_inc_test
class Test_Edk2PlatformIncremental():

    @pytest.fixture(scope='session')
    def PreTest(self):
        version = git_cmd("./edk2","rev-parse", "HEAD")[0]
        yield version.strip()

    @pytest.fixture(
                    params = edk2_testenv.collect_cases,
                    ids = ["%s -- %s -- | %s" % (case.name, case.type, case.case_file) for case in edk2_testenv.collect_cases])
    def setup_cases(self,request,caplog,PreTest):
        caplog.set_level(logging.INFO)
        LOGGER.info("before run EDK2 cases")
        case = request.param
        case.exclude_filelist_type = [".obj", ".map", ".lib", ".dll", ".bin",".tmp",".inf",".md",".txt"]
        LOGGER.info("Prepare EGS case %s" % case.name)
        repo = RepoEnv(edk2_testenv.build_workspace,'Tiano',case.inputs,case.repo)
        repo.repo_version['Tiano']['edk2'] = PreTest

        case.clean_env()
        LOGGER.info("Test environment is cleaned")
        repo.clean()
        repo.init()
        LOGGER.info("Clean repo and initialized repo")
        LOGGER.info("Test environment is cleaned")
        repo.apply(case)
        edk2_testenv.set_env(case)
        LOGGER.info("Case change is applyed for the 1st full build")
        fullbuildtime = case.execute(edk2_testenv.build_workspace)
        case.fullbuildtime = fullbuildtime
        LOGGER.info("1st full build (with change) is done")
        case.create_baseline()
        LOGGER.info("prepared the baseline")
        case.clean_env()
        LOGGER.info("the change is reverted")
        repo.clean()
        repo.init()
        LOGGER.info("Repo is cleaned")
        edk2_testenv.set_env(case)
        case.execute(edk2_testenv.build_workspace)
        LOGGER.info("2nd full build (without change) is done")
        case.create_original_line()
        if not case.verify():
            LOGGER.error("Case %s is not valid" % case.name)
            case.valid = False
        else:
            repo.apply(case)
        yield case
        case.clean_env()
        repo.clean()
#        case.clean_temp()
        
        LOGGER.info("Test Environment is cleand for case %s",case.name)

    def test_edk2(self,setup_cases,caplog):
        caplog.set_level(logging.INFO)
        case = setup_cases
        assert(case.valid)
        edk2_testenv.set_env(case)
        incbuildtime = case.execute(edk2_testenv.build_workspace,True)
        case.incbuildtime = incbuildtime
        LOGGER.info("Incremental build is done for case %s" % case.name)
        case.backup_result()
        assert(case.compare())
