import numpy as np
import pandas as pd
import re
import requests
import random
import sqlite3
import time

import corpora_darius as cd
import tracery
from tracery.modifiers import base_english

conn = sqlite3.connect("dwarf_fortress_00231.db")
api = 'http://127.0.0.1:9000/api/' #running https://gitlab.com/df_storyteller/df-storyteller with same legends file

adjectives = cd.adjectives
proverbs = cd.proverbs
wordcount = 0

# Utilities


def get_query(query, conn, remove_nans=True):
    """ Return dict style key, val results from a query, skipping nans"""
    conn.row_factory = sqlite3.Row
    cur = conn.execute(query)
    res = cur.fetchall()
    newresult = []
    for row in res:
        result = dict(zip(row.keys(), row))
        newrow = []
        for (key, val) in result.items():
            if remove_nans:
                if (val != 'nan') and (val != 'NaN') and (val != "-1") and val:
                    newrow.append((key,val))
            else:
                newrow.append((key, val))
        if newrow != []:
            newresult.append(newrow)
    return newresult

def strip_underscore(string):
    return string.replace('_', ' ')

def get_fields(text):
      # Get the ## surrounded fields from a template to expand in rules.
  import re
  matches=re.findall(r'(\#.+?\#)',text)
  # matches is now ['#String 1#', '#String 2#', '#String3#']
  return matches

def get_safe_string(value):
    if type(value) is str:
        if "[" in value:
            print(value)
            return value.replace("[", "").replace("]", "")
    return value

def reload_templates(file='templates_for_event_types.txt'):
    # file must be \t sep
    templatedf = pd.read_csv(file, sep="\t")
    templatedf.set_index('EventType', inplace=True)
    return templatedf

# Get HFs Queries

def get_list_of_deities():
    deities = get_query("select distinct hfid from hf_links where link_type='deity'", conn)
    deities = [int(x[0][1]) for x in deities]
    return deities

def get_entity_links(id, conn):
    query = "select * from hf_entity_links hel inner join entities on hel.entity_id=entities.id where hel.id='%s' order by random() limit 1"
    return get_query(query % id, conn)

def get_random_hf_sql(conn):
    query = f"""
    select * from hf
    ORDER BY RANDOM() LIMIT 1
    """
    return get_query(query, conn)

def get_random_hf_api():
    api = 'http://127.0.0.1:9000/api/'
    url = api + 'historical_figures?per_page=100&order_by=id&page=3'
    r = requests.get(url)
    res = r.json()
    data = res['data']
    return random.choice(data)

def get_hf_api(id):
    api = 'http://127.0.0.1:9000/api/'
    url = api + 'historical_figures/' + str(id)
    r = requests.get(url)
    res = r.json()
    time.sleep(1)
    return res

def get_hf_links(id):
    query = f"""
    select * from hf_links
    where id == '{id}'
    """
    return get_query(query, conn)

def get_entity_api(id):
    url = api + 'entities/' + str(id)
    r = requests.get(url)
    res = r.json()
    return res

def get_event_from_sql(id):
    rows = get_query(f"select * from events_per_sourceid where sourceid={id}",conn)
    if rows:
        events = [dict(x) for x in rows]
        return events
    else:
        return None

def get_worshippers(deityid):
    worshippers = get_query("select * from hf_links where link_type == 'deity' and hfid='%s'" % (str(deityid)), conn)
    return worshippers

# Events

def get_template_row(event):
    global templatedf
    matches = templatedf.loc[event['type']]
    if type(matches) != pd.core.series.Series and len(matches) > 1:
        for i, match in matches.iterrows():
            if match['SubTypeCol'] in event.keys() and match['SubTypeVal'] == event[match['SubTypeCol']]:
                return match.TemplateString
    else:
        return matches.TemplateString

