import os
import re
from concurrent.futures import Future

from interfaces import FileExplorer
import lloam


def extract_ticks(text):
    pattern = r'`(.*?)`'
    return re.findall(pattern, text)


class FileScout:
    def __init__(self, root_dir, query):
        self.fe = FileExplorer(root_dir, debug=True)
        self.query = query

        self.results = {}

        self.report = None


    def start(self):
        self.locate()
        self.aggregate()


    def locate(self):

        choice = self.choose_dirs()
        subdirs = list(set(extract_ticks(choice.options)))
        results = []

        for subdir in subdirs:
            subdir = os.path.split(subdir)[-1]
            if not os.path.exists(os.path.join(self.fe.full_cwd, subdir)):
                continue

            self.fe.cd(subdir)

            if os.path.isfile(self.fe.full_cwd):
                if "." not in subdir:
                    continue

                judgement = self.judge_file()

                if "yes" in judgement.answer.lower():
                    self.results[self.fe.cwd] = judgement

            else:
                self.locate()

            self.fe.cd("..")

        return results


    @lloam.prompt
    def choose_dirs(self):
        """
        {self.query}

        I'm in `{self.fe.cwd}`. Out of these options, which ones should I look at?
        Or if these aren't helpful just say "elsewhere".
        Please answer in one sentence.
        ```
        {self.fe.ls}
        ```

        [options]
        """


    @lloam.prompt
    def judge_file(self):
        """
        {self.query}

        Does this file contain information that we can use? Yes or no?
        ```
        {self.fe.cat}
        ```

        [answer].

        In a sentence, what does it tell us?

        [summary]
        """


    @lloam.prompt
    def make_report(self, result_string):
        """
        {self.query}

        For context:
        {result_string}

        Would you please compile this into a coherent narrative? Please be specific and include paths where possible

        [conclusion]
        """


    def aggregate(self):

        if not self.results:
            return None

        result_string = ""

        format_result = lambda name, info: f"`{name}`: {info}\n\n"

        for file, info in self.results.items():
            result_string += format_result(file, info.summary)

        report = self.make_report(result_string)
        self.report = report



if __name__ == "__main__":
    issue_dir = "evaluation/workspaces/sqlfluff_issue_6335"
    root_dir = os.path.join(issue_dir, "sqlfluff")

    # query = "I want to add a `CREATE FOREIGN DATA WRAPPER` statement for postgres."
    # query = "I want to figure out how to add new statements."

    # query = "I want to understand the architecture of this project."

    query = "I want to understand the architecture of this project. Its components, their implementations, and how they are used."


    scout = FileScout(root_dir, query)
    scout.start()
    report = scout.report

    conclusion = report.conclusion

    result_path = os.path.join(issue_dir, "info.md")
    with open(result_path, "w") as f:
        f.write(conclusion)


    # collected = locate(query, fe)
    # result = aggregate(query, collected)

    # print(result.conclusion)



