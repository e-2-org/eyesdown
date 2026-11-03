#!/usr/bin/env python3
"""
Builds the eyes-down site in docs/ from the original files at the root of
the repository, which it doesn't change.

The original is a bingo card (index_launch.html) of 30 numbers. Each number
opened a topic in a popup window: a chain of pages, each a picture with a
caption or a page of text, linked by "next". This script follows each chain
from the page the card opened, as a visitor would have, and writes:

  docs/topics.json          every topic: its number, title, colour, sounds and
                            pages (picture, caption or text), and its sections
  docs/topics/NN.html       each topic as a page of its own, for direct links
                            and for browsing without JavaScript
  docs/images/...           the pictures the topics use, at their original paths

The sounds are made by _scripts/audio.sh (see there).

  python3 _scripts/build.py           build docs/
  python3 _scripts/build.py --dump    list each topic's pages, without building
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'

WORDS = ('one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen '
         'sixteen seventeen eighteen nineteen twenty twentyone twentytwo twentythree twentyfour '
         'twentyfive twentysix twentyseven twentyeight twentynine thirty').split()

# the card's cell colours (index_launch.html)
COLOURS = {'pink': '#f8c7fb', 'yellow': '#f9f9b6', 'blue': '#c7fbfb', 'maeve': '#e0aefc', 'green': '#c7fbe0'}

# Repairs to the chains, as page paths relative to the root:
# the next page, where the original's link is missing or broken
NEXT = {
    # sinners7.html is empty (its text is recovered from sinners.html below)
    'four/sinners7.html': 'four/sinners8.html',
    'four/sinners9.html': 'four/sinners10.html',
    # the charms are numbered to 26, but 25 links back to the start
    'two/charms25.html': 'two/charms26.html',
}
# where a chain ends, though the page links on (to the start, or to a page that doesn't exist)
END = set()

# Two pages of Shaun Fox's talk (sinners7 and sinners9) are empty files. Their text is taken
# from an earlier transcription of the whole talk, sinners.html, between these words, with its
# speakers ("s:" and "a:") named as on the other pages
RECOVER = {
    'four/sinners7.html': ('Sinners, Saints and the Need for Greed', 'anyway she shouted'),
    'four/sinners9.html': ('s: its shifting', 'a: you can leave your bag'),
}
SPEAKERS = {'s': 'Shaun', 'a': 'Anna'}


def recover(path):
    full = decode(ROOT / 'four/sinners.html')
    start, end = RECOVER[rel(path)]
    passage = full[full.index(start):full.index(end)]
    turns = re.split(r'\n\s*(?=[sa]:)', passage.strip())
    out = []
    for turn in turns:
        m = re.match(r'([sa]):\s*(.*)', turn, re.S)
        text = html.escape(re.sub(r'\s+', ' ', m.group(2) if m else turn).strip())
        out.append(f'<p>{SPEAKERS[m.group(1)]}: {text}' if m else f'<p><b>{text}</b>')
    return '\n'.join(out)


# Contents for the topics that mix pictures with transcripts: {page number: section title}
SECTIONS = {
    4: {1: 'Staff', 7: 'Sinners, Saints and the Need for Greed: Shaun Fox at Camden Arts Centre'},
    6: {1: 'Belief', 11: 'A week of small miracles', 12: 'Miracles'},
    7: {1: 'Collaborative research', 3: 'Camden Talks', 9: "Questions for 'Playtime'",
        10: 'Sinners, Saints and the Need for Greed', 11: 'Shaun Fox: recordings',
        12: "Amy Plant and Anna Best, before 'Playtime'"},
    9: {1: 'Dave Neale, Chief Engineer', 30: 'The Wurlitzer'},
    10: {1: 'The questions', 2: 'Questionnaires', 39: 'Images found in the answers'},
    15: {1: 'Anna and Peter', 2: 'Images to be sourced', 4: 'Images', 5: 'The plan', 8: 'Soundtrack',
         11: 'Loot', 12: 'Apparitions', 15: 'Notes', 16: '16mm film'},
    17: {1: 'Talking Mecca', 10: 'The questions', 12: 'George, the caller', 33: 'A mother and daughter',
         48: 'Ivy', 54: 'An anonymous player', 56: 'Pat', 67: 'Ronnie'},
    28: {1: 'References', 12: 'Bas Jan Ader', 13: 'P. D. Ouspensky'},
    30: {1: 'Credits', 2: 'Barny Drabble: In Search of Real Life and Miracles'},
}

# Shaun Fox's recordings from his talk (sounds/shaun/, made by audio.sh), on his page in
# Camden Talks, in the order he said them, each labelled with its opening words
RECORDINGS = {
    'seven/camden_talks11.html': [
        ('intro', 'I\u2019m a manager with a company called Mecca Bingo\u2026'),
        ('customers', 'What is the diversity of customers at Kilburn?'),
        ('names', 'I try, as a manager, to make sure that I know people\u2019s names.'),
        ('rankents', 'Can you talk a bit about Rank?'),
        ('addict', 'She\u2019s a very, very keen bingo player\u2026'),
        ('decoretc', 'Our company wants to move towards a more uniform image\u2026'),
        ('addictive', 'Probably the most addictive form of gaming there is\u2026'),
        ('fruit', 'A huge amount of money goes into research\u2026'),
        ('income', 'Fruit machines account for one third of our income\u2026'),
        ('sell', 'If people are happy, they will spend more money\u2026'),
        ('losetime', 'There will never be windows or clocks\u2026'),
    ],
}


def decode(path):
    """The pages were written on both Windows and Mac: decode each in its own character set."""
    data = path.read_bytes()
    windows = sum(data.count(b) for b in (b'\x85', b'\x91', b'\x92', b'\x93', b'\x94', b'\x96', b'\x97'))
    mac = sum(data.count(b) for b in (b'\xc9', b'\xd0', b'\xd1', b'\xd2', b'\xd3', b'\xd4', b'\xd5'))
    return data.decode('mac_roman' if mac > windows else 'cp1252')


def rel(path):
    return path.resolve().relative_to(ROOT).as_posix()


def resolve(folder, href):
    """A link's target, matching the file name regardless of case, as the original server did."""
    href = href.split('#')[0]
    target = folder / href
    if target.exists():
        return target.resolve()
    for q in target.parent.glob('*') if target.parent.exists() else []:
        if q.name.lower() == target.name.lower():
            return q.resolve()
    return None


