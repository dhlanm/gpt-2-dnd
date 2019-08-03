import json
from collections import OrderedDict

def main():
    monsters = []
    with open('dndbeyond_scrape/dndbeyond.json') as f: 
        line = f.readline()
        while line: 
            if '<|startoftext|>' in line: 
                monster = ''
            elif '<|endoftext|>' in line:
                mon = OrderedDict(json.loads(monster))
                name = mon['name'] 
                monster = OrderedDict()
                for k in mon: 
                    if "Tags" in k:
                        continue
                    if "spellcasting" in k: 
                        monster["name_pre_spells"] = name
                    elif "action" in k: 
                        monster["name_pre_action"] = name
                    elif "trait" in k: 
                        monster["name_pre_trait"] = name
                    monster[k] = mon[k]
                    if k == "cha": 
                        monster["name_post_stats"] = name

                name = monster.pop("name")
                monster["monster_name"] = name
                monster.move_to_end("monster_name", last=False)
               
                monsters.append(monster)
            else: 
                monster += line
            line = f.readline()

    with open('homebrew.json', 'w') as outp:
        out_text = [json.dumps(m, indent=4) for m in monsters]
        out_text = '\n<|endoftext|>\n<|startoftext|>\n'.join(out_text)
        out_text = '<|startoftext|>\n' + out_text + '\n<|endoftext|>'
        outp.write(out_text)

if __name__ == '__main__': main()


    
