from bs4 import BeautifulSoup as Soup
import json

sizes = {"T": "Tiny", "S": "Small", "M": "Medium", "L": "Large", "H": "Huge", "G": "Gargantuan"}
align = {"C": "chaotic", "N": "neutral", "L": "lawful", "E": "evil", "G": "good", "U": "unaligned", "A": "any"}
infoblock = {"save": "Saving Throws", "skill": "Skills", "vulnerable": "Damage Vulnerabilities", "resist": "Damage Resistances", "immune": "Damage Immunities", "conditionImmune": "Condition Immunities", "senses": "Senses", "languages": "Languages", "cr": "Challenge"}
actiontypes = {"action": "Actions", "reaction": "Reactions", "legendary": "Legendary Actions"} 

def get_type(monster):
    if 'type' not in monster: 
        return None
    if type(monster['type']) is str: 
        return monster['type']
    return monster['type']['type'] + f"({', '.join(monster['type']['tags'])})"

def get_ac(monster): 
    acstring = ""
    ac = monster['ac']
    if type(ac[0]) is str or type(ac[0]) is int: 
        acstring += str(ac[0])
    else: 
        acstring += f"{ac[0]['ac']} ({ac[0]['from']})"
    if len(ac) > 1: 
        acstring += f" ({ac[1]['ac']} {ac[1]['condition']})"
    return acstring

def load(monster):
    if type(monster) == str:
        monster = json.loads(monster)
    with open('statblock.html', 'r') as f:
        # soup = Soup(f.read(), "html5lib")
        soup_i = 0
        stats = Soup('', 'html.parser')#soup.find('stat-block')
        ch = Soup(f'''<creature-heading>
                        <h1>{monster['monster_name']}</h1>
                        <h2>{sizes.get(monster.get('size'))} {get_type(monster)}, {" ".join([align.get(a) for a in monster.get('alignment')])}</h2>
                  ''', "html.parser")
        stats.insert(soup_i, ch)
        soup_i += 1
        ts = Soup(f'''<top-stats>
                    <property-line>
                      <h4>Armor Class</h4>
                      <p>{get_ac(monster)}</p>
                    </property-line>
                    <property-line>
                      <h4>Hit Points</h4>
                      <p>{monster.get('hp', {'average': None}).get('average')} ({monster.get('hp', {'formula': None}).get('formula')})</p>
                    <property-line>
                      <h4>Speed</h4>
                      <p>{', '.join([s + " " + str(monster['speed'][s]) + "ft" if s != "walk" else str(monster['speed'][s]) + "ft" for s in monster['speed']])}</p>
                    </property-line>
              ''', "html.parser")
        stats.insert(soup_i, ts)
        soup_i += 1
        ab = f'<abilities-block data-cha="{monster["cha"]}" data-con="{monster["con"]}" data-dex="{monster["dex"]}" data-int="{monster["int"]}" data-str="{monster["str"]}" data-wis="{monster["wis"]}"></abilities-block>'
        stats.insert(soup_i, Soup(ab, "html.parser"))
        soup_i += 1
        ib = ""
        for inf in infoblock: 
            if inf in monster:
                if type(monster[inf]) is list and type(monster[inf][-1]) is dict: #bludgeoning, piercing, slashing from nonmagical
                    nm = monster[inf][-1]
                    ib += f'''<property-line>
                                <h4>{infoblock[inf]}</h4>
                                <p>{", ".join(monster[inf][:-1])}; {", ".join(nm[inf])} {nm['note']}</p>
                              </property-line>
                           '''
                else:
                    ib += f'''<property-line>
                                <h4>{infoblock[inf]}</h4>
                                <p>{", ".join(monster[inf])}</p>
                              </property-line>
                           '''
        stats.insert(soup_i, Soup(ib, "html.parser"))
        soup_i += 1
        nl = '\n' #fstring {} blocks can't have \
        if 'spellcasting' in monster: 
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
                    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
                    # https://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712 :^)
                    for slot in spell.get('spells', {}):
                        if slot == "0": 
                            sp += f'''<p>Cantrips (at will): {', '.join(spell["spells"][slot]["spells"])}</p>'''
                        else: 
                            sp += f'''<p>{ordinal(int(slot))} level ({spell["spells"][slot]["slots"]} slots): {', '.join(spell["spells"][slot]["spells"])}</p>'''
                stats.insert(soup_i, Soup(sp, "html.parser"))
            soup_i += 1
        for action in actiontypes:
            if action in monster: 
                if action != "trait": 
                    header = f'''<h3>{actiontypes[action]}</h3>'''
                    if action == "legendary": 
                        header += f'''<p>The {monster['monster_name']} can take {monster.get("legendaryActions", 3)} legendary actions, choosing from the options below. Only one legendary action option can be used at a time and only at the end of another creature's turn. The {monster['monster_name']} regains spent legendary actions at the start of its turn.</p>'''
                    stats.insert(soup_i, Soup(header, "html.parser"))
                    soup_i += 1
                if action == "legendary" or action == "reaction": 
                    block_line = "line"
                else: 
                    block_line = "block" 
                for trait in monster[action]: 
                    tr = Soup(f'''<property-{block_line}>
                                <h4>{trait['name']}</h4>
                                <p>{nl.join(trait.get("entries", []))}</p>
                                </property-{block_line}>''', "html.parser")
                    stats.insert(soup_i, tr)
                    soup_i += 1

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

