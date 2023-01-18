# BlurBot
This is the Python source for the [C64DiskBot](https://botsin.space/@c64_disks) on Mastodon.

This bot monitors the release RSS feed of https://csdb.dk

If a new D64 is uploaded it generates a visual representation of the data on the disk.

This bot was created by [@dec_hl](https://mastodon.social/@dec_hl)

# Python script
Used packages
- Mastodon.py
- sqlite3
- xmltodict

# Image generator
You need [Processing](https://processing.org/) to compile and run the image generator.
It uses [Droid64](https://droid64.sourceforge.net/#home) to access the D64 images. Droid64 is under GPL license.
To run it in a headless Linux environment I use `xvfb-run`
It also needs a Processing font file called `CBM-8.vlw` (not included) for rendering the center text.
