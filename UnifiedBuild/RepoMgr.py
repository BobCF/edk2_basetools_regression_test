import toml
import os
import subprocess
class Repo():
    def __init__(self,workspace,name,link,branch,version):
        self.workspace = workspace
        self.name = name
        self.link = link
        self.branch = branch
        self.version = version
    
    def git_cmd(self, *args):
        with cd(self.workspace):
            error, lines = cli_cmd('git', *args)
            if error:
                raise git_error(message = self.get_giterror(['git']+list(args), error, lines))
            return lines
    def get_giterror(self, cmd, error_code, subprocess_lines):
        "Format and returns error message received from subprocess."
        git_command = " ".join([argument for argument in  cmd])
        error_message = " ".join([line for line in  subprocess_lines])
        return "\n Command:{} \n Code:{} \n Message:{}".format(git_command, error_code, error_message)
    
    def clone(self):
        ''' clone the repo to local '''
    
    def checkout(self):
        ''' check out self.branch '''
        
    def clean(self):
        ''' clean all the un-tracked files '''
        
    def reset(self):
        ''' reset the repo to self.version '''
        
    def apply_patches(self,patchfile):
        if patchfile:
            self.git_cmd("reset", "--hard") 
            self.git_cmd("am", "--3way", "--ignore-space-change", "--keep-cr", patchfile[0]) 
        
    def revert_patch(self):
        ''' apply the patch_path to specific repo named repo_name '''
    def reset_version(self,version):
        self.git_cmd("reset", version,"--hard") 
        
    def status(self):
        ''' 0 is repo does not exist, 1 is repo exists '''
        
class RepoMgr():
    def __init__(self,workspace, repo_conf):
        self.repo_conf = repo_conf
        self.workspace = workspace
        self._repos = None
        
    @property
    def Repos(self):
        if self._repos is None:
            self._repos = []
            for repo_info in self.repo_conf:
                if not repo_info:
                    continue
                self._repos.append(Repo(self.workspace, repo_info['name'],repo_info['git'],repo_info['branch'],repo_info['version']))
        return self._repos
    
    @property
    def ReposName(self):
        return [item.name for item in self.Repos]
    
    def get_repo(self,repo_name):
        return self.Repos[self.ReposName.index(repo_name)]
    
    def clone_all(self):
        ''' clone the repo of 'name' to local, if name is not in self.Repos return False, otherwise return clone status '''
    
    def reset_all(self):
        ''' reset all the repo to the revision in config file '''
        print("reset all")

    def clean_all(self):
        ''' clean all the repo '''
        print("clean all")

    def setup_repo(self):
        for repo in self.Repos:
            if repo.status() == 0:
                repo.clone()
            elif repo.status() == 1:
                repo.clean()
                repo.reset()
    def apply_cases(self,case):
        print(case)
        repo_name, patch_path = case
        print(patch_path)
        print("============")
        repo = self.get_repo(repo_name)
        repo.apply_patches([patch_path])

    def reset(self,case):
        repo_name, version = case
        repo = self.get_repo(repo_name)
        repo.reset_version(version)
 
class git_error(Exception):
    """Error to raise when Git commands fail."""
    def __init__(self, message):
        super().__init__(message)
        
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
            
