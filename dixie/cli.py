import os
import sys
file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(file_dir)

import argparse
import threading
import json
import time

from scout import FileScout
from chat import Chat
import lloam

SAVE_DIR = os.path.expanduser("~/.local/dixie_threads")

blue = lambda x: f"\033[94m{x}\033[0m"
cyan = lambda x: f"\033[96m{x}\033[0m"
green = lambda x: f"\033[92m{x}\033[0m"
red = lambda x: f"\033[91m{x}\033[0m"
yellow = lambda x: f"\033[93m{x}\033[0m"
bold = lambda x: f"\033[1m{x}\033[0m"
clear_line = lambda: print("\033[A\033[K", end="")




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
    chat = Chat(directory, SAVE_DIR)

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

    # directory = "/Users/lachlangray/sieve/GPEN"
    # # message = "how do I set up inference for this repository?"
    # message = "what model architecture is used in this repository?"

    # chat = Chat()
    # chat.user_message(message, directory)



