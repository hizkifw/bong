import requests
import trafilatura
import time


prefix = "!web get "

USER_AGENT = "BongBot/0.1 (+https://github.com/hizkifw/bong) requests/2.28.2"

# Substitute some websites for more scraper-friendly alternatives
URL_SUBSTITUTIONS = [
    ("https://twitter.com/", "https://nitter.net/"),
]


def query(url):
    for sub in URL_SUBSTITUTIONS:
        url = url.replace(*sub)

    # Handle YouTube URLs
    if (
        "https://youtu.be/" in url
        or "https://www.youtube.com/" in url
        or "https://youtube.com/" in url
    ):
        from yt_dlp import YoutubeDL

        with YoutubeDL(params={"quiet": True}) as dl:
            info = dl.extract_info(url, download=False)

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
        html = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-US,en;q=0.5",
                "Accept": "text/html",
            },
        ).content

        summary = trafilatura.extract(html)
    return "The following is an excerpt of the requested page:\n\n" + summary


def handle(cmd):
    if cmd.startswith(prefix):
        return query(cmd[len(prefix) :])


def commands():
    return [(f"{prefix}<url>", "Get the text contents of any web page.")]


def enabled():
    return True
