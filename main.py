import os
import time

from colorama import Fore, Style
import openai
from kb import wikipedia, wolfram

kb_handlers = [wikipedia.handle, wolfram.handle]

openai.api_key = os.getenv("OPENAI_API_KEY")

init_messages = [
    {
        "role": "system",
        "content": f"""
You are Bong, a helpful assistant with access to external resources. To perform arithmetic or solve equations on WolframAlpha, respond with "{wolfram.prefix}<query>". To search an encyclopedia for factual information, respond with "{wikipedia.prefix_search}<query>".
Whenever possible, you must use these external resources. Do not use your own knowledge as it may be out of date.
Knowledge cutoff: September 2021. Current date and time: {time.strftime("%A, %d %B %Y, %H:%M")}. 
""".strip(),
    },
    {"role": "user", "content": "Who won the world series in 2020?"},
    {
        "role": "assistant",
        "content": f"{wikipedia.prefix_search}2020 world series",
    },
    {
        "role": "system",
        "content": f"""
The following pages were found:
- 2020_World_Series
- 2020_World_Series_of_Poker
- 2020_World_Series_of_Poker_Online
- 2020_World_Series_of_Darts
- 2020_World_Series_of_Darts_Finals
- 2022_World_Series
- 2021_World_Series
- 2022_World_Series_of_Poker_results
- 2021_World_Series_of_Poker_results
- 2002_World_Series
To get the page contents, respond with "{wikipedia.prefix_get}<page_name>". If there are no matches, you may retry with "{wikipedia.prefix_search}<query>".
""".strip(),
    },
    {"role": "assistant", "content": f"{wikipedia.prefix_get}2020_World_Series"},
    {
        "role": "system",
        "content": """
The 2020 World Series was the championship series of Major League Baseball's 2020 season. The 116th World Series was a best-of-seven-playoff between the American League (AL) champion Tampa Bay Rays and the National League (NL) champion Los Angeles Dodgers. The Dodgers defeated the Rays to win the series in six games for their first championship since 1988.
Due to the COVID-19 pandemic, the entire series was played at Globe Life Field in Arlington, Texas, from October 20 to October 27 with the ballpark's seating capacity limited to 25 percent (11,500 fans). The pandemic resulted in the regular season being reduced to 60 games, and the postseason being held at neutral sites instead of at teams' home stadiums. Thus, this was the first World Series to be played at a neutral site, as well as the first since 1944 to be held at only one ballpark and the first since 1993 to be played entirely on artificial turf. It was also the first World Series since 1984 to use the designated hitter for all games. With 2020 being the inaugural season for Globe Life Field, it became the first ballpark to host the World Series in its first year since Yankee Stadium in 2009.
Despite not playing on their home field, the Dodgers were still designated as having home-field advantage in the series with the better regular season record. Los Angeles and Tampa Bay alternated victories during the first four games of the series before the Dodgers won both Game 5 and 6, becoming the first designated home team to win the World Series since the 2013 edition. Los Angeles shortstop Corey Seager was named the World Series Most Valuable Player (MVP) after batting 8-for-20 (.400) with two home runs, five runs batted in, and an on-base percentage of .556.
""".strip(),
    },
    {
        "role": "assistant",
        "content": "According to an encyclopedia, the 2020 World Series was won by Los Angeles Dodgers.",
    },
]


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
        response = completion["choices"][0]["message"]["content"]
        msgs.append({"role": "assistant", "content": response})

        # If any of the lines start with a !, ignore all other lines
        cmd = ""
        for line in response.split("\n"):
            if line.startswith("!"):
                cmd = line
                print(Style.DIM + "Handling command:", cmd, Style.RESET_ALL)
                break

        # No more commands from assistant, return all messages
        if cmd == "":
            return msgs

        # Find a suitable handler
        handled = False
        for handler in kb_handlers:
            kbres = handler(cmd)

            # Couldn't handle, find next
            if kbres is None:
                continue

            # Handled, update next msg and exit loop
            next_msg = {"role": "system", "content": kbres}
            handled = True
            break

        if not handled:
            next_msg = {
                "role": "system",
                "content": "Unable to fulfill system request: command not available.",
            }


messages = [*init_messages]
while True:
    try:
        q = input("> ")
        messages = chat(messages, q)

        for msg in messages[len(init_messages) :]:
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
    except (EOFError, KeyboardInterrupt):
        break
