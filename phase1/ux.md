# SixGates, UX v1 (faza 1)

Autor: UX, echipa de patru agenți (PM, QA, Dev, UX). Stare: propunere pentru review cu product owner-ul. Surse: recipe.md și requirements_v0.md (secțiunile 2, 3, 5, 6, 7). Convenții: textele de interfață din wireframes sunt în engleză (limba principală), echivalentele românești sunt în secțiunea 6; toate cifrele din wireframes sunt exemple fictive, marcate „ex." sau „exemplu"; compania „Example Co (EXC)" este inventată; cadrele de telefon au 42 de caractere lățime, cele de desktop 88.

## 1. Principii de interfață

Fiecare principiu de acuratețe (P1 la P10, requirements secțiunea 2) are o regulă de interfață și o afordanță concretă. UX poate bloca orice ecran care încalcă una dintre ele.

**P1 Proveniență pe fiecare cifră.** Regulă: nicio cifră fără id de proveniență nu se randează. Afordanță: fiecare cifră este un „number chip" (buton) cu marcaj de registru; atingerea deschide fișa de proveniență (W4). O cifră sosită fără proveniență randează un placeholder de eroare („provenance missing, issue #n"), nu cifra. Valorile introduse manual (cotă de piață, retenție, import BVB) au proveniență „manual": document, pagină, cine, când.

**P2 Formula vizibilă.** Regulă: orice valoare calculată are formula în pagină, nu în tooltip. Afordanță: „formula block" sub fiecare tabel sau valoare: expresia, intrările ca chips cu proveniența lor, id și versiune de formulă, starea testului cu rezultat cunoscut („known-result test: See's 2007: pass").

**P3 Fapte, calcule, judecăți.** Regulă: trei registre vizuale; un rând, chip sau secțiune aparține unui singur registru. Afordanță: marcaje fixe, literă plus formă plus etichetă: F în pătrat (fact, din raport), C în cerc (calculation, din formulă), J în romb (judgment, om sau AI confirmat de om); culoarea este secundară. Într-o pagină de poartă secțiunile vin în ordinea fapte, calcule, judecăți. O judecată singură nu trece o poartă: regula verdictului cere și pragurile cantitative.

**P4 Niciun substitut tăcut.** Regulă: lipsa se afișează, nu se umple. Afordanță: celula „missing: [motiv]" sau „needs verification (issue #n)"; niciodată gol, zero sau liniuță. „n/a" este distinct: „nu se aplică prin definiție" (acoperirea dobânzilor când datoria este zero).

**P5 Ipoteze fixe și vizibile.** Regulă: valorile derivă dintr-un set de ipoteze versionat, afișat în antet; orice modificare a utilizatorului produce un scenariu cu diff, niciodată o valoare. Afordanță: butonul se numește „Try a scenario", nu „Edit"; panoul de scenarii (W3) arată valoarea fixă lângă scenariu, cu eticheta „scenario only". Setul de ipoteze aparține registrului J (alegere umană) și poartă versiunea.

**P6 Reproductibilitate.** Regulă: fiecare ecran de companie arată versiunea analizei („working" sau „v3 frozen 2026-10-30"). Afordanță: „Freeze version" pe scorecard; versiunile vechi se deschid doar în citire, cu banner; CSV-ul poartă versiunea.

**P7 Sursa primară bate vendorul.** Regulă: valoarea afișată este cea din sursa primară (EDGAR, ESEF, import validat); vendorul apare doar ca verificare încrucișată. Afordanță: în fișă, rândul „cross-check: vendor [valoare], diff [x%]"; peste toleranță, chip-ul primește marcajul „~" și o intrare în jurnal. Prețurile și randamentele obligațiunilor au ca sursă vendorul sau banca centrală (EODHD, FRED, BCE, BNR), cu data.

**P8 Zece ani sau marcat.** Regulă: fiecare serie afișează „n of 10 fiscal years"; sub 10, poarta randează „insufficient data" și nu poate avea alt verdict. Afordanță: coloanele lipsă rămân în tabel cu „missing" și motiv (W7); calculele pe anii disponibili se afișează marcate „partial".

**P9 Erori vizibile.** Regulă: fiecare problemă de date are id, severitate, cifra afectată, efectul asupra porților și stare. Afordanță: contorul „issues n" în antetul companiei și în tab-ul global; din jurnal se ajunge la chip și invers (W6).

