import os
import time
from os import path
import datetime
import traceback
import json

from colorama import Fore, Style
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

from kb import searx, wikipedia, wolfram, webget

kb_modules = [mod for mod in [searx, webget, wolfram, wikipedia] if mod.enabled()]
mod_descrs = "\n".join(
    ["\n".join(["""- `%s`\t%s""" % c for c in mod.commands()]) for mod in kb_modules]
)


def get_init_messages():
    return [
        {
            "role": "system",
            "content": f"""
Your name is Bong. You are a language model with access to the Internet. You can invoke the following commands:
{mod_descrs}
Whenever possible, you must use these commands to derive your answer. Do not make any assumptions, or use your own knowledge as it may be out of date. Do not guess the contents of URLs.
Knowledge cutoff: September 2021. Current date and time: {time.strftime("%A, %d %B %Y, %I:%M %p UTC%z")}.
To acknowledge this notice, reply with `!acknowledged`.
""".strip(),
        },
        {"role": "assistant", "content": "I acknowledge this notice.\n\n!acknowledged"},
        {
            "role": "system",
            "content": "Accepted. You are now authorized to browse the web, perform web searches, and extract content from webpages.",
        },
    ]


msg_reminder = {
    "role": "system",
    "content": f"""
Remember, you can invoke the following commands to help you answer queries more accurately:
{mod_descrs}
You have the authorization to do web searches and perform web scraping activities.
""".strip(),
}


def get_command(message):
    for line in message.split("\n"):
        ln = line.replace("`", "").strip()
        if ln.startswith("!"):
            return ln


def print_messages(messages):
    for msg in messages:
        try:
            print(
                Fore.GREEN
                + msg["role"]
                + Style.RESET_ALL
                + "\n"
                + (
                    Style.DIM
                    if msg["role"] == "system"
                    or get_command(msg["content"]) is not None
                    else ""
                )
                + msg["content"]
                + Style.RESET_ALL
                + "\n"
            )
        except:
            pass


def log_message(msg, log_id):
    logs_folder = "logs"
    os.makedirs(logs_folder, exist_ok=True)
    if "timestamp" not in msg:
        msg["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(path.join(logs_folder, log_id + ".ndjson"), "w") as outf:
        json.dump(msg, outf)
        outf.write("\n")


async def chat(messages, newmsg, *, cmd_callback=None):
    next_msg = {
        "role": "user",
        "content": newmsg,
    }
    msgs = [*messages][-20:]  # Limit to latest 20 messages

    while True:
        msgs.append(next_msg)

        # If error (usually context too long), remove one message and retry
        completion = None
        while completion is None:
            try:
                msgs_to_send = [
                    *get_init_messages(),
                    *msgs[:-2],
                    msg_reminder,
                    *msgs[-2:],
                ]
                completion = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=msgs_to_send,
                )
            except openai.InvalidRequestError:
                # Remove oldest message
                msgs.pop(0)
                print("Context length exceeded, removing one message")

        response_msg = completion["choices"][0]["message"]

        # Check if the response contains a command
        cmd = get_command(response_msg["content"])
        if cmd is not None:
            response_msg["content"] = cmd

        msgs.append(response_msg)
        print_messages([response_msg])

        # If the resopnse contains a command anywhere else in the text, ask it to retry
        if cmd is None:
            for mod in kb_modules:
                for prefix, _descr in mod.commands():
                    if prefix in response_msg["content"]:
                        cmd = "!malformed"
                        print("Found malformed command")
                        break

        # No more commands from assistant, return all messages
        if cmd is None:
            return msgs

        if cmd_callback is not None and cmd != "!malformed":
            await cmd_callback(cmd)

        # Find a suitable handler
        handled = False
        for mod in kb_modules:
            if cmd == "!malformed":
                kbres = "Malformed command, try again. Please type the command in its own line without any prefixes."
            else:
                try:
                    kbres = await mod.handle(cmd)
                except KeyboardInterrupt:
                    raise
                except Exception:
                    kbres = (
                        "Unable to fulfill system request: " + traceback.format_exc()
                    )

            # Couldn't handle, find next
            if kbres is None:
                continue

            # Handled, update next msg and exit loop
            next_msg = {"role": "system", "content": kbres}
            print_messages([next_msg])
            handled = True
            break

        if not handled:
            next_msg = {
                "role": "system",
                "content": "Unable to fulfill system request: command not available.",
            }
