import json
import re

def json_parser(json_str, current, total_images):
    try:
        print("========="*5,"CAPTION RESPONSE [",current,"/", total_images,"] PARSED", "========="*5)
        data = json.loads(json_str)
        return data    
    except:
        print("ERROR HAPPENED")