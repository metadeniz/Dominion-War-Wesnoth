"""Set the br= brightness factor in the model URL of roster units: python3 -I setbr.py roster.json id=factor ..."""
import json, sys, re
R = json.load(open(sys.argv[1])); want = dict(a.split('=') for a in sys.argv[2:])
for fac in R:
    for u in fac['units']:
        if u['id'] in want:
            f = re.sub(r'&br=[0-9.]+', '', u['f']); u['f'] = f + '&br=' + want[u['id']]; print(u['id'], u['f'])
json.dump(R, open(sys.argv[1], 'w'), indent=1)
