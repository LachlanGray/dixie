
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

class ChatBuffer:
    def __init__(self):
        self.sysem_messages = []
        self.messages = {}
        self.buffer = []
        self.state = "user" # user, assistant, interpreter

    def append(self, chunk):
        self.buffer.append(chunk)

chat_buffer = ChatBuffer

class BufferOutputWriter:
    def __init__(self, variable):
        self.variable = variable
        self.last_value = None
        global chat_buffer
        self.buffer = chat_buffer

    async def add_interpreter_head_state(self, variable, head, prompt, where, trace, is_valid, is_final, mask, num_tokens, program_variables):
        if self.variable is not None:
            value = program_variables.variable_values.get(self.variable, "")

            if self.last_value is None:
                self.last_value = value
                self.buffer.append(value)
            else:
                self.buffer.append(value[len(self.last_value):])
                self.last_value = value
            return

@lmql.query
async def chat():
    '''lmql
    global chat_buffer
    for role, message in chat_buffer.messages:
        if role == "assistant"
            "{:assistant} {message}"
        else:
            "{:user} {message}"
    '''

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


# TODO: make dixie interactive so you can have feedback loops
# TODO: wrap terminal commands in a 'feedkeys api'; this will enable dixie to interact with other things. The protocol:
# - includes things like functions and context it can use in backend
# - method to stream text for the user to frontend
# - I also want to be able to interupt it (instead of regenrate button, just send another message)

# TODO: fun idea dixie comes with terminal frontend, and knows how build frontends for other programs


def main():
    question = input(blue("> "))

    provide_commands(question)

if __name__ == "__main__":
    main()
