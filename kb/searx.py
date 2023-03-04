import os
import requests
import json
from . import webget

prefix = "!search "
endpoint = os.getenv("SEARX_ENDPOINT")

USER_AGENT = "BongBot/0.1 (+https://github.com/hizkifw/bong) requests/2.28.2"


def query(query):
    results = requests.get(
        f"{endpoint}/search",
        params={"q": query, "format": "json"},
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.5",
            "Accept": "text/html",
        },
    ).text

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
        return results


def handle(cmd):
    if cmd.startswith(prefix):
        return query(cmd[len(prefix) :])


def commands():
    return [(f"{prefix}<query>", "Perform a web search for up-to-date information.")]


def enabled():
    return endpoint is not None and endpoint != ""
