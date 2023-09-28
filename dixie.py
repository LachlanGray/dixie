import lmql
import asyncio

from dataclasses import dataclass
from lmql.runtime.program_state import ProgramState

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

@lmql.decorators.streaming
def to_user(value: str, context: ProgramState):
    diff = context.get_diff("COMPLETION")
    if value:
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
    "{:assistant} The topic is \"[TOPIC] where STOPS_BEFORE(TOPIC, '\"')"
    TOPIC = TOPIC.split('"')[0] # stops before bug in lmql
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
    chat["messages"].append(("assistant", COMPLETION))
    """

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
    while True:
        user = input(blue("> "))
        if user == "exit":
            break
        chat["messages"].append(("user", user))
        print()
        response = await dispatch([reply(), name_convo()])
        print()

    print(chat)

if __name__ == "__main__":
    asyncio.run(main())


# @lmql.query
# def decide_action(message, actions):
#     """lmql
#     "{:system} The user will give you a message to interpret, and you must tell them the best followup action."
#     "{:user} Here is the message:\n\n"
#     "{message}"
#     "And here are the available actions:\n\n"
#     "{',\n'.join(actions)}"
#     "{:assistant} The appropriate action is '[ACTION]" where STOPS_BEFORE(ACTION, "'")
#     return ACTION
#     """

# @dataclass
# class Action:
#     description: str
#     fn: callable

# actions = {
#     "reply": Action("Immediately say something to the user.", reply),
# }

# async def reply(messages):
#     user_text = messages[-1][1]
#     action = await decide_action(user_text, list(actions.keys()))
