#!/usr/bin/env python3

import lmql
import os

black = lambda text: f"\033[30m{text}\033[0m"
red = lambda text: f"\033[31m{text}\033[0m"
green = lambda text: f"\033[32m{text}\033[0m"
yellow = lambda text: f"\033[33m{text}\033[0m"
blue = lambda text: f"\033[34m{text}\033[0m"
magenta = lambda text: f"\033[35m{text}\033[0m"
cyan = lambda text: f"\033[36m{text}\033[0m"
white = lambda text: f"\033[37m{text}\033[0m"

lprompt = green("> ")
lprompt = "    " + lprompt

def provide_commands(question):
    @lmql.query(model="openai/gpt-3.5-turbo", decoder="sample", temperature=0.75)
    def get_commands(question):
        '''lmql
        "{:user}{question}\n"
        "{:assistant} Enter the following in your shell:\n"
        "```\n"
        "[commands]" where STOPS_BEFORE(commands, "```")
        return commands.strip()
        '''

    commands = get_commands(question)[0]
    print()
    print(lprompt + commands.replace("\n", "\n" + lprompt))
    print()
    print("run? (Y/n)")
    yn = input(blue("> "))
    while yn not in ["Y", "n"]:
        print("Y or n please")
        yn = input(blue("> "))

    if yn == "n":
        return

    for command in commands.split("\n"):
        os.system(command)

def main():
    question = input(blue("> "))

    provide_commands(question)

if __name__ == "__main__":
    main()
