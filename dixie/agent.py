import os

from interfaces import Vim, FileExplorer
import lloam


@lloam.prompt
def choose_dir(query, ls):
    """
    {query}

    Of these options, where should I look?
    ```
    {ls}
    ```

    You should look in `[subdir]`
    """

@lloam.prompt
def judge_file(query, cat):
    """
    {query}

    Does this file contain information that we can use? Yes or no?
    ```
    {cat}
    ```

    [answer]. [elaboration]~
    """


@lloam.prompt
def judge_dir(query, ls):
    """
    {query}

    Does anything here look useful? Yes or no?
    ```
    {ls}
    ```

    [answer]. [elaboration]~
    """


def locate(query, fe):

    choice = choose_dir(query, fe.ls)

    subdir_or_file = choice.subdir

    fe.cd(subdir_or_file)

    if not os.path.isdir(fe.cwd):
        judgement = judge_file(query, fe.cat)

        if "yes" in judgement.answer.lower():
            return {
                "file": fe.cwd,
                "info": judgement
            }

        return None

    return locate(query, fe)



if __name__ == "__main__":
    root_dir = "/Users/lachlangray/dev/OpenHands"

    # vim = Vim(root_dir, nvim_port="7778")
    fe = FileExplorer(root_dir, debug=True)

    query = "I want to figure out the frontend framework used in this project."

    result = locate(query, fe)
    print(result)



