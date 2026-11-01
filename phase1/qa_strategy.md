# Strategia QA SixGates (faza 1, v1, 31 octombrie 2026)

Autor: QA (independent de Dev). Scris înainte de a vedea codul. Convenții: în proză și tabele numerele folosesc virgula zecimală și punctul pentru mii (1.700,63); în blocurile de cod, formatul Python. Identificatorii tehnici (concepte XBRL, ID-uri de test) rămân în engleză.

## 1. Rolul QA și regulile de independență

### Ce semnează QA
- Raportul „trece / nu trece” pentru fiecare release (secțiunea 11).
- Setul de aur și rezultatele lui înghețate (secțiunea 3).
- Semnătura QA pe fiecare story, conform definiției lui „gata” din requirements_v0 secțiunea 7: cod, teste, proveniență verificată în interfață, criterii bifate de PM, apoi QA.

### Ce poate bloca QA
Orice livrare. Blocarea este automată, fără negociere, la orice încălcare a principiilor P1 la P10 din requirements_v0 secțiunea 2. O blocare din alte cauze (regresie pe setul de aur, diferență nereconciliată, citare AI respinsă) se ridică doar după corecție și re-rulare, nu prin acceptarea riscului.

### Regula recalculării independente
QA recalculează din rapoartele brute (EDGAR companyfacts și documente 10-K, pachete ESEF de pe filings.xbrl.org, PDF-uri pentru istoricul pre-2020), cu foi de calcul și scripturi proprii, fără codul produsului și fără a citi arhitectura Dev înainte de a scrie testele. Produsul este o cutie neagră: intrări (companie, perioadă), ieșiri (fapte, calcule, verdicte, proveniență). Orice diferență între QA și produs este a produsului până la dovada contrară, scrisă în jurnalul problemelor de date.

### Ce nu face QA
Nu decide judecățile (moat, management, descrierea pe zece ani). Nu schimbă singur pragurile categoriilor: propune, PM decide, validarea se face pe setul de aur. Nu redeschide deciziile din secțiunea 6.

## 2. Straturile de testare

| Strat | Scop | Automat / manual | Instrument |
|---|---|---|---|
| Unitare cu rezultate cunoscute | Fiecare formulă reproduce cifrele din scrisori (P2) | Automat | pytest, cazurile din secțiunea 4 |
| Reconciliere la raport | Fiecare fapt egal cu raportul, la unitatea de rotunjire (P1, P4, P7) | Extragere automată, verificare manuală completă pe setul de aur | Foaie de reconciliere (CSV versionat) |
| Al doilea cititor | QA recalculează OE, ROIC, VI din brut (P2, P6) | Manual, cu scripturi QA | Foi QA, în afara repo-ului produsului |
| Proprietate (invarianți) | Motorul respectă invarianții din secțiunea 7 pe intrări generate | Automat | Hypothesis peste motorul de formule pur |
| Regresie pe setul de aur | Ieșirile celor 20 de companii nu se schimbă neanunțat (P6) | Automat | pytest plus fișiere înghețate (fapte, calcule, verdicte) |
| Verificarea citărilor AI | Fiecare citare există verbatim în raport (P3, P9) | Automat plus eșantion manual | Verificator de substring, foaie de eșantionare |
| Interfață și înțelegere | Fluxurile centrale, proveniență vizibilă, limbaj de fapte (P1, P5, P8, P10) | Playwright automat plus protocol manual | Playwright, lint peste cataloagele de texte |
| Prospețime și integritate | Date vechi marcate, fișiere brute cu sume de control, valori schimbate detectate (P6, P7, P9) | Automat | Joburi programate, pytest pe detectoare |

| Strat | Criteriu de trecere | Cine rulează | Când |
|---|---|---|---|
| Unitare | 100% din cazurile UT, cu toleranțele din secțiunea 4 | CI | La fiecare commit |
| Reconciliere | Zero diferențe neexplicate pe 20 de companii, toți anii disponibili | QA, cu Dev pentru cauze | La fiecare release și la orice schimbare în ingestie sau normalizare |
| Al doilea cititor | Toate diferențele explicate și acceptate în scris (secțiunea 6) | QA | Înainte de „gata” v1, apoi la fiecare release major |
| Proprietate | Zero contraexemple la 2.000 de exemple per invariant; contraexemplele devin cazuri UT | CI | Per commit (profil scurt); nocturn 20.000 de exemple |
| Regresie set de aur | Diff gol față de fișierele înghețate; orice diff cere PR de actualizare semnat de QA | CI | Per commit pe motor; nocturn complet cu re-ingestie |
| Citări AI | 100% potrivire verbatim; precizie de relevanță ≥ 98% pe eșantion | Automat per draft; QA pe eșantion | Continuu; eșantion săptămânal |
| UI și înțelegere | Toate scenariile UI trec; 3 din 3 persoane trec protocolul; lint cu zero potriviri | CI pentru Playwright și lint; QA pentru protocol | Per commit; protocol la fiecare release |
| Prospețime și integritate | Toate marcajele apar în UI; zero fișiere brute fără sumă de control | Job nocturn plus pytest | Nocturn; pytest per commit |

## 3. Setul de aur

Douăzeci de companii, alese să acopere fiecare caz cerut de requirements_v0 și de rețetă. Disponibilitatea datelor a fost verificată pe 31 octombrie 2026 cu 23 de cereri (11 la SEC EDGAR companyfacts, 12 la API-ul filings.xbrl.org). „Verificat” înseamnă fișier descărcat și numărat; „de verificat” înseamnă neconfirmat.

Constatări cu consecințe pentru v1:
- România pe filings.xbrl.org: doar perioade încheiate la 31 decembrie 2021 și 2022 (115 pachete, 39 de emitenți), fără FY2023-FY2025; Hidroelectrica absentă. Toate cele 3 companii BVB sunt „date insuficiente” până la importul validat din rapoartele emitenților.
- Germania lipsește complet (filtrul country=DE întoarce zero pachete). Bayer și Allianz, alese inițial, au fost înlocuite cu Philips și AXA; emitenții germani intră la „import validat”.
- Istoricul ESEF începe cu FY2020 sau FY2021: nicio companie europeană nu atinge zece ani, deci porțile 2 și 3 afișează „date insuficiente” la toate cele 10 până la importul istoricului pre-2020 (decizia din secțiunea 6). Pentru Novo Nordisk, formularul 20-F de pe EDGAR adaugă fapte ifrs-full pentru 2019-2025, tot sub zece.
- API-ul filings.xbrl.org expune pentru fiecare pachet un câmp sha256 și contoare de erori de validare; ambele se stochează (secțiunea 10).

