import os
import sys
import json
from collections import OrderedDict

def main():
    outfile = 'bestiary.json'
    
    if len(sys.argv) > 1:
        outfile = sys.argv[1]
    bes_files = os.listdir('bestiary') 
    monsters = []
    for b in bes_files:
        if '-' in b and 'fluff' not in b and 'bestiary' in b: 
            with open('bestiary/'+b, 'r') as fb:
                cont = json.loads(fb.read())
                for monster in cont['monster']:
                    if "_copy" in monster: 
                        continue
                    m = OrderedDict()
                    name = monster["name"]
                    for k in monster: 
                        if "Tags" in k:
                            continue
                        if "spellcasting" in k: 
                            m["name_pre_spells"] = name
                        elif "action" in k: 
                            m["name_pre_action"] = name
                        elif "trait" in k: 
                            m["name_pre_trait"] = name
                        m[k] = monster[k]
                        if k == "cha": 
                            m["name_post_stats"] = name
                    m = OrderedDict(m)
                    name = m.pop("name")
                    m["monster_name"] = name
                    m.move_to_end("monster_name", last=False)
                    m.pop("soundClip", None)
                    m.pop("otherSources", None)
                    m.pop("legendaryGroup", None)
                    # this is sort of cheating, but it should carry over the name context in longer entries better
                    # it's also a bit silly in the sense of order enforcing, but hey what can you do 
                    # TODO maybe add another one since these show up fairly late?? 
                    monsters.append(m)
    print(f"Total number of entries: {len(monsters)}")
    with open(outfile, 'w') as outp:
        out_text = [json.dumps(m, indent=4) for m in monsters]
        out_text = '\n<|endoftext|>\n<|startoftext|>\n'.join(out_text)
        out_text = '<|startoftext|>\n' + out_text + '\n<|endoftext|>'
        outp.write(out_text)

if __name__ == '__main__': main()
