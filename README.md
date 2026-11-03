# eyes-down

## by Anna Best

Archive and highlights from _Mecca_ at the State Mecca Bingo Hall, Kilburn (part of the _North London Link_ series of public art works), 1998–2000.

**Edited by:** Anna Best and Karen Stripp
**Technical collaborator:** Karen Martin
**Sound production:** Jon Pollard
**Additional scripting:** Nick Sloane
**Commissioned by:** Camden Arts Centre
**Produced by:** e-2

The piece is a bingo card. Each of its 30 numbers is a topic (Kilburn, Charms, The State, Staff, Gambling and so on): photographs, flyers, questionnaires and conversations with the players and staff of the State. Clicking a number calls it, opens its topic and marks it on the card; a full house wins.

## Layout

The original files are at the top of this repository, unchanged. The current version of the site is in `docs/`, which is what GitHub Pages publishes; it is a static site, built by the scripts in `_scripts/`. Summaries and transcripts of the Claude Code sessions are in `_sessions/`.

## The new version (2026)

The original opened each topic in a popup window, built its pages from framesets, and played its sounds from Flash files in hidden frames. The new version runs in any modern browser:

- **The card** (`docs/card.html`) is centred on the page. Clicking a number plays the caller's call, marks the number and opens its topic in a window over the card, the size of the original popup (582 × 640). Windows open from the top left, can be dragged by their title bar, which is the colour of the number's cell, and close with × or Escape. Marked numbers are kept in the browser; when all 30 are marked, "You've Won!" opens with the prize sound, and the card can be started again.
- **A topic** shows one page at a time, as the popup did: click the picture (or the arrows, or the arrow keys) for the next page. The topics that mix pictures with transcripts have a contents list.
- **Each topic is also a page of its own** (`docs/topics/01.html` to `30.html`), showing all its pages in order, for direct links and for browsing without JavaScript. `card.html#17` opens topic 17 on the card.
- **Sounds** play where the original's did: the film soundtrack when Film opens; the fruit machines and the Special Event's sounds when moving on from particular pages; the ten jingles from the cassette list in Jingles.
- **Shaun Fox's recordings.** Eleven recordings of Shaun Fox, a Mecca manager, talking at Camden Arts Centre were in the original files but not used. They are now on his page in Camden Talks (the photograph that had nothing else on it), in the order he said them, each labelled with its opening words.

### Order and repairs

Each topic is the chain of pages the original reached from the page the card opened, following its "next" links. Along the way:

- links that only worked because the original server ignored the case of file names (`tm_Ronnie67.html` for `tm_ronnie67.html`) are followed;
- Staff's pages 7 and 9, the start of Shaun Fox's talk "Sinners, Saints and the Need for Greed", are empty files. Their text is taken from an earlier transcription of the whole talk (`four/sinners.html`), as written there, with its speakers named as on the other pages;
- the last of the 26 charms (the cabbage) was never reached: page 25 linked back to the start;
- the pages were written partly on Windows and partly on a Mac, and each is read in its own character set, so that quotation marks and apostrophes come out right;
- page numbers ("12/98") are counted afresh, which corrects a few repeated or skipped numbers in the original captions.

Drafts that no chain reaches are left out: single-page versions of conversations that are also in the chains as pages, other versions of Anna and Karen's conversation in Afterthoughts (the one used is `ak1`–`ak27`), notes, and a copy of an encyclopedia entry. So are the web host's test pages and control panel files (`test/`, `img/`, `css/`).

### Sounds

`_scripts/audio.sh` makes the sounds in `docs/audio/`:

- the 30 number calls are copied out of their SWF files as they are, without re-encoding (`_scripts/swfmp3.py`);
- the jingles, the fruit machines and the Special Event's sounds (`sallyfh`, and `prizewin`, which is also the full house) are made from the Windows Media files in `sounds/`, which keep more of the music (up to about 10kHz, where the SWFs' 24kbit/s MP3s stop at about 7kHz), each the same stretch of sound as the SWF played;
- the film soundtrack is copied out of its SWF, because `sounds/film/filmall.asf` has a fault that loses half a second;
- Shaun Fox's recordings are made from `sounds/shaun/`.

The Windows Media files stay at the top of the repository and aren't published.

### Building

```
sh _scripts/audio.sh        # docs/audio/ (needs ffmpeg)
python3 _scripts/build.py   # docs/topics/, docs/images/, docs/card.html, docs/index.html
```

`python3 _scripts/build.py --dump` lists every topic's pages without building. The stylesheet and script (`docs/css/eyesdown.css`, `docs/js/eyesdown.js`) are written by hand.
