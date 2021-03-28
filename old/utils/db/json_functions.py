import json
try:
    from jsonpath_rw import jsonpath, parse
except:
    pass


def json_extract(json_doc: str, path: str):
    json_doc = json.loads(json_doc)
    jsonpath_expr = parse(path)

    matched = []
    for match in jsonpath_expr.find(json_doc):
        matched.append(match.value)
    if len(matched) == 1:
        return str(matched[0])
    elif len(matched) == 0:
        return None
    else:
        return str(matched)
