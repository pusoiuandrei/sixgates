# Raportul spike-ului de date (faza 1)

Generat 2026-10-31T21:26:07+00:00 de `spike/run_spike.py`. Toate cifrele provin din fapte descărcate (EDGAR companyfacts, filings.xbrl.org, FRED) sau din formule aplicate pe ele; nimic nu este estimat. Valorile sunt în milioane, în moneda de raportare a emitentului. Statusurile: `lipsă` = concept neraportat în sursă; `semnalat` = formula a refuzat calculul (de exemplu capital tangibil nepozitiv); `date insuficiente` = sub zece exerciții complete.

Intrare pentru prag: FRED DGS10 = 4.98% la 2026-10-29 (sursa: https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10). Pragul total implicit al setului de ipoteze v1 rămâne 10% (randamentul obligațiunii lungi plus prima aleasă), deci DGS10 este referința, nu rata folosită.

Ipoteze fixe (assumption_set v1-default, versiunea 1): prag 10%; creștere explicită 10 ani; calea joasă = jumătate din CAGR-ul istoric al OE, plafon 5%, creștere terminală 2%; calea înaltă = CAGR istoric, plafon 10%, creștere terminală 3%; fără creștere când CAGR-ul este negativ; capex de întreținere = min(capex, amortizare); alte cheltuieli fără numerar neadăugate (compensația în acțiuni tratată drept cost real); tot numerarul tratat ca excedentar la calculul capitalului tangibil; marja cerută 30 la 50% pentru afacere, 15 la 25% pentru franciză. Pragurile categoriilor din scrisoarea 2007 (excelent > 30% ROIC incremental și capex/vânzări < 5%; bun ≥ costul capitalului + 5 puncte; groaznic < costul capitalului) sunt propuse și trebuie validate pe setul de aur.

## Sumar pe companii

| Companie | Sursă | Exerciții extrase | Regula de zece ani | VI calculată |
|---|---|---|---|---|
| Apple Inc. (AAPL) | SEC EDGAR companyfacts | FY2009 la FY2025 (17), fereastră FY2016 la FY2025 | trece | da (interval) |
| The Coca-Cola Company (KO) | SEC EDGAR companyfacts | FY2009 la FY2025 (17), fereastră FY2016 la FY2025 | trece | da (interval) |
| Moody's Corporation (MCO) | SEC EDGAR companyfacts | FY2009 la FY2025 (17), fereastră FY2016 la FY2025 | trece | da (interval) |
| LVMH Moët Hennessy Louis Vuitton (LVMH) | ESEF via filings.xbrl.org | FY2020 la FY2024 (5), fereastră FY2020 la FY2024 | date insuficiente (0 consecutive complete) | nu: insufficient_data |
| OMV Petrom SA (SNP) | ESEF via filings.xbrl.org | FY2020 la FY2022 (3), fereastră FY2020 la FY2022 | date insuficiente (3 consecutive complete) | nu: insufficient_data |

## Apple Inc. (AAPL), USD milioane

Sursă: SEC EDGAR companyfacts. Exerciții disponibile: FY2009 la FY2025. Exerciții complete pentru regula de zece ani: 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025.

### Tabel A: venituri, profit net, câștigurile proprietarului, ROIC tangibil

| An | Venituri | Profit net | OE | ROIC tangibil |
|---|---|---|---|---|
| FY2016 | 215,639 | 45,687 | 51,540 | > 200% (capital tangibil neglijabil, 70x) |
| FY2017 | 229,234 | 48,351 | 48,541 | semnalat (capital tangibil ≤ 0) |
| FY2018 | 265,595 | 59,531 | 61,797 | > 200% (capital tangibil neglijabil, 10x) |
| FY2019 | 260,174 | 55,256 | 54,381 | > 200% (capital tangibil neglijabil, 5x) |
| FY2020 | 274,515 | 57,411 | 72,795 | > 200% (capital tangibil neglijabil, 6x) |
| FY2021 | 365,817 | 94,680 | 93,697 | semnalat (capital tangibil ≤ 0) |
| FY2022 | 394,328 | 99,803 | 108,299 | > 200% (capital tangibil neglijabil, 57x) |
| FY2023 | 383,285 | 96,995 | 99,274 | semnalat (capital tangibil ≤ 0) |
| FY2024 | 391,035 | 93,736 | 115,941 | semnalat (capital tangibil ≤ 0) |
| FY2025 | 416,161 | 112,010 | 96,355 | semnalat (capital tangibil ≤ 0) |

