import os
import sys
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(file_dir)

import argparse
import threading
import json
import time

from scout import FileScout
import lloam

blue = lambda x: f"\033[94m{x}\033[0m"
cyan = lambda x: f"\033[96m{x}\033[0m"
green = lambda x: f"\033[92m{x}\033[0m"
red = lambda x: f"\033[91m{x}\033[0m"
yellow = lambda x: f"\033[93m{x}\033[0m"
bold = lambda x: f"\033[1m{x}\033[0m"
clear_line = lambda: print("\033[A\033[K", end="")


SAVE_DIR = os.path.expanduser("~/.local/dixie_threads")

class Chat:
    def __init__(self):
        self.cwd= os.getcwd()
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

        os.makedirs(SAVE_DIR, exist_ok=True)

        with open(f"{SAVE_DIR}/{time.time()}.json", "w") as f:
            json.dump(record, f)


    @lloam.prompt
    def summarize(self):
        """
        {self.messages}

        Would you summarize our chat in a sentence?

        [text]
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

            elif log["level"] == "finished":
                clear_line()
                print(green(log["message"]))

                break

        self.refresh_context(scout.files)


def load_chats():
    chats = []
    for filename in os.listdir(SAVE_DIR):
        with open(f"{SAVE_DIR}/{filename}", "r") as f:
            record = json.load(f)

        chats.append({
            "time": record["last_opened"],
            "summary": record["summary"],
            "path": f"{SAVE_DIR}/{filename}"
        })

    return chats


def continue_chat():
    chats = load_chats()
    return max(chats, key=lambda x: x["time"])["path"]


def main():

    parser = argparse.ArgumentParser(description="Process a directory and query.")
    parser.add_argument("-c", action="store_true", help="Continue most recent chat")
    parser.add_argument("-d", type=str, help="Directory to confine the chat")

    # Parse the arguments
    args = parser.parse_args()

    directory = os.getcwd()
    chat = Chat()

    if args.c:
        saved = continue_chat()
        chat.load(saved)
    elif args.d:
        directory = args.d

    while True:
        text = input(blue("> "))
        if text == "exit":
            chat.save()
            break

        chat.user_message(text, directory)


if __name__ == "__main__":
    main()
