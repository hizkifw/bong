import os
import requests
import json
import aiohttp
from . import webget, USER_AGENT

endpoint = os.getenv("SEARX_ENDPOINT")


async def query(params):
    query = params["query"]
    query = query.replace('"', "")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{endpoint}/search",
            params={"q": query, "format": "json"},
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-US,en;q=0.5",
                "Accept": "text/html",
            },
        ) as res:
            results = await res.text()

    try:
        results = json.loads(results)

        outstr = "Web search results:\n\n"

        if len(results["infoboxes"]) > 0:
            ib = results["infoboxes"][0]
            outstr += (
                f"""
{ib['infobox']}
{ib['id']}
{ib['content']}
""".strip()
                + "\n\n"
            )

        for n, result in enumerate(results["results"][:5]):
            if (
                "content" in result
                and result["content"] != ""
                and result["content"] is not None
            ):
                outstr += (
                    f"""
{n+1}. {result['title']}
\tURL: {result['url']}
\tExcerpt: {result['content']}
""".strip()
                    + "\n\n"
                )

        if webget.enabled():
            outstr += f"""
To get more information on a webpage, invoke the `{webget.prefix}<url>` command.
For example, `{webget.prefix}{results['results'][0]['url']}`
""".strip()
        return outstr.strip()
    except:
        return results if isinstance(results, str) else json.dumps(results)


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
    return endpoint is not None and endpoint != ""