### Tabel B: ROIC incremental, categorie, datorie netă, conversie în numerar

| An | ROIC incr. 5 ani | Categorie 2007 (de validat) | Datorie netă / OE | CFO / profit net |
|---|---|---|---|---|
| FY2016 | > 200% (capital tangibil neglijabil, 40x) | bun | 0.39x | 1.45x |
| FY2017 | > 200% (capital tangibil neglijabil, 10x) | bun | 0.85x | 1.33x |
| FY2018 | > 200% (capital tangibil neglijabil, 4x) | bun | 0.78x | 1.30x |
| FY2019 | > 200% (capital tangibil neglijabil, 5x) | excelent | 0.14x | 1.26x |
| FY2020 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 0.30x | 1.41x |
| FY2021 | > 200% (capital tangibil neglijabil, 20x) | excelent | 0.66x | 1.10x |
| FY2022 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 0.66x | 1.22x |
| FY2023 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 0.50x | 1.14x |
| FY2024 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 0.36x | 1.26x |
| FY2025 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 0.46x | 1.00x |

ROIC incremental pe 10 ani la FY2025: n/a (capital nu a crescut, profit în creștere). Acoperirea dobânzilor FY2025: lipsă. Capex/vânzări FY2025: 3.1%. Identitatea creșterii FY2025: g implicit = n/a (capital tangibil neglijabil sau nepozitiv) față de CAGR NOPAT 5 ani observat 14.6%.

OE FY2025 fără termenul de capital de lucru: 112,010 (față de 96,355 cu ΔWC). Termenul ΔWC an de an face seria OE volatilă; o regulă de normalizare (de exemplu media pe 3 ani a ΔWC) este o decizie de luat în faza 2, nu o ipoteză a spike-ului.

### Poarta 5: interval de valoare intrinsecă

- OE FY2025: 96,355; CAGR OE pe fereastră: 7.2%; coeficient de variație OE: 0.30 (0 ani cu pierdere).
- VI (interval): 1,377,834 la 1,933,912 USD milioane (g explicit 3.6% la 7.2%, r = 10%, terminal 2% la 3%, 10 ani).
- Prețul pe care l-aș plăti (pe VI joasă, marjă franciză 15 la 25%): 1,033,375 la 1,171,159 USD milioane în total, adică 68.87 la 78.05 USD pe acțiune diluată.
- Încadrarea în franciză sau afacere este o judecată a omului; aici este doar un parametru al spike-ului.
- DCF invers: not_computed (no_price_source). Marja de siguranță: not_computed (no_price_source). Testul dolarului pe 5 ani: not_computed (no_price_source). Niciun furnizor de prețuri nu a fost accesibil din container (EODHD și Polygon cer cheie, stooq blocat, Yahoo limitat), deci toate metricile cu preț rămân necalculate.

## The Coca-Cola Company (KO), USD milioane

Sursă: SEC EDGAR companyfacts. Exerciții disponibile: FY2009 la FY2025. Exerciții complete pentru regula de zece ani: 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025.

### Tabel A: venituri, profit net, câștigurile proprietarului, ROIC tangibil

| An | Venituri | Profit net | OE | ROIC tangibil |
|---|---|---|---|---|
| FY2016 | 41,863 | 6,527 | 7,670 | 46.9% |
| FY2017 | 36,212 | 1,248 | -2,701 | 32.9% |
| FY2018 | 34,300 | 6,434 | 12,646 | 48.9% |
| FY2019 | 37,266 | 8,920 | 10,281 | 99.2% |
| FY2020 | 33,014 | 7,747 | 9,223 | 85.9% |
| FY2021 | 38,655 | 9,771 | 11,634 | 113.4% |
| FY2022 | 43,004 | 9,542 | 10,149 | 197.0% |
| FY2023 | 45,754 | 10,714 | 8,707 | > 200% (capital tangibil neglijabil, 2x) |
| FY2024 | 47,061 | 10,631 | 18,322 | 154.9% |
| FY2025 | 47,941 | 13,107 | 4,101 | semnalat (capital tangibil ≤ 0) |

### Tabel B: ROIC incremental, categorie, datorie netă, conversie în numerar

