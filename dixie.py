
import lmql
import asyncio

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

class CommandChunk:
    def __init__(self, command):
        self.command = command

    def __str__(self):
        return self.command

class ChatBuffer:
    '''
    Responsible for storing the chat history and interfacing with the frontend.

    When a completion is made, the tokens are streamed to a buffer here. When the flush
    function is called, something is done with them, like printing. The entire completion
    itself is returned from the assistant() function. The assistant function uses the 
    buffer output writer to communicate with the buffer instance.
    '''
    def __init__(self):
        self.sysem_messages = []
        self.messages = []
        self.assistant_buffer = []
        self.user_buffer = []
        self.streaming=False

    def stream(self, role: str, chunk: str):
        if role == "assistant":
            self.assistant_buffer.append(chunk)
        else:
            self.user_buffer.append(chunk)

    def send(self, role: str, message: str): # TODO: replace=True/false
        self.messages.append((role, message))

    def flush(self):
        '''
        Process chunks that have accumulated in the stream buffer. Override for different frontends.
        '''
        do_continue = True

        for chunk in self.assistant_buffer:
            if isinstance(chunk, CommandChunk):
                if chunk.command == "exit":
                    do_continue = False
                else:
                    raise Exception("Unknown command: " + chunk.command)
                continue

            print(chunk, end="")

        self.assistant_buffer.clear()
        return do_continue

    @property
    def top_chunk(self):
        return self.assistant_buffer[-1] if self.assistant_buffer else ""

    def __iter__(self):
        return iter(self.messages)


chat_buffer = ChatBuffer()

class BufferOutputWriter:
    def __init__(self, variable):
        self.variable = variable
        self.last_value = None
        self.buffer = chat_buffer

    async def add_interpreter_head_state(self, variable, head, prompt, where, trace, is_valid, is_final, mask, num_tokens, program_variables):
        if self.variable is not None:

            value = program_variables.variable_values.get(self.variable, "").strip()
            prompt_state = program_variables.runtime.root_state.query_head

            reached_end = prompt_state.result is not None

            if self.last_value is None:
                self.last_value = value
                self.buffer.stream("assistant", value)
            else:
                self.buffer.stream("assistant", value[len(self.last_value):])
                self.last_value = value

            return

    def terminate(self):
        self.buffer.stream("assistant", CommandChunk("exit"))

writer = BufferOutputWriter("response")

@lmql.query(model="chatgpt", output_writer=writer)
async def mouthpiece(buffer):
    '''lmql
    for role, content in chat_buffer.messages:
        if role == "assistant":
            "{:assistant}{content}"
        else:
            "{:user}{content}"

    "{:assistant} [response]"
    buffer.terminate()
    '''

async def flush_loop():
    do_continue = True
    while do_continue:

        do_continue = chat_buffer.flush()
        await asyncio.sleep(0.1)


async def dialogue_chat():
    user = ""
    while user != "exit":
        user = input(blue("> "))
        chat_buffer.send("user", user)
        print()

        result, _ = await asyncio.gather(mouthpiece(writer), flush_loop())
        response = result[0].variables["response"]
        chat_buffer.send("assistant", response)
        print()

# def provide_commands(question):# {{{
#     @lmql.query(model="openai/gpt-3.5-turbo", decoder="sample", temperature=0.75)
#     def get_commands(question):
#         '''lmql
#         "{:user}{question}\n"
#         "{:assistant} Enter the following in your shell:\n"
#         "```\n"
#         "[commands]" where STOPS_BEFORE(commands, "```")
#         return commands.strip()
#         '''

#     commands = get_commands(question)[0]
#     print()
#     print(lprompt + commands.replace("\n", "\n" + lprompt))
#     print()
#     print("run? (Y/n)")
#     yn = input(blue("> "))
#     while yn not in ["Y", "n"]:
#         print("Y or n please")
#         yn = input(blue("> "))

#     if yn == "n":
#         return

#     for command in commands.split("\n"):
#         os.system(command)


# TODO: make dixie interactive so you can have feedback loops
# TODO: wrap terminal commands in a 'feedkeys api'; this will enable dixie to interact with other things. The protocol:
# - includes things like functions and context it can use in backend
# - method to stream text for the user to frontend
# - I also want to be able to interupt it (instead of regenrate button, just send another message)

# TODO: fun idea dixie comes with terminal frontend, and knows how build frontends for other programs}}}


if __name__ == "__main__":
    asyncio.run(dialogue_chat())

