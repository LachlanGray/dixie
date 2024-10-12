import os
import re

from interfaces import Vim, FileExplorer
import lloam


def extract_ticks(text):
    pattern = r'`(.*?)`'
    return re.findall(pattern, text)


class Scout:
    def __init__(self, root_dir, query):
        self.fe = FileExplorer(root_dir, debug=True)
        self.query = query


    def locate(self):
        query = self.query

        choice = self.choose_dirs(query, self.fe)
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

                judgement = self.judge_file(query, self.fe.cat)

                if "yes" in judgement.answer.lower():
                    results.append({
                        "file": self.fe.cwd,
                        "info": judgement
                    })

            else:
                results += self.locate()

            self.fe.cd("..")

        return results

    @lloam.prompt
    def choose_dirs(self, query, fe):
        """
        {query}

        I'm in `{fe.cwd}`. Our of these options, which ones should I look at? Or if these aren't helpful "elsewhere". Please answer in one sentence.
        ```
        {fe.ls}
        ```

        You could look at `[options]
        """

    @lloam.prompt
    def judge_file(self, query, cat):
        """
        {query}

        Does this file contain information that we can use? Yes or no?
        ```
        {cat}
        ```

        [answer]. [elaboration]

        In one sentence, this file tells us: [summary].
        """


    @lloam.prompt
    def finish(self, query, results):
        """
        {query}

        I have the following:
        {results}

        Given that information, what can we conclude?

        [conclusion]
        """


    def aggregate(self, results):
        query = self.query

        if not results:
            return "I couldn't find anything that matched your query."

        summary = []
        for result in results:
            summary.append(f"`{result['file']}`:")
            summary.append(result["info"].summary)

        return self.finish(query, "\n".join(summary))



if __name__ == "__main__":
    root_dir = "/Users/lachlangray/dev/OpenHands"

    # vim = Vim(root_dir, nvim_port="7778")
    # fe = FileExplorer(root_dir, debug=True)

    # query = "I want to figure out the frontend framework used in this project."
    # query = "I want to figure out how user sessions work."
    # query = "I want to figure out how the backend connects to the frontend."
    query = "I want to figure out the frontend stack."

    scout = Scout(root_dir, query)
    collected = scout.locate()
    result = scout.aggregate(collected)
    print(result.conclusion)

    breakpoint()

    # collected = locate(query, fe)
    # result = aggregate(query, collected)

    # print(result.conclusion)