| An | ROIC incr. 5 ani | Categorie 2007 (de validat) | Datorie netă / OE | CFO / profit net |
|---|---|---|---|---|
| FY2016 | n/a (capital nu a crescut) | n/a (profit în scădere, capital eliberat) | 3.04x | 1.35x |
| FY2017 | n/a (capital nu a crescut) | n/a (profit în scădere, capital eliberat) | semnalat (OE ≤ 0) | 5.64x |
| FY2018 | n/a (capital nu a crescut) | n/a (profit în scădere, capital eliberat) | 2.22x | 1.19x |
| FY2019 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 3.07x | 1.17x |
| FY2020 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 3.46x | 1.27x |
| FY2021 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 2.59x | 1.29x |
| FY2022 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 2.71x | 1.15x |
| FY2023 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 3.26x | 1.08x |
| FY2024 | n/a (capital nu a crescut) | n/a (profit în scădere, capital eliberat) | 1.63x | 0.64x |
| FY2025 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 7.24x | 0.57x |

ROIC incremental pe 10 ani la FY2025: n/a (capital nu a crescut, profit în creștere). Acoperirea dobânzilor FY2025: 8.32x. Capex/vânzări FY2025: 4.4%. Identitatea creșterii FY2025: g implicit = n/a (capital tangibil neglijabil sau nepozitiv) față de CAGR NOPAT 5 ani observat 9.5%.

OE FY2025 fără termenul de capital de lucru: 13,107 (față de 4,101 cu ΔWC). Termenul ΔWC an de an face seria OE volatilă; o regulă de normalizare (de exemplu media pe 3 ani a ΔWC) este o decizie de luat în faza 2, nu o ipoteză a spike-ului.

### Poarta 5: interval de valoare intrinsecă

- OE FY2025: 4,101; CAGR OE pe fereastră: -6.7%; coeficient de variație OE: 0.58 (1 ani cu pierdere).
- VI (interval): 45,358 la 48,464 USD milioane (g explicit 0.0% la 0.0%, r = 10%, terminal 2% la 3%, 10 ani).
- Prețul pe care l-aș plăti (pe VI joasă, marjă franciză 15 la 25%): 34,019 la 38,554 USD milioane în total, adică 7.89 la 8.94 USD pe acțiune diluată.
- Încadrarea în franciză sau afacere este o judecată a omului; aici este doar un parametru al spike-ului.
- DCF invers: not_computed (no_price_source). Marja de siguranță: not_computed (no_price_source). Testul dolarului pe 5 ani: not_computed (no_price_source). Niciun furnizor de prețuri nu a fost accesibil din container (EODHD și Polygon cer cheie, stooq blocat, Yahoo limitat), deci toate metricile cu preț rămân necalculate.

## Moody's Corporation (MCO), USD milioane

Sursă: SEC EDGAR companyfacts. Exerciții disponibile: FY2009 la FY2025. Exerciții complete pentru regula de zece ani: 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025.

### Tabel A: venituri, profit net, câștigurile proprietarului, ROIC tangibil

| An | Venituri | Profit net | OE | ROIC tangibil |
|---|---|---|---|---|
| FY2016 | 3,604 | 267 | 1,170 | > 200% (capital tangibil neglijabil, 3x) |
| FY2017 | 4,204 | 1,001 | -95 | semnalat (capital tangibil ≤ 0) |
| FY2018 | 4,443 | 1,310 | 1,554 | > 200% (capital tangibil neglijabil, 4x) |
| FY2019 | 4,829 | 1,422 | 1,636 | > 200% (capital tangibil neglijabil, 7x) |
| FY2020 | 5,371 | 1,778 | 2,141 | > 200% (capital tangibil neglijabil, 15x) |
| FY2021 | 6,218 | 2,214 | 2,310 | semnalat (capital tangibil ≤ 0) |
| FY2022 | 5,468 | 1,374 | 1,175 | semnalat (capital tangibil ≤ 0) |
| FY2023 | 5,916 | 1,607 | 1,921 | > 200% (capital tangibil neglijabil, 5x) |
| FY2024 | 7,088 | 2,058 | 2,404 | > 200% (capital tangibil neglijabil, 9x) |
| FY2025 | 7,718 | 2,459 | 2,272 | > 200% (capital tangibil neglijabil, 37x) |

### Tabel B: ROIC incremental, categorie, datorie netă, conversie în numerar

