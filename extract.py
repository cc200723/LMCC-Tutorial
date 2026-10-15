import pdfplumber, os, sys
from pathlib import Path

# 输入 PDF 与输出目录均相对脚本位置解析，避免依赖运行时的 CWD。
BASE_DIR = Path(__file__).resolve().parent
files = [
 "LMCC-青少年组-新例题-2026.pdf",
 "LMCC-2025+第二轮试题解析+-+青少年组.pdf",
 "LMCC-2025+第一轮试题解析.pdf",
 "LMCC-2025+第二轮试题解析+-+成人组.pdf",
]
outdir = BASE_DIR / "work" / "text"
outdir.mkdir(parents=True, exist_ok=True)
for f in files:
    fp = BASE_DIR / f
    if not fp.exists():
        print("MISSING", f); continue
    base = os.path.splitext(f)[0]
    out = outdir / (base + ".txt")
    with open(out, "w", encoding="utf-8") as w:
        with pdfplumber.open(fp) as pdf:
            w.write(f"===== {f} | pages={len(pdf.pages)} =====\n\n")
            for i, page in enumerate(pdf.pages):
                w.write(f"\n----- PAGE {i+1} -----\n")
                txt = page.extract_text() or ""
                w.write(txt + "\n")
    print("OK", f, "pages", len(pdfplumber.open(fp).pages))
