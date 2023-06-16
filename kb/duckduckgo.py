import trafilatura
import aiohttp
from . import webget, USER_AGENT


async def query(params):
    query = params["query"]
    query = query.replace('"', "")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-US,en;q=0.5",
                "Accept": "text/html",
            },
        ) as res:
            html = await res.text()
            visible_index = html.find("<!-- This is the visible part -->")
            html = html[visible_index:]

        summary = trafilatura.extract(html)
        return summary


def functions():
    return [
        {
            "name": "web_search",
            "description": "Search the web for up-to-date information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for.",
                    }
                },
                "required": ["query"],
            },
            "handler": query,
        }
    ]


def enabled():
    return True