| An | ROIC incr. 5 ani | Categorie 2007 (de validat) | Datorie netă / OE | CFO / profit net |
|---|---|---|---|---|
| FY2016 | n/a (capital nu a crescut) | n/a (profit în scădere, capital eliberat) | 0.97x | 4.72x |
| FY2017 | 79.5% | excelent | semnalat (OE ≤ 0) | 0.75x |
| FY2018 | > 200% (capital tangibil neglijabil, 3x) | excelent | 2.48x | 1.12x |
| FY2019 | > 200% (capital tangibil neglijabil, 33x) | excelent | 2.23x | 1.18x |
| FY2020 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 1.74x | 1.21x |
| FY2021 | > 200% (capital tangibil neglijabil, 3x) | excelent | 2.39x | 0.91x |
| FY2022 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 4.71x | 1.07x |
| FY2023 | > 200% (capital tangibil neglijabil, 27x) | excelent | 2.50x | 1.34x |
| FY2024 | n/a (capital nu a crescut, profit în creștere) | excelent (profit în creștere fără capital suplimentar) | 1.85x | 1.38x |
| FY2025 | 120.0% | excelent | 2.00x | 1.18x |

ROIC incremental pe 10 ani la FY2025: > 200% (capital tangibil neglijabil, 4x). Acoperirea dobânzilor FY2025: 13.35x. Capex/vânzări FY2025: 4.2%. Identitatea creșterii FY2025: g implicit = n/a (capital tangibil neglijabil sau nepozitiv) față de CAGR NOPAT 5 ani observat 6.7%.

OE FY2025 fără termenul de capital de lucru: 2,613 (față de 2,272 cu ΔWC). Termenul ΔWC an de an face seria OE volatilă; o regulă de normalizare (de exemplu media pe 3 ani a ΔWC) este o decizie de luat în faza 2, nu o ipoteză a spike-ului.

### Poarta 5: interval de valoare intrinsecă

- OE FY2025: 2,272; CAGR OE pe fereastră: 7.6%; coeficient de variație OE: 0.44 (1 ani cu pierdere).
- VI (interval): 33,017 la 47,144 USD milioane (g explicit 3.8% la 7.6%, r = 10%, terminal 2% la 3%, 10 ani).
- Prețul pe care l-aș plăti (pe VI joasă, marjă franciză 15 la 25%): 24,763 la 28,064 USD milioane în total, adică 137.65 la 156.00 USD pe acțiune diluată.
- Încadrarea în franciză sau afacere este o judecată a omului; aici este doar un parametru al spike-ului.
- DCF invers: not_computed (no_price_source). Marja de siguranță: not_computed (no_price_source). Testul dolarului pe 5 ani: not_computed (no_price_source). Niciun furnizor de prețuri nu a fost accesibil din container (EODHD și Polygon cer cheie, stooq blocat, Yahoo limitat), deci toate metricile cu preț rămân necalculate.

## LVMH Moët Hennessy Louis Vuitton (LVMH), EUR milioane

Sursă: ESEF via filings.xbrl.org. Exerciții disponibile: FY2020 la FY2024. Exerciții complete pentru regula de zece ani: niciunul.

### Tabel A: venituri, profit net, câștigurile proprietarului, ROIC tangibil

| An | Venituri | Profit net | OE | ROIC tangibil |
|---|---|---|---|---|
| FY2020 | 44,651 | 4,702 | lipsă | lipsă |
| FY2021 | 64,215 | 12,036 | lipsă | 53.7% |
| FY2022 | 79,184 | 14,084 | lipsă | 58.0% |
| FY2023 | 86,153 | 15,174 | lipsă | 50.0% |
| FY2024 | 84,683 | 12,550 | lipsă | 33.1% |

### Tabel B: ROIC incremental, categorie, datorie netă, conversie în numerar

| An | ROIC incr. 5 ani | Categorie 2007 (de validat) | Datorie netă / OE | CFO / profit net |
|---|---|---|---|---|
| FY2020 | lipsă | lipsă | semnalat (OE ≤ 0) | 2.32x |
| FY2021 | lipsă | lipsă | semnalat (OE ≤ 0) | 1.55x |
| FY2022 | lipsă | lipsă | semnalat (OE ≤ 0) | 1.27x |
| FY2023 | lipsă | lipsă | semnalat (OE ≤ 0) | 1.21x |
| FY2024 | lipsă | lipsă | semnalat (OE ≤ 0) | 1.51x |

