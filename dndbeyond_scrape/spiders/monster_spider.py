import scrapy
import re
import logging
import json
from os import listdir
from os.path import isfile, join

# TODO make formally consts
msb = 'div.mon-stat-block__'
smsb = 'span.mon-stat-block__'
sizes = {"tiny": "T", "small": "S", "medium": "M", "large": "L", "huge": "H", "gargantuan": "G"}
alignments = {"chaotic": "C", "neutral": "N", "lawful": "L", "evil": "E", "good": "G", "unaligned": "U", "any": "A"}
stats = ['str', 'dex', 'con', 'int', 'wis', 'cha']

#this function is a garbage fire :) 
def set_traits(traits, entry, monster):
    i = 0
    while i < len(traits):
        if entry not in monster: 
            monster[entry] = []
        k = i
        entries = []
        if i + 1 < len(traits):
            j = i + 1
            entries = [traits[j]]
            # for melee attacks
            if j+1 < len(traits) and "weapon attack" in traits[j].lower(): 
                entries.append(traits[j+1])
                i += 1
                if j+2 < len(traits) and "Hit:" in traits[j+2] and "Hit:" not in traits[j+1]: 
                    entries.append(traits[j+2])
                    i += 1
                    if "Hit:" == traits[j+2] and j+3 < len(traits): 
                        entries.append(traits[j+3])
                        i += 1
            # otherwise go by length
            else: 
                while j < len(traits)-1: 
                    j += 1
                    if len(traits[j]) < 50: 
                        break
                    entries.append(traits[j])
                    i += 1
                    # if content is long it is probably a continuation
        if entries:
            monster[entry].append({'name': traits[k], 'entries': entries}) #really really fuzzy :\
        else: 
            monster[entry].append({'name': traits[k]})
        i += 2

