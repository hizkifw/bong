# bong

Giving ChatGPT access to the web. The name is definitely not related to any
search engine companies.

![screenshot](https://raw.githubusercontent.com/hizkifw/bong/main/.github/images/screenshot.png)

## Features

Bong is capable of surfing the web. Currently, it can:

- Search using [SearX](https://github.com/searx/searx)
- Query WolframAlpha for math
- Get the contents of Wikipedia articles
- Get a summary of any arbitrary URL
  - YouTube videos via [yt-dlp](https://github.com/yt-dlp/yt-dlp/)
  - Twitter via [Nitter](https://github.com/zedeus/nitter)
  - Other websites summarized using [trafilatura](https://github.com/adbar/trafilatura)

## Set up

You need:

- [OpenAI API Key](https://platform.openai.com/)
- [WolframAlpha API key](https://products.wolframalpha.com/api/) (free for first 2,000 queries per month)

Copy the `.envrc.example` file to `.envrc`, and fill in the fields. You can use
[`direnv`](https://direnv.net/) to automatically populate your environment, or
source the file directly.

```sh
# Create venv
python -m venv venv

# Activate venv
source ./venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Load environment variables
source ./.envrc

# Launch CLI
python main.py
```
