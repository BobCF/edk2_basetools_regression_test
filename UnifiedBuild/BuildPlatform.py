import toml
import subprocess
import os

def BuildPlatform(PlatformWorkingPath,BuildSteps,ignore_steps=None):
    if ignore_steps is None:
        ignore_steps = []
    env_dict = os.environ
    env_dict['PYTHON_HOME'] = r"c:\python27"
    for step in BuildSteps.get('step'):
        if step['name'] in ignore_steps:
            continue
        cmds = []
        comm_name = step.get('command').get("cmd")
        cmds.append(comm_name)
        paras = step.get('command').get("parameters")
        if paras:
            cmds.extend(paras)
        output_type = step.get('command').get("output_type")
        need_capture_output = False
        if "EnvVar" in output_type:
            cmds.append(">nul")
            cmds.append("&")
            cmds.append("set")
            need_capture_output = True
        print(cmds)
        rt = subprocess.run(cmds,capture_output=need_capture_output,cwd=PlatformWorkingPath,shell=True,text=True,env=env_dict)
        if rt.returncode != 0:
            print(rt.stderr)
            print(rt.stdout)
            exit(1)
        if "EnvVar" in output_type:
            envirmentvar = rt.stdout
            for envi in envirmentvar.split("\n"):
                try:
                    name,value = envi.split("=")
                    env_dict[name.strip()] = value.strip()
                except:
                    continue

if __name__ == "__main__":
    BuildPlatform()