# -*- coding: utf-8 -*-
"""Build the two output files from template.html + img/.

  index.html   for the folder / sending the file   (YouTube player embedded)
  deploy.html  for the published link              (YouTube opens in a new tab,
                                                    its player is blocked there)

Run:  python build.py
"""
import base64, io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

ORDER = ['p12', 'p01', 'p02', 'p03', 'p14', 'p08', 'p04',
         'p05', 'p07', 'p06', 'p09', 'p11', 'p13']
CAPTIONS = ["ikaw at ako ♥", "paborito ko 'to", "sa'yo lang", "kilig moments",
            "always us", "hay, mahal kita", "tayo ✨", "my happy place",
            "sana forever", "smile mo 🤍", "kahit saan, basta ikaw",
            "ang cute natin", "ulit tayo ♥"]
FLOWERS = 'p10'          # ang bouquet, nasa page 4
YT_URL = 'https://youtu.be/8hJJ2l8UaxQ'


def b64(path):
    with open(path, 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()


def fill(page, song):
    page = page.replace('{{PHOTOS}}', json.dumps([b64(f'img/{n}.jpg') for n in ORDER]))
    page = page.replace('{{CAPTIONS}}', json.dumps(CAPTIONS))
    page = page.replace('{{FLOWERS}}', b64(f'img/{FLOWERS}.jpg'))
    page = page.replace('{{SONG}}', song)
    assert '{{' not in page
    return page


def build_index(tpl):
    io.open('index.html', 'w', encoding='utf-8').write(fill(tpl, 'song.mp3'))


def build_deploy(tpl):
    """Artifact version: no document wrapper, no blocked external scripts."""
    page = tpl

    # the cover becomes a link to YouTube; the embedded player goes away
    page = page.replace('<div class="art" id="albumArt" onclick="toggleSong()"><!--COVER-->',
                        f'<a class="art" href="{YT_URL}" target="_blank" rel="noopener"><!--COVER-->')
    page = page.replace('</div><!--/COVER-->', '</a><!--/COVER-->')
    page = page.replace('          <div id="ytplayer"></div>\n', '')
    js_start, js_end = page.index('const YT_ID ='), page.index('/* hearts */')
    page = page[:js_start] + page[js_end:]

    # the disc just turns on its own, and the sleeve sits slightly open
    page = page.replace('    animation:spin 9s linear infinite;animation-play-state:paused;',
                        '    animation:spin 16s linear infinite;')
    page = page.replace('  .vinyl.playing{animation-play-state:running}\n', '')
    page = page.replace('  .disc-slot{width:min(165px,32%);margin-left:-7%;z-index:1;transition:transform .6s ease}',
                        '  .disc-slot{width:min(165px,32%);margin-left:-7%;z-index:1;transform:translateX(8%)}')

    # the platform supplies <html>/<head>/<body>, so ship only title+style+body
    title_link = page[page.index('<title>'):page.index('<style>')]
    title_link = '\n'.join(l for l in title_link.split('\n') if 'preconnect' not in l)
    style = page[page.index('<style>'):page.index('</style>') + len('</style>')]
    body = page[page.index('<body>') + len('<body>'):page.index('</body>')].strip()
    page = title_link + style + '\n' + body + '\n'

    # phone safe area, focus ring, reduced motion
    page = page.replace('    padding:12px;background:linear-gradient(to top',
                        '    padding:12px;padding-bottom:calc(12px + env(safe-area-inset-bottom,0px));\n'
                        '    background:linear-gradient(to top')
    page = page.replace('  .dot.on{background:var(--pink-deep);transform:scale(1.25)}',
                        '  .dot.on{background:var(--pink-deep);transform:scale(1.25)}\n'
                        '  .btn:focus-visible,.polaroid:focus-visible,.envelope:focus-visible,.art:focus-visible'
                        '{outline:3px solid var(--pink-deep);outline-offset:3px}\n'
                        '  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}')

    page = fill(page, '')
    for bad in ('<!DOCTYPE', '<html', '<head>', '</head>', '<body>', '</body>', '</html>', 'iframe_api'):
        assert bad not in page, bad
    io.open('deploy.html', 'w', encoding='utf-8').write(page)


tpl = io.open('template.html', encoding='utf-8').read()
build_index(tpl)
build_deploy(tpl)
for f in ('index.html', 'deploy.html'):
    print(f, round(os.path.getsize(f) / 1048576, 2), 'MB')
