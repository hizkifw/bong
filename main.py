import os
import time

from colorama import Fore, Style
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

from kb import searx, wikipedia, wolfram

kb_modules = [mod for mod in [searx, wolfram, wikipedia] if mod.enabled()]
mod_descrs = "\n".join(
    ["\n".join(["""- "%s"\t%s""" % c for c in mod.commands()]) for mod in kb_modules]
)

init_messages = [
    {
        "role": "system",
        "content": f"""
You are Bong, an assistant with access to the Internet. You can invoke the following commands:
{mod_descrs}
Whenever possible, you must use these commands to derive your answer. Do not make any assumptions, or use your own knowledge as it may be out of date.
Knowledge cutoff: September 2021. Current date and time: {time.strftime("%A, %d %B %Y, %H:%M")}.
To acknowledge this notice, reply with !acknowledged.
""".strip(),
    },
    {"role": "assistant", "content": "!acknowledged"},
    {"role": "user", "content": "when was hoshimachi suisei's first album released?"},
    {
        "role": "assistant",
        "content": f"{searx.prefix}hoshimachi suisei first album release date",
    },
    {
        "role": "system",
        "content": f"""
Web search results:

1. Hoshimachi Suisei - Wikipedia
        URL: https://en.wikipedia.org/wiki/Hoshimachi_Suisei
        Excerpt: Additionally, her first album, "Still Still Stellar", was released on 29 September 2021, and peaked at 5th on the Oricon daily album ranking, ...

2. Hoshimachi Suisei/Discography - Virtual YouTuber Wiki
        URL: https://virtualyoutuber.fandom.com/wiki/Hoshimachi_Suisei/Discography
        Excerpt: "Michizure" (Live ver.) (みちづれ), 2023/02/17. Title, Date. " ...

3. Suisei announces her 1st full album, "Still Still Stellar", with 12 ...
        URL: https://www.reddit.com/r/Hololive/comments/og4x66/suisei_announces_her_1st_full_album_still_still/
        Excerpt: Suisei announces her 1st full album, "Still Still Stellar", with 12 songs in total, to be released on September 29th! ☄️. r/Hololive - Suisei announces ...

4. Still Still Stellar Hoshimachi Suisei CD Album - CDJapan
        URL: https://www.cdjapan.co.jp/product/HOLO-2
        Excerpt: Description. VTuber Hoshimachi Suisei to release the first full-length album with 12 tracks in total, including new one(s).

5. Hoshimachi Suisei - Hololive Fan Wiki
        URL: https://hololive.wiki/wiki/Hoshimachi_Suisei
        Excerpt: Her first original, "comet" was first released on November 22, 2018 and her second, "天球、彗星は夜を跨いで" on March 22, 2019.
""".strip(),
    },
    {
        "role": "assistant",
        "content": """Hoshimachi Suisei's first album, "Still Still Stellar" was released on September 29, 2021.""",
    },
]


def print_messages(messages):
    for msg in messages:
        print(
            Fore.GREEN
            + msg["role"]
            + Style.RESET_ALL
            + "\n"
            + (
                Style.DIM
                if msg["role"] == "system" or msg["content"].startswith("!")
                else ""
            )
            + msg["content"]
            + Style.RESET_ALL
            + "\n"
        )


def chat(messages, newmsg):
    next_msg = {
        "role": "user",
        "content": newmsg,
    }
    msgs = [*messages]

    while True:
        msgs.append(next_msg)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=msgs,
        )
        response_msg = completion["choices"][0]["message"]
        msgs.append(response_msg)
        print_messages([response_msg])
        response = response_msg["content"]

        # If any of the lines start with a !, ignore all other lines
        cmd = ""
        for line in response.split("\n"):
            if line.startswith("!"):
                cmd = line
                break

        # No more commands from assistant, return all messages
        if cmd == "":
            return msgs

        # Find a suitable handler
        handled = False
        for mod in kb_modules:
            kbres = mod.handle(cmd)

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


print_messages(init_messages[:2])

messages = [*init_messages]
while True:
    try:
        print(Fore.GREEN + "user" + Style.RESET_ALL)
        q = input("> ")
        print("")

        messages = chat(messages, q)
    except (EOFError, KeyboardInterrupt):
        break