def get_all_events(idnumber, conn):
    query = f"""
    select * from events where
    snatcher_hfid = {idnumber} or
    woundee_hfid = {idnumber} or
    slayer_hfid = {idnumber} or
    seeker_hfid = {idnumber} or
    attacker_hfid = {idnumber} or
    changer_hfid = {idnumber} or
    hfid2 = {idnumber} or
    hist_figure_id = {idnumber} or
    group_1_hfid = {idnumber} or
    defender_general_hfid = {idnumber} or
    group_2_hfid = {idnumber} or
    changee_hfid = {idnumber} or
    hf_rep_1_of_2 = {idnumber} or
    hfid1 = {idnumber} or
    trickster_hfid = {idnumber} or
    doer_hfid = {idnumber} or
    hfid_target = {idnumber} or
    competitor_hfid = {idnumber} or
    new_leader_hfid = {idnumber} or
    hf_rep_2_of_1 = {idnumber} or
    attacker_general_hfid = {idnumber} or
    defender_general_hfid = {idnumber} or
    student_hfid = {idnumber} or
    giver_hist_figure_id = {idnumber} or
    receiver_hist_figure_id = {idnumber} or
    group_hfid = {idnumber} or
    winner_hfid = {idnumber} or
    target_hfid = {idnumber} or
    wounder_hfid = {idnumber} or
    hfid = {idnumber} or
    builder_hfid = {idnumber}
    """
    res = get_query(query, conn)
    if res:
        events = [dict(x) for x in res]
        return events
    else:
        return None


def get_event_strings(hf, count=1):
    hfid = hf['id']
    events = None
    strings = []
    if hf['categorised_events']:
        try:
            events = hf['categorised_events']['interesting'] + hf['categorised_events']['meh']
        except KeyError:
            events = None
    if events:
        for event in events:
            if 'competition' in event['type']:  # these are too hard
                continue
            #print('event using', event)
            rules = {}
            namerules = name_expansion_rules
            template = get_template_row(event)
            # there may be no template for this event type.
            if template:
                fields = get_fields(template)
                print("template", template)
                rules = write_field_terminal_rules(event, fields, namerules)
                #print("Data:", row)
                #print("rules", rules)
                # time modifier can go anywhere
                if 'year' in event:
                    origin = ['In year #year#, ' + template + ".", template + " in year #year#."]  # year applies to all of them can appear either place.
                else:
                    origin = [template + "."]
                rules['adjective'] = adjectives
                rules['origin'] = origin
                grammar = tracery.Grammar(rules)
                grammar.add_modifiers(base_english)
                ## add modifier queries 
                grammar.add_modifiers(queries)
                text = grammar.flatten("#origin#")
                if '((' in text:
                    print("error with template output:", text)
                    continue
                else:
                    if len(strings) <= count:
                        strings.append(text)
                    else:
                        return strings
            else:
                continue
        if strings:
            return strings
        return [""]

# Get HF from Code

def get_hfid_from_links(links, exclude=None):
    # what about checking for interesting people in this set?
    hf = None
    if len(links) > 0:
        random.shuffle(links)
        for link in links:
            myid = link['hf_id_other']
            if not myid in exclude:
                relationship = link['link_type']
                hf = get_hf_api(myid)
                break
        if hf:
            return (myid, hf, relationship)
        else:
            print('no good hf in links', myid)
            return (None, None, None)
    else:
        print("failed with links", links)
        return (None, None, None)

def get_hf_from_entity_links(entities, exclude=None):
    myid = None
    if len(entities) > 0:
        random.shuffle(entities)
        for entitytry in entities:
            entity = get_entity_api(entitytry['entity_id'])
            if entity['hf_ids']:
                myid = random.choice(entity['hf_ids']) # go thru each one?
                if myid not in exclude:
                    break
            else:
                return (None, None, None)
        if not myid:
            return (None, None, None)
        hf = get_hf_api(myid)
        time.sleep(1)
        smallentity = {}
        return (myid, hf, entity['name'].title())
    else:
        return (None, None, None)

