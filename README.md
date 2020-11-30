
# Dwarf Fortress Legends

Dwarf Fortress, in legends mode, can generate a world history stored in a legends.xml file, which you can extract and parse if you really want to [info](https://dwarffortresswiki.org/index.php/DF2014:Legends).  Over the past several years [see 2014 talk](https://www2.slideshare.net/arnicas/mining-someone-elses-magic-world-dwarf-fortress-story-generation) I've dabbled at this, moving the xml contents into a SQLite database format and using text generation to try to "describe" what's in the file.  My data file is posted at [my drive](https://drive.google.com/file/d/1xQjFVABP10uVskEpkEuOWUa-LWt4L9Xo/view?usp=sharing). 

The project at [DF-Storyteller]( https://gitlab.com/df_storyteller/df-storyteller) is also aimed at parsing and serving data from these files, and does a great job, but is in progress and missing some usability related functionality so far. (Thanks to Jacob Garbe for pointing it out!)

My project uses a local SQLite3 version of the xml data I created using pandas to process and combine tables; and a few queries to a linux hosting of the DF-Storyteller API when it was convenient.

I used Kate Compton's Tracery (and in particular Allison Parrish's [python port](https://github.com/aparrish/pytracery)) to generate text descriptions, but the code to feed them was pretty complex.  I also took advantage of Darius Kazemi's [Corpora project](https://github.com/dariusk/corpora) for random adjectives and proverbs to spice things up a bit.

## Process

The code tries to link characters together, giving a little tinned history of each one before moving on to their next connection.  Connections are either famil links, or members of the same organization ("entity"), worshippers of the same deity, or "event" partners -- e.g., someone's killer.  The last resort is to move to someone random and start fresh.

Each time a character is picked up, a tiny bio is generated, using details from their events and skills set.

## Sample

