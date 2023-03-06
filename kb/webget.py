import requests
import aiohttp
import trafilatura
import time
from . import USER_AGENT

prefix = "!web get "

# Substitute some websites for more scraper-friendly alternatives
URL_SUBSTITUTIONS = [
    ("https://twitter.com/", "https://nitter.net/"),
]


async def query(url):
    # Strip out anything after a space
    url = url.split(" ")[0]

    for sub in URL_SUBSTITUTIONS:
        url = url.replace(*sub)

    # Handle YouTube URLs
    if (
        "https://youtu.be/" in url
        or "https://www.youtube.com/" in url
        or "https://youtube.com/" in url
    ):
        from yt_dlp import YoutubeDL

        with YoutubeDL(
            params={
                "quiet": False,
                "extract_flat": True,
                "playlist_items": "1:10",
            }
        ) as dl:
            info = dl.extract_info(url, download=False)

        if info["_type"] == "playlist":
            playlist_entries = "\n".join(
                [
                    f"""
- Title: {entry['title']}
  URL: {entry['webpage_url'] if 'webpage_url' in entry else entry['url']}
""".strip()
                    for entry in info["entries"]
                ]
            )

            quoted_descr = "> " + info["description"].strip().replace("\n", "\n> ")

            summary = f"""
YouTube Playlist
Title: {info['title']}
Channel: {info['channel']}
Tags: {", ".join(info['tags'])}
Description:
{quoted_descr}

Entries:
{playlist_entries}

For more information on an entry, invoke the `{prefix.strip()}` command on the entry's URL.
""".strip()
        else:
            summary = f"""
YouTube Video
Title: {info['title']}
Channel: {info['channel']}
Upload date: {info['upload_date']}
Categories: {", ".join(info['categories'])}
View count: {info['view_count']}
Duration: {time.strftime('%H:%M:%S', time.gmtime(info['duration']))}
Description:
{info['description']}
""".strip()

    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept": "text/html",
                },
            ) as res:
                html = await res.text()

        summary = trafilatura.extract(html)
    return "The following is an excerpt of the requested page:\n\n" + summary


async def handle(cmd):
    if cmd.startswith(prefix):
        return await query(cmd[len(prefix) :])


def commands():
    return [(f"{prefix}<url>", "Safely get the text contents of any web page.")]


def enabled():
    return True
