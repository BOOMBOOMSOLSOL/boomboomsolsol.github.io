"""Check a built Jekyll site without network access or additional packages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import collections
import json
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1] if len(sys.argv) > 1 else '_site').resolve()
errors = []

class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.h1, self.ids, self.links, self.assets = path, 0, [], [], []
        self.canonical, self.description, self.social, self.scripts = [], [], [], []
        self.json_blocks, self.collecting, self.block = [], False, ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag in ['script', 'img'] and a.get('src'): self.assets.append(a['src'])
        if tag == 'img' and 'alt' not in a: errors.append(f'{self.path}: image without alt')
        if tag == 'link' and a.get('rel') == 'stylesheet': self.assets.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a['href'])
        if tag == 'meta' and a.get('name') == 'description': self.description.append(a.get('content'))
        if tag == 'meta' and a.get('property') == 'og:image': self.social.append(a.get('content'))
        if tag == 'script':
            self.scripts.append(a.get('src',''))
            if a.get('type') == 'application/ld+json': self.collecting, self.block = True, ''

    def handle_data(self, data):
        if self.collecting: self.block += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.collecting:
            self.json_blocks.append(self.block)
            self.collecting = False

docs = {}
for path in root.rglob('*.html'):
    rel = str(path.relative_to(root))
    doc = Document(rel)
    text = path.read_text()
    doc.feed(text)
    docs[path] = doc
    if doc.h1 != 1: errors.append(f'{rel}: expected 1 H1, got {doc.h1}')
    for attr in ['canonical', 'description', 'social']:
        if len(getattr(doc,attr)) != 1 or not getattr(doc,attr)[0]: errors.append(f'{rel}: missing/duplicate {attr}')
    duplicates = [x for x,c in collections.Counter(doc.ids).items() if c > 1]
    if duplicates: errors.append(f'{rel}: duplicate IDs {duplicates}')
    if any('tailwindcss.com' in s for s in doc.scripts): errors.append(f'{rel}: runtime Tailwind CDN remains')
    if '{{' in text or '{%' in text: errors.append(f'{rel}: unresolved Liquid')
    for block in doc.json_blocks:
        try: json.loads(block)
        except ValueError: errors.append(f'{rel}: malformed JSON-LD')

def resolve(url, current):
    parsed = urlsplit(url)
    if parsed.scheme and (parsed.scheme != 'https' or parsed.netloc != 'boomboomsolsol.app'): return None, ''
    if parsed.netloc and parsed.netloc != 'boomboomsolsol.app': return None, ''
    path = unquote(parsed.path)
    candidate = root / path.lstrip('/') if path.startswith('/') else current.parent / path
    if not path: candidate = current
    if candidate.is_dir(): candidate /= 'index.html'
    if not candidate.exists() and not candidate.suffix:
        candidate = candidate.with_suffix('.html')
    return candidate.resolve(), unquote(parsed.fragment)

checked_links = checked_assets = 0
for path,doc in docs.items():
    for url in doc.links + doc.assets + doc.social:
        target,anchor = resolve(url,path)
        if target is None: continue
        if not target.is_file(): errors.append(f'{doc.path}: missing target {url}'); continue
        if anchor and target in docs and anchor not in docs[target].ids: errors.append(f'{doc.path}: missing anchor {url}')
    checked_links += len(doc.links)
    checked_assets += len(doc.assets)

tree = ET.parse(root/'sitemap.xml')
locs = [x.text for x in tree.findall('.//{*}loc')]
if len(locs) != len(set(locs)): errors.append('sitemap: duplicate URLs')
for url in locs:
    target,_ = resolve(url,root/'index.html')
    if not target or not target.is_file(): errors.append(f'sitemap: missing {url}')
for route in ['apps/math','apps/english','download','account-deletion','privacy','terms','support','apps/vocabulary','apps/facts','download/vocabulary']:
    if not (root/route/'index.html').exists(): errors.append(f'missing public route /{route}/')
for route in ['privacy','terms','support']:
    if 'support@boomboomsolsol.app' not in (root/route/'index.html').read_text(): errors.append(f'{route}: contact missing')
ads = (root/'app-ads.txt').read_text()
if 'pub-2811424630268352' not in ads or 'pub-8970984079070400' not in ads: errors.append('publisher entry removed')
for app in ['math','english']:
    # Upcoming products must not acquire accidental public installation links.
    card = (root/'download/index.html').read_text().split('id="'+app+'"',1)[1].split('</article>',1)[0]
    if 'play.google.com' in card or 'apps.apple.com' in card: errors.append(f'{app}: unexpected store CTA')
summary = {'pages':len(docs),'links':checked_links,'asset_references':checked_assets,'sitemap_urls':len(locs),'errors':errors}
print(json.dumps(summary,ensure_ascii=False,indent=2))
sys.exit(bool(errors))
