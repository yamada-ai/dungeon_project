import json
import sys
import itertools

with open(sys.argv[1], "r") as f:
    data = json.load(f)

height = len(data["cellMap"])
width = len(data["cellMap"][0])
data["height"] = height
data["width"] = width
data["cellMap"] = list(itertools.chain.from_iterable(data["cellMap"]))

with open(sys.argv[2], "w") as f:
    json.dump(data, f)