def get_hfid_from_worshipper(analysed, exclude=None):
    anid = analysed['id']
    if not exclude:
        exclude = []
    worshippers = get_worshippers(anid)
    if len(worshippers) > 0:
        random.shuffle(worshippers)
    else:
        return (None, None, None)
    worshippers = [dict(x) for x in worshippers]
    for worship in worshippers:
        print(worship)
        if not worship['id'] in exclude:
            myid = worship['id']
            hf = get_hf_api(myid)
            time.sleep(1)
            if hf:
                return (myid, hf, 'worshipper')
    return (None, None, None)

def get_hfid_from_event(event, notid=id, exclude=None):
    # gets the first id match that's not the exclude one from the event
    if event:
        for key in event.keys():
            if re.findall(r'hfid|hist_figure_id|hf_rep', key) and event[key] != str(notid):
                hf = get_hf_api(event[key])
                time.sleep(1)
                if event[key] not in exclude:
                    print('using event', event)
                    return (event[key], hf, key)
    return (None, None, None)

def get_random_hf_and_id(exclude=None):
    myid = None
    count = 5
    tries = 0
    while not myid and tries < count:
        hf = get_random_hf_api()
        myid = hf['id']
        if myid not in exclude:
            break
        tries += 1
        myid = None
    if not myid:
        return (None, None, None)
    return (myid, hf, 'random')


def get_new_hf(analysed, exclude=None):
    # all return (myid, hf, (context))
    # possible get_hfid_from_sites? requires sites list
    myid = None
    source = None
    if analysed['links']:
        (myid, hf, context) = get_hfid_from_links(analysed['links'], exclude=exclude)
        if myid:
            source = "links"
    if not myid:
        if analysed['deity'] == False and analysed['categorised_events'] and 'random_event' in analysed['categorised_events']:
            (myid, hf, context) = get_hfid_from_event(analysed['categorised_events']['random_event'], notid=analysed['id'], exclude=exclude)
            source = "event"
        if analysed['deity'] == True:
            (myid, hf, context) = get_hfid_from_worshipper(analysed, exclude=exclude)
            source = "worshipper"
    if not myid:
        if analysed['entity_link']:
            (myid, hf, context) = get_hf_from_entity_links(analysed['entity_link'], exclude=exclude)
            source = "entity"
    if not myid:
        (myid, hf, context) = get_random_hf_and_id(exclude=exclude)
        source = "random"
    print("got new id from:", context, source)
    return (myid, hf, context, source)


# Core Analysis and Control Functions

def get_missing_db_fields(eventdict, templatefields):
    # templatefields may have "_string" in them. fix to get to the raw variable name and remove . modifiers.
    fields = [field.replace("_string#", "").replace("#", "") for field in templatefields]
    sep = "."
    fields = [field.split(sep, 1)[0] for field in fields]  # remove the possible .modifiers.  No dots in fields!
    querykeys = eventdict.keys()
    diff = set(fields) - set(querykeys)
    if diff:
        return list(diff)
    else: 
        return None

def write_field_terminal_rules(eventdict, templatefields, namerules):
    ## ads to the namerules and makes the terminals from the data row.
    ## The namerules are the ones that were created to fill in the id's with strings using modifiers.
    ## TODO: how to add new namerules on-demand?
    event = eventdict
    rules = dict()
    no_result_fields = []
    # actual terminals - fill in value from the query.
    for key, value in eventdict.items():
        rules[key] = [get_safe_string(value)]  # check for weird chars like [ ] that tracery doesn't like
    no_result_fields = get_missing_db_fields(event, templatefields)  # fields in template with no db return ('none')
    #print(templatefields, no_result_fields)
    if no_result_fields:
        for f in no_result_fields:
            rules[f] = [""]
    # write rules for template_string to expand to #field# which will get populated by the actual terminals.
    for field in templatefields:
        if no_result_fields and (not field in no_result_fields):
            try:
                namerules[field.replace('#', '')]  # lhs has no #
            except KeyError:
                rules[field.replace('#', '')] = [field.replace("_string#", "#")]  #heads towards a terminal without modif.
    newrules = {**namerules, **rules}  # in python3 this combines the dicts
    return newrules

