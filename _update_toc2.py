import re
from pathlib import Path

# 教材与脚本同目录；按脚本位置推导，避免硬编码本机绝对路径。
html_path = str(Path(__file__).resolve().parent / "LMCC青少年组教材-增强版.html")

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Extract all h1 and h2 headings with their ids and text
# h1: <h1 id="...">Chapter Title</h1>
# h2: <h2>Section Title</h2>
# Also handle <h1 id="..." ...>Title</h1> with attributes

# Pattern for h1 with id
h1_pattern = r'<h1\s+id="([^"]+)"[^>]*>(.+?)</h1>'
# Pattern for h2 (no id needed; 兼容带属性写法如 <h2 id="...">)
h2_pattern = r'<h2\b[^>]*>(.+?)</h2>'

# Build TOC entries: list of (level, href, text)
entries = []
# Find all h1 and h2 in order
# We need to find them in document order
all_headings = []
for m in re.finditer(h1_pattern, html):
    all_headings.append((m.start(), 1, m.group(1), m.group(2)))
for m in re.finditer(h2_pattern, html):
    all_headings.append((m.start(), 2, None, m.group(1)))

# Sort by position
all_headings.sort(key=lambda x: x[0])

# Only include headings that are in the main content (after TOC, before appendices end)
# Find the TOC end position
toc_start = html.find('<nav id="toc">')
toc_end = html.find('</nav>', toc_start)

# Filter headings that come after the TOC
all_headings = [h for h in all_headings if h[0] > toc_end]

# Build TOC HTML
toc_items = []
current_chapter = None
chapter_subs = []

def flush_chapter():
    global chapter_subs
    if current_chapter is not None:
        sub_html = ""
        if chapter_subs:
            sub_html = '<ol class="toc-sub">'
            for sub_text in chapter_subs:
                sub_html += f'<li>{sub_text}</li>'
            sub_html += '</ol>'
        toc_items.append(f'<li><a href="#{current_chapter[0]}">{current_chapter[1]}</a>{sub_html}</li>')
        chapter_subs = []

for pos, level, hid, text in all_headings:
    # Clean text - remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    if level == 1:
        flush_chapter()
        current_chapter = (hid, clean_text)
    elif level == 2:
        chapter_subs.append(clean_text)

flush_chapter()

new_toc_inner = ''.join(toc_items)
new_toc = f'<nav id="toc"><h2>目录</h2><ol>{new_toc_inner}</ol></nav>'

# Replace old TOC
new_html = html[:toc_start] + new_toc + html[toc_end+6:]

with open(html_path, "w", encoding="utf-8") as f:
    f.write(new_html)

print(f"TOC updated. {len(toc_items)} chapters.")
for item in toc_items:
    # Extract chapter title for reporting
    m = re.search(r'>([^<]+)</a>', item)
    if m:
        title = m.group(1)[:50]
        sub_count = item.count('<li>') - 1  # subtract the chapter li itself
        print(f"  {title}: {sub_count} subsections")

print(f"File size: {len(new_html)} chars")
