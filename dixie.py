#!/usr/bin/env python

import lmql
import asyncio
import subprocess

from lmql.runtime.program_state import ProgramState

import warnings
warnings.filterwarnings("ignore")


# colors {{{
black = lambda text: f"\033[30m{text}\033[0m"
red = lambda text: f"\033[31m{text}\033[0m"
green = lambda text: f"\033[32m{text}\033[0m"
yellow = lambda text: f"\033[33m{text}\033[0m"
blue = lambda text: f"\033[34m{text}\033[0m"
magenta = lambda text: f"\033[35m{text}\033[0m"
cyan = lambda text: f"\033[36m{text}\033[0m"
white = lambda text: f"\033[37m{text}\033[0m"
# }}}

lmql.set_default_model("chatgpt")
# lmql.set_default_model("gpt-4")

@lmql.decorators.streaming
def to_user(value: str, context: ProgramState):
    diff = context.get_diff("COMPLETION")
    if value and diff:
        parts = value.split("```")

        if "`" in diff:
            print(green(diff), end='')
            return

        if len(parts) % 2:
            print(diff, end='')
        else:
            print(green(diff), end='')

@lmql.query
async def name_convo():
    """lmql
    message = chat['messages'][0][1]
    "{:user} In a few words, what's the topic of the following message:\n***\n"
    "{message}\n***"
    "{:assistant} The topic is \"[TOPIC] " where STOPS_BEFORE(TOPIC, '\"')
    chat["title"] = TOPIC.strip()
    """

@lmql.query
async def reply():
    """lmql
    messages = chat['messages']
    for role, content in messages:
        if role == "assistant":
            "{:assistant}{content}"
        else:
            "{:user}{content}"
    "{:assistant}[@to_user COMPLETION]"
    chat["messages"].append(("assistant", COMPLETION.lstrip()))
    print()
    """

@lmql.query
async def run_commands(message=None):
    """lmql
    "{:system}You provide shell commands to the user. You present a command and offer to run it."
    if message is None:
        messages = chat['messages']
        for role, content in messages:
            if role == "assistant":
                "{:assistant}{content}"
            else:
                "{:user}{content}"
    else:
        "{:user}{message}"
    print(green("----------------------------------------"))
    "{:assistant}Here's what I can execute:\n```\n"
    "[@to_user COMPLETION]" where STOPS_BEFORE(COMPLETION, "\n```")
    print(green("\n----------------------------------------"))

    conf_string = "Do you want me to run it?"
    chat["messages"].append(("assistant", "```\n" + COMPLETION.lstrip() + "\n```\n\n" + conf_string))

    proceed = input(f"Run it? (y/n) {blue('>')} ")
    if proceed == "y":
        chat["messages"].append(("user", "yes"))
        result = subprocess.run(COMPLETION, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)
        chat["messages"].append(("assistant", "```\n" + result.stdout + "\n```"))
        if result.stdout:
            print(green("----------------------------------------"))
            print(result.stdout)
            print(green("\n----------------------------------------"))
        else:
            print(green("Done."))
    else:
        print("Aborting...")
        chat["messages"].append(("user", "no"))


    return COMPLETION.lstrip()
    """

actions = [
    "run commands: The user is explicitly asking me to run or execute something.",
    "question: The user is not asking me to perform any action, they are only asking a question.",
]

action_map = {
    "question": reply,
    "run commands": run_commands,
}

@lmql.query
async def actions_required(message=None):
    """lmql
    last_message = message
    if message is None:
        last_message = chat['messages'][-1][1]
    "{:user}A user has sent me the message:\n***\n"
    "{last_message}\n***\n"
    "which of the following is most appropriate?\n"
    choices = ',\n'.join(actions)
    "{actions}"
    "{:assistant}The most accurate choice is \"[ACTION]\" " where STOPS_BEFORE(ACTION, ":")
    return ACTION.strip()
    """

async def next_action(message=None):
    action = await actions_required(message)
    action = action[0]
    await action_map[action]()

async def dispatch(coroutines):
    tasks = [asyncio.create_task(coro) for coro in coroutines]
    while tasks:
        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            try:
                result = task.result()
            except Exception as e:
                raise e # raise the exception for now


chat = {
    "title": "",
    "messages": []
}


async def main():
    user = ""
    user = input(blue("> "))
    chat["messages"].append(("user", user))
    response = await dispatch([next_action(), name_convo()])
    while True:
        user = input(blue("> "))
        if user == "exit":
            break
        chat["messages"].append(("user", user))
        response = await next_action()

    print(chat)

if __name__ == "__main__":
    asyncio.run(main())

