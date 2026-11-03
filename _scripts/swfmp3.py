"""Extract the MP3 sound from SWF files, without re-encoding.

Streamed sound (SoundStreamBlock tags) is joined, dropping each block's
4-byte header (sample count and seek samples); an event sound (DefineSound)
is written from after its 2-byte seek samples.

  python3 _scripts/swfmp3.py OUTDIR file.swf ...
"""
import sys, zlib, struct
from pathlib import Path

def tags(data):
    body = zlib.decompress(data[8:]) if data[:3] == b'CWS' else data[8:]
    nbits = body[0] >> 3
    pos = (5 + 4 * nbits + 7) // 8 + 4
    while pos < len(body):
        code_len, = struct.unpack_from('<H', body, pos); pos += 2
        code, ln = code_len >> 6, code_len & 0x3f
        if ln == 0x3f:
            ln, = struct.unpack_from('<I', body, pos); pos += 4
        yield code, body[pos:pos + ln]
        pos += ln
        if code == 0:
            break

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
for f in sys.argv[2:]:
    stream, event = b'', []
    for code, b in tags(Path(f).read_bytes()):
        if code == 19:
            stream += b[4:]
        elif code == 14 and b[2] >> 4 == 2:
            event.append(b[9:])
    data = stream or (event[0] if event else b'')
    if data:
        (out / (Path(f).stem + '.mp3')).write_bytes(data)
    print(f, len(data), 'bytes', 'stream' if stream else 'event' if event else 'NONE')
