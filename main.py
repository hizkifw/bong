from chat import print_messages, init_messages, chat
from colorama import Fore, Style

if __name__ == "__main__":
    print_messages(init_messages[:2])

    messages = []
    while True:
        try:
            print(Fore.GREEN + "user" + Style.RESET_ALL)
            q = input("> ")
            print("")

            messages = chat(messages, q)
        except (EOFError, KeyboardInterrupt):
            break
