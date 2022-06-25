import re
import sys

substpat = re.compile(r"\s*<!-- SUBST (.*) -->\s*")

for line in sys.stdin:
    if substpat.match(line):
        srcfilename = substpat.sub(r"src/inc/\1", line)
        with open(srcfilename, "r", encoding="utf-8") as srcfile:
            for line in srcfile:
                print(line, end="")
    else:
        print(line, end="")