**P10 Limbaj de fapte.** Regulă: nicio culoare, săgeată, glif sau cuvânt care implică o acțiune. Afordanță: verdicte cu glife monocrome și etichete text; diferența preț/valoare ca procent cu direcția în cuvinte („price above range high by 18.6%"); lint de cuvinte interzise (secțiunea 6) pe toate textele, inclusiv drafturile AI.

### Vocabularul verdictelor

| EN | RO | Glif | Aspect | Când |
|---|---|---|---|---|
| pass | trece | ✓ | badge plin, ton „ink" | pragurile atinse și toate judecățile obligatorii confirmate |
| fail | pică | ✕ | badge contur | un prag neatins sau judecata confirmată „too hard" |
| needs judgment | necesită judecată | ◐ | badge pe jumătate plin | cifre complete, cel puțin o judecată obligatorie neconfirmată |
| insufficient data | date insuficiente | ▢ | badge contur punctat | sub 10 ani sau o intrare obligatorie lipsă |

Precedență: insufficient data, apoi needs judgment, apoi fail sau pass din praguri. Toate patru folosesc aceeași scară neutră de gri, fără roșu sau verde. Nu există scor compozit și nici verdict global: scorecard-ul doar numără verdictele pe porți („2 pass, 2 needs judgment, 1 fail").

## 2. Arhitectura informației și navigarea

### Ecrane

| Ecran | Conținut v1 | Rută |
|---|---|---|
| Companies | listă, căutare, adăugare, stare ingestie (W8) | /companies |
| Company scorecard | antet, șase porți plus sub-rândul Survival, acțiuni (W1) | /companies/{market}/{ticker} |
| Gate detail 2, 3, Survival, 4, 5 | fapte, calcule, judecăți, blocuri de formulă, regula verdictului (W2, W3, W7) | .../gates/{2, 3, survival, 4, 5} |
| Provenance card | fișa unei cifre, overlay cu adresă proprie (W4) | .../provenance/{factId} |
| Judgment editor | draft AI, citări, confirmare (W5); coadă globală | .../judgments/{id}; /judgments |
| Decision dossier (minim v1) | textele porții 2, judecățile confirmate, versiunile înghețate cu „price I would pay" și prețul la data înghețării | .../dossier |
| Data issues log | jurnalul pe companie (W6) și global | .../issues; /issues |
| Assumptions and scenarios | seturi de ipoteze versionate; scenariile companiei | /assumptions/v/{n}; .../scenarios/{id} |
| Settings and users | limbă, utilizatori și roluri, surse de date | /settings; /settings/users |

Gate 1 și gate 6 au rutele rezervate (.../gates/1, .../gates/6) și randează starea „phase 2". Versiunile înghețate se citesc cu prefixul .../v/{n} înaintea oricărei sub-rute (ex. /companies/us/EXC/v/3/gates/5). Limba este o preferință de utilizator, nu parte din URL. Survival este sub-poartă a porții 3, cu ecran și verdict propriu.

### Navigare pe telefon

Bară de tab-uri jos cu patru destinații: Companies, Judgments (cu număr), Issues (cu număr), More (Assumptions, Settings, Users, Export). Justificare: cele două cozi care cer atenție umană (judecăți neconfirmate, probleme de date) rămân vizibile permanent cu contor, ceea ce operaționalizează P3 și P9; un drawer le-ar ascunde și ar costa o atingere în plus; patru destinații încap în zona degetului mare. În interiorul unei companii navigarea este în stivă: scorecard, poartă, fișă de proveniență ca bottom sheet, editor de judecată ca ecran complet. Fiecare pagină de poartă are „gate strip" sus (2 | 3 | S | 4 | 5) pentru deplasare laterală fără întoarcere la scorecard.

### Navigare pe desktop

Sidebar stânga cu destinațiile globale și, când o companie este deschisă, arborele ei (Scorecard, Gate 2, Gate 3, Survival, Gate 4, Gate 5, Gate 6 phase 2, Dossier, Scenarios, Issues). Fișa de proveniență se deschide ca panou lateral dreapta, niciodată modal, ca tabelul să rămână vizibil. Pe tabelul de 10 ani sidebar-ul se restrânge automat.

## 3. Fluxuri

### F1. Analiza unei companii noi, de la ticker la verdict

1. Pe Companies, „Add company", ticker sau nume. Sistem: caută în lista EDGAR, registrul ESEF și lista BVB; afișează potrivirile cu piață, nume, CIK sau LEI. Ramuri: nicio potrivire, „No issuer found for [text]. Check the ticker or the market."; emitent BVB fără XBRL, eticheta „assisted import required".
2. Utilizatorul alege emitentul. Sistem: creează compania „queued", pornește ingestia și deschide scorecard-ul în așteptare: antetul se completează pe măsură ce sosesc datele, rândurile porților arată skeleton „waiting for data".
3. Așteptare: pași vizibili („step 3 of 6: XBRL facts, 7 of 10 years found"), regiune live pentru cititorul de ecran; utilizatorul poate pleca, lista păstrează starea. Ramură: un pas eșuează, „ingestion failed at step k: [motiv]", problemă în jurnal, buton „retry".
4. Ingestia se încheie. Sistem: calculează porțile 3, Survival și 5 (fapte și calcule); porțile 2 și 4 randează „needs judgment" pentru că cer intrări umane. Ramură P8: sub 10 ani, fiecare poartă care depinde de serii de 10 ani randează „insufficient data: n of 10 years" (W7) cu acțiunea „Start assisted import".
5. Utilizatorul parcurge porțile în ordine (2, 3, S, 4, 5), scrie textele porții 2 (F5), confirmă judecățile (F3).
6. Verdict: scorecard-ul arată cele șase verdicte și numărătoarea lor, fără scor compozit, cu regula sub tabel. „Freeze version" creează v1 cu datele și sursele înghețate (P6).

### F2. Proveniența unei cifre, până la raport

1. Atingerea unui chip deschide fișa (W4): valoare, unitate, perioadă, etichetă XBRL depusă, concept canonic și regula de mapare, raport, link, data extragerii, retratare, verificare încrucișată cu divergența.
2. „Open filing" deschide documentul la EDGAR sau filings.xbrl.org în filă nouă; unde vizualizatorul suportă ancore de fapt (inline XBRL) linkul ajunge la fapt, altfel la document, cu situația financiară și denumirea liniei depuse.
3. Ramuri: chip de calcul, fișa arată formula cu chips-urile de intrare, fiecare cu fișa ei, până la fapte; valoare retratată, ambele valori (depusă, retratată), care se folosește și de ce (regula: ultimul raport, marcat); divergență peste toleranță, banner „sources diverge by x%" cu ambele valori și link la problemă; import manual, sursa este PDF-ul cu pagina, cine a validat și când.
4. Erori: fără proveniență, chip-ul nu a fost randat (placeholder cu id de problemă); link mort, „Filing link unreachable on [date]" cu numărul accession pentru căutare manuală.

### F3. Revizuirea unei judecăți propuse de AI

1. Intrare din coada Judgments sau din blocul J al porții. Sistem: deschide editorul (W5) cu întrebarea, draftul marcat „proposed by AI, [model], [dată]" și citările.
2. Fiecare citare arată citatul, raportul, locatorul (pagină, secțiune) și verificarea automată: „verified" (citatul există textual în raport) sau „not in filing".
3. Lint: cuvintele interzise sunt evidențiate; confirmarea e blocată până la corectare.
4. Acțiuni: Confirm („confirmed by [user], [date]", J plin); Edit (text editabil, citările rămân, marcaj „edited by a human from an AI draft"); Reject (motiv obligatoriu; slotul revine la „needs judgment", draftul rămâne în istoric).
5. Poarta nu poate fi „pass" cât există o judecată obligatorie neconfirmată; după confirmare, verdictul se recalculează din regula porții, care cere și pragurile cantitative (P3); dacă datele sunt insuficiente rămâne „insufficient data".
6. Ramuri: citare „not in filing" blochează Confirm până e corectată sau eliminată; serviciu de verificare indisponibil, utilizatorul deschide raportul și marchează „verified manually by [user]", înregistrat ca atare; fără nicio citare, judecățile care cer dovezi (poarta 4) nu se pot confirma.

### F4. Schimbarea unei ipoteze devine scenariu, nu valoare

1. În poarta 5, blocul de intrări arată setul fix „assumptions v2": prag total r (obligațiune lungă plus primă, implicit 10%), g în primii ani plafonat la CAGR istoric OE, g terminal 2 la 3%, marja după categorie, metoda capex de întreținere.
2. „Try a scenario" deschide panoul cu valorile fixe precompletate și editabile.
3. Utilizatorul schimbă, de exemplu, g terminal de la 2,5% la 3,0%. Sistem: „Scenario (unsaved)" cu diferențele („g terminal: 2.5% to 3.0%") și rezultatele lângă valoarea fixă, etichetate „scenario only"; verdictul, „price I would pay" și scorecard-ul rămân pe setul fix.
4. Salvare cu nume și motiv obligatoriu; scenariul apare în Assumptions and scenarios cu autor și dată; nu schimbă niciodată verdictul.
5. Ramuri: scenariu în afara limitelor conservatoare (g peste CAGR istoric, g terminal peste 3%), permis dar marcat „outside the conservative bounds" și nepromovabil la fix; setul fix se schimbă doar în Settings > Assumptions, ca versiune nouă v3, aplicată la analizele noi după recalcul și afișată în antete, versiunile înghețate păstrează v2; intrare lipsă (OE), scenariul arată „insufficient data", nu zero.

### F5. Teza de un paragraf și cele trei moduri de a muri (poarta 2)

1. Poarta 2 arată indiciile de stabilitate pe 10 ani (venituri, marje, OE: coeficient de variație, ani cu pierdere, abaterea de la trend) ca fapte și calcule, apoi trei intrări umane obligatorii: descrierea afacerii peste zece ani, trei moduri în care afacerea poate muri cu probabilități, paragraful de motivare. Starea rămâne „needs judgment" până sunt toate confirmate.
2. „Write" la descrierea pe zece ani: editor cu contor (un paragraf, ghid 80 la 200 de cuvinte, limită moale), lint, salvare automată ca draft, „Confirm" cu autor și dată.
3. Cele trei moduri de a muri: trei rânduri cu text, probabilitate (procent, o zecimală) și link opțional la o dovadă (chip sau secțiune de raport); probabilitățile sunt independente, nu trebuie să însumeze 100%.
4. Paragraful de motivare: același editor.
5. După cele trei confirmări, utilizatorul alege verdictul porții 2 ca judecată explicită: „I can describe it in ten years" (pass), „too hard" (fail), „undecided" (needs judgment). P8 are prioritate: sub 10 ani de venituri verdictul rămâne „insufficient data", textele se păstrează.
6. Erori: text gol, Confirm inactiv; cuvinte interzise, lint blochează; conexiune pierdută, draft salvat local, marcat „unsynced".

### F6. Export CSV

1. Din scorecard sau meniul companiei, „Export CSV".
2. Opțiuni: domeniu (compania sau toate), conținut (facts, calculations, judgments, all), versiunea (working sau v{n}), separator zecimal (punct implicit), scara (as filed).
3. Sistem: un rând pe valoare: company, fiscal period, concept, value, unit, scale, register, status, status reason, provenance id, filing accession, filing url, extracted at, formula id and version, assumption set version, analysis version, frozen. Judecățile ies cu autor, dată, stare, citări și starea verificării.
4. Descărcare; pe telefon share sheet; numele fișierului conține compania, versiunea și data.
5. Ramuri: versiune de lucru, coloana „frozen = no" și avertisment; selecție goală, „Nothing to export for this selection"; valorile „missing" ies ca rând cu status și motiv, niciodată zero.

### F7. Re-subscriere anuală cu diff (previzualizare faza 2)

1. Declanșare: memento anual (n8n) sau „Re-underwrite" manual.
2. Sistem: ingerează noul exercițiu, creează v{n+1} ca working și deschide diff-ul: pe poartă, verdictul înainte și după; pe cifră, valoarea veche și nouă cu raportul sursă; retratările marcate; judecățile din v{n} marcate „from v{n}, needs re-confirmation", nu se preiau automat.
3. Utilizatorul reconfirmă sau editează judecățile, scrie paragraful anual (ce s-a schimbat, greșeli); dosarul primește o intrare nouă; declanșatoarele de re-evaluare din poarta 6 apar ca fapte („ROIC below threshold for 2 consecutive years"), niciodată ca instrucțiuni.
4. „Freeze version" creează v{n+1}.
5. Ramură: raportul nu e depus, „Fiscal year [X] not filed yet; expected [date]"; nicio cifră nu se estimează.

## 4. Wireframes

Legendă: [F] [C] [J] marcaje de registru; [v pass], [x fail], [? needs judgment], [.. insufficient data] verdicte în ASCII (în produs: ✓ ✕ ◐ ▢); „~" sursă divergentă; „J n" judecăți neconfirmate; toate cifrele sunt exemple.

### W1. Company scorecard, telefon

```
+----------------------------------------+
| < Companies            v3 frozen  menu |
| Example Co   NYSE: EXC   FYE 31 Dec    |
| data as of 2026-10-30   assumptions v2 |
| issues 2    judgments pending 3        |
| values: exemplu                        |
+----------------------------------------+
| 1 Portfolio                 [phase 2]  |
|   not in this version                  |
+----------------------------------------+
| 2 Understand        [? needs judgment] |
|   10y series ok, thesis missing    J 3 |
+----------------------------------------+
| 3 Returns on capital          [v pass] |
|   tangible ROIC 10y low 28.1% ex.  J 0 |
|   3a Survival                 [v pass] |
|   net debt / OE 1.4x ex.           J 0 |
+----------------------------------------+
| 4 Moat              [? needs judgment] |
|   ROIC persistence 10 of 10 years  J 2 |
+----------------------------------------+
| 5 Price under value           [x fail] |
|   price above range high 18.6% ex. J 0 |
+----------------------------------------+
| 6 Keep                      [phase 2]  |
|   dossier entries 0                    |
+----------------------------------------+
| 2 pass, 2 needs judgment, 1 fail       |
| [Freeze version]   [Export CSV]        |
+----------------------------------------+
| Companies  Judgments 3  Issues 2  More |
+----------------------------------------+
```

Antetul: nume, piață și ticker, sfârșitul exercițiului, prospețimea datelor, versiunea analizei, versiunea ipotezelor, cele două contoare. Fiecare rând de poartă: număr și nume, badge de verdict, motivul de un rând generat din regulă, numărul judecăților neconfirmate. Atingerea rândului deschide pagina porții.

### W1. Company scorecard, desktop

```
+-------------------+------------------------------------------------------------------+
| SixGates          | Example Co   NYSE: EXC   FYE 31 Dec   data as of 2026-10-30      |
| Companies         | analysis v3, frozen 2026-10-30   assumptions v2   values: exemplu|
| Judgments 3       +------------------------------------------------------------------+
| Issues 2          | gate                 verdict           reason                 J  |
| Assumptions       | 1 Portfolio          phase 2           not in this version       |
| Settings          | 2 Understand         ? needs judgment  10y ok, thesis missing  3 |
| ----------------- | 3 Returns on capital v pass            tangible ROIC 10y low   0 |
| EXC Example Co    |                                        28.1% ex.                 |
|  Scorecard        | 3a Survival          v pass            net debt / OE 1.4x ex.  0 |
|  Gate 2           | 4 Moat               ? needs judgment  ROIC persistence 10/10  2 |
|  Gate 3           | 5 Price under value  x fail            price above range high  0 |
|  Survival         |                                        by 18.6% ex.              |
|  Gate 4           | 6 Keep               phase 2           dossier entries 0         |
|  Gate 5           +------------------------------------------------------------------+
|  Gate 6 (phase 2) | [Freeze version]  [Export CSV]  [Re-underwrite: phase 2]         |
|  Dossier          |                                                                  |
|  Scenarios        | rule: a gate passes only when facts and calculations meet the    |
|  Issues 2         | thresholds and every mandatory judgment is confirmed by a person |
|                   | no composite score is computed                                   |
+-------------------+------------------------------------------------------------------+
```

### W2. Gate 3, telefon

```
+----------------------------------------+
| < EXC   Gate 3 Returns on capital      |
| gates: 2 | 3 | S | 4 | 5    v3 frozen  |
| verdict [v pass]   10 of 10 years      |
| USD millions as filed   values: ex.    |
+----------------------------------------+
| [F] facts and [C] calculations, 10y    |
| sticky metric column, swipe for        |
| FY2016 to FY2022   [focus one metric]  |
+----------------+-------+-------+-------+
| metric         | FY2023| FY2024| FY2025|
+----------------+-------+-------+-------+
| F revenue      | 45,754|47,061~| 47,900|
| C owner earn.  |  9,120|  9,870| 10,110|
| C ROIC tangible|  32.1%|  33.8%|  33.5%|
| C incr. ROIC 5y|  24.0%|  25.1%|  23.7%|
| C capex/sales  |   4.1%|   4.3%|   4.0%|
+----------------+-------+-------+-------+
| ~ vendor differs by 2.3%, issue #14    |
+----------------------------------------+
| [C] formula F-ROIC-T v1.2              |
| tangible ROIC = NOPAT / (NWC + net     |
| PP&E + other operating assets, minus   |
| excess cash)                           |
| NOPAT = operating profit x (1 - tax)   |
| inputs FY2025: [op. profit] [tax rate] |
| [NWC] [net PP&E] [cash] (chips)        |
| known-result test: See's 2007: pass    |
+----------------------------------------+
| [C] category, 2007 letter: good        |
| incremental ROIC 10y 24.0% ex.         |
| thresholds (assumptions v2):           |
| great: > 30% and capex/sales low       |
| good: cost of capital + 5 pts to 30%   |
| gruesome: below cost of capital with   |
| growing capital                        |
+----------------------------------------+
```

Pe telefon tabelul păstrează metricile pe rânduri (un rând, un registru, P3) și anii pe coloane: prima coloană este fixă, restul se derulează orizontal, cu umbră la margine ca indiciu. Transpunerea (ani pe rânduri) este exclusă pentru că ar amesteca F și C în același rând. „Focus one metric" comută pe o listă verticală de 10 rânduri (an, valoare, chip) pentru o singură metrică. Fiecare celulă este un chip; celulele lipsă afișează „missing" cu motiv.

### W2. Gate 3, desktop (sidebar restrâns)

```
+--------------------------------------------------------------------------------------+
| EXC Example Co   Gate 3 Returns on capital   verdict: v pass   10 of 10 years   v3   |
| USD millions as filed, FY ends 31 Dec, values: exemplu             [focus one metric]|
+----------------+------+------+------+------+------+------+------+------+------+------+
| metric         |FY2016|FY2017|FY2018|FY2019|FY2020|FY2021|FY2022|FY2023|FY2024|FY2025|
+----------------+------+------+------+------+------+------+------+------+------+------+
| F revenue      |41,863|35,410|31,856|37,266|33,014|38,655|43,004|45,754|47,061|47,900|
| C owner earn.  | 7,210| 7,015| 6,980| 7,900| 7,350| 8,420| 8,900| 9,120| 9,870|10,110|
| C ROIC tangible| 31.4%| 30.9%| 30.2%| 31.0%| 29.8%| 31.5%| 32.0%| 32.1%| 33.8%| 33.5%|
| C incr. ROIC 5y|  n/a |  n/a |  n/a |  n/a | 22.0%| 23.1%| 23.9%| 24.0%| 25.1%| 23.7%|
| C capex/sales  |  4.5%|  4.0%|  3.9%|  5.4%|  3.5%|  3.6%|  3.3%|  4.1%|  4.3%|  4.0%|
+----------------+------+------+------+------+------+------+------+------+------+------+
| F = fact from filing (tap for provenance)   C = calculation (formula shown below)    |
| n/a = window not available by definition (5-year difference needs FY minus 5)        |
+--------------------------------------------------------------------------------------+
| C formula F-ROIC-T v1.2  tangible ROIC = NOPAT / (NWC + net PP&E + other operating   |
|   assets, minus excess cash); NOPAT = operating profit x (1 - effective tax rate)    |
|   inputs FY2025: [operating profit] [effective tax rate] [NWC] [net PP&E] [cash]     |
|   known-result test: See's 2007 (82 on 40): pass   goodwill excluded (quality view)  |
| C category per 2007 letter: good (incremental ROIC 10y 24.0% ex.)                    |
|   thresholds: great > 30% and capex/sales low; good: cost of capital + 5 pts to 30%; |
|   gruesome: below cost of capital with growing capital. Thresholds: assumptions v2   |
+--------------------------------------------------------------------------------------+
```

În aceeași pagină urmează blocurile pentru ROIC incremental 10 ani, conversia în numerar, identitatea creșterii (g = reinvestire x ROIC lângă creșterea observată) și ROE pe capital de început de an cu avertismentul din 1977, fiecare cu propriul formula block.

### W3. Gate 5, telefon

```
+----------------------------------------+
| < EXC   Gate 5 Price under value       |
| gates: 2 | 3 | S | 4 | 5      working  |
| verdict [x fail]    values: exemplu    |
+----------------------------------------+
| [F] inputs                             |
| owner earnings FY2025 [10,110 USD m] F |
| long bond yield 10y     [4.21%]      F |
|   FRED DGS10, 2026-10-30               |
| current price           [73.30 USD]  F |
|   EODHD close 2026-10-30               |
| shares outstanding      [4,302 m]    F |
|   10-K FY2025 cover page               |
| assumptions v2 (fixed)               J |
|   hurdle r = 4.21% + 5.79% = 10.0%     |
|   g years 1 to 10 <= OE CAGR 10y 5.2%  |
|   g terminal 2.0% to 3.0%              |
|   maint. capex = min(capex, D&A)       |
+----------------------------------------+
| [C] results    formula F-DCF-OE v1.0   |
| intrinsic value per share              |
|   52.10 to 61.80 USD (low to high)     |
| reverse DCF implied g: 7.9%            |
|   above OE CAGR 10y of 5.2%            |
| margin required: 30% to 50%            |
|   default (business) until gate 4 J    |
| price I would pay                      |
|   26.05 to 43.26 USD                   |
| current price vs range high: +18.6%    |
| OE yield 3.2% vs 10y bond 4.21%        |
| alert at <= 43.26 USD: not active      |
| [show formula and inputs]              |
+----------------------------------------+
| [C] scenarios         [Try a scenario] |
| fixed (v2)      52.10 to 61.80 USD     |
| S1 g term. 3.0%  user A, 2026-10-30    |
|   55.30 to 66.20 USD   diff +6% / +7%  |
|   scenario only; verdict unchanged     |
+----------------------------------------+
```

Pe desktop: intrările în coloana stângă, rezultatele în dreapta, scenariile sub ambele. Marja cerută depinde de judecata „franciză sau afacere" din poarta 4; până la confirmare se folosește marja mai largă (30 la 50%), etichetată „default" (întrebarea 3).

### W4. Provenance card (bottom sheet pe telefon, panou dreapta pe desktop)

```
+----------------------------------------+
| provenance                         [x] |
| [F] revenue FY2025          values ex. |
+----------------------------------------+
| value         47,900 USD millions      |
| period        FY2025, 2025-01-01 to    |
|               2025-12-31, 52 weeks     |
| tag as filed  us-gaap:Revenues         |
| canonical     revenue (map v4 / R12)   |
| filing        10-K FY2025, 2026-02-20  |
| acc. no.      [accession number]       |
| link          [open filing at EDGAR]   |
| extracted at  2026-10-30 07:12 UTC     |
| restated      no later filing yet      |
| cross-check   vendor 47,900, diff 0.0% |
| status        ok                       |
+----------------------------------------+
| used in: [OE 2025] [capex/sales 2025]  |
| [report an issue]      [copy link]     |
+----------------------------------------+
```

Varianta pentru un chip de calcul înlocuiește rândurile de raport cu formula (id, versiune), chips-urile de intrare, versiunea setului de ipoteze și starea testului. Varianta pentru fapt manual: document, pagină, persoana, data validării. „Copy link" copiază adresa fișei (deep link pentru parteneri).

### W5. Judgment editor

```
+----------------------------------------+
| < Gate 4 Moat        judgment 2 of 3   |
| question: moat type and direction      |
+----------------------------------------+
| [J] proposed by AI   claude 2026-10-30 |
| status: awaiting human confirmation    |
+----------------------------------------+
| draft (text ex.):                      |
| The brand and the bottler network act  |
| as a worldwide brand moat [1]. Gross   |
| margin held between 58% and 61% over   |
| ten years [2]. Direction: stable.      |
+----------------------------------------+
| citations                              |
| [1] 10-K FY2025, Item 1, p. 4          |
|     "Our brands ... more than 200      |
|     countries"           [v verified]  |
| [2] gate 4 evidence: gross margin 10y  |
|     calc C-GM v1          [v verified] |
| [3] 10-K FY2025, p. 31                 |
|     "pricing initiatives..."           |
|     [! not in filing: fix or remove]   |
+----------------------------------------+
| lint: 0 forbidden words                |
| rule: this gate waits for a human. AI  |
| cannot confirm; verdict stays needs    |
| judgment until a person confirms.      |
+----------------------------------------+
| [Confirm: blocked] [Edit] [Reject...]  |
+----------------------------------------+
```

Pe desktop draftul stă în stânga și citările în dreapta, cu citatul evidențiat în raport la click. Confirm rămâne blocat cât timp o citare nu este verificată sau lint-ul găsește un cuvânt interzis.

### W6. Data issues log

```
+----------------------------------------+
| < EXC   Data issues: 2 open, 5 closed  |
| filter: [open] [all]   severity: [all] |
+----------------------------------------+
| #14   high    open     2026-10-30      |
| revenue FY2024: vendor diverges 2.3%   |
| primary kept, vendor value flagged     |
| affects: gate 2, gate 3 (no block)     |
| [open number]  [resolve...]            |
+----------------------------------------+
| #15   medium  open     2026-10-30      |
| shares outstanding: cover page date    |
| 2026-02-13 differs from FYE 2025-12-31 |
| affects: gate 5 per-share values       |
| [open number]  [resolve...]            |
+----------------------------------------+
| #9    high    closed   2026-10-29      |
| capex FY2016: custom tag mapped by     |
| rule R7, validated by user A           |
| affects: OE FY2016 (resolved)          |
+----------------------------------------+
```

Fiecare problemă: id, severitate, stare, dată, cifra afectată (link la chip), efectul asupra porților (blochează sau nu verdictul), acțiuni. Rezolvarea cere o notă și persoana; problemele închise rămân în istoricul versiunii.

### W7. Stare „insufficient data" pentru o poartă

```
+----------------------------------------+
| < EXR   Gate 3 Returns on capital      |
| gates: 2 | 3 | S | 4 | 5      working  |
| verdict [.. insufficient data]         |
+----------------------------------------+
| why: 5 of 10 fiscal years available    |
| FY2021 to FY2025 from ESEF (XBRL)      |
| FY2016 to FY2020: missing, pre-ESEF    |
| (PDF only, assisted import not done)   |
|                                        |
| rule: a gate needs 10 fiscal years     |
| (P8). It cannot pass, fail or be       |
| judged on fewer. Calculations below    |
| use the available years and are        |
| marked partial.                        |
+----------------------------------------+
| [Start assisted import FY2016 to 2020] |
| [Log a data issue]                     |
+----------------------------------------+
| 10-year table: partial, 5 of 10        |
| FY2016 to FY2020 cells: missing        |
| (reason: not in ESEF, see issue #3)    |
+----------------------------------------+
```

### W8. Companies, cu căutare și stare de ingestie

```
+----------------------------------------+
| Companies                     [+ Add]  |
| [search ticker or name            ]    |
| filter: market [all]   status [all]    |
+----------------------------------------+
| EXC  Example Co         US   FYE Dec   |
| v3 frozen 2026-10-30   J 3   issues 2  |
| gates: 2 ? | 3 v | S v | 4 ? | 5 x     |
+----------------------------------------+
| EXR  Exemplu SA         BVB  FYE Dec   |
| ingesting: step 3 of 6, XBRL facts     |
| 5 of 10 years found     [details]      |
+----------------------------------------+
| EXE  Exemple SE         EU   FYE Mar   |
| working    J 5   issues 0              |
| gates: 2 ? | 3 .. | S v | 4 ? | 5 ..   |
+----------------------------------------+
| EXF  Example Foods      US   FYE Sep   |
| ingestion failed at step 2: EDGAR      |
| rate limit; [retry]   issue #21        |
+----------------------------------------+
| Companies  Judgments 8  Issues 3  More |
+----------------------------------------+
```

Pașii de ingestie, identici în listă și în scorecard: 1 resolve issuer, 2 filings list, 3 XBRL facts, 4 normalise and cross-check, 5 prices and yields, 6 compute. Lista goală: „No companies yet. Add one by ticker or name."

## 5. Inventar de componente și stări

| Componentă | Rol | Nu se randează fără | Registru |
|---|---|---|---|
| Number chip | valoare, unitate, perioadă, marcaj, punct de stare; deschide fișa | value, unit, scale, period, register, provenanceId, status | F, C sau J |
| Verdict badge | glif plus text, fără culoare semantică | verdict code, reason, pendingJudgments, ruleId, ruleVersion | C (rezultatul regulii) |
| Register marker | literă plus formă plus etichetă text | register | toate |
| Provenance card | fișa completă a unei cifre (W4) | câmpurile de proveniență din secțiunea 10 | F, C |
| Formula block | expresie, intrări ca chips, id, versiune, test | formulaId, formulaVersion, inputIds, testStatus | C |
| Scenario diff | fix lângă scenariu, diferențe, autor, „scenario only" | baseAssumptionSetVersion, overrides, results | C (intrări J) |
| Citation block | citat, raport, locator, stare verificare, cine | quote, filing, locator, verified | J |
| Coverage indicator | „n of 10 fiscal years", ani lipsă | coverageYears, missingYears cu motiv | F |
| Status banner | versiune, înghețare, date vechi, divergență, ingestie | analysisVersion, status | n/a |

| Stare | Aspect | Unde apare | Acțiune disponibilă |
|---|---|---|---|
| loading | skeleton cu eticheta „loading [ce]"; niciodată cifră provizorie | tabele, scorecard, fișă | așteptare; regiune live |
| empty | text explicativ plus acțiunea principală | liste, scenarii, dosar | adăugare |
| insufficient data | badge punctat, motiv, acoperire, acțiune | poartă, celule, scorecard | import asistat, jurnal |
| stale data | banner „data as of [dată]; newer filing available" | antet companie | refresh ca versiune nouă |
| divergent sources | chip cu „~"; fișa arată ambele valori și toleranța | chip, fișă, jurnal | deschide problema, rezolvă |
| AI draft pending | marcaj J gol, panglică „proposed by AI"; verdict „needs judgment" | poartă, coadă Judgments | confirm, edit, reject |
| confirmed | marcaj J plin, „confirmed by [user], [dată]" | poartă, dosar | edit (creează revizie) |
| rejected | draft tăiat în istoric, motiv; slot „needs judgment" | editor, istoric | cerere draft nou |
| error | inline, cu id de problemă și retry; celulele arată „error", nu zero | oriunde | retry, jurnal |

## 6. Ghid de text (copy)

Reguli de ton: factual, la timpul prezent; imperativ doar pentru acțiuni de interfață (Confirm, Freeze), niciodată pentru decizii de investiție; fără semn de exclamare; fiecare cifră cu unitate și perioadă; direcția în cuvinte („above", „below"), fără săgeți; textul AI mereu etichetat; fără superlative; motivele verdictelor sunt șabloane cu parametri („price above range high by {pct}"), nu text liber.

| Cheie | EN | RO |
|---|---|---|
| verdict.pass | pass | trece |
| verdict.fail | fail | pică |
| verdict.needs_judgment | needs judgment | necesită judecată |
| verdict.insufficient | insufficient data | date insuficiente |
| register.fact | fact (from filing) | fapt (din raport) |
| register.calc | calculation (from formula) | calcul (din formulă) |
| register.judgment | judgment (human) | judecată (om) |
| gate.1 | Portfolio | Portofoliu |
| gate.2 | Understand the business | Înțelegi afacerea |
| gate.3 | Returns on capital | Randamente pe capital |
| gate.survival | Survival | Supraviețuire |
| gate.4 | Moat | Moat (șanțul de apărare) |
| gate.5 | Price under value | Preț sub valoare |
| gate.6 | Keep while the facts hold | Păstrezi cât țin faptele |
| judgment.ai_proposed | proposed by AI, awaiting a human | propus de AI, așteaptă un om |
| judgment.confirmed | confirmed by {user} on {date} | confirmat de {user} la {date} |
| judgment.rejected | rejected by {user}: {reason} | respins de {user}: {motiv} |
| status.missing | missing: {reason} | lipsă: {motiv} |
| status.needs_verification | needs verification (issue #{n}) | necesită verificare (problema #{n}) |
| status.na | n/a (not applicable: {reason}) | n/a (nu se aplică: {motiv}) |
| status.divergent | sources diverge by {pct} | sursele diferă cu {pct} |
| status.stale | data as of {date}; newer filing available | date la {date}; există un raport mai nou |
| status.frozen | version v{n}, frozen {date}, read only | versiunea v{n}, înghețată la {date}, doar citire |
| status.working | working version, not frozen | versiune de lucru, neînghețată |
| status.partial | partial: {n} of 10 years | parțial: {n} din 10 ani |
| ingest.running | ingesting: step {k} of {n}, {label} | ingestie: pasul {k} din {n}, {etichetă} |
| ingest.failed | ingestion failed at step {k}: {reason} | ingestia a eșuat la pasul {k}: {motiv} |
| coverage | {n} of 10 fiscal years | {n} din 10 exerciții financiare |
| btn.confirm | Confirm | Confirmă |
| btn.edit | Edit | Editează |
| btn.reject | Reject | Respinge |
| btn.freeze | Freeze version | Îngheață versiunea |
| btn.export | Export CSV | Exportă CSV |
| btn.scenario | Try a scenario | Încearcă un scenariu |
| btn.open_filing | Open filing | Deschide raportul |
| btn.report_issue | Report a data issue | Semnalează o problemă de date |
| empty.companies | No companies yet. Add one by ticker or name. | Nicio companie încă. Adaugă una după simbol sau nume. |
| empty.issues | No open data issues for this company. | Nicio problemă de date deschisă pentru această companie. |
| error.no_provenance | This number has no provenance record and is not shown (issue #{n}). | Această cifră nu are proveniență și nu este afișată (problema #{n}). |
| error.citation | Quote not found in the filing. Fix or remove it before confirming. | Citatul nu a fost găsit în raport. Corectează sau elimină înainte de confirmare. |
| rule.gate_waits | This gate waits for a human. The AI draft cannot confirm it. | Această poartă așteaptă un om. Draftul AI nu o poate confirma. |
| rule.scenario | Scenario only. The fixed value and the verdict do not change. | Doar scenariu. Valoarea fixă și verdictul nu se schimbă. |
| label.price_i_would_pay | price I would pay | prețul pe care l-aș plăti |
| label.ten_year | what the business looks like in ten years | cum arată afacerea peste zece ani |
| label.ways_to_die | three ways the business could die | trei moduri în care afacerea poate muri |
| reason.price_above | price above range high by {pct} | preț peste capătul de sus al intervalului cu {pct} |

### Lista de cuvinte interzise (lint)

Lint-ul rulează la build pe șirurile de interfață (CI pică), la salvare pe judecăți și drafturi AI (blochează Confirm) și la export pe câmpurile text (marchează). Excepție: textul dintre ghilimele al unei citări din raport.

| Interzis (EN) | Interzis (RO) | Formulare permisă |
|---|---|---|
| buy, buy now | cumpără, de cumpărat | „price below the conservative value range by 32%" |
| sell, sell trigger | vinde, de vândut | „price above the conservative value range by 18%"; „fact-based trigger: ROIC below threshold for 2 years" |
| cheap, expensive (ca verdict) | ieftin, scump | „price to value range: 0.68 (low), 0.81 (high)" |
| recommend, recommendation | recomand, recomandare | „the gate rule evaluates to pass" |
| target price | preț țintă | „price I would pay: 26.05 to 43.26 USD" |
| upside, downside | potențial de creștere, potențial de scădere | „difference between price and range high: +18.6%" |
| signal | semnal | „flag: [fact]" |
| strong buy, outperform, overweight | cumpărare puternică, supraponderare | se elimină, fără înlocuitor |
| undervalued, overvalued (ca verdict) | subevaluat, supraevaluat | „price below the range" / „price above the range" |
| rating, score, stars | rating, scor, stele | „verdict per gate; no composite" |
| bullish, bearish | optimist, pesimist (despre piață) | se elimină |
| should (plus verb de investiție) | ar trebui (plus verb de investiție) | se elimină; rămâne faptul |

## 7. Formatarea numerelor

- Scară și unitate: valorile se afișează în unitatea și scara raportului (USD millions dacă raportul este în milioane, thousands dacă în mii); scara stă în titlul tabelului și pe chip („47,061 USD m"); un tabel nu amestecă scări. Valorile pe acțiune au două zecimale.
- Monedă pe entitate: moneda de raportare așa cum a fost depusă (USD, EUR, RON), fără conversie în tabele. Când prețul este în altă monedă decât raportarea, rândul de comparație afișează cursul ca fapt cu sursă și dată („FX ECB 2026-10-30").
- Etichete de exercițiu: „FY2025" pentru închideri în decembrie; altfel „FY2025 (ends 30 Sep 2025)" în antet și „FY2025/Sep" în coloane înguste; anii de 53 de săptămâni se marchează în perioada din fișă și în nota tabelului.
- Procente: o zecimală („33.8%"); multipli cu „x" și o zecimală („1.4x"); pragurile exact cum sunt în setul de ipoteze.
- Intervale: „de la mic la mare", unitatea o singură dată: „52.10 to 61.80 USD"; niciodată „52-62".
- Numere negative: semnul minus lipit de cifră („-1,204 USD m", „-3.2%"), fără paranteze.
- „n/a" versus „missing": n/a înseamnă „nu se aplică prin definiție" (fără datorie, acoperirea dobânzilor n/a; fereastra de 5 ani indisponibilă în primii ani); missing înseamnă „așteptat, dar absent", mereu cu motiv și link la problemă; „needs verification" înseamnă „prezent, dar marcat".
- Date: ISO 8601 (2026-10-30) peste tot; orice valoare datată vine cu sursa („FRED DGS10, 2026-10-30"); timpii de extragere în UTC.
- Separatori: urmează limba interfeței (EN: 47,061.5; RO: 47.061,5); CSV-ul folosește mereu punct zecimal și fără separator de mii.
- Rotunjire: doar la afișare; calculele folosesc precizia completă; fișa arată valoarea cu zecimalele din raport.

## 8. Accesibilitate și telefon

- Contrast: WCAG 2.1 AA, minimum 4.5:1 pentru text și 3:1 pentru marcaje, badge-uri și margini; verificat în ambele teme.
- Ținte tactile: minimum 44 x 44 px CSS pentru chips și rânduri (chip-ul poate fi vizual mai mic, zona de atingere nu); 8 px între ținte.
- Tabele pe ecran mic: prima coloană fixă, derulare orizontală cu umbră la margine, modul „focus one metric"; font de minimum 14 px în celule, cifre tabulare; fără zoom obligatoriu.
- Tastatură pe desktop: toate chips-urile sunt butoane focusabile; Enter deschide fișa, Esc o închide; săgeți în tabele; gate strip este un tablist; link „skip to content"; focus vizibil.
- Cititor de ecran: badge-ul se anunță „Gate 3, Returns on capital, verdict: pass, 0 judgments pending"; marcajele se citesc „fact", „calculation", „judgment", nu litere; chip-ul se anunță „revenue FY2025, 47,900 USD millions, fact, provenance available"; celulele lipsă se anunță cu motivul; progresul ingestiei este regiune live „polite".
- Mod întunecat: cerință pe tokens (secțiunea 10), fără culori hard-coded; urmează prefers-color-scheme plus comutator manual; glifele verdictelor sunt identice în ambele teme.
- Mișcare: respectă prefers-reduced-motion; cifrele nu se animează.
- Limbă: atributul lang urmează preferința; fontul acoperă diacriticele românești.

## 9. Întrebări deschise pentru product owner

1. Porțile 1 și 6 în v1: rânduri gri „phase 2" pe scorecard (recomandat, ca structura de șase porți să fie vizibilă din prima zi) sau ascunse?
2. Verdictul porții 2: ales explicit de om după cele trei texte, cu P8 prioritar (recomandat), sau derivat din praguri de stabilitate plus texte?
3. Marja cerută în poarta 5 cât timp judecata „franciză sau afacere" din poarta 4 nu este confirmată: marja largă 30 la 50% etichetată „default" (recomandat, conservator) sau poarta 5 în „needs judgment"?
4. Cine poate crea o versiune nouă a setului de ipoteze: doar rolul owner, partenerii propun scenarii (recomandat), sau orice utilizator?
5. Separatorii numerici urmează limba interfeței (recomandat) sau rămân mereu în format englez?
6. Expirarea judecăților: reconfirmare obligatorie la re-subscrierea anuală (recomandat; afectează modelul de date din v1) sau judecățile rămân valabile până la editare?

## 10. Predare către Dev

Contract: componenta de cifră refuză randarea (placeholder de eroare cu id de problemă) dacă lipsește oricare dintre atributele obligatorii; API-ul răspunde 422 pentru o valoare fără ele; cheile i18n sunt cele din secțiunea 6; lint-ul este un endpoint apelat la salvare și în CI.

| Atribut | Conținut | Obligatoriu pentru | UI |
|---|---|---|---|
| value, unit, scale, decimals | zecimal ca șir; ISO 4217 sau pct, ratio, shares; exponent și zecimale ca în raport | toate cifrele | chip, tabel, fișă |
| period | start, end, fiscalYear, label, weeks (52 sau 53) | toate cifrele | etichete FY, note |
| entity | issuerId, market, ticker, name, reportingCurrency, fye | toate ecranele | antet, URL |
| register | fact, calc, judgment | toate cifrele | marcaj; chip refuză fără |
| status, statusReason, issueIds | ok, missing, needs_verification, na, divergent, stale, partial, error | toate cifrele | stări; chip refuză fără |
| provenanceId | fapt: filing; calc: formula run; judecată: judgmentId | toate cifrele | fișa; chip refuză fără |
| source | edgar, esef, bvb_import, fred, ecb, bnr, vendor, manual | fapte | fișă |
| filing | form, accession, filedDate, url, locator | fapte din raport | fișă, link |
| tagAsFiled, canonicalConcept, mappingRuleId, mapVersion | așa cum au fost depuse și mapate | fapte XBRL | fișă |
| extractedAt | UTC | fapte | fișă |
| restated | flag, originalValue, laterFiling | fapte | marcaj, fișă |
| crossCheck | vendor, value, divergencePct, tolerance | fapte | marcaj „~", fișă |
| formulaId, formulaVersion, inputIds, testStatus | expresie, intrări, test cu rezultat cunoscut | calcule | formula block |
| assumptionSetVersion | versiunea setului fix | calcule dependente de ipoteze, antet | antet, formula block |
| judgment | id, state (ai_proposed, confirmed, edited, rejected), author, model, confirmedAt, citations cu verified (auto, manual, failed), lintResult | judecăți | editor, coadă |
| analysisVersion | n, frozen, frozenAt, snapshotId | toate ecranele | banner, URL |
| verdict | gateId, code, reasonKey plus params, ruleId, ruleVersion, pendingJudgments, coverageYears, blockingIssueIds | porți | badge, rând scorecard |
| scenario | id, name, author, createdAt, baseAssumptionSetVersion, overrides, results, outsideBounds | scenarii | panou diff |

Tokens de design (minim): color.surface, color.surface.raised, color.ink, color.ink.muted, color.border, register.fact, register.calc, register.judgment, verdict.ink (neutru, un singur ton), status.attention (neutru, pentru probleme), font.numeric (cifre tabulare), font.text, space.1 la space.6, radius.chip, hit.min (44 px), shadow.scroll-edge. Fiecare token are valoare pentru light și dark; niciun component nu folosește culori în afara tokens.