def categorize_events(events):
    sort_of_interesting = ['change hf state', 'change hf job', 'add hf hf link']
    not_interesting = ['hf simple battle event']
    collected = {}
    collected['meh'] = []
    collected['interesting'] = []
    collected['death'] = []
    for event in events:
        if event['type'] == 'hf died':
            collected['death'] = event
        if event['type'] not in not_interesting:
            if event['type'] in sort_of_interesting:
                collected['meh'].append(event)
            else:
                collected['interesting'].append(event)
    return collected

def hf_analysed(hf):
    myid = hf['id']
    events = get_all_events(myid, conn)
    alleventsdict = {}
    myevent = None
    if events and len(events) > 0:
        alleventsdict = categorize_events(events)
        if len(alleventsdict['interesting']) > 0:
            for event in alleventsdict['interesting']:
                if event['type'] != "competition":  # has wrong type of arguments for alternate hfid (list)
                    alleventsdict['random_event'] = myevent
                    break
            myevent = random.choice(alleventsdict['interesting'])
        elif 'meh' in alleventsdict and len(alleventsdict['meh']) > 1:
            myevent = random.choice(alleventsdict['meh'])
    # sites?
    age = None
    if 'death_year' in hf and hf['death_year'] != '-1':
        age =  abs((int(hf['death_year']) - int(hf['birth_year'])))
    else:
        if hf['birth_year'] != '-1':
            age = "still alive"
        else:
            age = "ageless"
    if int(myid) in deities:
        deity = True
    else:
        deity = False
    processed_hf = {**hf,
                    'age': age,
                    'events': events,
                    'deity': deity,
                    'categorised_events': alleventsdict,
                    'skills_opinions': get_skill_opinions(hf['skills'])
                    }
    return processed_hf

def describe_hf(analysed):
    global handle
    rules = {
    'origin': ["#[#setPronouns#][hero:#hf_name#]top#"],
    }
    event_strings = get_event_strings(analysed, count=4)
    try:
        event_strings = " ".join(event_strings)
    except:
        event_strings = ""
    #print("event strings", event_strings)
    time.sleep(1)
    if analysed['deity'] == False:
        rules['top'] = ["#hero# #heroWas# a #caste# #race#. #age# #goals# #skills# #links# #entity# #pet# #events#",
            "#hero# #heroWas# a #caste# #race#. #goals# #skills# #age# #entity# #links# #events#",
            "#hero# #heroWas# a #race#. #goals# #events# #pet# #skills# #entity# #links# #age#"]
    else:
        rules['top'] = ["#hero# #heroWas# a deity. #spheres# #worshippers#"]
    rules = add_rules(analysed, rules)
    rules['events'] = [event_strings]
    grammar = tracery.Grammar(rules)
    grammar.add_modifiers(base_english)
    text = grammar.flatten("#origin#")
    handle.write("\n")
    handle.write(text)
    handle.write("\n")
    return text

# String Code and Tracery

def add_correct_pronouns(analysed):
    gender = analysed['caste']
    if gender.lower() == "default":
        return "[heroThey:they][heroThem:them][heroTheir:their][heroTheirs:theirs][heroWas:were][heroThemselves:themselves]"
    if gender.lower() == "male":
        return "[heroThey:he][heroThem:him][heroTheir:his][heroTheirs:his][heroWas:was][heroThemselves:himself]"
    if gender.lower() == "female":
        return "[heroThey:she][heroThem:her][heroTheir:her][heroTheirs:hers][heroWas:was][heroThemselves:herself]"

