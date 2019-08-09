from bs4 import BeautifulSoup as Soup
import json

sizes = {"T": "Tiny", "S": "Small", "M": "Medium", "L": "Large", "H": "Huge", "G": "Gargantuan"}
align = {"C": "chaotic", "N": "neutral", "L": "lawful", "E": "evil", "G": "good", "U": "unaligned", "A": "any alignment"}
infoblock = {"save": "Saving Throws", "skill": "Skills", "vulnerable": "Damage Vulnerabilities", "resist": "Damage Resistances", "immune": "Damage Immunities", "conditionImmune": "Condition Immunities", "senses": "Senses", "languages": "Languages", "cr": "Challenge"}
actiontypes = {"trait": "Traits (should not appear)", "action": "Actions", "reaction": "Reactions", "legendary": "Legendary Actions"} 

def get_type(monster):
    if 'type' not in monster: 
        return None
    if type(monster['type']) is str: 
        return monster['type']
    if 'swarmSize' in monster['type'] and 'tags' not in monster['type']:
        return monster['type']['type']
    tags = []
    if 'tags' not in monster['type']: 
        print('weird typestring! ' + str(monster['type']))
        return monster['type'].get('type')
    for tag in monster['type']['tags']:
        if type(tag) is str:
            tags.append(tag)
        else: 
            tags.append(tag.get('prefix', '') + ' ' + tag.get('tag', ''))
    return monster['type']['type'] + f"({', '.join(tags)})"

def get_ac(monster): 
    acstring = ""
    if 'ac' not in monster: 
        return None
    ac = monster.get('ac')
    if type(ac[0]) is str or type(ac[0]) is int: 
        acstring += str(ac[0])
    else: 
        acstring += f"{ac[0]['ac']} ({', '.join(ac[0].get('from', [ac[0].get('condition', '')]))})"
    if len(ac) > 1: 
        acstring += f" ({ac[1]['ac']} {ac[1].get('condition', '')})"
    return acstring

def load(monster):
    if type(monster) == str:
        monster = json.loads(monster)
    with open('statblock.html', 'r') as f:
        # soup = Soup(f.read(), "html5lib")
        stats = Soup('', 'html.parser')#soup.find('stat-block')
        if 'type' in monster and 'swarmSize' in monster['type']: 
            ch = Soup(f'''<creature-heading>
                        <h1>{monster['monster_name']}</h1>
                        <h2>{sizes.get(monster.get('size'))} swarm of {sizes.get(monster['type']['swarmSize'])} {get_type(monster)}s, {" ".join([align.get(a) for a in monster.get('alignment', [])])}</h2>
                  ''', "html.parser")
        else:
            ch = Soup(f'''<creature-heading>
                        <h1>{monster['monster_name']}</h1>
                        <h2>{sizes.get(monster.get('size'))} {get_type(monster)}, {" ".join([align.get(a, '') for a in monster.get('alignment', [])])}</h2>
                  ''', "html.parser")
        stats.append(ch)
        
        ts = f'''<top-stats>
                    <property-line>
                      <h4>Armor Class</h4>
                      <p>{get_ac(monster)}</p>
                    </property-line>
                    <property-line>
                      <h4>Hit Points</h4>
                      <p>{monster.get('hp', {'average': None}).get('average')} ({monster.get('hp', {'formula': None}).get('formula')})</p>
                    </property-line>
                    <property-line>
                      <h4>Speed</h4>
                      <p>{', '.join([s + " " + str(monster['speed'][s]) + "ft" if s != "walk" else str(monster['speed'][s]) + "ft" for s in monster['speed']])}</p>
                    </property-line>
              '''
        
        ts += f'<abilities-block data-cha="{monster.get("cha")}" data-con="{monster.get("con")}" data-dex="{monster.get("dex")}" data-int="{monster.get("int")}" data-str="{monster.get("str")}" data-wis="{monster.get("wis")}"></abilities-block>'
        ib = ""
        for inf in infoblock: 
            if inf in monster:
                if type(monster[inf]) is list and type(monster[inf][-1]) is dict: #bludgeoning, piercing, slashing from nonmagical
                    nm = monster[inf][-1]
                    ib += f'''<property-line>
                                <h4>{infoblock[inf]} </h4>
                                <p>{", ".join(monster[inf][:-1])}; {", ".join(nm[inf])} {nm['note']}</p>
                              </property-line>
                           '''
                elif type(monster[inf]) is list:
                    ib += f'''<property-line>
                                <h4>{infoblock[inf]} </h4>
                                <p>{", ".join(monster[inf])}</p>
                              </property-line>
                           '''
                elif type(monster[inf]) is dict: 
                    ib += f'''<property-line>
                                <h4>{infoblock[inf]} </h4>
                                <p>{", ".join([k + ' ' + monster[inf][k] for k in monster[inf]])}</p>
                              </property-line>
                           '''

                else: 
                    ib += f'''<property-line>
                                <h4>{infoblock[inf]} </h4>
                                <p>{str(monster[inf])}</p>
                              </property-line>
                           '''

        ts += ib
        stats.append(Soup(ts + '</top-stats>', 'html.parser')) 
        nl = '\n' #fstring {} blocks can't have \
        if 'spellcasting' in monster: 
            ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
            # https://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712 :^)
            for spell in monster['spellcasting']: 
                sp = f'''<property-block>
                        <h4>{spell['name']}</h4>
                        <p>{nl.join(spell['headerEntries'])}</p>
                      '''
                if 'innate' in spell['name'].lower():
                    if 'will' in spell: 
                        sp += f'''<p>{', '.join(spell['will'])}</p>'''
                    if 'daily' in spell: 
                        if '1' in spell['daily']: 
                            sp += f'''<p>{', '.join(spell['daily']['1'])}</p>'''
                        if '3e' in spell['daily']: 
                            sp += f'''<p>{', '.join(spell['daily']['3e'])}</p>'''
                else: 
                    for slot in spell.get('spells', {}):
                        if slot == "0": 
                            sp += f'''<p>Cantrips (at will): {', '.join(spell["spells"][slot]["spells"])}</p>'''
                        else: 
                            sp += f'''<p>{ordinal(int(slot))} level ({spell["spells"][slot]["slots"]} slots): {', '.join(spell["spells"][slot]["spells"])}</p>'''
                sp += "</property-block>"
                stats.append(Soup(sp, "html.parser"))
            
        for action in actiontypes:
            if action in monster: 
                if action != "trait": 
                    header = f'''<h3>{actiontypes[action]}</h3>'''
                    if action == "legendary": 
                        header += f'''<p>The {monster['monster_name']} can take {monster.get("legendaryActions", 3)} legendary actions, choosing from the options below. Only one legendary action option can be used at a time and only at the end of another creature's turn. The {monster['monster_name']} regains spent legendary actions at the start of its turn.</p>'''
                    stats.append(Soup(header, "html.parser"))
                    
                if action == "legendary" or action == "reaction": 
                    block_line = "line"
                else: 
                    block_line = "block" 
                for trait in monster[action]: 
                    tr = Soup(f'''<property-{block_line}>
                                <h4>{trait['name']}</h4>
                                <p>{nl.join(trait.get("entries", []))}</p>
                                </property-{block_line}>''', "html.parser")
                    stats.append(tr)
                    

        return stats#soup