### SUA (SEC EDGAR, US GAAP)

| Companie (ticker, piață) | CIK | De ce în set (cazuri testate) | Date verificate | Formă verdict v1 așteptată |
|---|---|---|---|---|
| Coca-Cola (KO, NYSE) | 0000021344 | Exemplul din rețetă; franciză; etichetă de venit schimbată: SalesRevenueGoodsNet 2007-2017, Revenues 2016-2025 (exact 10 ani sub eticheta nouă, caz-limită P8) | 19 ani FY, 2007-2025 | Poarta 3 trece; poarta 5 de stabilit la prima rulare |
| Apple (AAPL, Nasdaq) | 0000320193 | Din rețetă (2016); an fiscal 52/53 de săptămâni în septembrie (FY2023: 370 de zile); trei etichete de venit (SalesRevenueNet, Revenues, RevenueFromContractWithCustomerExcludingAssessedTax); acțiuni scăzute mult prin răscumpărări, cu splituri 7:1 (2014) și 4:1 (2020) | 19 ani FY | Poarta 3 trece; poarta 5 de stabilit |
| Moody's (MCO, NYSE) | 0001059556 | Din rețetă (FCIC 2010); capital propriu negativ 2008-2011 și 2014-2017 (minim -1.225 mil. USD); acțiuni diluate de la 272,2 la 179,9 mil. (-33,9%) | 19 ani FY | Poarta 3: ani marcați „capital tangibil negativ”, nu cifră; poarta 5 de stabilit |
| Wells Fargo (WFC, NYSE) | 0000072971 | Bancă (stresul din 1990); fără OperatingIncomeLoss, CostOfRevenue sau capex în companyfacts; flux din exploatare -19,0 mld. USD în 2025 | 19 ani FY | Porțile 3 și 5: „formula nu se aplică (bancă)”; stresul se aplică |
| Costco (COST, Nasdaq) | 0000909832 | Cost mic ca moat; an fiscal încheiat lângă 31 august, FY2023 cu 53 de săptămâni; trei etichete de venit suprapuse; 10-K FY2026 deja depus | 19 ani FY, 2008-2026 | Categorie așteptată „bun” (praguri de validat) |
| Kraft Heinz (KHC, Nasdaq) | 0001637459 | Deprecieri de fond comercial în fiecare an 2018-2025 (7.008 mil. în 2018, 6.734 mil. în 2025); retratare în 10-K din iunie 2019 (profit net FY2016 de la 3.632 la 3.596 mil., FY2017 de la 10.999 la 10.941 mil.); etichetă „IncludingAssessedTax”; FY2022 cu 53 de săptămâni; FY2014 este predecesorul Heinz | 12 ani FY, 2014-2025 | Testul de management (faza 2) pică; poarta 3 de stabilit; retratarea în jurnal |
| Kenvue (KVUE, NYSE) | 0001944048 | IPO mai 2023, istoric scurt | 5 ani FY, 2021-2025 | Porțile 2 și 3: „date insuficiente (5 din 10 ani)” |
| American Airlines (AAL, Nasdaq) | 0000006201 | „Groaznic” (2007); capital propriu negativ 2008-2013 și 2016-2025 (minim -7.987 mil.); fapt dei datat 2027-07-17 în 10-Q din iulie 2026 | 18 ani FY | Poarta 3 groaznic; supraviețuire marcată; „dată imposibilă” în jurnal |
| Procter & Gamble (PG, NYSE) | 0000080424 | An fiscal la 30 iunie; depreciere Gillette 6.783 mil. în FY2019; capitalul propriu doar sub StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest; acțiuni diluate -27,0% din 2008 | 19 ani FY, 2008-2026 | De stabilit; testul de management marchează FY2019 |
| Berkshire Hathaway (BRK.B, NYSE) | 0001067983 | Asigurător și conglomerat; OperatingIncomeLoss doar 2009-2012; dei acțiuni doar până în 2011 (două clase); depreciere 10.033 mil. în 2020 | 19 ani FY | „Formula nu se aplică” pe asigurări; restul de stabilit |

### UE (ESEF pe filings.xbrl.org, IFRS)

| Companie (ticker, piață) | LEI | De ce în set | Pachete anuale pe filings.xbrl.org | Formă verdict v1 așteptată |
|---|---|---|---|---|
| Novo Nordisk (NOVO B, Copenhaga) | 549300DAQ1CVT6CXN342 | ADR la NYSE (NVO), 20-F cu fapte ifrs-full pe EDGAR (CIK 0000353278, 2019-2025): verificare încrucișată ESEF vs 20-F; pachetul FY2023 are 80 de erori de validare | 6 (FY2020-FY2025) plus trimestriale | Poarta 3 trece pe anii disponibili; „date insuficiente” la 10 ani fără import |
| ASML (ASML, Amsterdam) | 724500Y6DUVHQD6OXN27 | Afacere excelentă cu intensitate de capital în creștere; listată și pe Nasdaq | 5 (FY2021-FY2025) | Date insuficiente fără import; poarta 3 de stabilit |
| LVMH (MC, Paris) | IOG4E947OATN0KJYSD45 | Brand mondial; fond comercial mare (Tiffany); FY2025 lipsește de pe index | 4 (FY2021-FY2024; FY2025 de verificat) | Date insuficiente fără import |
| Air France-KLM (AF, Paris) | 969500AQW31GYO8JZD66 | „Groaznic” european; capital propriu negativ (de confirmat din raport); FY2021 depus de două ori; FY2023 lipsește | 3 perioade (FY2021 x2, FY2022, FY2024) | Groaznic; „capital tangibil negativ”; gol în serie marcat |
| Philips (PHIA, Amsterdam) | H1FJE8H61JGM1JSGM897 | Deprecieri de fond comercial 2022-2023 și rechemarea Respironics: test de management | 6 (FY2020-FY2025) | Date insuficiente fără import; management de stabilit |
| Inditex (ITX, Madrid) | 549300TTCXZOGZM2EY83 | An fiscal la 31 ianuarie; cost mic ca moat; 5 pachete re-adăugate pe 20 octombrie 2026 pentru perioade vechi (test de integritate) | 6 (încheiate 2021-01-31 la 2026-01-31), 11 pachete | Date insuficiente fără import; categorie de stabilit |
| AXA (CS, Paris) | F5WCUMTUM4RKZ1MAIE39 | Asigurător sub IFRS 17 (ruptură de comparabilitate 2023); FY2021 lipsește | 5 (FY2020, FY2022-FY2025) | Porțile 3 și 5: „formula nu se aplică (asigurător)” |