def lived_for(hf):
    if hf['death_year'] != '-1':
        return 'lived for ' + str(abs((int(hf['death_year']) - int(hf['birth_year'])))) + ' years.'
    else:
        if hf['birth_year'] != '-1':
            return 'was born in the year ' + hf['birth_year'] + ' and is still living.'
        else:
            return "was born at the beginning of time and is still living."

def get_worshippers_text(analysed):
    myid = analysed['id']
    worshippers = get_worshippers(myid)
    count = len(worshippers)
    # add random worshippers?
    return [f"#heroThey.capitalize# had {count} worshippers.", f"{count} beings worshipped #hero#."]


def get_goals_text(analysed):
    # comes from api as a text list, not a string.
    # text could be a list of goals or a single one, or none.
    text = analysed['goal']
    if not text or text == "None":
        return random.choice(["#heroThey.capitalize# had no goals to speak of.", "", "#heroThey.capitalize# #heroWas# largely unmotivated."])
    if type(text) is str:
        return f"#heroTheir.capitalize# secret goal was {text}."
    else:
        return "#heroTheir.capitalize# secret goals were " + ",".join(text) + '.'

def get_deity_spheres_text(hf):
    if hf['deity']:
        spheres = hf['sphere']  # a list
        if len(spheres) > 1:
            return ["#heroTheir.capitalize# spheres of interest were " + ', '.join(spheres) + "."]
        if len(spheres) == 1:
            return ["#heroTheir.capitalize# sphere of interest was " + spheres[0] + "."]
        else:
            return ["#heroThey.capitalize# had no spheres of interest.", "#hero# cared about nothing."] 
    else:
        return ['']

def skill_eval(score):
    score = int(score)
    if score >= 11000:
        return 'outstanding'
    if score >= 6800:
        return 'expert'
    if score >= 6000:
        return 'super'
    if score >= 4400:
        return 'talented'
    if score >= 3500:
        return 'excellent'
    if score >= 2800:
        return 'pretty good'
    if score >= 1600:
        return 'ok'
    if score >= 1200:
        return 'not bad'
    if score >= 500:
        return 'rather crap'
    if score >= 0:
        return 'really bad'
    
def get_skill_opinions(skills):
    skillwithopinions = []
    boring_skills = ['DODGING', 'GRASP_STRIKE', 'STANCE_STRIKE', 'SHIELD','ARMOR','DISCIPLINE']
    for skill in skills:
        newskill = skill
        newskill['opinion'] = skill_eval(skill['total_ip'])
        skillwithopinions.append(newskill)
    return skillwithopinions

def skill_fix(skill):
    fixes = {
    'grasp_strike': 'grasping and striking',
    'stance_strike': 'taking a stance and striking',
    'situational_awareness': 'noticing what\'s going on',
    'dissect_fish': 'dissecting fish',
    'processfish': 'doing useful things with fish',
    'fish': 'fishing',
    'shield': 'using a shield',
    'tanner': 'tanning hides',
    'armor': 'using armor properly',
    'butcher': 'butchering animals',
    'cook': 'cooking',
    'axe': 'using an axe',
    'spear': 'throwing a spear',
    'pacify': 'pacifying others who are upset',
    'animalcare': 'caring for animals',
    'judging_intent': 'figuring out what others intend',
    'comedy': 'telling jokes',
    'wax_working': 'making candles',
    'animaltrain': 'training animals',
    'sneak': 'sneaking around',
    'dyer': 'dying cloth',
    'siegeoperate': 'operating a seige (whatever that means)',
    'bow': 'using a bow',
    'dissect_vermin': 'dissecting vermin',
    'sword': 'the sword',
    'console': 'consoling others',
    'glassmaker': 'making glass things',
    'mace': 'the mace',
    'hammer': 'using a hammer',
    'milk': 'milking cows',
    'potash_making': 'making potash',
    'whip': 'using a whip',
    'diagnose': 'diagnosing illness',
    'dress_wounds': 'dressing wounds',
    'lye_making': 'making lye',
    'bite': 'biting attackers',
    'encrustgem': 'encrusting things with gems',
    'cutgem': 'cutting gemstones',
    'processplants': 'doing things with plants',
    'bow': 'using a bow',
    'operate_pump': 'operating a pump',
    'mechanics': 'doing mechanical things',
    'melee_combat': 'hand-to-hand combat',
    'forge_armor': 'forging armor',
    'plant': 'plants',
    'set_bone': 'setting bones',
    'forge_weapon': 'forging weapons',
    'pike': 'weilding a pike',
    'geld': 'gelding things'
    }
    try:
        return fixes[skill]
    except KeyError:
        # if it's not there, it's ok as is, e.g., 'wrestling'
        return skill
    
