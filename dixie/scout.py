import os
import re
import asyncio
import time
from collections import defaultdict

from interfaces import FileExplorer
import lloam



class FileScout(lloam.Agent):
    def __init__(self, root_dir, initial_query):
        super().__init__()
        self.explorer = FileExplorer(root_dir)
        _, self.project = os.path.split(root_dir)

        self.initial_query = initial_query
        self.files = {}
        self.dirs = {}

        self.explore_tasks = asyncio.Queue()
        self.file_tasks = asyncio.Queue()

    def start(self):
        asyncio.run(self._start())


    async def _start(self, timeout=10):
        self.log(f"Exploring {self.project}", level="update")
        await self.explore_tasks.put(self.explore_dir(""))


        while not self.explore_tasks.empty():
            try:
                task = self.explore_tasks.get_nowait()
                await asyncio.wait_for(task, timeout=timeout)

            except asyncio.TimeoutError:
                self.log(f"Explore task timed out after {timeout} seconds", level="error")

            except Exception as e:
                self.log(f"An error occurred: {e}", level="error")


        while not self.file_tasks.empty():
            try:
                task = self.file_tasks.get_nowait()
                await asyncio.wait_for(task, timeout=timeout)

                self.log(f"{self.file_tasks.qsize()} files remaining", level="update")


            except asyncio.TimeoutError:
                file_path = os.path.join(task.directory, task.filename)
                self.log(f"{file_path} timed out after {timeout} seconds", level="error")
                self.files[file_path] = "This file failed to read. If it's important, ."



        self.log(f"{len(self.files)} files chosen", level="finished")



    async def explore_dir(self, dir_path):

        subdirs = self.choose_dirs(dir_path)
        files = self.choose_files(dir_path)

        self.dirs[dir_path] = {}

        async for subdir in subdirs.choices.astream():
            subdir_path = os.path.join(dir_path, subdir)

            if subdir_path in self.dirs:
                self.log(f"Already explored {subdir_path} (skipping)", level="warning")
                continue

            if self.explorer.is_dir(subdir_path):
                self.log(f"Exploring {subdir_path}", level="update")

                await self.explore_tasks.put(self.explore_dir(subdir_path))

            else:
                self.log(f"nonexistent directory {subdir_path}", level="warning")


        async for file in files.choices.astream():
            file_path = os.path.join(dir_path, file)

            if not self.explorer.is_file(file_path):
                self.log(f"nonexistent file {subdir_path}", level="warning")
                continue

            self.log(f"Reading {file_path}", level="update")

            desc = self.describe_file(dir_path, file)
            await self.file_tasks.put(desc)

            # desc = self.describe_file(dir_path, file)
            self.files[file_path] = desc.description

            # await self.tasks.put(self.files[file_path])


    @lloam.prompt
    def choose_files(self, directory):
        """
        {self.initial_query}

        I'm in the project directory `{directory}`:
        ```
        {self.explorer.ls(directory)}
        ```

        In a sentence, which files should I investigate?
        Please use `backticks` to denote files.

        [[`[choices]`]]

        """


    @lloam.prompt
    def choose_dirs(self, directory):
        """
        {self.initial_query}

        I'm in the project directory `{directory}`:
        ```
        {self.explorer.ls(directory)}
        ```

        In a sentence, which subdirectories should I investigate?
        Please use `backticks` to indicate directories.

        [[`[choices]`]]

        """

    @lloam.prompt()
    def describe_file(self, directory, filename):
        """
        {self.initial_query}

        From the directory {directory}:
        ```
        {self.explorer.ls(directory)}
        ```

        Here are the contents of `{filename}`:
        ```
        {self.explorer.cat(directory + '/' + filename)}
        ```

        In a few sentences, what do we learn from this file?
        [[description]]
        """