def card():
    """The card: 6 rows of 10 cells, each [colour, number or None]; and each number's first page."""
    s = decode(ROOT / 'index_launch.html')
    inner = s[s.index('cellspacing="2"'):]
    rows = []
    for tr in re.findall(r'(?is)<tr>(.*?)</tr>', inner):
        cells = []
        for cls, content in re.findall(r'(?is)<td[^>]*class="(\w+)"[^>]*>(.*?)</td>', tr):
            m = re.search(r"windowOpener\('([\w/.]+)', 'img(\d+)'\)", content)
            cells.append([cls, int(m.group(2)) if m else None, m.group(1) if m else None])
        if cells:
            rows.append(cells)
    return rows


def text_of(fragment):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()


def parse_page(path):
    """A page of a topic: its picture or text, caption, colour, links and sounds."""
    s = decode(path)
    page = {'path': rel(path)}
    body = re.search(r'(?is)<body([^>]*)>(.*)</body>', s) or re.search(r'(?is)<body([^>]*)>(.*)', s)
    attrs, content = (body.group(1), body.group(2)) if body else ('', s)
    m = re.search(r'(?i)body\s*\{\s*background-color:\s*(#[0-9a-f]{6})', s) or re.search(r'(?i)bgcolor="?(#[0-9a-f]{6})', attrs)
    page['bg'] = m.group(1).lower() if m else '#cccccc'

    # the next page: the first link to another page of the topic (sound frames are N.html and hiddenN.html)
    page['links'] = []
    # (the whole file: the jingles' image map comes before <body>)
    for tag in re.findall(r'(?is)<(?:a|area)\b[^>]*>', s):
        h = re.search(r'(?i)(?<![.\w])href\s*=\s*"?([^"\s>]+)', tag)
        if not h or not h.group(1).lower().endswith(('.html', '.htm')) or re.fullmatch(r'\d+\.html', h.group(1)):
            continue
        target = resolve(path.parent, h.group(1))
        page['links'].append(rel(target) if target else 'MISSING ' + h.group(1))
        sound = re.search(r"hidden\.location\.href='(hidden\d*\.html)'", tag)
        if sound:
            page['sound_next'] = sound_of(path.parent / sound.group(1))

    imgs = [(src, w, h) for src, w, h in re.findall(
        r'(?is)<img[^>]*?src="([^"]+)"[^>]*?width="?(\d+)"?[^>]*?height="?(\d+)"?', content) if 'pixel' not in src]
    # the caption is the white strip under the picture: "Kilburn: High Road<br>1/9"
    cap = re.findall(r'(?is)<td bgcolor="#ffffff"\s*align="center">(.*?)</td>', content)
    if imgs:
        src, w, h = imgs[0]
        page['kind'] = 'picture'
        page['img'] = {'src': rel(path.parent / src), 'width': int(w), 'height': int(h)}
        areas = re.findall(r'(?is)<area\b[^>]*>', s)
        if areas:
            page['areas'] = [{
                'coords': [int(c) for c in re.search(r'coords="([^"]+)"', a).group(1).split(',')],
                'href': re.search(r'href="([^"]+)"', a).group(1),
            } for a in areas]
    else:
        page['kind'] = 'text'
        cell = re.search(r'(?is)cellpadding="15"[^>]*>\s*<tr>\s*<td[^>]*>(.*?)</td>', content)
        page['html'] = recover(path) if rel(path) in RECOVER else cell.group(1) if cell else content
    if cap:
        parts = [text_of(p) for p in re.split(r'(?i)<br\s*/?>', cap[0])]
        parts = [p for p in parts if p]
        page['caption'] = parts[0] if parts else ''
        if len(parts) > 1:
            page['count'] = parts[1]
    return page


