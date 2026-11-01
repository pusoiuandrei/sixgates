#!/usr/bin/env bash
# Downloads the primary-source corpus used for the principles audit (phase 1, 2 November 2026).
# Texts are not versioned in the repo (copyright); run this script to rebuild corpus/txt locally.
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p raw txt
UA="Mozilla/5.0 SixGates research"
curl -sS -A "$UA" -o raw/letters_index.html https://www.berkshirehathaway.com/letters/letters.html
for y in $(seq 1977 1997); do curl -sS -A "$UA" -o raw/$y.html https://www.berkshirehathaway.com/letters/$y.html; done
for f in 1998pdf.pdf final1999pdf.pdf 2000pdf.pdf 2001pdf.pdf 2002pdf.pdf 2003ltr.pdf; do curl -sS -A "$UA" -o raw/$f https://www.berkshirehathaway.com/letters/$f; done
for y in $(seq 2004 2025); do curl -sS -A "$UA" -o raw/${y}ltr.pdf https://www.berkshirehathaway.com/letters/${y}ltr.pdf; done
curl -sS -A "$UA" -o raw/ownman.pdf https://www.berkshirehathaway.com/ownman.pdf
curl -sS -A "$UA" -o raw/buffett_50years_2014.pdf "https://www.berkshirehathaway.com/SpecialLetters/WEB%20past%20present%20future%202014.pdf"
curl -sS -A "$UA" -o raw/munger_50years_2014.pdf "https://www.berkshirehathaway.com/SpecialLetters/CTM%20past%20present%20future%202014.pdf"
curl -sS -L -A "$UA" -o raw/buffett_florida1998.pdf https://tilsonfunds.com/BuffettUofFloridaspeech.pdf
curl -sS -A "$UA" -o raw/munger_usc1994_fs.html https://fs.blog/a-lesson-on-worldly-wisdom/
curl -sS -A "$UA" -o raw/munger_harvard1995_fs.html https://fs.blog/great-talks/psychology-human-misjudgment/
python3 - <<'PY'
import re, html, glob, os, subprocess
for f in glob.glob('raw/*.html'):
    if 'index' in f: continue
    s=open(f,encoding='utf-8',errors='ignore').read()
    s=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
    s=re.sub(r'<br\s*/?>|</p>|</div>|</li>|</h\d>','\n',s,flags=re.I); s=re.sub(r'<[^>]+>','',s); s=html.unescape(s); s=re.sub(r'\n\s*\n+','\n\n',s)
    name=os.path.basename(f).replace('.html','').replace('_fs','')
    open(f'txt/{name}.txt','w',encoding='utf-8').write(s)
for f in glob.glob('raw/*.pdf'):
    b=os.path.basename(f); m=re.search(r'(\d{4})',b)
    name=(m.group(1) if (m and b[:4].isdigit() or b.startswith('final')) else b.replace('.pdf',''))
    subprocess.run(['pdftotext','-layout',f,f'txt/{name}.txt'],check=False)
PY
echo "done: $(ls txt | wc -l) text files"
