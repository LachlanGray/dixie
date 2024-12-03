import os
import re
import asyncio
import time

from interfaces import FileExplorer
import lloam

def extract_ticks(text):
    pattern = r'`(.*?)`'
    matches = re.findall(pattern, text)
    return list(set(matches))


class FileScout(lloam.Agent):
    def __init__(self, root_dir, query, cache_dir=None, subdirs=[]):
        self.fe = FileExplorer(root_dir)
        if subdirs:
            for subdir in subdirs:
                self.fe.cd(subdir)

        self.query = query

        self.sub_scouts = []
        self.results = {}
        self.cache_path = None

        if cache_dir:
            cache_file = hash(query)
            self.cache_path = os.path.join(cache_dir, f"{cache_file}.json")


    def start(self):
        asyncio.run(self.search())

        fmt = lambda file, desc: f"`{file}`: {desc}\n\n"
        results_str = ""
        for k, v in self.results.items():
            try:
                desc = v.description
                results_str += fmt(k, desc)
            except:
                print("rate limitted...")
                time.sleep(3)


        self.results_str = results_str
        self.summary = self.summarize(results_str)
        _ = self.summary.summary


    async def search(self, top=True):
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
                    print(self.fe.cwd)
                except UnicodeDecodeError:
                    # weird file, can't read it
                    pass

                finally:
                    self.fe.cd("..")

            elif os.path.isdir(item_path):
                self.sub_scouts.append(FileScout(self.fe.root_dir, self.query, subdirs=self.fe.subdirs + [item] ))
                tasks.append(self.sub_scouts[-1].search(top=False))

        await asyncio.gather(*tasks)

        for scout in self.sub_scouts:
            self.results.update(scout.results)

        # if top:
        #     # asyncio gather self.results values
        #     await asyncio.gather(*self.results.values())

        # TODO: check for stuff after closing 


    @lloam.prompt
    def file_judgement(self):
        """
        {self.query}

        {self.directory.purpose}

        {self.directory.selection}

        I've opened `{self.fe.cwd}` and here's what I see:
        ```
        {self.fe.cat}
        ```
        In a sentence, what does it tell us?

        [description]
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

    @lloam.prompt
    def summarize(self, results_str):
        """
        {self.query}

        For context:
        {results_str}


        [summary]
        """


if __name__ == "__main__":
    root_dir = "evaluation/workspaces/OpenHands_issue_4420/OpenHands"
    query = "I want to understand how the frontend connects to the backend"

    scout = FileScout(root_dir, query)
    scout.observe()
    scout.start()

    print(scout.summary)