def sound_of(hidden):
    """The SWF a hidden frame page plays, if any."""
    if not hidden.exists():
        return None
    m = re.search(r'(?i)value="([^"]+\.swf)"', decode(hidden))
    return m.group(1) if m else None


def topic(number, start):
    """Follow a topic's chain of pages from the page the card opened."""
    first = ROOT / start
    t = {'number': number, 'folder': first.parent.name, 'pages': []}
    s = decode(first)
    frames = dict(re.findall(r'(?i)<frame name="(\w+)" src="([^"]+)"', s))
    seen = {rel(first)}
    if frames:
        # a frameset: the topic in the top frame, and a sound in the hidden one
        t['sound_open'] = sound_of(first.parent / frames['hidden'])
        first = first.parent / frames['top']
    t['title'] = text_of((re.search(r'(?is)<title>(.*?)</title>', s) or re.search('()', '')).group(1))
    path = rel(first)
    seen.discard(path)
    while path and path not in seen:
        seen.add(path)
        page = parse_page(ROOT / path)
        t['pages'].append(page)
        nxt = NEXT.get(path) or next((l for l in page['links'] if not l.startswith('MISSING')), None)
        path = None if path in END else nxt
    return t


def topics():
    out = []
    for row in card():
        for colour, number, start in row:
            if number:
                t = topic(number, start)
                t['colour'] = COLOURS[colour]
                out.append(t)
    return sorted(out, key=lambda t: t['number'])


def dump():
    for t in topics():
        print(f"== {t['number']} {t['folder']} '{t['title']}' {t['colour']} pages={len(t['pages'])}"
              + (f" sound_open={t['sound_open']}" if t.get('sound_open') else ''))
        for i, p in enumerate(t['pages']):
            what = p.get('caption', '') if p['kind'] == 'picture' else text_of(p['html'])[:70]
            extra = ''.join(f' {k}={p[k]}' for k in ('sound_next', 'areas') if k in p)
            print(f"  {i + 1:3d} {p['kind'][:4]} {p['path'].split('/')[-1]:22s} {p.get('count', ''):6s} {what}{extra[:80]}")



# ---------- output ----------

ALLOWED = {'p', 'br', 'b', 'i', 'u', 'ol', 'ul', 'li'}