def get_one_skill_string(skill):
    if skill:
        return skill['opinion'] + " at " + skill_fix(skill['skill'].lower())
    else:
        return "maybe good at fighting stuff."


def get_allskills_string(skills):
    # skills here have opinions already
    if skills:
        strings = [get_one_skill_string(skill) for skill in skills]
        return ', '.join(strings) + '.'
    else:
        return 'bad at everything, basically.' 
    

def get_artifact_name(text, *params):
    global conn
    rows = []
    if text == 'None':
        return ""
    artifactid = int(text)
    rows = get_query(
        f"select name from artifacts where id={artifactid}",
        conn)
    rows = dict(rows[0])
    return str(rows['name'].title())

# the connection object can't be easily passed in, since one text arg - must be global?

def get_battle_counts_by_year(text, *params):
    global conn
    kwargs=dict(param.split('=') for param in params)
    rows = []
    year = int(text)
    rows = get_query(
        f"select count(type) as count from events where type like '%battle%' and year={year} group by type",
        conn)
    rows = dict(rows[0])
    return str(rows['count'])

def get_mood_string(text):
    if not text or text == 'None':
        return ""
    else:
        return "because of #mood#"
    
def get_slayer_race_string(text):
    if not text or text == 'None':
        return "a killer of unknown race"
    else:
        return "a " + text.replace("_", ' ').lower()
    
def get_cause_string(text):
    if not text or text == 'None':
        return ""
    if text == "struck":
        return random.choice(["(cruelly struck down)", "(struck from behind)", "(struck by a blade)"])
    else:
        return text
    
def get_reason_string(text):
    if not text or text == 'None':
        return ""
    else:
        return "because of " + text

def get_site_name(text, *params):
    global conn
    rows = []
    if not text or text == 'None':
        return ""
    else:
        siteid = int(text)
        rows = get_query(
            f"select name from sites where id={siteid}",
            conn)
        # should be just one row
        rows = dict(rows[0])
        return f"the {random.choice(adjectives)} {rows['name'].title()}"

def get_hfid_name(id):
    if id != '':
        hf = get_hf_api(id)
        if hf:
            try:
                return hf['name'].title()
            except:
                pass
    return "someone unnamed"
   
def get_skills_versions(hf):
    strings = []
    if hf['skills_opinions']:
        strings.append(get_allskills_string(hf['skills_opinions']))
        strings.append(get_one_skill_string(random.choice(hf['skills_opinions'])))
    return strings

def get_best_worst_skills_strings():
    global conn
    # text is hf_id. note this doesn't handle case where all skills are same ip value.
    query = f"""
    select * from (select * from hf_skills where id = '{text}' order by total_ip ASC limit 1) a
    union
    select * from (select * from hf_skills where id = '{text}' order by total_ip DESC limit 1) b
    """
    if text == "None":
        return "No one with skills."
    rows = get_query(query, conn)
    result = ""
    if rows and len(rows) == 2:
        best = dict(rows[0])
        result += f"#heroTheir.capitalize# best skill was {best['skill']},"
        worst = dict(rows[1])
        result += f" and #heroTheir# worst was {worst['skill']}."
    if rows and len(rows) == 1:
        best = dict(rows[0])
        result += f"#heroTheir.capitalize# only skill was {best['skill']}."
    if len(rows) == 0:
        result = "#heroThey.capitalize# had no skills."
    return result


