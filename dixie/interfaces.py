import os
import subprocess
import time
import shutil
from pynvim import attach

from utils import port_is_busy


class FileExplorer:
    def __init__(self, root_dir, debug=False):
        self.root_dir = root_dir
        self.project = os.path.split(root_dir)[-1]

        self.subdirs = []
        self.history = []

        self._debug = debug

    def log(self, message):
        if self._debug:
            print(f"\033[34m{message}\033[0m")

        self.history.append(message)

    @property
    def cwd(self):
        return os.path.join(self.project, *self.subdirs)

    @property
    def full_cwd(self):
        return os.path.join(self.root_dir, *self.subdirs)

    @property
    def ls(self):
        self.log(f"ls -l {self.cwd}")
        result = subprocess.run(['ls' , self.full_cwd], capture_output=True, text=True)
        return result.stdout

    def cd(self, subdir):
        if subdir == "..":
            if os.path.isdir(os.path.join(self.full_cwd, subdir)):
                self.log(f"cd ..")
            else:
                self.log(f"close {self.subdirs[-1]}")

            self.subdirs.pop()
        else:
            if os.path.exists(os.path.join(self.full_cwd, subdir)):
                if os.path.isdir(os.path.join(self.full_cwd, subdir)):
                    self.log(f"cd {subdir}")
                else:
                    self.log(f"open {subdir}")

                self.subdirs.append(subdir)
            else:
                self.log(f"cd: no such file or directory: {subdir}")
                assert False

    @property
    def cat(self):
        self.log(f"read {self.cwd}")
        result = subprocess.run(['cat', self.full_cwd], capture_output=True, text=True)
        return result.stdout



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


