
# Dwarf Fortress Legends

Dwarf Fortress, in legends mode, can generate a world history stored in a legends.xml file, which you can extract and parse if you really want to [info](https://dwarffortresswiki.org/index.php/DF2014:Legends).  Over the past several years [see 2014 talk](https://www2.slideshare.net/arnicas/mining-someone-elses-magic-world-dwarf-fortress-story-generation) I've dabbled at this, moving the xml contents into a SQLite database format and using text generation to try to "describe" what's in the file.  My data file is posted at [my drive](https://drive.google.com/file/d/1xQjFVABP10uVskEpkEuOWUa-LWt4L9Xo/view?usp=sharing). 

The project at [DF-Storyteller]( https://gitlab.com/df_storyteller/df-storyteller) is also aimed at parsing and serving data from these files, and does a great job, but is in progress and missing some usability related functionality so far. (Thanks to Jacob Garbe for pointing it out!)

My project uses a local SQLite3 version of the xml data I created using pandas to process and combine tables; and a few queries to a linux hosting of the DF-Storyteller API when it was convenient.

I used Kate Compton's Tracery (and in particular Allison Parrish's [python port](https://github.com/aparrish/pytracery)) to generate text descriptions, but the code to feed them was pretty complex.  I also took advantage of Darius Kazemi's [Corpora project](https://github.com/dariusk/corpora) for random adjectives and proverbs to spice things up a bit.

## Process

The code tries to link characters together, giving a little tinned history of each one before moving on to their next connection.  Connections are either famil links, or members of the same organization ("entity"), worshippers of the same deity, or "event" partners -- e.g., someone's killer.  The last resort is to move to someone random and start fresh.

Each time a character is picked up, a tiny bio is generated, using details from their events and skills set.  There are bugs to fix especially relating to event order.

The output file is [here](https://github.com/arnicas/nano-genmo-2020-dwarves/blob/master/output_v1.md).


## Sample

There are outstanding issues with event order, punctuation, and variety. But:

**Olngo Hellcrest was father to Smunstu Dungeonroom.**

Olngo Hellcrest was a human. His secret goal was rule the world. In year 193, It Must Have Been Cinder, a poem described as serious was written by Olngo Hellcrest dream . In year 199, My Friend Wisp, a poem described as forceful was written by Olngo Hellcrest . Esteem Dutiful, a poem described as serious was written by Olngo Hellcrest in year 205. The Calamitous Conqueror And Depression, a poem described as forceful was written by Olngo Hellcrest in year 211. We See Gleam, a poem described as forceful was written by Olngo Hellcrest in year 211. He was rather crap at caring for animals, rather crap at crossbow, rather crap at dissecting vermin, rather crap at dodging, outstanding at poetry, outstanding at speaking, rather crap at trapping, rather crap at writing. He was a member in the The Savage Hex, an organization of goblins. He was related to 10 others. He lived for 179 years.

**Damsto Scratchtick was child to Olngo Hellcrest.**

Damsto Scratchtick was a human. She had no goals to speak of. In year 207, Damsto Scratchtick was wounded by Darksummit The Wasp Of Glossing in the smothered Wormterrors. In year 214, The Sense And Radiance, a poem described as mechanical was written by Damsto Scratchtick . Damsto Scratchtick was foully murdered by Mebzuth Coalsea (a dwarf) at overworked the didactic Frayghouls in year 223. In year 213, Damsto Scratchtick changed jobs in the material Wormterrors. Damsto Scratchtick changed jobs in the exulting Wormterrors in year 214. She was rather crap at gelding things. She was a member in the The Dungeon Of Lies, an organization of goblins. Unhappily, Damsto Scratchtick never had kids. She lived for 22 years.