def get_link_strings(analysed):
    strings = []
    children = 0
    count = len(analysed['links'])
    strings.append(f"#heroThey.capitalize# #heroWas# related to {count} others.")
    if count > 0:
        for link in analysed['links']:
            if link['link_type'] == "child":
                children += 1
        if children == 0:
            strings.append("Sadly, #heroThey# never had children.")
            strings.append("Unhappily, #hero# never had kids.")
        else:
            strings.append(f"#heroThey.capitalize# had {children} children.")
    return strings

def get_state_string(text):
    return text
    
def get_entity_strings(analysed):
    count = len(analysed['entity_link'])
    strings = []
    strings.append(f"#heroThey.capitalize# #heroWas# a member of {count} organizations.")
    if count > 0:
        entity = random.choice(analysed['entity_link'])
    # {'hf_id': 373, 'entity_id': 74, 'link_type': 'member', 'link_strength': None}
        role = entity['link_type']
        if entity:
            info = get_entity_api(entity['entity_id'])
            entityname = info['name'].title()
            entityrace = info['race']
            strings.append(f"#heroThey.capitalize# #heroWas# a {role} in the {entityname}, an organization of {entityrace}s.")
            strings.append(f"#hero# was a {role} in the {entityname}, an organization of {entityrace}s.")
    else:
        strings.append("#hero.capitalize# never joined any groups.")
        strings.append("#heroThey.capitalize# never worked with organizations.")
    return strings

def get_written_content_name(id):
    res = requests.get('http://127.0.0.1:9000/api/written_contents/' + str(id))
    if res.status_code == 200:
        data = res.json()
        if 'style' in data and len(data['style']) > 0:
            return f"{data['title'].title()}, a {data['form']} described as {data['style'][0]['label']}"
        else:
            return f"{data['title'].title()}, a {data['form']}"
    else:
        return "an unknown written work"

def get_pet_strings(analysed):
    if analysed['journey_pet'] == None or analysed['journey_pet'] == []:
        return ['']
    else:
        return [f"#heroTheir.capitalize# pet on #heroTheir# travels was {analysed['journey_pet']}."]


#  Code to Run

deities = get_list_of_deities()
templatedf = reload_templates()

id_fields = ['snatcher_hfid',
 'woundee_hfid',
'slayer_hfid',
 'seeker_hfid',
 'attacker_hfid',
 'changer_hfid',
 'hfid2',
 'hist_figure_id',
 'group_1_hfid',
 'defender_general_hfid',
 'group_2_hfid',
 'changee_hfid',
 'hist_fig_id',
 'hf_rep_1_of_2',
 'hfid1',
 'trickster_hfid',
 'doer_hfid',
 'hfid_target',
 'competitor_hfid',
 'new_leader_hfid',
 'hf_rep_2_of_1',
 'attacker_general_hfid',
 'student_hfid',
 'giver_hist_figure_id',
 'receiver_hist_figure_id',
 'group_hfid',
 'winner_hfid',
 'target_hfid',
 'wounder_hfid',
 'hfid',
 'builder_hfid']

