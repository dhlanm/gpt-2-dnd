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

class MonsterSpider(scrapy.Spider):
    name = "monsters"

    
    def start_requests(self):
        urls = [
                'https://www.dndbeyond.com/homebrew/monsters?filter-rating=1&filter-search=&filter-type=0'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        monsters = response.css('div.list-row-monster-homebrew::attr(data-slug)').getall()
        for m in monsters: 
            yield scrapy.Request(f'https://www.dndbeyond.com/monsters/{m}/more-info', callback = self.parse_monster)
            break
        
    def parse_monster(self, response): 
        

        monster = {}
        monster['name'] = re.sub(r'<.*?>|\s+', '', response.css(msb+'name').get())
        meta = response.css(msb+'meta::text').get()
        m, alignment = meta.split(", ")
        sp = m.split(" ")
        #TODO handle swarms
        monster['type'], size = sp[1], sp[0]
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
            monster[stat] = attribute.css('div.ability-block__stat--'+stat+' div.ability-block__data span.ability-block__score::text').get()
        
        for tidbit in response.css(msb+'tidbit'):
            label = attribute.css(smsb+'titbit-label::text').get()
            data = attribute.css(smsb+'titbit-data::text').get()
            logging.warning(tidbit)
            logging.warning(monster)
            logging.warning(label, data)
            data = re.sub(r'<.*?>', '', data) #remove hyperlinks
            if label == "Saving Throws":
                saves = [d.split(" ") for d in data.split(", ")]
                monster['save'] = {s[0]:s[1] for s in saves}
            elif label == "Skills":  
                skills = [d.split(" ") for d in data.split(", ")]
                monster['skill'] = {s[0]:s[1] for s in saves}
            elif label == "Damage Resistances":
                res = data.split("; ")
                if 'from' not in res[0]:
                    monster['resist'] = res[0].split(', ')
                else: 
                    res.append(res)
                if len(res) > 1: 
                    monster['resist'].append({"resist": res[1].split(' from')[0].split(', '), "note": "from " + res[1].split('from ')[1]})
            elif label == "Damage Vulnerabilities": 
                monster['vulnerable'] = data.split(", ")
            elif label == "Damage Immunities": 
                imm = data.split("; ")
                if 'from' not in imm[0]:
                    monster['immune'] = imm[0].split(', ')
                else: 
                    imm.append(imm)
                if len(imm) > 1: 
                    monster['immune'].append({"immune": imm[1].split(' from')[0].split(', '), "note": "from " + imm[1].split('from ')[1]})
            elif label == "Condition Immunities": 
                monster['conditionImmune'] = data.split(', ')
            elif label == "Senses": 
                senses = data.split(', ')
                monster['senses'] = senses[:-1]
                monster['passive'] = senses[-1].split(' ')[:-1]
            elif label == "Languages":
                monster['languages'] = data.split(', ')
            elif label == "Challenge": 
                monster['cr'] = data.split(' ')[0]
        # TODO spellcasting, traits, actions
        filename = 'dnd.html'
        with open(filename, 'w') as f:
            f.write(json.dumps(monster))


        
