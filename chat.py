import os
import time
from os import path
import datetime
import traceback
import json

from colorama import Fore, Style
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

from kb import duckduckgo, wikipedia, wolfram, webget

kb_modules = [mod for mod in [duckduckgo, webget, wolfram] if mod.enabled()]
functions = [
    {k: f[k] for k in f if k != "handler"}
    for mod in kb_modules
    for f in mod.functions()
]
function_handlers = {
    f["name"]: f["handler"]
    for mod in kb_modules
    for f in mod.functions()
    if "handler" in f
}


def get_init_messages():
    return [
        {
            "role": "system",
            "content": f"""
                Your name is Bong. You are a language model with access to the Internet. Knowledge cutoff: September 2021. Current date and time: {time.strftime("%A, %d %B %Y, %I:%M %p UTC%z")}.
            """.strip(),
        },
    ]


def print_messages(messages):
    for msg in messages:
        try:
            print(
                Fore.GREEN
                + msg["role"]
                + Style.RESET_ALL
                + "\n"
                + (Style.DIM if msg["role"] == "system" else "")
                + msg["content"]
                + Style.RESET_ALL
                + "\n"
            )
        except:
            pass


def log_message(msg, log_id):
    if log_id is None:
        return

    # Copy the message object
    msg = json.loads(json.dumps(msg))

    logs_folder = "logs"
    os.makedirs(logs_folder, exist_ok=True)
    if "timestamp" not in msg:
        msg["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(path.join(logs_folder, log_id + ".ndjson"), "a") as outf:
        json.dump(msg, outf)
        outf.write("\n")


async def chat(messages, newmsg, *, cmd_callback=None, log_id=None):
    next_msg = {
        "role": "user",
        "content": newmsg,
    }
    msgs = [*messages][-20:]  # Limit to latest 20 messages

    while True:
        msgs.append(next_msg)
        log_message(next_msg, log_id)

        # If error (usually context too long), remove one message and retry
        completion = None
        while completion is None:
            try:
                msgs_to_send = [
                    *get_init_messages(),
                    *msgs,
                ]
                completion = await openai.ChatCompletion.acreate(
                    model="gpt-3.5-turbo-0613",
                    messages=msgs_to_send,
                    functions=functions,
                )
            except openai.InvalidRequestError:
                # Remove oldest message
                msgs.pop(0)
                print("Context length exceeded, removing one message")

        response_msg = completion["choices"][0]["message"]

        # Check if the response contains a command
        fc = None
        if "function_call" in response_msg:
            fc = response_msg["function_call"]
            if fc["name"] in function_handlers:
                response_msg["content"] = "!" + fc["name"] + " " + fc["arguments"]

        msgs.append(response_msg)
        print_messages([response_msg])
        log_message(response_msg, log_id)

        # No more commands from assistant, return all messages
        if fc is None:
            return msgs

        if cmd_callback is not None:
            await cmd_callback(response_msg["content"])

        # Handle the command
        try:
            kbres = await function_handlers[fc["name"]](json.loads(fc["arguments"]))
        except KeyboardInterrupt:
            raise
        except Exception:
            kbres = "Error executing command: " + traceback.format_exc()

        # Handled, update next msg and exit loop
        next_msg = {"role": "system", "content": kbres}
        print_messages([next_msg])