def clean(fragment):
    """A transcript page's HTML: paragraphs, line breaks and emphasis, without its "next" links."""
    s = re.sub(r'(?is)<a\b[^>]*>\s*(next|back|previous|more)?\s*</a>', '', fragment)
    s = re.sub(r'(?is)</?(?!(?:%s)\b)\w+[^>]*>' % '|'.join(ALLOWED), '', s)   # unwrap anything else
    s = re.sub(r'(?i)<(\w+)\s[^>]*>', r'<\1>', s)                             # no attributes
    s = re.sub(r'(?i)</p>', '', s)
    s = re.sub(r'(?i)\s*(<[ou]l>)', r'<p>\1', s)                              # lists are blocks of their own
    s = re.sub(r'(?i)(</[ou]l>)\s*', r'\1<p>', s)
    paras = []
    for chunk in re.split(r'(?i)<p>', s):
        chunk = re.sub(r'\s+', ' ', chunk).strip()
        chunk = re.sub(r'^(<br>\s*)+|(\s*<br>)+$', '', chunk).strip()
        if not chunk or chunk == '&nbsp;':
            continue
        paras.append(chunk if chunk.lower().startswith(('<ol>', '<ul>')) else f'<p>{chunk}</p>')
    return '\n'.join(paras)


def mp3(swf):
    return f"audio/{swf.replace('.swf', '.mp3')}" if swf else None


def output(t):
    """A topic as published: what topics/NN.json and topics/NN.html are made from."""
    pages = []
    sound = None   # a sound played on the way to the next page
    for p in t['pages']:
        out = {'kind': p['kind'], 'bg': p['bg']}
        if p['kind'] == 'picture':
            out['img'] = p['img']
            out['caption'] = p.get('caption', '')
        else:
            out['html'] = clean(p['html'])
            if p.get('caption'):
                out['caption'] = p['caption']
        if sound:
            out['sound'] = sound
        sound = mp3(p.get('sound_next'))
        if p.get('areas'):
            # the jingles: each area plays a jingle, or goes to the next page
            out['areas'] = []
            for a in p['areas']:
                x1, y1, x2, y2 = a['coords']
                box = [min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1)]
                if re.fullmatch(r'\d+\.html', a['href']):
                    out['areas'].append({'box': box, 'sound': mp3(sound_of(ROOT / t['folder'] / a['href']))})
                else:
                    out['areas'].append({'box': box, 'next': True})
        if p['path'] in RECORDINGS:
            out['recordings'] = [{'src': f'audio/shaun/{f}.mp3', 'title': title} for f, title in RECORDINGS[p['path']]]
        pages.append(out)
    o = {'number': t['number'], 'title': t['title'], 'colour': t['colour'], 'pages': pages}
    if t.get('sound_open'):
        o['sound'] = mp3(t['sound_open'])
    if t['number'] in SECTIONS:
        o['sections'] = [{'page': n, 'title': title} for n, title in SECTIONS[t['number']].items()]
    return o