ROIC incremental pe 10 ani la FY2024: lipsă. Acoperirea dobânzilor FY2024: 42.78x. Capex/vânzări FY2024: 6.5%. Identitatea creșterii FY2024: g implicit = lipsă față de CAGR NOPAT 5 ani observat lipsă.

OE FY2024 fără termenul de capital de lucru: lipsă (față de lipsă cu ΔWC). Termenul ΔWC an de an face seria OE volatilă; o regulă de normalizare (de exemplu media pe 3 ani a ΔWC) este o decizie de luat în faza 2, nu o ipoteză a spike-ului.

### Poarta 5: interval de valoare intrinsecă

- Nu se calculează: insufficient_data (exerciții complete: niciunul).
- DCF invers: not_computed (no_price_source). Marja de siguranță: not_computed (no_price_source). Testul dolarului pe 5 ani: not_computed (no_price_source). Niciun furnizor de prețuri nu a fost accesibil din container (EODHD și Polygon cer cheie, stooq blocat, Yahoo limitat), deci toate metricile cu preț rămân necalculate.

## OMV Petrom SA (SNP), RON milioane

Sursă: ESEF via filings.xbrl.org. Exerciții disponibile: FY2020 la FY2022. Exerciții complete pentru regula de zece ani: 2020, 2021, 2022.

### Tabel A: venituri, profit net, câștigurile proprietarului, ROIC tangibil

| An | Venituri | Profit net | OE | ROIC tangibil |
|---|---|---|---|---|
| FY2020 | 19,717 | 1,291 | 1,291 | lipsă |
| FY2021 | 26,011 | 2,864 | 4,673 | 12.0% |
| FY2022 | 61,344 | 10,301 | 9,420 | 44.9% |

### Tabel B: ROIC incremental, categorie, datorie netă, conversie în numerar

| An | ROIC incr. 5 ani | Categorie 2007 (de validat) | Datorie netă / OE | CFO / profit net |
|---|---|---|---|---|
| FY2020 | lipsă | lipsă | lipsă | 4.30x |
| FY2021 | lipsă | lipsă | lipsă | 2.44x |
| FY2022 | lipsă | lipsă | lipsă | 1.10x |

ROIC incremental pe 10 ani la FY2022: lipsă. Acoperirea dobânzilor FY2022: 16.59x. Capex/vânzări FY2022: 5.2%. Identitatea creșterii FY2022: g implicit = 3.8% față de CAGR NOPAT 5 ani observat lipsă.

OE FY2022 fără termenul de capital de lucru: 12,157 (față de 9,420 cu ΔWC). Termenul ΔWC an de an face seria OE volatilă; o regulă de normalizare (de exemplu media pe 3 ani a ΔWC) este o decizie de luat în faza 2, nu o ipoteză a spike-ului.

### Poarta 5: interval de valoare intrinsecă

- Nu se calculează: insufficient_data (exerciții complete: 2020, 2021, 2022).
- OE FY2022 există (9,420), dar poarta nu trece fără zece ani.
- DCF invers: not_computed (no_price_source). Marja de siguranță: not_computed (no_price_source). Testul dolarului pe 5 ani: not_computed (no_price_source). Niciun furnizor de prețuri nu a fost accesibil din container (EODHD și Polygon cer cheie, stooq blocat, Yahoo limitat), deci toate metricile cu preț rămân necalculate.

## Jurnalul problemelor de date

Grupat pe companie, severitate și tip, limitat la fereastra de analiză plus anul de bază; perioadele sunt comasate. Jurnalul complet, linie cu linie și pentru toți anii, este în `out/data_issues_us.csv`, `out/data_issues_eu.csv` și `out/data_issues_metrics.csv`.

