
# Dwarf Fortress Legends

_AlERT: This code repo is a mess, because of the short deadline under which I did it... it's being refactored and updated for a blog post._

Dwarf Fortress, in legends mode, can generate a world history stored in a legends.xml file, which you can extract and parse if you really want to ([info](https://dwarffortresswiki.org/index.php/DF2014:Legends)).  Over the past several years ([see 2014 talk](https://www2.slideshare.net/arnicas/mining-someone-elses-magic-world-dwarf-fortress-story-generation))I've dabbled at this, moving the xml contents into a SQLite database format and using text generation to try to "describe" what's in the file.  My data file is posted at [my drive](https://drive.google.com/file/d/1xQjFVABP10uVskEpkEuOWUa-LWt4L9Xo/view?usp=sharing). I haven't yet posted my code to convert the legends file, sorry.

Fyi: The project at [DF-Storyteller]( https://gitlab.com/df_storyteller/df-storyteller) is also aimed at parsing and serving data from these files, and does a great job, but is in progress and missing some usability related functionality so far. (Thanks to Jacob Garbe for pointing it out!)

My project uses a local SQLite3 version of the xml data I created using pandas to process and combine tables; and a few queries to a linux hosting of the DF-Storyteller API when it was convenient.

I used Kate Compton's Tracery (and in particular Allison Parrish's [python port](https://github.com/aparrish/pytracery)) to generate text descriptions, but the code to feed them was pretty complex.  I also took advantage of Darius Kazemi's [Corpora project](https://github.com/dariusk/corpora) for random adjectives and proverbs to spice things up a bit.

## Process

The code tries to link characters together, giving a little tinned history of each one before moving on to their next connection.  Connections are either famil links, or members of the same organization ("entity"), worshippers of the same deity, or "event" partners -- e.g., someone's killer.  The last resort is to move to someone random and start fresh.

Each time a character is picked up, a tiny bio is generated, using details from their events and skills set.  There are bugs to fix especially relating to event ordering.

The database table data looks something like this:

```
[('index', 536),
  ('id', '536'),
  ('year', '3'),
  ('seconds72', '16800'),
  ('type', 'hf died'),
  ('hfid', '259'),
  ('site_id', '25'),
  ('slayer_hfid', '84'),
  ('slayer_race', 'NIGHT_CREATURE_9'),
  ('slayer_caste', 'MALE'),
  ('cause', 'struck')],

[('id', '0'),
  ('name', 'nocpur haleflew the snarling simplicity'),
  ('race', 'HYDRA'),
  ('caste', 'FEMALE'),
  ('appeared', '1'),
  ('birth_year', '-272'),
  ('death_year', '204'),
  ('associated_type', 'STANDARD'),
  ('entity_link',
   "[OrderedDict([('link_type', 'enemy'), ...('entity_id', '997')]), OrderedDict([('link_type', 'enemy'), ('entity_id', '1151')])]"),
  ('sphere', "['muck', 'rebirth', 'strength']")]
```

In order to make text out of this, there are string replacement rules and templates (for the events in particular).  A template string for an event looks like:

```
#hfid_string# settled  #site_id_string# #reason_string# #mood_string#
```

In brief, for each historical figure, the code create grammar terminals from the id numbers, with functions that look up the names in the correct table until the string is filled in with text only.  Since many fields optionally appear, some strings return "" if they can't be resolved.

```
rules['hfid_string'] = [#hfid.get_name_string#]
rules['hfid'] = ['340']
```

I'll clean up the code and make classes etc in the next few weeks.

The output v2 file (minor bug fixes from v1) is [here](https://github.com/arnicas/nano-genmo-2020-dwarves/blob/master/output2.md).


## Sample

There are outstanding issues with punctuation and a few event templates, but v2 fixes a few issues in the nano v1 entry.

## *"A good thing is soon snatched up."*

**Asu Fellmunched was a co-member with Rin Confusedrenowned in the organization The Council Of Stances.**

Asu Fellmunched was a male human. He lived for 220 years. He was largely unmotivated. He had no skills. Unhappily, Asu Fellmunched never had kids. He was a member in the The Council Of Stances, an organization of humans.  

**Luc Controlcaves was father to Asu Fellmunched.**

Luc Controlcaves was a male human. He lived for 198 years.  He was not bad at clothesmaking, rather crap at telling jokes, rather crap at consoling others, really bad at conversation, really bad at flattery, really bad at intimidation, rather crap at figuring out what others intend, really bad at lying, really bad at negotiation, rather crap at persuasion, not bad at woodcraft. He was related to 4 others. Luc Controlcaves was a member in the The Confederations Of Duty, an organization of humans.  In year 197, Luc Controlcaves settled  in the shoestring Crushappeared  . Luc Controlcaves settled  in the hitless Cleanmaws because of flight  in year 217. In year 217, Luc Controlcaves changed jobs in the totalled Cleanmaws. In year 218, a relationship began between Luc Controlcaves and waterproof Gisep Throwerinch. Luc Controlcaves changed jobs in the shoestring Cleanmaws in year 224.
