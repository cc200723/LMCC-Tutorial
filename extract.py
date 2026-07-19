import pdfplumber, os, sys
files = [
 "LMCC-青少年组-新例题-2026.pdf",
 "LMCC-2025+第二轮试题解析+-+青少年组.pdf",
 "LMCC-2025+第一轮试题解析.pdf",
 "LMCC-2025+第二轮试题解析+-+成人组.pdf",
]
outdir="work/text"
for f in files:
    if not os.path.exists(f): 
        print("MISSING",f); continue
    base=os.path.splitext(f)[0]
    out=os.path.join(outdir, base+".txt")
    with open(out,"w",encoding="utf-8") as w:
        with pdfplumber.open(f) as pdf:
            w.write(f"===== {f} | pages={len(pdf.pages)} =====\n\n")
            for i,page in enumerate(pdf.pages):
                w.write(f"\n----- PAGE {i+1} -----\n")
                txt=page.extract_text() or ""
                w.write(txt+"\n")
    print("OK",f,"pages",len(pdfplumber.open(f).pages))
