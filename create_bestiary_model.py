import os
import sys
import json


def main():
    outfile = 'bestiary.json'
    
    if len(sys.argv) > 1:
        outfile = sys.argv[1]
    bes_files = os.listdir('bestiary') 
    monster = []
    for b in bes_files:
        if '-' in b and 'fluff' not in b and 'bestiary' in b: 
            with open('bestiary/'+b, 'r') as fb:
                cont = json.loads(fb.read())
                monster += cont['monster']

    with open(outfile, 'w') as outp:
        format_kludge = []
        for m in monster:
            format_kludge.append(m)
            format_kludge.append('["wowauniquestring"]')

        out_text = json.dumps(monster, indent=4)
        out_text.replace('["wowauniquestring"]', '\n\n') 
        # add an extra line break between each monster to hopefully try to convince gpt-2 of something
        outp.write(out_text)

if __name__ == '__main__': main()
