# Teste de regresie pentru screen

Rulare: `python3 -m unittest discover -s tools/screen/tests -p "test_*.py"` (sau `pytest -q tools/screen/tests`). Fără rețea.
`daily.py` le rulează primul; dacă pică unul, brief-ul zilnic nu se produce (cod de ieșire 2), iar sesiunea programată raportează eroarea în loc de companii.

Trei straturi:
- `test_screen_rules.py`: o companie sintetică pe regulă. Fiecare caz e o greșeală făcută o dată sau o regulă a cadrului care nu are voie să alunece: anul fiscal fals din cifre TTM (Amazon), split exact față de emisiune prin fuziune (Leidos) față de eroare de scară (KLA), datoria sub etichete de „notes” (Oracle), FCF după SBC în K4 (pragul 5x), ROE nedefinit la capital negativ (Moody's), capital tangibil neglijabil (Adobe, CME), plafonarea ratei de impozit, intervalul OE la capex de trei ori D&A, răscumpărările nete, rupturile de trend pe 3 față de 7 ani.
- `test_screen_fixtures.py`: fapte reale înghețate (extrase din SEC frames la 10 noiembrie 2026, `fixtures/*.json.gz`) pentru AMZN, AAPL, KLAC, ORCL, LDOS, KO, MCO, ADBE, CME, NVDA, CHKP, cu rezultatele verificate după corecturi. Fixturile nu se actualizează: o schimbare aici înseamnă că o regulă a alunecat, nu că s-a mișcat piața.
- `test_pipeline.py`: lanțul complet pe un univers mic (patru companii reale plus o bancă sintetică ce trece toate filtrele numerice și trebuie să cadă la K7), cu prețurile înlocuite; plus funcțiile brief-ului: identitatea Gordon pentru VI, inversarea creșterii implicite, benzile de preț fără cuvinte de verdict, eligibilitatea, rotația, verificarea de sănătate, formatarea românească.

Când adaugi o regulă nouă sau corectezi o eroare, adaugi întâi cazul care pică, apoi codul.
