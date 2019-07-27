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
        out_text = [json.dumps(m, indent=4) for m in monster]
        out_text = '\n<|endoftext|>\n<|startoftext|>\n'.join(out_text)
        out_text = '<|startoftext|>\n' + out_text + '\n<|endoftext|>'
        outp.write(out_text)

if __name__ == '__main__': main()
