# bong

Giving ChatGPT access to the web. The name is definitely not related to any
search engine companies.

![screenshot](https://raw.githubusercontent.com/hizkifw/bong/main/.github/images/screenshot.png)

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

# Launch
python main.py
```