| Companie | Severitate | Concept | Perioade | Problemă |
|---|---|---|---|---|
| AAPL | high | d_and_a | 2016 | etichete sinonime cu valori diferite; cea mai recent depusă păstrată, necesită verificare |
| AAPL | high | diluted_shares | 2018 | split de acțiuni retratat doar în rapoartele ulterioare; seria pe acțiune inutilizabilă fără factor de split |
| AAPL | high | dividends_paid | 2016 la 2017 | etichete sinonime cu valori diferite; cea mai recent depusă păstrată, necesită verificare |
| AAPL | high | tangible_capital | 2016, 2020, 2022 la 2025 | capital tangibil nepozitiv: ROIC semnalat, nu calculat |
| AAPL | medium | cfo | 2016 la 2017 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| AAPL | medium | current_liabilities | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| AAPL | medium | d_and_a | 2016 la 2017 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| AAPL | medium | debt_long | 2015 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| AAPL | medium | diluted_shares | 2018 la 2019 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| AAPL | medium | dividends_paid | 2015 la 2016 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| AAPL | medium | goodwill | 2018 la 2025 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| AAPL | medium | interest_expense | 2024 la 2025 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| AAPL | low | cfo | 2015 | schimbare de etichetă XBRL între exerciții |
| AAPL | low | d_and_a | 2015 la 2016 | schimbare de etichetă XBRL între exerciții |
| AAPL | low | intangibles | 2018 la 2025 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| AAPL | low | revenue | 2016 la 2017 | schimbare de etichetă XBRL între exerciții |
| AAPL | low | st_borrowings | 2015 la 2025 | etichetă de rezervă (mai largă sau mai îngustă) folosită, notată |
| AAPL | low | st_investments | 2015 la 2025 | sumă parțială: o componentă lipsește |
| AAPL | low | st_investments | 2018 | schimbare de etichetă XBRL între exerciții |
| AAPL | info | all | toate | companyfacts nu expune decimals și nici etichetele proprii; ambele cer instanța XBRL a raportului |
| AAPL | info | d_and_a | 2015 | suprascriere per emitent spre eticheta corectă, justificată |
| AAPL | info | fiscal_year | 2015 la 2025 | exercițiu de 52 sau 53 de săptămâni |
| KO | high | revenue | 2017 | etichete sinonime cu valori diferite; cea mai recent depusă păstrată, necesită verificare |
| KO | high | tangible_capital | 2024 | capital tangibil nepozitiv: ROIC semnalat, nu calculat |
| KO | medium | capex | 2017 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | cash | 2017 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | cfo | 2016 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | current_assets | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | current_liabilities | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | debt_long | 2015, 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | goodwill | 2017 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | income_tax | 2017 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | intangibles | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | interest_expense | 2017 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | ltd_current | 2015, 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | operating_income | 2016 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | ppe_net | 2017 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | pretax_income | 2017 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | revenue | 2017 la 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | medium | st_borrowings | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| KO | low | debt_long | 2023 | schimbare de etichetă XBRL între exerciții |
| KO | low | intangibles | 2020 la 2025 | sumă parțială: o componentă lipsește |
| KO | low | intangibles | 2020, 2024 | schimbare de etichetă XBRL între exerciții |
| KO | low | ltd_current | 2023 | schimbare de etichetă XBRL între exerciții |
| KO | low | revenue | 2016 | schimbare de etichetă XBRL între exerciții |
| KO | low | st_borrowings | 2015 la 2016 | etichetă de rezervă (mai largă sau mai îngustă) folosită, notată |
| KO | low | st_borrowings | 2017, 2019, 2022 | schimbare de etichetă XBRL între exerciții |
| KO | low | st_investments | 2021 | schimbare de etichetă XBRL între exerciții |
| KO | info | all | toate | companyfacts nu expune decimals și nici etichetele proprii; ambele cer instanța XBRL a raportului |
| KO | info | current_liabilities | 2015 | diferență doar de rotunjire între rapoarte |
| MCO | high | tangible_capital | 2016, 2020 la 2021 | capital tangibil nepozitiv: ROIC semnalat, nu calculat |
| MCO | medium | capex | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| MCO | medium | cfo | 2015 la 2017 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| MCO | medium | current_liabilities | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| MCO | medium | debt_long | 2015 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| MCO | medium | equity | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| MCO | medium | equity | 2015 la 2017 | capital propriu negativ |
| MCO | medium | operating_income | 2016 la 2017 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| MCO | medium | pretax_income | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| MCO | medium | st_investments | 2018 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| MCO | low | debt_long | 2020 | etichetă de rezervă (mai largă sau mai îngustă) folosită, notată |
| MCO | low | debt_long | 2020 la 2021 | schimbare de etichetă XBRL între exerciții |
| MCO | low | dividends_paid | 2017 | schimbare de etichetă XBRL între exerciții |
| MCO | low | ltd_current | 2015, 2020 la 2022 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| MCO | low | pretax_income | 2019 | schimbare de etichetă XBRL între exerciții |
| MCO | low | revenue | 2016 | schimbare de etichetă XBRL între exerciții |
| MCO | low | st_borrowings | 2015 la 2016, 2018 la 2025 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| MCO | low | st_borrowings | 2017 | schimbare de etichetă XBRL între exerciții |
| MCO | low | st_investments | 2015 la 2025 | sumă parțială: o componentă lipsește |
| MCO | info | all | toate | companyfacts nu expune decimals și nici etichetele proprii; ambele cer instanța XBRL a raportului |
| MCO | info | capex | 2017 | diferență doar de rotunjire între rapoarte |
| MCO | info | cfo | 2017 la 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | current_assets | 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | d_and_a | 2017 la 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | debt_long | 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | equity | 2016 la 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | goodwill | 2017 la 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | income_tax | 2017 la 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | intangibles | 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | interest_expense | 2017 la 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | ltd_current | 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | net_income | 2017 la 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | operating_income | 2017 la 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | ppe_net | 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | pretax_income | 2017 | diferență doar de rotunjire între rapoarte |
| MCO | info | revenue | 2017 la 2018 | diferență doar de rotunjire între rapoarte |
| MCO | info | share_repurchases | 2017 la 2018 | diferență doar de rotunjire între rapoarte |
| LVMH | high | all | toate | istoric ESEF scurt pe filings.xbrl.org; regula de zece ani nu poate fi îndeplinită din această sursă |
| LVMH | high | d_and_a | 2020 la 2024 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| LVMH | medium | ComprehensiveIncome | 2021 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| LVMH | medium | ComprehensiveIncomeAttributableToNoncontrollingInterests | 2022 la 2023 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| LVMH | medium | ProfitLossAttributableToNoncontrollingInterests | 2022 la 2023 | retratare: valoarea din raportul mai nou diferă de cea veche; cea mai nouă păstrată, ambele în jurnal |
| LVMH | medium | interest_expense | 2020 la 2021 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| LVMH | medium | pretax_income | 2020 la 2024 | profit înainte de impozit neetichetat; afișat ca identitate profit + impozit, marcat derivat |
| LVMH | medium | share_repurchases | 2020 la 2024 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| LVMH | low | ltd_current | 2020 la 2024 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| LVMH | low | operating_income | 2022 | schimbare de etichetă XBRL între exerciții |
| LVMH | low | st_investments | 2020 la 2024 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| LVMH | info | all | 2021 la 2024 | unități ignorate (pe acțiune, rapoarte) |
| LVMH | info | capex | 2020 la 2024 | suprascriere per emitent spre eticheta corectă, justificată |
| LVMH | info | interest_expense | 2022 la 2024 | suprascriere per emitent spre eticheta corectă, justificată |
| LVMH | info | operating_income | 2022 la 2024 | suprascriere per emitent spre eticheta corectă, justificată |
| SNP | high | all | toate | istoric ESEF scurt pe filings.xbrl.org; regula de zece ani nu poate fi îndeplinită din această sursă |
| SNP | medium | debt_long | 2020 la 2022 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| SNP | medium | diluted_shares | 2020 la 2022 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| SNP | medium | goodwill | 2020 la 2022 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| SNP | medium | share_repurchases | 2020 la 2022 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| SNP | low | capex | 2021 | schimbare de etichetă XBRL între exerciții |
| SNP | low | cfo | 2020 la 2022 | etichetă de rezervă (mai largă sau mai îngustă) folosită, notată |
| SNP | low | current_assets | 2020 la 2022 | etichetă de rezervă (mai largă sau mai îngustă) folosită, notată |
| SNP | low | current_liabilities | 2020 la 2022 | etichetă de rezervă (mai largă sau mai îngustă) folosită, notată |
| SNP | low | d_and_a | 2020 la 2022 | etichetă de rezervă (mai largă sau mai îngustă) folosită, notată |
| SNP | low | ltd_current | 2020 la 2022 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| SNP | low | st_borrowings | 2020 la 2022 | concept neraportat în taxonomia standard; marcat lipsă (posibil etichetă proprie sau linie inexistentă) |
| SNP | info | all | 2021 la 2022 | unități ignorate (pe acțiune, rapoarte) |
| SNP | info | all | 2021 la 2022 | depuneri duplicate pentru același exercițiu (versiuni lingvistice sau al doilea OAM) |
| SNP | info | all | toate | monedă diferită de USD/EUR; fără conversie, fără amestec |
| SNP | info | capex | 2020 la 2022 | suprascriere per emitent spre eticheta corectă, justificată |