class MonsterSpider(scrapy.Spider):
    name = "monsters"

    
    def start_requests(self):
        #urls = ['https://www.dndbeyond.com/homebrew/monsters?filter-rating=1&filter-search=&filter-type=0']
        lok = 'C:/Users/David/Documents/gpt-2-dnd/dndbeyond_scrape/cache'
        urls = ['file://' + join(lok, f) for f in listdir(lok) if isfile(join(lok, f))]
        # urls = [c for c in urls if "Archsorcerer" in c]
        # yield scrapy.Request(url='https://www.dndbeyond.com/monsters/301697-red-wizard-voskiir-vampire/more-info', callback=self.parse_monster)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_monster)

    def parse(self, response):
        monsters = response.css('div.list-row-monster-homebrew::attr(data-slug)').getall()
        # for m in monsters: 
        #    yield scrapy.Request(f'https://www.dndbeyond.com/monsters/{m}/more-info', callback = self.parse_monster)
        # n = response.css('li.b-pagination-item-next a::attr(href)').get()
        # yield scrapy.Request(f'https://www.dndbeyond.com/{n}')
    def parse_monster(self, response): 
        

        monster = {}
        name = re.sub(r'<.*?>', '', response.css(msb+'name').get())
        monster['name'] = re.sub(r'\s+', ' ', name)
        meta = response.css(msb+'meta::text').get()
        m, alignment = meta.split(", ")
        if "swarm" not in m:
            sp = m.split(" ")
            monster['type'], size = sp[1], sp[0]
            monster['size'] = sizes.get(size.lower())
        else: 
            sp = m.split(" ")
            mtype, size, swarmsize = sp[4], sp[0], sp[1] # size swarm of swarmsize mtype
            monster['type'] = {'type': mtype, 'swarmsize': sizes.get(swarmsize.lower())}
            monster['size'] = sizes.get(size.lower())
        monster['source'] = 'HBW' #homebrew
        monster['alignment'] = [alignments.get(a) for a in alignment.lower().split(" ") if a != "alignment"]

        ac, hp = [None, None], [None, None]
        speed = [None]
        for attribute in response.css(msb+'attribute'):
            label = attribute.css(smsb+'attribute-label::text').get()
            label = re.sub(r'\s+', ' ', label)
            value = attribute.css(smsb+'attribute-data-value::text').get()
            value = re.sub(r'\s+', ' ', value)
            extra = attribute.css(smsb+'attribute-data-extra::text').get()
            if extra:
                extra = re.sub(r'\s+', ' ', extra)
                
            if label == "Armor Class": 
                ac = {'ac': value, 'from': [extra]}
            elif label == "Hit Points": 
                hp = {'average': value, 'formula': extra}
            elif label == "Speed":
                speed = {}
                for s in value.split(", "):
                    sp = s.split(" ")
                    if sp[0] == '':
                        sp[0] = 'walk'
                    speed[sp[0]] = sp[1].replace("ft.", "")
        monster['ac'] = ac
        monster['hp'] = hp
        monster['speed'] = speed
        

        # TODO fix me and below
        for stat in stats: 
            monster[stat] = response.css('div.ability-block__stat--'+stat+' div.ability-block__data span.ability-block__score::text').get()
        
        for tidbit in response.css(msb+'tidbit'):
            label = tidbit.css(smsb+'tidbit-label::text').get()
            data = tidbit.css(smsb+'tidbit-data').get()
            data = re.sub(r'<.*?>', '', data) #remove hyperlinks
            data = re.sub(r'\s+', ' ', data).strip()
            if label == "Saving Throws":
                saves = [d.split(" ") for d in data.split(", ")]
                monster['save'] = {s[0]:s[1] for s in saves}
            elif label == "Skills":  
                skills = [d.split(" ") for d in data.split(", ")]
                monster['skill'] = {s[0]:s[1] for s in skills}
            elif label == "Damage Resistances":
                res = data.split("; ")
                if 'from' not in res[0]:
                    monster['resist'] = res[0].split(', ')
                else: 
                    res.append(res[0])
                if len(res) > 1:
                    if 'resist' in monster:
                        monster['resist'].append({"resist": res[1].split(' from')[0].split(', '), "note": "from " + res[1].split('from ')[1]})
                    else: 
                        monster['resist'] = [{"resist": res[1].split(' from')[0].split(', '), "note": "from " + res[1].split('from ')[1]}]
            elif label == "Damage Vulnerabilities": 
                monster['vulnerable'] = data.split(", ")
            elif label == "Damage Immunities": 
                imm = data.split("; ")
                if 'from' not in imm[0]:
                    monster['immune'] = imm[0].split(', ')
                else: 
                    imm.append(imm[0])
                if len(imm) > 1: 
                    if 'immune' in monster:
                        monster['immune'].append({"immune": imm[1].split(' from')[0].split(', '), "note": "from " + imm[1].split('from ')[1]})
                    else: 
                        monster['immune'] = [{"immune": imm[1].split(' from')[0].split(', '), "note": "from " + imm[1].split('from ')[1]}]
            elif label == "Condition Immunities": 
                monster['conditionImmune'] = data.split(', ')
            elif label == "Senses": 
                senses = data.split(', ')
                if len(senses) > 1:
                    monster['senses'] = senses[:-1]
                monster['passive'] = senses[-1].split(' ')[-1]
            elif label == "Languages":
                monster['languages'] = data.split(', ')
            elif label == "Challenge": 
                monster['cr'] = data.split(' ')[0]
        # TODO spellcasting, traits, actions
        for db in response.css(msb+'description-block'):
            heading = db.css(msb+'description-block-heading::text').get()
            content = db.css(msb+'description-block-content').get()
            content = re.sub(r'<a.*?>|</a>', ' ', content)
            content = re.sub(r'<span.*?>|</span>', ' ', content)
            content = re.sub(r'\s\s+', ' ', content)
            content = re.sub(r'<.*?>', '\n', content)
            content = [c.replace('\xa0', ' ') for c in content.split('\n') if c.strip() and not re.match('^\W+$', c)]
            if not heading: 
                #then, traits & spellcasting
                spellcaster = False
                if any("spellcasting" in c.lower() for c in content): 
                    spellcaster = True
                # this is all fuzzy because people do this differently and real NLP is beyond me
                if spellcaster: 
                    spells = []
                    traits = []
                    spellname = "spellcasting"
                    spellname_set = False
                    spelldesc = ""
                    for c in content: 
                        if "spellcasting ability" in c.lower(): 
                            spelldesc = c
                        elif "spellcasting" in c.lower():
                            if spellname_set: 
                                if spellname.lower() in ["spellcasting.", "spellcasting", "innate spellcasting", "innate spellcasting."]:
                                    traits.append(c)
                            else:
                                spellname = c
                                spellname_set = True
                        elif ("level" in c.lower() and "slot" in c.lower()) or ("at will" in c.lower() or "at-will" in c.lower() or ("/day" in c.lower() and "legendary" not in c.lower() and not any("slot" in sp for sp in spells))): 
                            spells.append(c)
                        else: 
                            if c[0] == '*': 
                                continue #just throw away this dang edge case >:^(
                            traits.append(c)
                    if "innate" not in spellname.lower() and not any(("at will" in spell.lower() and "cantrip" not in spell.lower()) for spell in spells): 
                        s = {}
                        for spell in spells: 
                            sp = spell.split(":")
                            if "cantrip" in sp[0].lower(): 
                                s["0"] = {"spells": [name for name in sp[1].split(', ')]}
                            else: 
                                if "/day" in spell.lower(): 
                                    traits.append(spell)
                                    continue
                                l = sp[0][0]
                                ns = sp[0].split('(')[1][0]
                                s[l] = {"slots": ns, "spells": [name for name in sp[1].split(', ')]}
                        monster['spellcasting'] = [{'name': spellname, 'headerEntries': spelldesc, "spells": s}]
                    else: 
                        will = []
                        daily = {}
                        for spell in spells: 
                            if "will" in spell.lower(): 
                                if len(spell.strip().split(":")) == 1 or spell.strip()[-1] == ":":
                                    ind = content.index(spell)+1
                                    if ind == len(content): 
                                        continue
                                    w = content[ind]
                                    will += w.split(", ")
                                    if w in traits:
                                        traits.remove(w)
                                else:
                                    will += spell.split(": ")[1].split(", ")
                            else: 
                                sp= spell.lower().split("/day each: ")
                                if len(sp) == 1: 
                                    sp = spell.lower().split("/day:")
                                n = sp[0][0]
                                if n == "3": 
                                    n = "3e"
                                if len(sp) == 1: 
                                    ind = content.index(spell)+1
                                    if ind == len(content): 
                                        continue
                                    d = content[ind]
                                    daily[n] = d.split(", ")
                                    if d in traits:
                                        traits.remove(d)
                                else: 
                                    daily[n] = sp[1].split(", ")
                        
                        monster['spellcasting'] = [{'name': spellname, 'headerEntries': spelldesc, "will": will, "daily": daily}]
                else: 
                    traits = content
                set_traits(traits, 'trait', monster)
            else: 
                if "reaction" in heading.lower(): 
                    set_traits(content, 'reaction', monster)
                elif "legendary" in heading.lower(): 
                    set_traits(content[1:], 'legendary', monster)
                elif "action" in heading.lower(): 
                    set_traits(content, 'action', monster)


        filename = 'dndbeyond.json'
        with open(filename, 'a') as f:
            f.write('<|startoftext|>\n')
            f.write(json.dumps(monster, indent=4))
            f.write('\n<|endoftext|>\n')
        with open('cache/'+monster['name']+'.html', 'wb') as f: 
            f.write(response.body)


        