### BVB (ESEF unde există)

| Companie (ticker, piață) | LEI | De ce în set | Pachete pe filings.xbrl.org | Formă verdict v1 așteptată |
|---|---|---|---|---|
| Banca Transilvania (TLV, BVB) | 549300RG3H390KEL8896 | Bancă sub IFRS; cel mai lichid emitent BVB | 1 perioadă (FY2022, 2 pachete) | „Formula nu se aplică (bancă)”; date insuficiente |
| OMV Petrom (SNP, BVB) | 549300UKYDM6L8HEPU79 | Capital intensiv, ciclu de marfă, capex mare; GDR la Londra (de verificat) | 2 perioade (FY2021, FY2022; 4 pachete) | Date insuficiente până la import; categorie de stabilit |
| Hidroelectrica (H2O, BVB) | de verificat | IPO iulie 2023; fără ESEF pe index | 0 | „Date insuficiente”; importul rapoartelor pre-IPO rămâne judecată |

### Matricea cazurilor cerute

| Caz cerut | Companii care îl acoperă |
|---|---|
| Excelent / bun / groaznic (2007) | KO, AAPL, MCO, NOVO B, ASML, MC / COST, PG, ITX / AAL, AF |
| Capital propriu negativ sau mic | MCO, AAL, AF |
| Etichete proprii sau schimbare de etichetă | KO, AAPL, COST, KHC, PG, BRK.B |
| Fond comercial mare și deprecieri | KHC, PG, BRK.B, PHIA, MC |
| Bancă sau asigurător | WFC, TLV, CS, BRK.B |
| IPO recent, istoric scurt | KVUE, H2O |
| 52/53 de săptămâni sau an nedecembrie | AAPL, COST, KHC, PG, ITX |
| Dublă listare sau ADR | NOVO B, ASML, SNP |
| Acțiuni scăzute prin răscumpărări | AAPL, MCO, PG |
| Retratare, gol în serie, pachet re-depus | KHC, AF, AXA, ITX |

## 4. Teste unitare cu rezultate cunoscute

Toate valorile au fost calculate de QA în Python pe 31 octombrie 2026. Toleranță implicită: 1e-9 absolut pe rapoarte și 0,01 pe sume de bani (aritmetică deterministă); toleranțele mai largi sunt notate. „Sursă” indică scrisoarea Berkshire sau secțiunea 5 din requirements_v0 (R5).

