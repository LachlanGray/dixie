import os
import subprocess
import time
import shutil

from utils import port_is_busy


class FileExplorer:
    def __init__(self, root_dir, debug=False):
        self.root_dir =  root_dir

    @property
    def system_cwd(self):
        return os.path.join(self.root_dir)

    def is_dir(self, path):
        system_path = os.path.join(self.root_dir, path)

        return os.path.isdir(system_path)

    def is_file(self, path):
        system_path = os.path.join(self.root_dir, path)
        return os.path.isfile(system_path)

    def ls(self, directory=None):
        if directory:
            system_directory = os.path.join(self.root_dir, directory)
            result = subprocess.run(['ls', system_directory], capture_output=True, text=True)

            return result.stdout


        result = subprocess.run(['ls', self.system_cwd], capture_output=True, text=True)
        return result.stdout


    def cat(self, file_path):
        system_file_path = os.path.join(self.root_dir, file_path)

        try:
            if not os.path.exists(system_file_path):
                return f"cat: {file_path}: No such file or directory"

            if os.path.isdir(system_file_path):
                return f"cat: {file_path}: Is a directory"

            result = subprocess.run(['cat', '-n', system_file_path], capture_output=True, text=True)

        except UnicodeDecodeError as e:
            return f"<binary>"

        file_contents = result.stdout
        return file_contents





if __name__ == "__main__":
    file = "hello.txt"
    workspace_dir = "test_examples"

    # vim ##########
    # workspace_dir = os.path.join(os.getcwd(), workspace_dir)

    # vim = Vim(workspace_dir, nvim_port="7778")
    # vim.open(file)

    # text = "hi there this is\n some text\nmore\nmore"
    # vim.append(file,text)

    # vim.save()
    # # breakpoint()

    # # file explorer ##########
    # explorer = FileExplorer(workspace_dir)
    # explorer.ls()
    # explorer.cd("backend")
    # explorer.ls()


