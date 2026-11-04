# eyes-down redux: session summary

3 November 2026, working with Claude Code on the `html-port` branch, merged into `main` (pull request #1) and published at [e-2-org.github.io/eyesdown](https://e-2-org.github.io/eyesdown/). The same session worked on other e-2 projects. The eyes-down part of the conversation is in [transcript.md](transcript.md); the README describes the site in full.

## Aim

eyes-down (Anna Best, with Karen Stripp, Karen Martin, Jon Pollard and Nick Sloane, for Camden Arts Centre, produced by e-2) is the archive of Anna's residency at the State Mecca Bingo Hall, Kilburn, presented as a bingo card. Pete had thought it still worked, but it played its sound from Flash files, opened everything in popups and was built from framesets, and its pages badly needed reorganising. The aim was a static site in `docs/`.

## What was there

- **734 HTML pages, 95 SWFs and 32 ASF (Windows Media) files.**
- **The card:** 30 numbers, each a topic (Kilburn, Charms, The State, Staff, Gambling…). Clicking one played the caller's call from a SWF in a hidden frame, opened the topic in a 582×640 popup and marked the number. A full house brought up "Bingo!" with the prize sound.
- **Topics** were chains of 4 to 105 pages, each a photograph with a caption or a page of transcript, moved through by clicking.
- **Problems found:**
  - muddled chains: Dave's conversation spliced into "The Building", Talking Mecca a single 96-page chain through questionnaires and six interviews, a blank "Shaun" page in Camden Talks;
  - 31 links that only worked because the old server ignored the case of file names, and 16 to pages that don't exist, mostly in drafts;
  - three copies of Anna and Karen's conversation;
  - 11 recordings of Shaun Fox, a Mecca manager, that nothing used;
  - the web host's control panel files (`test/`, `img/`, `css/`);
  - text in mixed character sets, so apostrophes showed as `�`.

## Decisions (Pete's)

- Windows like the Contact site's, with title bars in the colours of the card's cells.
- The card centred on the page, with windows opening from the top left.
- Shaun's recordings on his blank page in Camden Talks.
- Re-encode sounds from the ASF files if they're better quality than the SWFs' MP3s, but leave the ASFs out of the published site.
- Use the `ak1`–`ak28` version of Anna and Karen's conversation and leave the others out.

## What was built

- **`_scripts/build.py`** reads the original pages, follows each topic's chain from the page the card opened, and writes `docs/topics/NN.json` and `NN.html`, `docs/card.html`, `docs/index.html` and the images the site uses. `--dump` lists every topic's pages without building.
- **`_scripts/swfmp3.py`** copies the MP3 sound out of a SWF without re-encoding. **`_scripts/audio.sh`** makes `docs/audio/`.
- **`docs/css/eyesdown.css`** and **`docs/js/eyesdown.js`**, written by hand:
  - the card centred, marks kept in the browser, windows cascading from the top left, draggable, closed with × or Escape, scaled down on phones (one at a time below 700px);
  - one page at a time in each window, as the popups were: click the picture, the arrows or the arrow keys; contents lists for the long mixed topics;
  - a full house opens "You've Won!" with the prize sound and a button to start a new card;
  - `card.html#17` opens topic 17, and each topic is also a page of its own (`topics/17.html`) that works without JavaScript.

## Sound

- **ASF or MP3?** The ASFs are about 20 kbit/s WMA. For music they keep sound up to about 10 kHz, where the SWFs' 24 kbit/s MP3s stop at about 7 kHz; for speech they're no better. So the jingles, fruit machines and Special Event sounds are re-encoded from the ASFs, each cut to exactly the stretch the SWF played (found by lining up the audio).
- **The film soundtrack** comes from its SWF, because `filmall.asf` has a decoding fault that loses about half a second.
- **The 30 number calls** have no ASF, so they're copied out of their SWFs as they are.
- **Shaun Fox's recordings** were transcribed locally with faster-whisper (`medium.en`) to put them in the order he spoke them in his talk, and each is labelled with its opening words.
- The ASFs stay at the repository root, unpublished.

## Repairs

- Staff's pages 7 and 9, the start of Shaun Fox's talk, are empty files. Their text was recovered from an earlier transcription (`four/sinners.html`), word for word.
- The 26th charm (the cabbage) was never reached, because page 25 linked back to the start.
- Each page is read in its own character set (Mac Roman or Windows-1252), so quotation marks and apostrophes come out right.
- Page counts are worked out afresh, correcting repeated and skipped numbers in the original captions.
- Afterthoughts uses `ak1`–`ak27`: there is no `ak28`, and the last page linked to a file that doesn't exist.

## Checks

In headless Chrome at 1280×800 and 390×844, served at `/eyesdown/`: every one of about 900 references resolves, every sound is used, there are no script errors, and windows, the full house, the contents lists and Shaun's recordings work.

## Publishing

Committed on `html-port` (`8cc1fdf`), pushed, merged into `main` by Pete, who switched on GitHub Pages from `main`, `/docs`. The e-2 site's eyes-down page now links to it.

## To check

- The section titles and recording labels were written for the redux; they should be checked against Anna's wording.
- The two recovered Staff pages use the rougher, unedited transcription.
- Sounds tied to a page play on arriving at it with "next"; the original played them on clicking through from the page before, which comes to the same thing.
- Some of the original marked-number GIFs are slightly offset, and look doubled on the card; they are Anna's images, so they were left as they are.