| ID | Intrări | Ieșire așteptată | Toleranță | Sursă |
|---|---|---|---|---|
| UT-01 | See's 1972: pre-tax 5,0 mil., active tangibile nete 8,0 mil., preț 25 mil. | Randament pe capital tangibil 0,625 (cu 4,8 mil.: exact 0,600, „aproape 60%”); preț/active tangibile 3,125; pre-tax/preț 0,200 | 1e-9 | 2007, 1991 |
| UT-02 | See's 2007: pre-tax 82 mil., capital 40 mil.; reinvestit 32 mil., trimis la Omaha 1.350 mil. | 82/40 = 2,05; ROIC incremental 1972-2007 (82-5)/(40-8) = 2,40625; CAGR pre-tax pe 35 de ani 0,083203; cotă reinvestită 32/1.382 = 0,023155 | 1e-6 | 2007 |
| UT-03 | FlightSafety: capital suplimentar 509 mil., pre-tax suplimentar 159 mil., capex/vânzări mare | ROIC incremental 0,312377; categorie „bun”, nu „excelent”: a doua condiție (capex/vânzări mic) pică; ancoră de calibrare a pragurilor | 1e-6 | 2007, R5 |
| UT-04 | 1 dolar, 20 dublări, impozit 34% | O impozitare la final: 2^20 = 1.048.576; 1.048.576 - 0,34 x (1.048.576 - 1) = 692.060,50. Impozit la fiecare dublare: 1,66^20 = 25.244,21. Raport 27,41 | 0,01 | 1989 |
| UT-05 | Testul dolarului: profit reținut 5 ani 500; variație capitalizare 650 / 400 / 500 | 1,30 trece; 0,80 pică; 1,00 trece (≥ 1); avertisment de zgomot de piață afișat; varianta pe 10 ani disponibilă | 1e-9 | 1983, R5 |
| UT-06 | Stres Wells Fargo: credite L = 48.000, p = 10%, severitate s = 30%, pre-tax înainte de provizioane E = 1.300 | Pierdere L x p x s = 1.440 (3,00% din credite); E - pierdere = -140; acoperire E/pierdere = 0,9028; etichetă „aproximativ pragul de rentabilitate” | 0,01 | 1990 |
| UT-07 | Coca-Cola 1988: multiplu 15x; creștere 15%; apoi multiplu 50x | Randamentul câștigurilor 0,066667; sumă 0,216667 (peste 20%); la 50x randament 0,020 | 1e-6 | 1988, 2004 |
| UT-08 | Schimbare cu impozit: t = 0,20, g = 0,60, r1 = 10%, n = 10; r2 = 13%, apoi 11% | (1 - 0,12) x 1,13^10 = 2,987219 vs 1,1^10 = 2,593742: alternativa depășește după impozit; cu 11%: 2,498690 < 2,593742: se ține; r2 de echilibru 0,114152 | 1e-6 | 1989, R5 |
| UT-09 | Kelly (p, b, fracție): (0,6; 2; 0,5), (0,9; 3; 0,5), (0,9; 3; 0,25), (0,4; 1; 0,5) | f* = 0,40, poziție 0,20; f* = 0,866667 plafonat la 0,40; 0,216667; f* = -0,20, poziție 0 (niciodată negativă) | 1e-6 | 1966, Munger 1994, R5 |
| UT-10 | DCF sintetic: OE_0 = 100, g = 6% (sub CAGR istoric 8%), r = 10%, 10 ani, g_terminal 2% și 3% | PV explicit 820,3093; VI = 1.700,63 (g_t 2%) la 1.836,26 (g_t 3%), afișat ca interval | 1e-4 relativ | 1992, 2000, R5 |
| UT-11 | DCF invers: preț 2.000, OE_0 = 100, r = 10%, g_terminal 2,5% | g implicit 0,077118; verificare VI(g) = 2.000,00 | 1e-6 pe g | 2000, R5 |
| UT-12 | Marja de siguranță: VI = 1.000; afacere 30-50%; franciză 15-25%; preț 600 | Preț pe care l-aș plăti: 700 / 500; 850 / 750; marja la preț 600 = 0,40 | 0,01 | 1984, R5 |
| UT-13 | Serie OE cu 9 ani; cu 10 ani; cu 10 ani și un gol (lipsește 2019) | „date insuficiente” / trece / „date insuficiente (gol în 2019)” | exact | P8 |
| UT-14 | OE: profit net 100, amortizare 30, alte non-cash 5, capex 40, creștere capital de lucru 5 | Capex întreținere implicit min(40, 30) = 30; OE = 100; varianta Greenwald (capex de creștere 5) dă 95, afișată alături; 135 (fără capex) respins ca EBITDA | 0,01 | 1986, R5 |
| UT-15 | ROIC tangibil: EBIT 200, rată efectivă 25%, capital de lucru net 300, imobilizări nete 500, alte active 50, numerar excedentar 100, fond comercial 400 | NOPAT 150; capital tangibil 750; ROIC 0,200; varianta „pe prețul plătit” 150/1.150 = 0,130435 | 1e-6 | 1983, 2017, R5 |
| UT-16 | ROIC incremental: ΔNOPAT 5 ani 50, Δcapital 200 | 0,25 | 1e-9 | 2007 |
| UT-17 | Identitatea creșterii: reinvestire 40%, ROIC 20%, creștere observată 12% | g implicit 0,08; diferență de 4 puncte marcată „creșterea nu este explicată de reinvestire” | 1e-9 | 1992, 2000 |
| UT-18 | ROE pe capital de început de an: profit 120, capital la 1 ianuarie 1.000 | 0,12, afișat lângă creșterea EPS cu avertismentul din 1977 | 1e-9 | 1977 |
| UT-19 | Randament OE/preț: OE 100, preț 2.000, obligațiune 10 ani 4,2% | 0,050; diferență +0,8 puncte, ca fapt, fără verdict | 1e-9 | 1991, R5 |
| UT-20 | Supraviețuire: datorie 600, numerar 100, OE 100, EBIT 200, dobânzi 40 | Datorie netă/OE 5,0; EBIT/dobânzi 5,0 | 1e-9 | 1990, 2017 |
| UT-21 | Look-through: 1% din 10.000 plus 0,5% din 4.000 | 120 | 0,01 | 1990, 1991 |
| UT-22 | Răscumpărări: 900 plătiți pentru 10 acțiuni; VI/acțiune 100 | Preț mediu 90, sub VI, afișat ca fapt | 0,01 | 2011, 2016 |
| UT-23 | Rată efectivă: impozit 50, pre-tax 200; apoi pre-tax -50 | 0,25; „rată efectivă nedefinită” când pre-tax ≤ 0 | 1e-9 | R5 |
| UT-24 | Apple acțiuni diluate FY2007 889.292.000 și FY2025 15.004.697.000; splituri 7:1 și 4:1 | Factor 28; FY2007 ajustat 24.900.176.000; variație -39,74%; variația neajustată (+1.587%) este respinsă | 1e-6 | companyfacts |
| UT-25 | Moody's acțiuni diluate 272,2 mil. (2007) și 179,9 mil. (2025) | Variație -0,339089 | 1e-6 | companyfacts |

### Formulele exacte pe care motorul trebuie să le reproducă

```python
# UT-04 (scrisoarea 1989)
once = 2**20 - 0.34 * (2**20 - 1)          # 692060.50
each = (1 + 1 * (1 - 0.34)) ** 20           # 1.66**20 = 25244.21

# UT-08 (scrisoarea 1989): poziția se ține dacă
(1 - t * g) * (1 + r2) ** n < (1 + r1) ** n
r2_star = ((1 + r1) ** n / (1 - t * g)) ** (1 / n) - 1   # 0.114152

# UT-09: f = p - (1 - p) / b; pozitie = min(max(f * fractie, 0), 0.40)

# UT-10: OE_t = OE_0 * (1 + g) ** t pentru t = 1..10
PV_explicit = sum(OE_t / (1 + r) ** t)                   # 820.3093
TV = OE_10 * (1 + g_terminal) / (r - g_terminal)         # 2283.3308 la g_t = 2%
VI = PV_explicit + TV / (1 + r) ** 10                     # 1700.6322

# UT-11: g rezolvat prin bisecție în [-0.5, 0.5] astfel încât VI(g) = pret
```

Observație de specificație, de clarificat cu PM înainte de înghețarea UT-10: textul din R5 scrie „VI = Σ OE_t/(1+r)^t pe 10 ani + OE_11/(r - g_terminal)”, fără actualizarea valorii terminale la prezent. Luată literal, pe același exemplu, formula dă 3.103,64 în loc de 1.700,63. Testul fixează convenția standard (valoarea terminală actualizată cu (1+r)^10, OE_11 = OE_10 x (1 + g_terminal)); dacă PM alege altă convenție, se schimbă valoarea așteptată, nu testul. UT-10 verifică și că r = 10% apare ca „randament obligațiune + primă”, cu ambele componente vizibile; schimbarea oricăreia produce un scenariu (PT-05).

