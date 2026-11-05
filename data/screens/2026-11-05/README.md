# Scanarea din 5 noiembrie 2026: S&P 500 (inclusiv Dow 30) și emitenții listați pe Nasdaq

Întrebarea: ce companii din cercul de competență al utilizatorului (tehnologie, securitate cibernetică, fintech și domenii înrudite) trec filtrele de respingere rapidă K1 la K7 ale cadrului SixGates v2.3 și au, în plus, un indicator de preț care nu le exclude din start?

Aritmetică cu surse și judecăți atribuite, nu sfat de investiții. Pragurile sunt parametri propuși (secțiunea 13 din cadru), nu reguli ale lui Buffett sau Munger.

## Pași și fișiere

1. `fetch_frames.py`: descarcă din SEC XBRL frames API (https://data.sec.gov/api/xbrl/frames/...) câte o valoare pe companie și perioadă pentru 29 de concepte de flux (CY2014 la CY2026) și 24 de concepte de bilanț (toate trimestrele CY2014Q1I la CY2026Q4I); 1.781 de cadre, 2,38 milioane de fapte, fiecare cu numărul depunerii (`accn`). Baza `frames.db` (360 MB) nu este versionată; se reface cu scriptul în circa 6 minute.
2. `universe.json`: 3.798 de CIK-uri = constituenții S&P 500 (503 simboluri, 500 CIK-uri, din `datasets/s-and-p-500-companies` pe GitHub, cu sectorul GICS) plus toți emitenții cu listare Nasdaq din `company_tickers_exchange.json` al SEC (3.453 CIK-uri). Dow 30 este inclus în S&P 500.
3. `screen.py`: aliniază exercițiile fiscale după data de sfârșit a faptului (nu după eticheta cadrului), ia ultimele zece exerciții și calculează K1 (sub 7 exerciții sau peste 2 ani cu pierdere), K3 (ROE median pe capitalul de început de an sub 12%), K4 (datorie netă peste 5 × (CFO minus capex) sau acoperirea dobânzilor sub 3), K5 (CAGR acțiuni diluate peste 2% pe an pe 5 ani sau compensație în acțiuni peste 10% din venituri), indiciile K2 (R&D peste 15% din venituri, abatere a veniturilor peste 20% într-un an). Salturile de 1,5 la 20 ori în seria de acțiuni sunt tratate ca split sau eroare de scară și ajustate, cu marcaj. Rezultat: `screen_all.csv`, `funnel.json`.
4. `sic_lookup.py`: codul SIC, sfârșitul exercițiului și formularele anuale (10-K sau 20-F) din API-ul submissions al SEC, pentru companiile care trec K1, K3, K4, K5. Rezultat: `sic.json`.
5. `rank_circle.py`: K7 (bănci, asigurători, REIT-uri, societăți de achiziție scoase) și restrângerea la cerc (coduri SIC și subindustrii GICS pentru software, internet, servicii IT, semiconductori, hardware, rețele, distribuție IT, comerț online, plăți, burse și date financiare, finanțare de consum, brokeri, consultanță); ordonare după indicatori de calitate (fără scor afișat); preț de la Yahoo Finance pentru primele 40. Rezultat: `ranked.csv`, `ranked.json`.
6. Finaliștii au fost reverificați din `companyfacts` (depuneri 10-K sau 20-F) cu extractorul din `spike/sec_facts.py` și convertiți în fișiere de analiză pentru dashboard cu `tools/from_spike.py`: `data/analyses/{CHKP,ADBE,ACN,FDS,FICO,INTU}/2026-11-05_v1.json`. `finalists.json` conține indicatorul de preț: OE_jos și OE_sus din ultimul exercițiu, acțiunile de pe coperta ultimei depuneri (dei:EntityCommonStockSharesOutstanding), prețul Yahoo Finance din 5 noiembrie 2026, randamentul OE față de DGS10 (FRED, 4,95% la 3 noiembrie 2026), creșterea implicită pe zece ani la r = 6% și r = 8%, grila VI (r 6, 8, 10%; g 0, 4, 8%; creștere terminală 2,5%).

## Pâlnia

| Pas | Companii |
| --- | --- |
| Univers (S&P 500 sau listare Nasdaq) | 3.798 |
| Cu fapte XBRL anuale (depun 10-K sau 20-F în US GAAP) | 3.230 |
| K1 trece (cel puțin 7 exerciții, cel mult 2 ani cu pierdere) | 1.016 |
| și K3 trece (ROE median cel puțin 12%) | 565 |
| și K4 trece (datorie netă cel mult 5 × FCF, acoperire cel puțin 3) | 401 |
| și K5 trece (diluare cel mult 2% pe an, SBC cel mult 10% din venituri) | 332 |
| în cercul utilizatorului, după K7 | 104 |
| cu indicator de preț sub pragul propus (preț sub 0,5 × VI_jos la g plafonat 8%, r 6%) și fără semnal de excludere | 6 reverificate, 3 prezentate |

## Limite cunoscute

Cadrele SEC conțin doar fapte fără dimensiuni; companiile care raportează acțiunile pe clase (Visa) rămân fără CAGR al acțiunilor. Capexul total din OE_jos penalizează companiile în plin ciclu de investiții (Microsoft, Amazon). Emitenții străini cu IFRS nu apar (ASML). Prețul este de la un vendor, nu din depuneri. Nicio cifră nu a fost estimată: ce lipsește este „lipsă” sau „neclar”.
