#!/usr/bin/python
import json
import sys
from jsonschema import validate
from jsonschema import ValidationError

# quick and dirty schema validation check
if __name__ == "__main__":
    schema = json.load(open(sys.argv[1]))
    file = json.load(open(sys.argv[2]))
    try:
        #print(schema)
        #print(file)
        validate(file, schema)
        print(True)
    except ValidationError as err:
        print("Schema Validation Error: {0}\n".format(err))
        print(False)