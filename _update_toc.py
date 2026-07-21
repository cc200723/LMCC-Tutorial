import re

with open('LMCC青少年组教材-增强版.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS for toc-sub if not already present
if 'toc-sub' not in content.split('<nav id="toc">')[0]:
    css_addition = """
#toc ol.toc-sub{margin:2px 0 8px 0; padding-left:18px; list-style:none; columns:1;}
#toc ol.toc-sub li{font-size:12.5px; color:#555; margin:1px 0;}
#toc ol.toc-sub li a{color:#555;}
"""
    content = content.replace(
        '#toc a:hover{text-decoration:underline;}',
        '#toc a:hover{text-decoration:underline;}' + css_addition
    )
    print('Added toc-sub CSS')
else:
    print('toc-sub CSS already present')

# 2. Generate new TOC
pattern = r'<(h1)\s+id="([^"]+)"[^>]*>([^<]+)</h1>|<(h2)(?:\s+id="([^"]+)")?[^>]*>([^<]+)</h2>'
matches = re.findall(pattern, content)

chapters = []
current_chapter = None
for m in matches:
    if m[0] == 'h1':
        hid = m[1]
        text = m[2]
        current_chapter = {'id': hid, 'text': text, 'sections': []}
        chapters.append(current_chapter)
    elif m[3] == 'h2':
        hid = m[4] if m[4] else None
        text = m[5]
        if current_chapter:
            current_chapter['sections'].append({'id': hid, 'text': text})

# Build TOC HTML
toc_items = []
for ch in chapters:
    if ch['text'] == '目录':
        continue
    toc_items.append('<li><a href="#' + ch['id'] + '">' + ch['text'] + '</a>')
    if ch['sections']:
        toc_items.append('<ol class="toc-sub">')
        for sec in ch['sections']:
            if sec['id']:
                toc_items.append('<li><a href="#' + sec['id'] + '">' + sec['text'] + '</a></li>')
            else:
                toc_items.append('<li>' + sec['text'] + '</li>')
        toc_items.append('</ol>')
    toc_items.append('</li>')

new_toc = '<nav id="toc"><h2>目录</h2><ol>' + ''.join(toc_items) + '</ol></nav>'

# 3. Replace old TOC
old_toc_pattern = r'<nav id="toc"><h2>目录</h2><ol>.*?</ol></nav>'
content_new = re.sub(old_toc_pattern, lambda m: new_toc, content, count=1, flags=re.DOTALL)

if content_new != content:
    with open('LMCC青少年组教材-增强版.html', 'w', encoding='utf-8') as f:
        f.write(content_new)
    print('Successfully replaced TOC. New file size:', len(content_new), 'chars')
    print('Chapters in TOC:', len(chapters))
    print('Sections in TOC:', sum(len(ch['sections']) for ch in chapters))
else:
    print('ERROR: TOC replacement failed - no change detected')
