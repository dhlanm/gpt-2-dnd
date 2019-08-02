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
                for m in cont['monster']:
                    if "_copy" in m: 
                        continue
                    m = {k:m[k] for k in m if "Tags" not in k}
                    m.pop("soundClip", None)
                    action, trait = "", ""
                    trait = m.pop("trait", None)
                    action = m.pop("action", None) 
                    if trait:
                        m["name_pre_trait"] = m["name"]
                        m["trait"] = trait
                    if action:
                        m["name_pre_action"] = m["name"]
                        m["action"] = action
                    # this is sort of cheating, but it should carry over the name context in longer entries better
                    # it's also a bit silly in the sense of order enforcing, but hey what can you do 
                    # TODO maybe add another one since these show up fairly late?? 
                    monster.append(m)
    print(f"Total number of entries: {len(monster)}")
    with open(outfile, 'w') as outp:
        out_text = [json.dumps(m, indent=4) for m in monster]
        out_text = '\n<|endoftext|>\n<|startoftext|>\n'.join(out_text)
        out_text = '<|startoftext|>\n' + out_text + '\n<|endoftext|>'
        outp.write(out_text)

if __name__ == '__main__': main()