if __name__=='__main__': 
    load('''
    {
        "monster_name": "One-Eyed Shiver",
        "size": "M",
        "type": {
            "type": "humanoid",
            "tags": [
                "human"
            ]
        },
        "source": "PotA",
        "alignment": [
            "C",
            "E"
        ],
        "ac": [
            12,
            {
                "ac": 15,
                "condition": "with {@spell mage armor}",
                "braces": true
            }
        ],
        "hp": {
            "average": 49,
            "formula": "9d8 + 9"
        },
        "speed": {
            "walk": 30
        },
        "str": 10,
        "dex": 14,
        "con": 12,
        "int": 13,
        "wis": 13,
        "cha": 17,
        "name_post_stats": "One-Eyed Shiver",
        "skill": {
            "arcana": "+3",
            "perception": "+3",
            "intimidation": "+5"
        },
        "immune": [
            "cold"
        ],
        "passive": 13,
        "languages": [
            "Common"
        ],
        "cr": "3",
        "name_pre_trait": "One-Eyed Shiver",
        "trait": [
            {
                "name": "Chilling Mist",
                "entries": [
                    "While it is alive, the one-eyed shiver projects an aura of cold mist within 10 feet of itself. If the one-eyed shiver deals damage to a creature in this area, the creature also takes 5 ({@damage 1d10}) cold damage."
                ]
            }
        ],
        "name_pre_action": "One-Eyed Shiver",
        "action": [
            {
                "name": "Dagger",
                "entries": [
                    "{@atk mw} {@hit 4} to hit, reach 5 ft. or range 20/60 ft., one target. {@h}4 ({@damage 1d4 + 2}) piercing damage."
                ]
            },
            {
                "name": "Eye of Frost",
                "entries": [
                    "The one-eyed shiver casts ray of frost from its missing eye. If it hits, the target is also {@condition restrained}. A target {@condition restrained} in this way can end the condition by using an action, succeeding on a {@dc 13} Strength check."
                ]
            }
        ],
        "page": 207,
        "name_pre_spells": "One-Eyed Shiver",
        "spellcasting": [
            {
                "name": "Spellcasting",
                "headerEntries": [
                    "The one-eyed shiver is a 5th-level spellcaster. Its spellcasting ability is Charisma (spell save {@dc 13}, {@hit 5} to hit with spell attacks). It knows the following sorcerer spells:"
                ],
                "spells": {
                    "0": {
                        "spells": [
                            "{@spell chill touch}",
                            "{@spell mage hand}"
                        ]
                    },
                    "1": {
                        "slots": 4,
                        "spells": [
                            "{@spell fog cloud}",
                            "{@spell mage armor}",
                            "{@spell thunderwave}"
                        ]
                    },
                    "2": {
                        "slots": 3,
                        "spells": [
                            "{@spell mirror image}",
                            "{@spell misty step}"
                        ]
                    },
                    "3": {
                        "slots": 2,
                        "spells": [
                            "{@spell fear}"
                        ]
                    }
                },
                "ability": "cha"
            }
        ]
    }
   ''')

