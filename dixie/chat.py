import os
import threading
import json
import time

import lloam

from scout import FileScout

blue = lambda x: f"\033[94m{x}\033[0m"
cyan = lambda x: f"\033[96m{x}\033[0m"
green = lambda x: f"\033[92m{x}\033[0m"
red = lambda x: f"\033[91m{x}\033[0m"
yellow = lambda x: f"\033[93m{x}\033[0m"
bold = lambda x: f"\033[1m{x}\033[0m"
clear_line = lambda: print("\033[A\033[K", end="")


class Chat:
    def __init__(self, cwd, save_dir):
        self.cwd = cwd
        self.save_dir = save_dir
        self.files = {}

        self.messages = [{
            "role": "system",
            "content": "",
        }]

        self.refresh_context()
        self.summary = None

    def save(self):
        if self.summary is None:
            self.summary = self.summarize().text.result()

        record = {
            "messages" : self.messages,
            "files": self.files,
            "summary": self.summary,
            "last_opened": time.time()
        }

        os.makedirs(self.save_dir, exist_ok=True)

        with open(f"{self.save_dir}/{time.time()}.json", "w") as f:
            json.dump(record, f)


    @lloam.prompt
    def summarize(self):
        """
        {self.messages}

        Would you summarize our chat in a sentence?

        [[text].]
        """


    def load(self, filename):
        with open(filename, "r") as f:
            record = json.load(f)

        self.messages = record["messages"]
        self.files = record["files"]
        self.summary = record["summary"]
        self.refresh_context()


    def refresh_context(self, new_files={}):
        for k in new_files:
            if k not in self.files:
                self.files[k] = str(new_files[k])
            else:
                self.files[k] = self.files[k] + "\n" + str(new_files[k])

        cwd = f"Current directory: {self.cwd}"
        contents = "Directory contents:\n" + "\n".join(os.listdir(self.cwd))
        files_context = "File info:\n" + "\n\n".join([f"**{k}**: {v}" for k, v in self.files.items()])

        new_context = f"{cwd}\n{contents}\n{files_context}"

        self.messages[0]["content"] = new_context


    def user_message(self, text, directory):
        self.cwd = directory
        self.refresh_context()

        self.messages.append({
            "role": "user",
            "content": text
        })


        self.scout(self.messages)

        completion = lloam.completion(self.messages)

        for chunk in completion.stream():
            print(green(chunk), end="")
        print()


        self.messages.append({
            "role": "assistant",
            "content": completion.result()
        })


    def scout(self, query):
        scout = FileScout(self.cwd, query)

        threading.Thread(target=scout.start).start()

        print()
        for log in scout.stream():
            if log["level"] == "update":
                clear_line()
                print(cyan(log["message"]))

            elif log["level"] == "error":
                clear_line()
                print(red(log["message"]))
                print()

            elif log["level"] == "finished":
                clear_line()
                print(green(log["message"]))

                break

        self.refresh_context(scout.files)


