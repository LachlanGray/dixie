import os
import re
import asyncio

from interfaces import FileExplorer
import lloam

def extract_ticks(text):
    pattern = r'`(.*?)`'
    matches = re.findall(pattern, text)
    return list(set(matches))


class FileScout(lloam.Agent):
    def __init__(self, root_dir, query, cache_dir=None):
        self.fe = FileExplorer(root_dir)
        self.query = query

        self.sub_scouts = []
        self.results = {}
        self.cache_path = None

        if cache_dir:
            cache_file = hash(query)
            self.cache_path = os.path.join(cache_dir, f"{cache_file}.json")


    def start(self):
        asyncio.run(self.search())


    async def search(self):
        self.directory = self.survey()

        await self.directory
        selection = extract_ticks(self.directory.selection)

        tasks = []
        for item in selection:
            item_path = os.path.join(self.fe.full_cwd, item)

            if not os.path.exists(item_path):
                continue

            if os.path.isfile(item_path):
                if "." not in item:
                    # assume it's a binary
                    continue

                self.fe.cd(item)
                try:
                    self.results[self.fe.cwd] = self.file_judgement()
                except UnicodeDecodeError:
                    # weird file, can't read it
                    pass

                finally:
                    self.fe.cd("..")

            elif os.path.isdir(item_path):
                self.sub_scouts.append(FileScout(item_path, self.query))
                tasks.append(self.sub_scouts[-1].search())

        await asyncio.gather(*tasks)

        for scout in self.sub_scouts:
            self.results.update(scout.results)


    @lloam.prompt
    def file_judgement(self):
        """
        {self.query}

        {self.directory.purpose}

        {self.directory.selection}

        In a sentence, what should we look for in `{self.fe.cwd}`?

        [scope]


        I've opened `{self.fe.cwd}` and here's what I see:
        ```
        {self.fe.cat}
        ```
        In a sentence, what does it tell us?

        [result].

        """


    @lloam.prompt
    def survey(self):
        """
        {self.query}

        For the moment, I'm in the directory `{self.fe.cwd}` as I manually look for useful files.

        Here's what I see:
        ```
        {self.fe.ls}
        ```
        In a sentence, what purpose does this directory serve and how might it be relevant?

        [purpose].


        Out of the options, which ones should I look at? (use ` to denote folder/file names)
        If nothing here is relevant just say "Elsewhere".

        [selection]
        """



if __name__ == "__main__":
    issue_dir = "evaluation/workspaces/sqlfluff_issue_6335"
    root_dir = os.path.join(issue_dir, "sqlfluff")

    # query = "I want to add a `CREATE FOREIGN DATA WRAPPER` statement for postgres."
    # query = "I want to figure out how to add new statements."
    # query = "I want to understand the architecture of this project."

    # query = "I want to figure out how to add new statements."

    query = "I want to understand the architecture of this project."
    # query = "I want to add a `CREATE FOREIGN DATA WRAPPER` statement for postgres."


    scout = FileScout(root_dir, query)
    stop_event = scout.observe()
    scout.start()
    stop_event.set()

    print("DONE")

    # try:
    #     scout.start()
    # except KeyboardInterrupt:
    #     # Stop observing when Ctrl-C is pressed
    #     stop_event.set()
    #     # Continue with the rest of the program

    # print("DONE")
    breakpoint()


