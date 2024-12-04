import os
import subprocess
import time
import shutil
from pynvim import attach

from utils import port_is_busy


class FileExplorer:
    def __init__(self, root_dir, debug=False):
        self.root_dir, self.project = os.path.split(root_dir)

        self.subdirs = [self.project]
        self.history = []

        self._debug = debug

    def log(self, message):
        if self._debug:
            print(f"\033[34m{message}\033[0m")

        self.history.append(message)


    @property
    def cwd(self):
        if self.subdirs == []:
            return "/"
        return os.path.join(*self.subdirs)

    @property
    def system_cwd(self):
        return os.path.join(self.root_dir, *self.subdirs)

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

        self.log(f"ls {self.cwd}")
        result = subprocess.run(['ls', self.system_cwd], capture_output=True, text=True)
        return result.stdout

    def cd(self, subdir_or_dir):
        if subdir_or_dir == "..":
            if self.subdirs == []:
                return f"cd: already at root"

            self.subdirs.pop()

        if subdir_or_dir == "/":
            self.subdirs = []
            return

        if os.path.exists(os.path.join(self.system_cwd, subdir_or_dir)):
            self.subdirs.append(subdir_or_dir)
            return

        # directory = os.path.join(self.project, subdir_or_dir)
        directory = subdir_or_dir
        system_directory = os.path.join(self.root_dir, directory)

        if not os.path.exists(system_directory):
            return f"cd: no such file or directory: {directory}"

        if not os.path.isdir(system_directory):
            return f"cd: not a directory: {directory}"

        self.subdirs = directory.split("/") # remove the project name


    def cat(self, subdir_or_path):
        # if path, it includes the project name
        if os.path.exists(os.path.join(self.system_cwd, subdir_or_path)):
            system_file_path = os.path.join(self.system_cwd, subdir_or_path)
            file_path = os.path.join(self.cwd, subdir_or_path)

        else:
            file_path = subdir_or_path
            system_file_path = os.path.join(self.root_dir, file_path)

        if not os.path.exists(system_file_path):
            return f"cat: {file_path}: No such file or directory"

        if os.path.isdir(system_file_path):
            return f"cat: {file_path}: Is a directory"

        result = subprocess.run(['cat', '-n', system_file_path], capture_output=True, text=True)
        file_contents = result.stdout

        return file_contents





class Vim:
    def __init__(
            self,
            root_dir:str,
            nvim_address:str="127.0.0.1",
            nvim_port:str = "7777"
    ):

        self.nvim_address = nvim_address
        self.nvim_port = nvim_port
        if port_is_busy(nvim_address, nvim_port):
            raise Exception(f"Socket {nvim_address}:{nvim_port} is already in use.")

        self.root_dir = root_dir
        os.chdir(self.root_dir)

        self.log(f"Starting nvim instance at {nvim_address}:{nvim_port}")
        self.nvim_process = subprocess.Popen(['nvim','-u', 'NONE', '--headless', '--listen', f'{self.nvim_address}:{self.nvim_port}'])

        for retries in range(10):
            try:
                time.sleep(1)
                self.vim = attach('tcp', address=self.nvim_address, port=int(self.nvim_port))
                self.log("Success")
                break
            except:
                if retries == 10:
                    raise Exception("Could not open vim instance.")
                self.log("Retrying connection...")


        if os.listdir(self.swp_dir):
            shutil.rmtree(self.swp_dir, ignore_errors=True)
            self.log(f"Removed swp files from {self.swp_dir}")


    def log(self, message):
        print(f"\033[32m{message}\033[0m")

    def get_range(self, buffer_name, start=0, end=-1):
        buf = self.buffers[buffer_name]
        start = start + 1
        end = len(buf) if end == -1 else end + 1

        return buf.range(start, end)

    def replace(self, buffer_name, start, end, text):
        rng = self.get_range(buffer_name, start, end)
        n_new = len(text.splitlines())

        self.log(f"line {start}:")
        self.log("-" + "\n-".join(rng[:]))
        rng[:] = text.splitlines()
        self.log("+" + "\n+".join(rng[:n_new]))

    def insert(self, buffer_name, line, text):
        rng = self.get_range(buffer_name, line, line)
        rng.append(text.splitlines())

        n_new = len(text.splitlines())
        self.log(f"line {line}:")
        self.log("+" + "\n+".join(rng[:n_new]))

    def delete(self, buffer_name, start, end):
        rng = self.get_range(buffer_name, start, end)
        self.log(f"line {start}:")
        self.log("-" + "\n-".join(rng[:]))
        rng[:] = []


    def append(self, buffer_name, text):
        buf = self.buffers[buffer_name]
        lines = text.splitlines()
        self.log(f"line {len(buf)}:")
        self.log("+" + "\n+".join(lines))
        buf.append(lines)

    def save(self):
        self.log(":w")
        output = self.vim.command_output(":w")
        self.log(output)

    def open(self, file_path):
        full_path = os.path.join(self.root_dir, file_path)
        cmd = f":edit {full_path}"
        self.log(cmd)
        output = self.vim.command_output(cmd)
        if output:
            self.log(output)

    @property
    def swp_dir(self):
        return self.vim.command_output("echo &directory")


    @property
    def buffers(self):
        buffers = {
            self.vim.request('nvim_buf_get_name', n).split(self.root_dir + "/")[-1]:n 
            for n in self.vim.request('nvim_list_bufs')
        }

        return buffers



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


