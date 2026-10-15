import re
from collections import defaultdict
from pathlib import Path

path = str(Path(__file__).resolve().parent / 'LMCC青少年组教材-增强版.html')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Extract headings with line numbers
headings = []
for i, line in enumerate(lines):
    for m in re.finditer(r'<(h[1234])[^>]*>(.*?)</\1>', line, re.DOTALL):
        tag = m.group(1)
        text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        headings.append((tag, text, i+1))

# Identify chapter boundaries
chapters = []
current_chapter = None
current_headings = []
for h in headings:
    tag, text, line = h
    if tag == 'h1':
        if current_chapter:
            chapters.append((current_chapter, current_headings))
        current_chapter = text
        current_headings = [h]
    else:
        current_headings.append(h)
if current_chapter:
    chapters.append((current_chapter, current_headings))

issues = []

for ch_name, ch_h in chapters:
    m_ch = re.search(r'第\s*(\d+)\s*章', ch_name)
    if not m_ch:
        continue
    ch_num = int(m_ch.group(1))
    if ch_num < 1 or ch_num > 12:
        continue

    # Collect h2s and their h3s
    h2_list = []
    current_h2 = None
    current_h3s = []
    for h in ch_h:
        tag, text, line = h
        if tag == 'h2':
            if current_h2:
                h2_list.append((current_h2, current_h3s))
            current_h2 = (text, line)
            current_h3s = []
        elif tag == 'h3' and current_h2:
            current_h3s.append((text, line))
    if current_h2:
        h2_list.append((current_h2, current_h3s))

    # 1. Check h2 numbering continuity
    h2_numbers = []
    for h2_info, h3s in h2_list:
        h2_text, h2_line = h2_info
        m = re.match(r'(\d+)\.(\d+)', h2_text)
        if m:
            h2_numbers.append((int(m.group(1)), int(m.group(2)), h2_text, h2_line))
        elif re.match(r'\d+\s', h2_text):
            m2 = re.match(r'(\d+)', h2_text)
            if m2:
                h2_numbers.append((int(m2.group(1)), 0, h2_text, h2_line))

    expected_next = None
    for i, (ch_part, sec_part, text, line) in enumerate(h2_numbers):
        if expected_next is not None and sec_part != 0:
            if sec_part != expected_next:
                issues.append({
                    'chapter': ch_num,
                    'type': 'h2_gap',
                    'line': line,
                    'text': text,
                    'description': f"H2 numbering gap: expected {ch_part}.{expected_next}, found {ch_part}.{sec_part}"
                })
        if sec_part != 0:
            expected_next = sec_part + 1

    # 2. Check h3 numbering continuity within each h2
    for h2_info, h3s in h2_list:
        h2_text, h2_line = h2_info
        if not h3s:
            continue
        h2_prefix_match = re.match(r'(\d+\.\d+)', h2_text)
        if not h2_prefix_match:
            continue
        h2_prefix = h2_prefix_match.group(1)
        
        h3_numbers = []
        for h3_text, h3_line in h3s:
            m = re.match(re.escape(h2_prefix) + r'\.(\d+)', h3_text)
            if m:
                h3_numbers.append((int(m.group(1)), h3_text, h3_line))
        
        if len(h3_numbers) >= 2:
            expected = h3_numbers[0][0] + 1
            for idx in range(1, len(h3_numbers)):
                actual = h3_numbers[idx][0]
                if actual != expected:
                    issues.append({
                        'chapter': ch_num,
                        'type': 'h3_gap',
                        'line': h3_numbers[idx][2],
                        'text': h3_numbers[idx][1],
                        'description': f"H3 numbering gap under {h2_text}: expected {h2_prefix}.{expected}, found {h2_prefix}.{actual}"
                    })
                expected = actual + 1

    # 4 & 5. Check content length between h2s
    h2_positions = [(h[1], h[2]) for h in ch_h if h[0] == 'h2']
    
    for idx in range(len(h2_positions) - 1):
        h2_text, start_line = h2_positions[idx]
        _, end_line = h2_positions[idx+1]
        
        section_lines = lines[start_line:end_line-2]
        text_content = '\n'.join(section_lines)
        clean = re.sub(r'<[^>]+>', '', text_content)
        clean = re.sub(r'\s+', '', clean)
        char_count = len(clean)
        
        if char_count < 50:
            issues.append({
                'chapter': ch_num,
                'type': 'short_section',
                'line': start_line,
                'text': h2_text,
                'description': f"Very short section ({char_count} chars) between {h2_text} and next h2"
            })
        elif char_count < 200:
            issues.append({
                'chapter': ch_num,
                'type': 'nearly_empty',
                'line': start_line,
                'text': h2_text,
                'description': f"Nearly empty section ({char_count} chars) between {h2_text} and next h2"
            })

