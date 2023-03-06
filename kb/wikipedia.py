import aiohttp
from . import USER_AGENT

prefix_search = "!wikipedia search "
prefix_get = "!wikipedia get "


async def search(query):
    # Search for the page
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "opensearch", "search": query, "format": "json"},
            headers={"User-Agent": USER_AGENT},
        ) as res:
            search = await res.json()

    if len(search[3]) == 0:
        return f"""Search returned no results. You may retry with "{prefix_search}<query>"."""

    return (
        "The following pages were found:\n- "
        + "\n- ".join([u[len("https://en.wikipedia.org/wiki/") :] for u in search[3]])
        + f"""\nTo get the page contents, respond with "{prefix_get}<page_name>". If there are no matches, you may retry with "{prefix_search}<query>"."""
    )


async def get_page(query):
    async with aiohttp.ClientSession() as session:
        async with session.get(
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
        ) as res:
            page = await res.json()

    pages = page["query"]["pages"]
    return pages[next(iter(pages))]["extract"]


async def handle(cmd):
    if cmd.startswith(prefix_search):
        return await search(cmd[len(prefix_search) :])
    elif cmd.startswith(prefix_get):
        return await get_page(cmd[len(prefix_get) :])


def commands():
    return [(f"{prefix_search}<query>", "Search for an article in Wikipedia.")]


def enabled():
    return True