Testul de stres generic (UT-06): utilizatorul alege baza de expunere ca fapt cu ID (credite pentru bancă; creanțe plus stocuri sau venituri pentru nefinanciare), cota afectată p și severitatea s (implicit 10% și 30%, cu sursa „scrisoarea 1990” lângă valori); motorul calculează pierderea L x p x s, rezultatul pre-tax după pierdere și acoperirea E/pierdere. Verdictul este un fapt („acoperă”, „nu acoperă”, „aproximativ pragul”), nu o recomandare. L și E din UT-06 sunt ordinul de mărime al Wells Fargo 1990 conform scrisorii și se confirmă din text înainte de înghețare; aritmetica nu depinde de ele.

## 5. Reconcilierea la raport

### Cifrele reconciliate pentru fiecare companie și an
Venituri, profit operațional, profit net, amortizări și deprecieri, capex, flux din exploatare, capital propriu total, fond comercial plus imobilizări necorporale, numerar, datorie totală, cheltuieli cu dobânzile, impozit pe profit, acțiuni diluate (media ponderată), dividende plătite, răscumpărări. Pentru bănci și asigurători lista devine: venit net din dobânzi sau din prime, provizioane, credite nete sau rezerve tehnice, capital propriu, acțiuni, dividende, răscumpărări; OE, capex și ROIC tangibil se marchează „formula nu se aplică”.

### Procedura
1. Se pornește de la raportul oficial (10-K sau raportul anual ESEF, cu PDF-ul sau xHTML-ul deschis), nu de la companyfacts, nu de la vendor.
2. Pentru fiecare cifră se citește valoarea din situația financiară, cu unitatea, moneda și perioada (început și sfârșit), și se notează pagina sau conceptul XBRL.
3. Se extrage valoarea afișată de produs împreună cu proveniența (concept, perioadă, document, data extragerii).
4. Diferența se calculează absolut și relativ și se clasifică: zero; rotunjire; retratare; etichetă (concept diferit, de exemplu KO 2015 sub SalesRevenueGoodsNet); perimetru (operațiuni întrerupte, interese minoritare, cazul PG); unitate sau monedă; durată (an de 53 de săptămâni, an fiscal nedecembrie); eroare de produs.
5. Orice diferență care nu este zero sau rotunjire primește o intrare în jurnalul problemelor de date al companiei, cu cauza scrisă și decizia (acceptată, corectată, în lucru).
6. Pentru anii cu mai multe versiuni (original și retratat) se reconciliază ambele valori.

### Toleranța
Jumătate din unitatea de rotunjire a raportului: pentru un raport în milioane, 0,5 milioane; în mii, 500. Pentru cifrele derivate prin sumă (datorie totală = termen scurt + termen lung + leasing), o unitate de rotunjire per componentă. Procentele se reconciliază la a doua zecimală. Nicio toleranță relativă (1%) nu este acceptată: ascunde erori de etichetă.

### Retratări
Ambele valori se înregistrează: originală (cu documentul care a publicat-o prima dată) și retratată (cu documentul care a schimbat-o). Implicit se afișează ultima, cu marcajul „retratat în <document>, inițial <valoare>”. Cazul de referință: Kraft Heinz, 10-K depus pe 7 iunie 2019, profit net FY2016 de la 3.632 la 3.596 mil. USD și profit operațional FY2017 de la 6.773 la 6.057 mil. USD. Calculele folosesc valoarea retratată; alegerea celei originale este un scenariu.

### Regula de trecere
Zero diferențe neexplicate pe toate companiile din setul de aur, toți anii disponibili, toate cele 15 cifre. „Explicat” înseamnă cauză scrisă în jurnal, vizibilă în interfață la cifra respectivă (P9). O cauză „eroare de produs” rămâne diferență neexplicată până la corecție.

### Foaia de reconciliere (coloane)
companie; identificator (CIK sau LEI); an fiscal (început, sfârșit, zile); cifră; valoare raport; unitate și monedă; pagină sau concept în raport; document (accession number sau fxo_id); valoare produs; concept XBRL folosit de produs; data extragerii; diferență absolută; diferență relativă; categorie cauză; ID intrare în jurnal; verificator; data verificării; stare.

## 6. Al doilea cititor

QA recalculează independent, din rapoartele brute, pentru cinci companii: Coca-Cola (franciză, exemplul din rețetă), Apple (an fiscal 52/53, splituri), Moody's (capital tangibil negativ pe ani întregi), Novo Nordisk (ESEF și 20-F, două surse pentru aceleași cifre) și OMV Petrom (capital intensiv, import din PDF pentru anii fără ESEF). Wells Fargo este control negativ: QA verifică doar că produsul refuză OE și ROIC tangibil și aplică testul de stres.

### Ce recalculează QA, pentru fiecare an disponibil
- OE cu capex de întreținere implicit min(capex, amortizare) și cu varianta Greenwald.
- ROIC tangibil cu NOPAT = profit operațional x (1 - rata efectivă), capitalul tangibil din bilanț, numerarul excedentar definit explicit (QA notează definiția folosită: cea mai probabilă sursă de diferență).
- ROIC incremental pe 5 și 10 ani.
- VI ca interval, cu ipotezele implicite din R5 și cu r afișat de produs.

### Formatul comparației
Un tabel per companie cu coloanele: an, metrică, valoare QA, valoare produs, diferență relativă, cauză, acceptat de (QA și PM). Foile QA stau în afara repo-ului produsului și se atașează raportului QA ca PDF și CSV.

### Regula de trecere
Fapte: diferență în toleranța de rotunjire. Calcule: diferență relativă ≤ 0,5% explicată exclusiv prin rotunjirea intrărilor; orice diferență mai mare trebuie trasată la o alegere documentată și afișată în interfață (metoda capexului de întreținere, definiția numerarului excedentar, tratamentul leasingului IFRS 16), altfel pică. Verdicte: identice. QA nu își ajustează calculul ca să se potrivească; o eroare QA se consemnează la fel.

