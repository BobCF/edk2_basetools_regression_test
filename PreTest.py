import os
import yaml
import subprocess
import sys

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

if __name__ == "__main__":

    if len(sys.argv) == 3 and sys.argv[1] == '-c':
        f = os.path.abspath(sys.argv[2])
        with open(os.path.abspath(f),"r") as fd:
            data = yaml.load(fd.read(),Loader=yaml.FullLoader)
            for line in data['init']:
                if line.strip().endswith(".patch"):
                    print(line)
                    git_cmd("./edk2","am", "--3way", "--ignore-space-change", "--keep-cr", os.path.join(os.path.dirname(os.path.abspath(f)),line.strip()))
    else:
        exit(1)


