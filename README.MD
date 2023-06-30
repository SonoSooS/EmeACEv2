# EmeACE v2

A payload framework built on top of Pokémon Emerald Summary screen ACE.

## Repo layout

- payload.S contains the actual payload written into the savefile
- chkfix.py installs the payload into the save, and fixes up the box area checksum after modifying it
- pokeace - Copy.sav is a quick savefile I made for testing, but you can supply your own as well

## Recommended use

- Free up slot 2 in your party (it WILL be overwritten!)
- Free up PC data from Box 2 (they will be overwritten)
- Dump your Emerald save file with GBA Save Tool on a DS or DS Lite
- Insert your flashcart SD into your computer
- Copy and rename your savefile next to payload.S as "pokeace - Copy.sav" (change in chkfix.py)
- Run `armips payload.S`
- Run `python3 chkfix.py`
- Copy "pokeace.sav" back to your flashcart SD into the same folder you found it
- Flash back the newly modified .sav to your Emerald cartridge
- Trigger the ACE by opening the Summary screen from the party menu (navigating from an other Pokémon will crash the game, don't do that)

## Credits

- Kingcom for [ARMIPS](https://github.com/Kingcom/armips)
- Bulbagarden for [the Bulbapedia article describing savefile documentation](https://bulbapedia.bulbagarden.net/wiki/Save_data_structure_(Generation_III))
- everyone involved with [the Pokémon Emerald decompilation project](https://github.com/pret/pokeemerald)

## Footnote

I've discovered and exploited this independently almost a year ago, and it has been sitting on my disk since that, unreleased.

Since my 2nd hospital visit, I've completely forgot what the magic values and addresses are, so I can't add any more comments to the code than it already has, and I'm sorry for that.

This is released as-is, it should work with the English copy of Emerald (BPEE00).

## Technical details which I can still remember

This exploit uses a stack corruption where [a garbage name is copied to the stack](https://github.com/pret/pokeemerald/blob/8822264130ec2a95b52ef450ee9db127f93bb777/src/pokemon_summary_screen.c#L2759), and it just so happens that the value trashed to the stack will be a valid pointer into PC data.  
On the English copy of Emerald (BPEE00), species 0x425A is the only value which doesn't completely obliterate the stack, while also jumping to a really favorable location in the PC box data (0x02EB0169), *and* also working in emulators without hitting an assertion.

There are no other species values which even come close to usable (as in, they either jump outside of any usable save region, or they completely obliterate memory), so the stack has to be fixed by a small veneer before jumping to the actual payload (usually stored in PC data, as it's the easiest to modify), so if the payload were to return then it won't cause even more chaos.

```ARM
ADD SP, #12 @ adjust SP past the corrupted region
POP {r0}    @ pop untouched return value into r0
MOV LR, r0  @ set return address of payload
```

There is also one more caveat: the payload *will* be called every frame infinitely, unless `CB2_ReturnToField` is called inside of the main payload.