# 3. Check orphan figures
# 上下文标题取 figure 之前的最近 h2/h3/h4（含本小节标题），而非只认 h3：
# 教材正文中大量插图紧跟段落正文、位于 h2/h3 小节内部，仅向前 50 行找 h3 会误报。
figure_positions = []
for i, line in enumerate(lines):
    if '<figure' in line:
        nearest_heading = None
        for j in range(i - 1, max(i - 200, -1), -1):
            for m in re.finditer(r'<(h[234])[^>]*>(.*?)</\1>', lines[j], re.DOTALL):
                nearest_heading = re.sub(r'<[^>]+>', '', m.group(2)).strip()
                break
            if nearest_heading:
                break
        # 无标题上下文时，若图带 figcaption 且前文有正文引用（如图 3-4 所示），仍视为有效插图
        if not nearest_heading:
            fig_block = '\n'.join(lines[i:i + 64])
            cap_m = re.search(r'<figcaption>图\s*([\d\.\-]+)', fig_block)
            if cap_m:
                ref_pat = re.compile(r'图\s*' + re.escape(cap_m.group(1)) + r'[」”]?所示')
                for j in range(i - 1, max(i - 8, -1), -1):
                    if ref_pat.search(lines[j]):
                        nearest_heading = '(' + cap_m.group(1) + ')'
                        break
        figure_positions.append((i + 1, nearest_heading))

orphan_figures = [fp[0] for fp in figure_positions if not fp[1]]

# Specific check: Chapter 1 section 1.4 subsections 1.4.1 and 1.4.2
ch1_h = None
for ch_name, ch_h in chapters:
    if '第 1 章' in ch_name:
        ch1_h = ch_h
        break

ch1_h3s = [(h[1], h[2]) for h in ch1_h if h[0] == 'h3'] if ch1_h else []
h3_14 = [(text, line) for text, line in ch1_h3s if text.startswith('1.4')]
print("=== Chapter 1 H3s under section 1.4 ===")
for text, line in h3_14:
    print(f"  {text} (line {line})")

if not any(text.startswith('1.4.1') for text, _ in h3_14):
    issues.append({'chapter':1, 'type':'missing_h3', 'line':0, 'text':'1.4.1', 'description':'Missing H3 heading 1.4.1 in Chapter 1 section 1.4'})
if not any(text.startswith('1.4.2') for text, _ in h3_14):
    issues.append({'chapter':1, 'type':'missing_h3', 'line':0, 'text':'1.4.2', 'description':'Missing H3 heading 1.4.2 in Chapter 1 section 1.4'})

# Print summary
print("\n" + "="*70)
print("STRUCTURAL AUDIT RESULTS")
print("="*70)
print(f"\nTotal issues found: {len(issues)}")
print(f"Orphan figures (no preceding h2/h3/h4 within 200 lines): {len(orphan_figures)}")

if issues:
    print("\n--- ISSUES BY CHAPTER ---")
    for ch in range(1, 13):
        ch_issues = [iss for iss in issues if iss['chapter'] == ch]
        if ch_issues:
            print(f"\nChapter {ch}:")
            for iss in ch_issues:
                print(f"  [{iss['type'].upper()}] Line {iss['line']}: {iss['text']!r}")
                print(f"      -> {iss['description']}")

if orphan_figures:
    print(f"\n--- ORPHAN FIGURES ({len(orphan_figures)} total) ---")
    print(f"  Lines: {orphan_figures[:20]}{'...' if len(orphan_figures)>20 else ''}")
