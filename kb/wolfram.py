import wolframalpha
import os

api_key = os.getenv("WOLFRAMALPHA_API_KEY")
wc = wolframalpha.Client(api_key)


def parse_wolfram(res):
    plaintext = ""
    for p in res.pod:
        plaintext += p["@title"] + ":\n"
        subpods = p["subpod"] if isinstance(p["subpod"], list) else [p["subpod"]]
        for subpod in subpods:
            if subpod["plaintext"] is not None:
                plaintext += subpod["plaintext"] + "\n\n"
            else:
                plaintext += "(no plaintext data)\n\n"
    return plaintext.strip()


async def query(params):
    query = params["query"]
    try:
        res = wc.query(query)
        if "didyoumeans" in res:
            closest_query = res["didyoumeans"]["didyoumean"][0]["#text"]
            return parse_wolfram(wc.query(closest_query))

        return parse_wolfram(res)
    except:
        return "Error querying information"


def functions():
    return [
        {
            "name": "wolfram_alpha",
            "description": "Query Wolfram Alpha for mathematical computation and factual information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The mathematical problem to solve or the factual information to query.",
                    }
                },
                "required": ["query"],
            },
            "handler": query,
        }
    ]


def enabled():
    return api_key is not None and api_key != ""
