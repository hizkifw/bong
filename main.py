import asyncio
from chat import print_messages, get_init_messages, chat
from colorama import Fore, Style


async def main():
    print_messages(get_init_messages()[:2])

    messages = []
    while True:
        try:
            print(Fore.GREEN + "user" + Style.RESET_ALL)
            q = input("> ")
            print("")

            messages = await chat(messages, q)
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
