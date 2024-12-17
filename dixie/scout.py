import os
import re
import asyncio
import time
from collections import defaultdict

from interfaces import FileExplorer
import lloam

def extract_ticks(text):
    inline_pattern = r'`(.*?)`'
    inline_matches = re.findall(inline_pattern, text)

    return list(set(inline_matches) - {''})


class FileScout(lloam.Agent):
    def __init__(self, root_dir, initial_query):
        super().__init__()
        self.explorer = FileExplorer(root_dir)

        self.initial_query = initial_query
        self.files = {}

        self.tasks = {}
        self.task_graph = defaultdict(list)


    def start(self):
        asyncio.run(self._start())


    async def _start(self, timeout=10):
        await self.explore_dir(self.explorer.cwd)

        n_files = len(self.tasks)

        self.log(f"Awaiting {n_files} tasks to complete.", level="update")
        try:
            for coro in asyncio.as_completed(self.tasks.values(), timeout=timeout):
                n_files -= 1
                await coro
                self.log(f"Awaiting {n_files} tasks to complete.", level="update")
        except asyncio.TimeoutError:
            self.log(f"Timed out after {timeout} seconds", level="error")

            for k in self.tasks:
                if not self.tasks[k].done():
                    self.tasks[k].cancel()
                    self.files[k] = "This file timed out. If it's important, mention it, otherwise ignore."
                    self.log(f"{k} timed out", level="error")

        self.log(f"{len(self.tasks)} tasks done.", level="finished")


    async def explore_dir(self, directory):
        if directory in self.task_graph:
            self.log(f"Already explored {directory} (skipping)", level="warning")
            return

        self.log(f"Exploring {directory}", level="update")

        ls = self.explorer.ls(directory)

        # get useful dirs
        useful_dirs = self.choose_dirs(directory, ls)

        # get useful files
        useful_files = self.choose_files(directory, ls)


        # create describe task for every file
        await useful_files
        selected_files = extract_ticks(useful_files.filenames.result())
        self.log(f"prompt: {useful_files}", level="prompt")
        self.log(f"file selection: {selected_files}")


        for selected_file in selected_files:
            if self.explorer.is_file(selected_file):
                file_path = selected_file
            else:
                selected_file = os.path.split(selected_file)[-1]
                file_path = os.path.join(directory, selected_file)

            if not self.explorer.is_file(file_path):
                self.log(f"{file_path} is not a file", level="warning")
                continue

            self.log(f"Describing file {file_path}")
            task = asyncio.create_task(
                self.get_file_description(file_path)
            )
            self.tasks[file_path] = task
            self.task_graph[directory].append(file_path)


        # create explore task for every child dir
        await useful_dirs
        selected_dirs = extract_ticks(useful_dirs.directories.result())
        self.log(f"prompt: {useful_dirs}", level="prompt")
        self.log(f"dir selection: {selected_dirs}")

        children = []

        for selected_dir in selected_dirs:
            selected_dir = os.path.split(selected_dir)[-1]
            selected_dir = os.path.join(directory, selected_dir)

            if not self.explorer.is_dir(selected_dir):
                self.log(f"{selected_dir} is not a valid directory", level="warning")
                continue


            self.task_graph[directory].append(selected_dir)
            task = asyncio.create_task(self.explore_dir(selected_dir))

            children.append(task)


        # ensure all children have initiated file descriptions
        await asyncio.gather(*children)


    async def get_file_description(self, path):
        self.log(f"Opening {path}", level="update")

        contents = self.explorer.cat(path)
        description = self.describe_file(path, contents)
        await description

        description = description.description
        self.files[path] = description


    @lloam.prompt
    def choose_files(self, directory, ls):
        """
        {self.initial_query}

        In the directory `{directory}`:
        ```
        {ls}
        ```

        In a sentence, which files should I investigate?
        [[filenames]]
        """

    @lloam.prompt()
    def choose_dirs(self, directory, ls):
        """
        {self.initial_query}

        In the directory `{directory}`, here are its contents:
        ```
        {ls}
        ```

        In a few sentences, which subdirectories should I explore?
        Please use `backticks` to indicate directories
        [[directories]]
        """

    @lloam.prompt()
    def describe_file(self, filename, contents):
        """
        {self.initial_query}

        Here are the contents of `{filename}`:
        ```
        {contents}
        ```

        In a few sentences, what do we learn from this file?
        [[description]]
        """


if __name__ == "__main__":
    test_dir = "/Users/lachlangray/dev/dixie/evaluation/workspaces/sqlfluff_issue_6335/sqlfluff"
    scout = FileScout(test_dir, "I want to know all the dependencies of this project")


    scout.start()
    print(scout.summary)






