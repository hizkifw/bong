import requests

USER_AGENT = "BongBot/0.1 (+https://github.com/hizkifw/bong) requests/2.28.2"

prefix_search = "!encyclopedia search "
prefix_get = "!encyclopedia get "


def search(query):
    # Search for the page
    search = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={"action": "opensearch", "search": query, "format": "json"},
        headers={"User-Agent": USER_AGENT},
    ).json()

    if len(search[3]) == 0:
        return f"""Search returned no results. You may retry with "{prefix_search}<query>"."""

    return (
        "The following pages were found:\n- "
        + "\n- ".join([u[len("https://en.wikipedia.org/wiki/") :] for u in search[3]])
        + f"""\nTo get the page contents, respond with "{prefix_get}<page_name>". If there are no matches, you may retry with "{prefix_search}<query>"."""
    )


def get_page(query):
    page = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "prop": "extracts",
            "titles": query,
            "exintro": "true",
            "explaintext": "true",
            "format": "json",
        },
        headers={"User-Agent": USER_AGENT},
    ).json()

    pages = page["query"]["pages"]
    return pages[next(iter(pages))]["extract"]


def handle(cmd):
    if cmd.startswith(prefix_search):
        return search(cmd[len(prefix_search) :])
    elif cmd.startswith(prefix_get):
        return get_page(cmd[len(prefix_get) :])


def commands():
    return [(f"{prefix_search}<query>", "Search for an article in an encyclopedia.")]


def enabled():
    return True