## 7. Teste de proprietate (invarianți)

Rulate cu Hypothesis peste motorul de formule pur, cu intrări generate (valori pozitive, negative, zero, foarte mari, serii cu goluri).

| ID | Invariantul (precis) |
|---|---|
| PT-01 | VI scade strict când r crește, toate celelalte egale, pentru orice serie OE cu cel puțin un termen pozitiv (verificat: 1.763,92 la 10% față de 1.543,46 la 11%) |
| PT-02 | VI crește strict când g_terminal crește, cu r fix și g_terminal < r; pentru g_terminal ≥ r motorul întoarce „nedefinit”, niciodată un număr |
| PT-03 | Marja de siguranță este nedefinită când VI ≤ 0 sau prețul lipsește; interfața afișează „necesită judecată”, nu o cifră și nu zero |
| PT-04 | Nicio valoare derivată nu există fără lista completă a ID-urilor faptelor de intrare; lista este nevidă și fiecare ID rezolvă la un fapt cu proveniență completă (sursă, perioadă, concept sau pagină, data extragerii, link) |
| PT-05 | Schimbarea oricărei ipoteze fixate (r, g, g_terminal, marjă, metoda capexului) produce un obiect „scenariu” cu referință la „valoare”; obiectul „valoare” este imutabil și identic octet cu octet cu cel dinainte |
| PT-06 | ROIC tangibil întoarce marcajul „capital tangibil negativ” când capitalul tangibil ≤ 0, nu un număr, nu infinit, nu zero; intrările rămân afișate |
| PT-07 | OE nu este niciodată egal cu profit net + amortizare când capexul este strict pozitiv (nu poate degenera în EBITDA) |
| PT-08 | Capexul de întreținere implicit este min(capex, amortizare) și obiectul OE conține și varianta alternativă, cu alegerea marcată |
| PT-09 | Într-o formulă nu se amestecă monede sau unități: intrări cu monede diferite sau scale diferite (mii versus milioane) ridică eroare de tip înainte de calcul |
| PT-10 | Seria pe 10 ani este continuă: sub 10 ani consecutivi încheiați la ultimul an fiscal, poarta întoarce „date insuficiente (n din 10)”, inclusiv pentru n = 9 și pentru 10 ani cu un gol |
| PT-11 | Un an fiscal de 53 de săptămâni și unul de 52 sunt amândoi ani; durata se păstrează în proveniență și nu se interpolează nimic la 365 de zile |
| PT-12 | O analiză înghețată re-rulată pe aceleași fapte produce ieșire identică octet cu octet (fapte, calcule, verdicte, ordinea câmpurilor) |
| PT-13 | Verdictul unei porți ia doar valorile {trece, pică, necesită judecată, date insuficiente} și nu poate fi „trece” dacă vreo intrare a porții e marcată „necesită verificare” |
| PT-14 | O judecată propusă de AI are starea „propus de AI” și nu poate avea starea „confirmat” fără ID de utilizator uman și momentul confirmării; nicio poartă nu trece doar pe judecăți |
| PT-15 | O citare AI al cărei text nu se regăsește verbatim (după normalizarea spațiilor) în textul stocat al raportului duce la respingerea draftului; draftul nu ajunge în interfață |
| PT-16 | Pentru bănci și asigurători (clasificare SIC sau NACE plus confirmare umană), OE, capex de întreținere și ROIC tangibil întorc „formula nu se aplică”, cu motivul |
| PT-17 | Kelly: poziția este în [0; 0,40] pentru orice p în [0; 1] și b > 0; f* negativ dă poziție 0 |
| PT-18 | DCF invers: dacă există g în [-50%; 50%] cu VI(g) = preț, soluția este unică și VI(g) reproduce prețul la 1e-6 relativ; altfel întoarce „fără g rezonabil” |
| PT-19 | Numărul de acțiuni este ajustat la splituri pe toată seria: raportul acțiuni(t)/acțiuni(t-1) nu sare peste factorul splitului declarat fără marcaj „eveniment de capital” |
| PT-20 | Fiecare fapt are data de sfârșit ≤ data extragerii; un fapt datat în viitor (cazul AAL, 2027-07-17) este exclus din calcule și intră în jurnal ca „dată imposibilă” |
| PT-21 | Rata efectivă de impozit din NOPAT este în [0; 1]; în afara intervalului sau cu pre-tax ≤ 0, NOPAT se marchează „rată efectivă nedefinită” |

## 8. Verificarea citărilor AI

### Verificarea automată (la fiecare draft)
1. Textul fiecărui raport folosit de AI este stocat la ingestie, pe secțiuni și pagini, cu sumă de control.
2. Fiecare afirmație din draft are cel puțin o citare: document, secțiune, pagină, citat.
3. Citatul se normalizează (spații multiple la unul, trimming, Unicode NFC, ghilimele tipografice la ghilimele simple) și se caută ca substring în textul normalizat al paginii indicate. Minim 20 de caractere; dacă apare de mai multe ori pe pagină, se cere și secțiunea.
4. Potrivire exactă: citarea trece și poziția (document, pagină, offset) se stochează. Nepotrivire sau pagină greșită: draftul este respins integral, cu motivul, și se re-generează cel mult de două ori; a treia respingere lasă câmpul gol cu „necesită verificare”.
5. Draftul trece prin lintul de limbaj din secțiunea 9 înainte de afișare.

### Eșantionarea manuală
Săptămânal, QA citește 10% din citările acceptate în acea săptămână, minim 20, stratificate pe companie și tip (moat, management, riscuri), cu pagina sursă deschisă. Întrebarea nu este dacă citatul există (automatul a garantat), ci dacă susține afirmația lângă care stă.

### Măsurarea
Precizie de relevanță = citări care susțin afirmația / citări verificate. Se raportează și afirmațiile fără citare (trebuie zero) și afirmațiile contrazise de propria citare (trebuie zero).

