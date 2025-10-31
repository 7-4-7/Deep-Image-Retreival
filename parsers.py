import json
import re

def json_parser(json_str):
    try:
        cleaned = re.sub(r"^```[a-zA-Z]*\n?|```$", "", json_str.strip())
        data = json.loads(cleaned)
        return data
    except Exception as e:
        print("ERROR HAPPENED:", e)
        print("Raw text was:\n", json_str)
        return None
