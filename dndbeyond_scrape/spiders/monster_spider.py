import scrapy
import re
import logging
import json

# TODO make formally consts
msb = 'div.mon-stat-block__'
smsb = 'span.mon-stat-block__'
sizes = {"tiny": "T", "small": "S", "medium": "M", "large": "L", "huge": "H", "gargantuan": "G"}
alignments = {"chaotic": "C", "neutral": "N", "lawful": "L", "evil": "E", "good": "G", "unaligned": "U", "any": "A"}
stats = ['str', 'dex', 'con', 'int', 'wis', 'cha']

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
        urls = [
                'https://www.dndbeyond.com/homebrew/monsters?filter-rating=1&filter-search=&filter-type=0'
        ]
        # yield scrapy.Request(url='https://www.dndbeyond.com/monsters/301697-red-wizard-voskiir-vampire/more-info', callback=self.parse_monster)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        monsters = response.css('div.list-row-monster-homebrew::attr(data-slug)').getall()
        for m in monsters: 
            yield scrapy.Request(f'https://www.dndbeyond.com/monsters/{m}/more-info', callback = self.parse_monster)
        n = response.css('li.b-pagination-item-next a::attr(href)').get()
        yield scrapy.Request(f'https://www.dndbeyond.com/{n}')
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
            content = re.sub(r'<a.*?>|</a>', '', content)
            content = re.sub(r'<span.*?>|</span>', '', content)
            content = re.sub(r'<.*?>', '\n', content)
            content = [c.replace('\xa0', '') for c in content.split('\n') if c.strip() and not re.match('^\W+$', c)]

            if not heading: 
                #then, traits & spellcasting
                spellcaster = False
                if "spellcasting" in (c.lower() for c in content): 
                    spellcaster = True
                # this is all fuzzy because people do this differently and real NLP is beyond me
                if spellcaster: 
                    spells = []
                    traits = []
                    spellname = "spellcasting"
                    spelldesc = ""
                    for c in content: 
                        if "spellcasting ability" in c.lower(): 
                            spelldesc = c
                        elif "spellcasting" in c.lower():
                            spellname = c
                        elif ("level" in c.lower() and "slot" in c.lower()) or ("at will" in c.lower() or ("/day" in c.lower() and "legendary" not in c.lower())): 
                            spells.append(c)
                        else: 
                            if c[0] == '*': 
                                continue #just throw away this dang edge case >:^(
                            traits.append(c)
                    if "innate" not in spellname: 
                        s = {}
                        for spell in spells: 
                            sp = spell.split(":")
                            if "cantrip" in sp[0].lower(): 
                                s["0"] = {"spells": [f'(@spell {name})' for name in sp[1].split(', ')]}
                            else: 
                                l = sp[0][0]
                                ns = sp[0].split('(')[1][0]
                                s[l] = {"slots": ns, "spells": [f'(@spell {name})' for name in sp[1].split(', ')]}
                        monster['spellcasting'] = [{'name': spellname, 'headerEntries': spelldesc, "spells": s}]
                    else: 
                        will = []
                        daily = {}
                        for spell in spells: 
                            if "will" in spell.lower(): 
                                will += spell.split(": ")[1].split(", ")
                            else: 
                                sp= spell.split("/day: ")
                                n = sp[0][0]
                                if n == "3":
                                    n = "3e"
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


        