def esc(s):
    return html.escape(s, quote=True)


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="icon" href="{base}favicon.ico">
<link rel="stylesheet" href="{base}css/eyesdown.css">
{head}</head>
<body class="{cls}">
{body}
</body>
</html>
"""


def topic_html(o):
    """A topic as a page of its own: every page in order, for direct links and without JavaScript."""
    sections = {s['page']: s['title'] for s in o.get('sections', [])}
    items = []
    for i, p in enumerate(o['pages'], 1):
        if i in sections:
            items.append(f'<h2 id="p{i}">{esc(sections[i])}</h2>')
        if p['kind'] == 'picture':
            img = p['img']
            body = (f'<img src="../{img["src"]}" width="{img["width"]}" height="{img["height"]}" alt="{esc(p["caption"])}" loading="lazy">'
                    f'<figcaption>{esc(p["caption"])} <span class="count">{i}/{len(o["pages"])}</span></figcaption>')
            if p.get('recordings'):
                body += '<ol class="recordings">' + ''.join(
                    f'<li><a href="../{r["src"]}">{esc(r["title"])}</a></li>' for r in p['recordings']) + '</ol>'
            items.append(f'<figure class="topic-page" id="page{i}">{body}</figure>')
        else:
            items.append(f'<article class="topic-page topic-text" id="page{i}" style="--bg:{p["bg"]}">{p["html"]}'
                         f'<p class="count">{i}/{len(o["pages"])}</p></article>')
    body = (f'<header class="topic-head" style="--c:{o["colour"]}"><a href="../card.html#{o["number"]}">eyes-down</a> '
            f'<h1><span class="n">{o["number"]}</span> {esc(o["title"])}</h1></header>\n<main class="topic-all">\n'
            + '\n'.join(items) + '\n</main>')
    return PAGE.format(title=f'{o["number"]} {esc(o["title"])} – eyes-down', base='../', head='',
                       cls='topic', body=body)


def card_html(rows, titles):
    cells = []
    for row in rows:
        for colour, n, start in row:
            if n:
                word = WORDS[n - 1]
                cells.append(f'<a class="cell {colour}" href="topics/{n:02d}.html" data-n="{n}" title="{esc(titles[n])}">'
                             f'<img src="images/numbers/{word}.gif" width="75" height="70" alt="{n}: {esc(titles[n])}"></a>')
            else:
                cells.append(f'<span class="cell {colour}"></span>')
    body = ('<main class="card-page">\n<div class="card" id="card">\n' + '\n'.join(cells) + '\n</div>\n'
            '<p class="card-help"><a href="index.html">eyes-down</a> by Anna Best. Click the numbers.'
            ' <button type="button" id="new-card" hidden>Start a new card</button></p>\n</main>')
    head = '<script src="js/eyesdown.js" defer></script>\n'
    return PAGE.format(title='eyes-down', base='', head=head, cls='card-body', body=body)


def index_html():
    s = decode(ROOT / 'index.html')
    credits = re.search(r'(?is)<p><font size="\+2">.*?Produced by.*?</p>', s).group(0)
    credits = re.sub(r'(?is)</?font[^>]*>', '', credits)
    credits = credits.replace('<b>eyes-down</b>', '<h1>eyes-down</h1>', 1).replace('<p><h1>', '<h1>').replace('</h1><br>', '</h1><p>')
    credits = credits.replace('http://www.e-2.org/', 'https://e-2-org.github.io/')
    credits = re.sub(r'\s*\n\s*', '\n', credits)
    body = ('<main class="front">\n<a class="front-card" href="card.html"><img src="index2.gif" width="100" height="100" alt="Play eyes-down"></a>\n'
            f'<div class="front-text">\n{credits}\n<p class="front-play"><a href="card.html">Play</a></p>\n</div>\n</main>')
    return PAGE.format(title='eyes-down by Anna Best', base='', head='', cls='front-body', body=body)


def build():
    rows = card()
    ts = topics()
    outs = [output(t) for t in ts]
    for d in ('topics', 'images'):
        shutil.rmtree(DOCS / d, ignore_errors=True)
    (DOCS / 'topics').mkdir(parents=True)
    images = {'images/numbers/%s.gif' % w for w in WORDS} | {'images/numbers/img%d_on.gif' % n for n in range(1, 31)}
    images |= {'images/bingo.jpg'}
    for o in outs:
        images |= {p['img']['src'] for p in o['pages'] if p['kind'] == 'picture'}
        (DOCS / 'topics' / f'{o["number"]:02d}.json').write_text(json.dumps(o, ensure_ascii=False, separators=(',', ':')))
        (DOCS / 'topics' / f'{o["number"]:02d}.html').write_text(topic_html(o))
    for src in sorted(images):
        (DOCS / src).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / src, DOCS / src)
    for f in ('index2.gif', 'favicon.ico'):
        shutil.copy2(ROOT / f, DOCS / f)
    (DOCS / 'card.html').write_text(card_html(rows, {o['number']: o['title'] for o in outs}))
    (DOCS / 'index.html').write_text(index_html())
    (DOCS / '.nojekyll').write_text('')
    print(f'{len(outs)} topics, {sum(len(o["pages"]) for o in outs)} pages, {len(images)} images')


if __name__ == '__main__':
    if '--dump' in sys.argv:
        dump()
    else:
        build()
