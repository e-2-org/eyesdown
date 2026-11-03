#!/bin/sh
# Makes the sounds in docs/audio/ from the original files.
#
# The original played its sounds from Flash files (SWF) in hidden frames.
#  - The number calls (1.swf to 30.swf) have no other source: their MP3 sound
#    is copied out of the SWFs as it is, without re-encoding (_scripts/swfmp3.py).
#  - The other sounds were also kept as Windows Media files (sounds/*/*.asf).
#    The SWFs' MP3s are 24kbit/s and cut off above about 7kHz; the ASF files
#    keep the music up to about 10kHz, so these are made from the ASF files,
#    each the same stretch of sound as its SWF (only jingle 1 is an excerpt).
#    The film soundtrack is the exception: filmall.asf has a decoding error
#    that loses half a second, so it is copied out of filmall.swf instead.
#  - Shaun Fox's recordings from his talk at Camden Arts Centre were only
#    kept as ASF files.
#
#   sh _scripts/audio.sh
set -eu
cd "$(dirname "$0")/.."
OUT=docs/audio
rm -rf "$OUT"
mkdir -p "$OUT/numbers" "$OUT/shaun"

# the number calls, and the film soundtrack
python3 _scripts/swfmp3.py "$OUT/numbers" $(seq -f '%g.swf' 1 30) > /dev/null
python3 _scripts/swfmp3.py "$OUT" sounds/film/filmall.swf > /dev/null

# mp3 OUTPUT [ffmpeg input and filter options]: MP3, keeping the source's sample rate and channels.
# The ASF files' timestamps are out of order, so they are decoded to plain PCM first
mp3() {
    out=$1
    shift
    ffmpeg -v error "$@" -f wav - | ffmpeg -v error -y -f wav -i - -c:a libmp3lame -q:a 2 "$out"
}

for f in fmahoy fmmoney fmpyang; do mp3 "$OUT/$f.mp3" -i sounds/fruitmachines/$f.asf; done
for f in prizewin sallyfh; do mp3 "$OUT/$f.mp3" -i sounds/duet/$f.asf; done
# jingle 1 is 13.3s from 6.46s into jing1.asf
mp3 "$OUT/jingles1.mp3" -ss 6.46 -t 13.26 -i sounds/jingles/jing1.asf -af afade=t=out:st=13.21:d=0.05
for n in 2 3 4 5 6 7 8 9 10; do mp3 "$OUT/jingles$n.mp3" -i sounds/jingles/jing$n.asf; done

for f in sounds/shaun/*.asf; do mp3 "$OUT/shaun/$(basename "$f" .asf).mp3" -i "$f"; done

ls "$OUT" "$OUT"/* | wc -l
du -sh "$OUT"
