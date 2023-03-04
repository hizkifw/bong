import wolframalpha
import os

wc = wolframalpha.Client(os.getenv("WOLFRAMALPHA_API_KEY"))

prefix = "!wolfram "


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


def query(query):
    try:
        res = wc.query(query)
        if "didyoumeans" in res:
            closest_query = res["didyoumeans"]["didyoumean"][0]["#text"]
            return parse_wolfram(wc.query(closest_query))

        return parse_wolfram(res)
    except:
        return "Error querying information"


def handle(cmd):
    if cmd.startswith(prefix):
        return query(cmd[len(prefix) :])
