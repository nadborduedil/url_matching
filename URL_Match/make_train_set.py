import sys
import json

_, urls_path, output_path = sys.argv

with open(urls_path, "rb") as urls_file, open(output_path, "wb") as output:
    for line in urls_file:
        org, name, urls = json.loads(line)
        print name
        for url in urls:
            output.write("%s\t%s\t%s\t\n" % (org, name, json.dumps(url)))