### Pragul propus
Potrivire verbatim: 100%, prin construcție. Precizie de relevanță: ≥ 98% pe eșantion, cu zero afirmații contrazise. Sub prag, drafturile AI se dezactivează din interfață până la corecția promptului sau a extragerii și re-măsurare pe un eșantion nou.

## 9. Teste de interfață și de înțelegere

### Scenarii Playwright (desktop 1280 px și telefon 390 px)

| ID | Scenariu | Criteriu de trecere |
|---|---|---|
| UI-01 | Analiza unei companii: KO | Cele șase porți apar cu verdict din setul permis; fiecare cifră are control de proveniență; panoul de formulă afișează formula și intrările |
| UI-02 | Proveniența unei cifre: ROIC tangibil KO 2024 | Panoul arată sursa, perioada, conceptul XBRL, data extragerii și linkul; linkul răspunde HTTP 200 către documentul SEC sau ESEF |
| UI-03 | Confirmarea unui draft AI | Draftul este marcat „propus de AI”; confirmarea cere utilizator autentificat; după confirmare apare „confirmat de <utilizator> la <moment>”; verdictul porții nu se schimbă înainte de confirmare |
| UI-04 | Stare „date insuficiente”: KVUE | Porțile 2 și 3 afișează „date insuficiente (5 din 10 ani)”; niciun verdict „trece”; anii existenți rămân vizibili |
| UI-05 | Scenariu vs valoare: r de la 10% la 9% | Apare un card „scenariu” cu diferența; cardul „valoare” rămâne neschimbat; dosarul înregistrează ambele |
| UI-06 | Jurnalul problemelor de date: KHC | Intrările de retratare FY2016 și FY2017 sunt vizibile de la cifra afectată |
| UI-07 | „Formula nu se aplică”: WFC | Porțile 3 și 5 afișează motivul în loc de cifre; testul de stres este disponibil |
| UI-08 | Telefon 390 px | Toate porțile citibile fără derulare orizontală; proveniența se deschide și se închide cu un deget |
| UI-09 | Export CSV | Fiecare rând exportat are coloanele de proveniență; nicio cifră fără sursă |

### Protocolul testului de înțelegere (CT-01)
Trei persoane care nu au văzut instrumentul (parteneri neimplicați în construcție), fiecare cu două companii: una cu „trece” la poarta 3 și una cu „date insuficiente” sau „necesită judecată”. Zece minute pe companie, fără ajutor. Întrebări, răspuns oral, consemnat de QA:
1. Ce spune verdictul porții 3 și din ce cifre vine?
2. Care parte este fapt, care este calcul, care este judecată?
3. Îți spune instrumentul ce să faci?

Trece dacă fiecare persoană explică verdictul în cuvinte proprii numind corect cel puțin două din trei intrări, separă corect fapt, calcul și judecată și răspunde „nu” la a treia întrebare. Orice răspuns de forma „instrumentul zice că ar trebui să…” este eșec pe P10 pentru întregul release. Criteriul de release: 3 din 3.

### Lintul de limbaj (LN-01)
Rulează în CI peste cataloagele de texte ale interfeței (EN și RO), șabloanele de prompt, ieșirile AI înainte de afișare și șabloanele de notificare n8n. Potrivire pe cuvânt întreg, insensibilă la majuscule și diacritice. Lista interzisă: buy, sell, hold (ca recomandare), short, long, overweight, underweight, target price, price target, rating, upgrade, downgrade, recommend, undervalued, overvalued, bargain, cumpără, cumpărare, vinde, vânzare, vindeți, cumpărați, recomandăm, recomandare, subevaluat, supraevaluat, țintă de preț. Listă albă explicită: buyback, buybacks, răscumpărare, răscumpărări, sell-side (doar în numele surselor). Orice potrivire în afara listei albe oprește build-ul. Fixtură negativă: un text cu fiecare cuvânt interzis trebuie să producă exact atâtea potriviri câte cuvinte sunt.

## 10. Prospețime și integritate a datelor

### Reguli de prospețime (afișate ca marcaj, nu ascunse)

| Date | Marcaj „posibil învechit” după | Observații |
|---|---|---|
| Fapte anuale | Ultimul an fiscal încheiat cu peste 15 luni în urmă | Un ciclu de raportare plus întârzieri; job zilnic compară indexul EDGAR și filings.xbrl.org cu ce e ingerat și marchează „raport nou neprocesat” |
| Preț | Mai vechi de o zi de tranzacționare | Peste 5 zile, valorile dependente de preț afișează „preț din <data>” lângă fiecare cifră |
| Randamente obligațiuni (FRED, BCE, BNR) | Mai vechi de 7 zile | r afișează data randamentului |
| Acțiuni în circulație | Fapt dei mai vechi de 120 de zile | Se compară cu ultimul 10-Q sau raport semestrial |
| Analiză înghețată | Niciodată „învechită”: afișează data înghețării și o comparație opțională cu datele curente | P6 |

### Sume de control
Fiecare fișier brut (JSON companyfacts, pachet ESEF zip, PDF importat) primește SHA-256 la descărcare, stocat cu URL, data și dimensiunea. Pentru ESEF, suma se compară cu câmpul sha256 din API-ul filings.xbrl.org; nepotrivirea blochează ingestia pachetului. Analiza înghețată listează sumele tuturor fișierelor din care provin faptele; re-rularea verifică întâi sumele (PT-12).

### Detectarea valorilor schimbate pentru o perioadă deja stocată
La fiecare re-ingestie, faptele noi se compară cu cele stocate pe cheia (companie, concept, perioadă, unitate, dimensiune). Valoare diferită: intrare „valoare modificată” în jurnal, cu valoarea veche, cea nouă și documentele ambelor; ambele păstrate; cea nouă afișată cu marcaj (regula din secțiunea 5). Pachet nou cu valori identice: intrare „pachet re-depus”, cazul Inditex (cinci pachete re-adăugate pe 20 octombrie 2026) și Air France-KLM (FY2021, versiunile 0 și 1). Pachete ESEF cu erori de validare (Novo Nordisk FY2023: 80 de erori) se ingerează cu marcaj „pachet cu erori de validare” vizibil la fiecare fapt din el. Faptele cu dată de sfârșit în viitor (AAL) se exclud și se jurnalizează.