name_expansion_rules = dict()
# all possible hfid roles in templates - but if they need to still get the data element, they need a new lhs of rule:
name_expansion_rules = {id + "_string": [ f"#{id}.get_hfid_name#"] for id in id_fields}
name_expansion_rules['site_id_string'] = ["#site_id.get_site_name#"]
name_expansion_rules['artifact_id_string'] = ["#artifact_id.get_artifact_name#"]
name_expansion_rules['cause_string'] = ["#cause.get_cause_string#"]
name_expansion_rules['wc_id_string'] = ["#wc_id.get_written_content_name#"]
name_expansion_rules['slayer_race_string'] = ["#slayer_race.get_slayer_race_string#"]
name_expansion_rules['mood_string'] = ["#mood.get_mood_string#"]  
name_expansion_rules['reason_string'] = ["#reason.get_reason_string#"] 
name_expansion_rules['goal_string'] = ["#goal.get_goals#"]  # renders these into string

queries = {
    'get_battle_count': get_battle_counts_by_year,
    'get_site_name': get_site_name,
    'get_hfid_name': get_hfid_name,
    'get_artifact_name': get_artifact_name, 
    'get_skills' : get_best_worst_skills_strings,
    'get_state': get_state_string,
    'get_cause_string': get_cause_string,
    'get_mood_string': get_mood_string,
    'get_reason_string': get_reason_string,
    'get_slayer_race_string': get_slayer_race_string,
    'get_written_content_name': get_written_content_name
}

def add_rules(analysed, rules):
    rules['setPronouns'] = add_correct_pronouns(analysed)
    rules['hf_name'] = [analysed['name'].title()]
    rules['caste'] = [analysed['caste']]
    rules['race'] = [analysed['race']]
    if not analysed['deity']:
        rules['age'] = ['#heroThey.capitalize# ' + lived_for(analysed)]
        rules['goals'] = [get_goals_text(analysed)]
        skilltext = get_skills_versions(analysed)  # move below into get_skills_versions wrapper
        if skilltext:
            rules['skills'] = ['#heroThey.capitalize# was ' + skilltext[0], "#heroThey.capitalize# was " + skilltext[1] + "."]
        else:
            rules['skills'] = ['', '#heroThey.capitalize# #heroWas# no good at anything useful.', '', '#heroThey.capitalize# had no skills.']
        rules['entity'] = get_entity_strings(analysed)
        rules['adjectives'] = adjectives
        rules['links'] = get_link_strings(analysed)
        rules['pet'] = get_pet_strings(analysed)
    else:
        rules['spheres'] = get_deity_spheres_text(analysed)
        rules['worshippers'] = get_worshippers_text(analysed)
    return rules

def print_transition(prev, new, context, source):
    if '_type' in context and source == 'entity':
        transition = f"{prev['name'].title()} was a co-member with {new['name'].title()} in {context['name'].title()}."
    elif source == "event":
        transition = f"Something happened between {new['name'].title()} and {prev['name'].title()}."
    elif source == "random":
        transition = f"Moving on randomly, after a dead end, to {new['name'].title()}."
    else:
        transition = f"{new['name'].title()} was {context} to {prev['name'].title()}."
    #print("transition", transition)
    return transition

def loop(count = 5):
    global handle
    alltext = ''
    exclude = []
    handle.write("\n##*\"" + random.choice(proverbs) + "\"*\n")
    (myid, hf, context) = get_random_hf_and_id(exclude=exclude)
    analysed = hf_analysed(hf)
    exclude.append(myid)
    print("id", myid)
    text = describe_hf(analysed)
    alltext += text + '\n'
    for i in range(count):
        prevhf = hf.copy()
        (myid, hf, context, source) = get_new_hf(analysed, exclude=exclude)
        print(i)
        analysed = hf_analysed(hf)
        print("new id", myid)
        # transition text
        #print("source text is:", source)
        if source == "random":
            handle.write("\n##*\"" + random.choice(proverbs) + "\"*\n")
        trans = print_transition(prevhf, hf, context, source)
        handle.write("\n**")
        handle.write(trans)
        handle.write("**\n")
        exclude.append(myid)
        text = describe_hf(analysed)
        alltext += text
    handle.close()
    return alltext

handle = open('test_file.md', 'a')
handle.write("\n")
loop(count = 210)
handle.close()