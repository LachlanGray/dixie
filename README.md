# The Dixie Flatline
>*“Lemme take that a sec, Case. . . .” The matrix blurred and phased as the Flatline executed an intricate series of jumps with a speed and accuracy that made Case wince with envy.*
>
>*“Shit, Dixie. . . .”*
>
>*“Hey, boy, I was that good when I was alive. You ain’t seen nothin’. No hands!”*
>
>– From William Gibson's *Neuromancer* [^1]

Basically another interactive terminal assistant.

## Installation
The idea is that everything is contained in `dixie.py`, so you can rename it to an activation command of your choice, and move it to your path.

1. Clone this or copy the contents of `dixie.py` somewhere on your `$PATH`, e.g.
```
mv dixie.py /usr/local/bin/dixie.py
```
2. Rename the file to the activation command of your choice (I use "hey")
```
mv dixie.py /usr/local/bin/hey
```
3. Make sure you have a recent LMQL release ([master branch](https://github.com/eth-sri/lmql) is a safe bet) available to your system python, and that you've got your `OPENAI_API_KEY` environment variable set

## Usage
Now, you can say `hey` to your terminal, and you'll start a chat with gpt-3.5 (will support other models at some point). If you *explicitly* ask it to do something it will offer commands which you can accept or reject. Otherwise it will chat as usual.

[^1]: Published in 1984, possibly the coolest book ever written, and full of eerie similarities to recent events.
    An all-time favourite character of mine is the construct of a legendary hacker known as the Dixie Flatline; his consciousness flashed to a ROM. Though it can't form new memories and experiences like the original, it can read and write cyberspace swiftly, making it a valuable companion.