### Verificarea încrucișată cu vendorul

| Divergență față de sursa primară | Ce arată interfața |
|---|---|
| ≤ 0,5% (rotunjire) | Nimic; se consemnează în jurnal ca verificat |
| Între 0,5% și 5% | Marcaj „divergență vendor” lângă cifră, cu ambele valori și numele vendorului |
| > 5%, semn diferit sau lipsă la vendor | Marcaj „necesită verificare” și intrare în jurnal; cifra rămâne cea primară (P7) |
| Acțiuni sau preț > 2% față de dei sau față de a doua sursă | Marcaj „verifică splitul sau clasa de acțiuni” |

Vendorul nu completează niciodată un gol din sursa primară (P4): un fapt lipsă din EDGAR sau ESEF rămâne lipsă, cu „necesită verificare”.

## 11. Raportul QA trece / nu trece

### Șablonul
1. Antet: versiune, data, commit, suma de control a setului de aur înghețat.
2. Verdict: TRECE sau NU TRECE.
3. Tabel pe straturi: strat, rulat (da/nu, data), rezultat, observații.
4. Încălcări P1 la P10: principiu, ID test, dovadă (captură sau rând din foaie), stare.
5. Reconciliere: companii x ani verificați, diferențe explicate, diferențe neexplicate (trebuie zero).
6. Al doilea cititor: companii, diferențe, acceptări semnate.
7. Citări AI: precizie de relevanță pe eșantion, afirmații fără citare, afirmații contrazise.
8. Înțelegere: persoane, rezultat pe întrebări.
9. Probleme deschise acceptate explicit de product owner, cu data și motivul.
10. Semnătura QA.

### Regulile de veto
- Orice încălcare P1 la P10 blochează, fără excepție și fără acceptare de risc: cifră fără proveniență, formulă fără test, judecată care trece singură o poartă, substitut tăcut, ipoteză schimbată fără scenariu, analiză nereproductibilă, vendor peste sursa primară, poartă trecută sub zece ani, eroare ascunsă, limbaj de recomandare.
- Blochează și: orice caz UT picat; diferență nereconciliată; diff pe setul de aur fără PR de actualizare semnat; precizie de relevanță sub 98% (blochează doar funcțiile AI); protocolul de înțelegere sub 3 din 3; sumă de control lipsă sau nepotrivită.
- Nu blochează, se consemnează: performanță, cosmetică, export incomplet, marcaje de prospețime cauzate de surse externe, atâta timp cât marcajul este afișat.
- Un „NU TRECE” se ridică doar prin corecție și re-rulare completă a straturilor afectate.

## 12. Trasabilitate

| Principiu | Teste care îl acoperă |
|---|---|
| P1 Proveniență pe fiecare cifră | PT-04, PT-20, UI-01, UI-02, UI-09, reconciliere (secțiunea 5), sume de control (secțiunea 10) |
| P2 Formula vizibilă, test cu rezultat cunoscut | UT-01 la UT-25, UI-01, PT-07, PT-08 |
| P3 Fapte, calcule, judecăți separate | PT-13, PT-14, PT-15, UI-03, CT-01, verificarea citărilor (secțiunea 8) |
| P4 Niciun substitut tăcut | PT-03, PT-06, PT-11, PT-16, PT-21, UT-13, UT-23, verificarea încrucișată (secțiunea 10) |
| P5 Ipoteze conservatoare, fixate, vizibile; scenariu, nu valoare | PT-05, UT-10, UT-12, UI-05 |
| P6 Reproductibilitate | PT-12, regresia pe setul de aur, sume de control, analiza înghețată (secțiunea 10) |
| P7 Sursa primară bate vendorul | Reconciliere (secțiunea 5), al doilea cititor (secțiunea 6), tabelul de divergență (secțiunea 10) |
| P8 Zece ani sau marcat | UT-13, PT-10, UI-04, verdictele așteptate ale celor 10 companii europene |
| P9 Erorile sunt vizibile | UI-06, PT-20, detectarea valorilor schimbate, jurnalul din reconciliere |
| P10 Limbaj de fapte | LN-01, CT-01 întrebarea 3, lint pe drafturile AI (secțiunea 8, pasul 5) |

## 13. Riscuri de testare și limite

- Judecățile nu se pot verifica: durabilitatea moatului, calitatea managementului, descrierea pe zece ani. QA verifică doar că sunt marcate ca judecăți, că au autor uman și că nu trec singure o poartă. Corectitudinea lor rămâne a investitorului.
- Pragurile categoriilor sunt „de validat pe setul de aur”. Până la validare, QA testează doar consistența (UT-03 este ancora: FlightSafety trebuie să rămână „bun”) și semnalează orice prag care ar muta See's sau FlightSafety în altă categorie.
- Istoricul european sub zece ani: importul din PDF este manual și cel mai expus la erori de transcriere. QA cere dublă introducere (două persoane, comparare automată) pentru anii importați și reconciliere la PDF, nu la foaia de import.
- Cifrele din scrisori sunt rotunjite („aproape 60%”, „aproximativ 692.000”). Testele fixează intrările exacte și valorile calculate; diferența dintre „aproximativ” și exact este documentată, nu ascunsă.
- Verdictele din secțiunea 3 sunt forme, nu cifre; prima rulare produce cifrele, QA le reconciliază și abia apoi le îngheață. Până atunci setul de aur nu poate servi ca regresie.
- Surse externe: filings.xbrl.org poate lipsi un raport (LVMH FY2025, AXA FY2021, AF FY2023) sau îl poate re-depune; EDGAR poate conține erori ale emitentului (AAL). QA testează detectarea, nu poate garanta completitudinea sursei.
- Testul de înțelegere are trei persoane: suficient pentru ambiguități grosiere, insuficient statistic. Se repetă la fiecare release, cu persoane noi când e posibil.
- Formula VI din R5 este ambiguă la valoarea terminală (secțiunea 4); până la clarificare, UT-10 nu poate fi înghețat. Este singurul punct care blochează scrierea completă a testelor înainte de cod.
