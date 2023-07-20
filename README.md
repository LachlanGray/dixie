# The Dixie Flatline
>*“Lemme take that a sec, Case. . . .” The matrix blurred and phased as the Flatline executed an intricate series of jumps with a speed and accuracy that made Case wince with envy.*
>
>*“Shit, Dixie. . . .”*
>
>*“Hey, boy, I was that good when I was alive. You ain’t seen nothin’. No hands!”*
>
>– From William Gibson's *Neuromancer* [^1]

A(nother) digital construct to help you hack away in the terminal.

## Installation
1. Clone this somewhere and make Dixie executable with
```
chmod +x dixie.py
```
2. Move `dixie.py` somewhere on your path, and choose a name for the activation command (I use "hey"). For example:
```
mv dixie.py /usr/local/bin/hey
```
3. Make sure LMQL 0.0.6.5+ is available to your system python, and that you have set your `OPENAI_API_KEY` environment variable

## Usage
Activate Dixie with the keyword you chose. Say what you want to do, and receive a list of commands to accomplish it. Say `Y` to run them or `n` to reject them.

```
$ hey
> I want to create a new folder called data and a file inside that says "hello world"

    > mkdir data
    > cd data
    > echo "hello world" > file.txt

run? (Y/n)
> Y
```

**BE CAREFUL IT DOES NOT FILTER DANGEROUS COMMANDS!!!** Use at your own risk.

Much more functionality to come.


[^1]: Published in 1984, possibly the coolest book ever written, and full of eerie similarities to recent events.
    An all-time favourite character of mine is the construct of a legendary hacker known as the Dixie Flatline; his consciousness flashed to a ROM. Though it can't form new memories and experiences like the original, it can read and write cyberspace swiftly, making it a valuable companion.
