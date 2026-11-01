# Audit B: metoda de analiză și formulele motorului, verificate în corpus

Data: 2 noiembrie 2026. Domeniu: recipe.md, secțiunea „How to analyse a company (the method)” (filtrul, sursele de candidați, pașii 1-6), requirements_v0.md secțiunea 5 și pragurile din PRD 4.10 care invocă un an de scrisoare. Metodă: grep în /home/claude/corpus/txt. Prescurtări: OM = Owner's Manual; Fla98 = University of Florida, 1998; M94 = Munger, USC 1994; M95 = Munger, Harvard 1995; 50y = scrisoarea „Past, Present and Future” (2014); CA = criteriile de achiziție (scrisorile 1982-1991 și 2014). Afirmațiile din afara corpusului verificate pe web (o căutare pe afirmație) sunt marcate „verificat pe web, nu în corpus”. Citatele sunt verbatim, cel mult 12 cuvinte.

## Tabelul 1: Dovezi

| ID | Principiul sau formula | Dovezi găsite | Recurență | Clasificare |
|---|---|---|---|---|
| B-01 | Filtrul: înțelegi, economie bună, oameni cinstiți, preț | 1977.txt: "(1) one that we can understand, (2) with favorable long-term prospects" (1977) | 15: 1977, 1978, 1981, 1987, 1991, 1992, 1994, 1996, 2003, 2007, 2017, 2018, 2019, 2022, Fla98 | Regulă recurentă |
| B-02 | Prețul ultimul; majoritatea cad la prima poartă | 1978.txt; Fla98 (înțelegerea elimină 90%): "but (4) often prevents action" (1978) | 5: 1978, 2007, 2017, 2019, Fla98 | Regulă recurentă |
| B-03 | Candidați din 10-K, rapoarte de concurenți, reviste | negăsit ca regulă; 2017 o atribuie managerilor care au pierdut pariul: "studied 10-Ks, interviewed managements, read trade journals" (2017) | 0 | Neconfirmat în corpus |
| B-04 | Scuttlebutt; întrebi CEO ce rival ar cumpăra | buffett_florida1998.txt: "If you could only buy stock in one coal company" (Fla98) | 1: Fla98 | Regulă enunțată o dată |
| B-05 | Excluzi ce se vinde cu comision mare | munger_usc1994: "anything with a big commission and a 200-page prospectus, don't buy it" (M94) | 1: M94 | Regulă enunțată o dată |
| B-06 | Poți spune cum arată afacerea peste zece ani | buffett_florida1998.txt: "If I can't see where they will be ten years from now" (Fla98) | 5: 1996, 2005, 2010, 2011, Fla98 | Regulă recurentă |
| B-07 | Complexă sau în schimbare rapidă: exclusă | 1992.txt: "If a business is complex or subject to constant change" (1992) | 6: 1992, 1996, 1999, 2000, 2007, M94 | Regulă recurentă |
| B-08 | Motivul încape într-un paragraf, altfel nu cumperi | 1994.txt, nu Fla98: "big investment idea can usually be explained in a short paragraph" (1994) | 1: 1994 | Regulă enunțată o dată |
| B-09 | Grămada „prea greu” | expresia lipsește; cercul există: "knowing its boundaries, however, is vital" (1996) | 0; cercul: 1996, 1999, 2001, 2013, Fla98, M94 | Neconfirmat în corpus |
| B-10 | Puterea de preț, prima întrebare | 1981.txt; FCIC 2010 verificat pe web, nu în corpus: "an ability to increase prices rather easily" (1981) | 6: 1981, 1990, 1991, 2014, Fla98, M94 | Regulă recurentă |
| B-11 | Randament pe capital tangibil; cu și fără fond comercial | 2017.txt, 1983.txt (anexa); CA spun ROE: "good returns on the net tangible assets required to operate the business" (2017) | 13: 1983, 1987, 2007, 2010-2016, 2017, 2019, 2020 | Regulă recurentă |
| B-12 | ROE pe capital de început, nu creșterea EPS | 1977.txt; 1979.txt (testul principal): "operating earnings on beginning equity capital amounted to 19%" (1977) | 4: 1977, 1979, 1981, 1987 | Regulă recurentă |
| B-13 | Excelent, bun, groaznic după capitalul cerut | 2007.txt: "an ever-increasing stream of earnings with virtually no major capital requirements" (2007) | 2: 1992, 2007 | Regulă enunțată o dată |
| B-14 | Cifrele See's, FlightSafety, linii aeriene | 2007.txt: "a good, but far from See's-like, return on our incremental investment" (2007) | See's: 1983, 1991, 2007, 50y, cu cifre diferite | Ilustrare punctuală |
| B-15 | Creșterea contează doar la randament incremental bun | 1992.txt: "Growth benefits investors only when the business in point can invest" (1992) | 6: 1984, 1991, 1992, 2000, 2007, 2017 | Regulă recurentă |
| B-16 | OE: profit + amortizări minus capex de menținere | 1986.txt, singura cu termenul: "the average annual amount of capitalized expenditures for plant and equipment" (1986) | 1: 1986 | Regulă enunțată o dată |
| B-17 | Nu EBITDA, nu „cash flow” fără (c) | 2000.txt: "does management think the tooth fairy pays for capital expenditures?" (2000) | 11: 2000, 2001, 2002, 2012-2016, 2018, 2023, 2024 | Regulă recurentă |
| B-18 | Putere de câștig constantă; fără proiecții și redresări | CA; 1979.txt: "future projections are of little interest to us, nor are turn-around situations" (1982) | 13: 1979, 1982-1991, 1995, 2014 | Regulă recurentă |
| B-19 | Datorie puțină sau deloc | CA: "businesses earning good returns on equity while employing little or no debt" (1982) | 11: 1982-1991, 2014 | Regulă recurentă |
| B-20 | Test de stres Wells Fargo: 10% credite, 30% pierdere | 1990.txt: "averaging 30% of principal, the company would roughly break even" (1990) | 1: 1990 | Ilustrare punctuală |
| B-21 | Inflația favorizează afacerile cu puține active tangibile | 1983.txt (anexa): "During inflation, Goodwill is the gift that keeps giving" (1983) | 2: 1981, 1983 | Regulă enunțată o dată |
| B-22 | Moat durabil care protejează randamente mari | 1993.txt, 2007.txt: "setting up a protective moat around their economic castles" (1993) | 14: 1986, 1993, 1995, 1996, 2005, 2007, 2008, 2011-2016, Fla98 | Regulă recurentă |
| B-23 | Moat-uri: cost minim sau brand mondial | 2007.txt: "being the low-cost producer (GEICO, Costco) or possessing a powerful world-wide brand" (2007) | 9: 1983, 1986, 1991, 2007, 2013-2016, Fla98 | Regulă recurentă |
| B-24 | Munger: avantaje de scară; „surfing” | munger_usc1994: "advantages of scale are ungodly important" (M94) | 1: M94 | Regulă enunțată o dată |
| B-25 | Testul de franciză; franciza tolerează management slab | 1991.txt: "is thought by its customers to have no close substitute" (1991) | 2: 1983 (parțial), 1991 | Regulă enunțată o dată |
| B-26 | Testul capitalului: un rival cu un miliard | buffett_florida1998.txt: "give me a billion dollars and how much can I hurt" (Fla98) | 1: Fla98 | Regulă enunțată o dată |
| B-27 | Cere manager-vedetă, deci nu e afacere mare | 2007.txt: "if a business requires a superstar to produce great results" (2007) | 2: 1991 (reciproca), 2007 | Regulă enunțată o dată |
| B-28 | Inevitabili față de impostori | 1996.txt: "for every Inevitable, there are dozens of Impostors" (1996) | 1: 1996 | Regulă enunțată o dată |
| B-29 | Urmărești direcția moat-ului, nu nivelul | 2005.txt: "widening the moat must take precedence" (2005) | 11: 1986, 1990, 1991, 1995, 1996, 2005, 2007, 2008, 2011, 2012, Fla98 | Regulă recurentă |
| B-30 | Candoare: raportezi ce ai vrea să afli; greșeli admise | 1983.txt, ownman.txt (12): "tell you the business facts that we would want to know" (1983) | 6: 1983, 1989, 2000, 2002, 2024, OM | Regulă recurentă |
| B-31 | Testul dolarului pe profitul reținut | 1983.txt; ownman.txt îl reformulează: "at least $1 of market value for each $1 retained" (1983) | 3: 1983, 1984, OM | Regulă recurentă |
| B-32 | Răscumpărări doar sub valoarea intrinsecă | 2011.txt; nimic în 1983: "Continuing shareholders are hurt unless shares are purchased below intrinsic value" (2011) | 8: 1984, 1999, 2011, 2016, 2018, 2019, 2022, 2023 | Regulă recurentă |
| B-33 | Emisiune doar la valoare egală; fără imperiu | 1982.txt, 1983.txt, ownman.txt (8, 10): "A managerial wish list will not be filled at shareholder expense" (1983) | 7: 1981, 1982, 1983, 1984, 1996, 2017, OM | Regulă recurentă |
| B-34 | Rezistența la imperativul instituțional | 1989.txt: "an institution will resist any change in its current direction" (1989) | 3: 1989, 1990, 2004 | Regulă recurentă |
| B-35 | Integritate, inteligență, energie (Kiewit) | doar Fla98, despre angajări: "three things in hiring people: integrity, intelligence and energy" (Fla98) | 1: Fla98 | Regulă enunțată o dată |
| B-36 | Jocheu față de cal: economia afacerii domină | 1980.txt: "it is the reputation of the business that remains intact" (1980) | 3: 1980, 1985, 1989 | Regulă recurentă |
| B-37 | Moody's cumpărat fără a cunoaște managementul | FCIC 2010, verificat pe web, nu în corpus: "I knew nothing about the management of Moody's" (FCIC 2010) | 0 | Neconfirmat în corpus |
| B-38 | VI = numerarul scos pe durata rămasă, actualizat | ownman.txt: "discounted value of the cash that can be taken out" (OM) | 6: 1989, 1992, 1993, 1994, 2000, OM | Regulă recurentă |
| B-39 | Aesop; rata fără risc = obligațiuni lungi | 2000.txt: "which we consider to be the yield on long-term U.S. bonds" (2000) | 1: 2000 | Regulă enunțată o dată |
| B-40 | Estimări conservatoare | 2000.txt: "We try, therefore, to keep our estimates conservative" (2000) | 3: 1999, 2000, 2011 | Regulă recurentă |
| B-41 | Fără primă de risc; riscul prin certitudine și marjă | „risk premium”: zero apariții; doar structura Aesop (2000) | 0 | Neconfirmat în corpus |
| B-42 | Aproximativ corect; intervale, nu precizie falsă | 1993.txt: "better to be approximately right than precisely wrong" (1993) | 7: 1986, 1993, 1999, 2000, 2010, 2019, OM | Regulă recurentă |
| B-43 | Dacă nu e evident fără spreadsheet, nu e evident | absent; 2017 spune altceva: "Spreadsheets never disappoint" (2017) | 0 | Neconfirmat în corpus |
| B-44 | Companie minunată la preț corect | 1989.txt: "better to buy a wonderful company at a fair price" (1989) | 3: 1989, 2012, 2014 | Regulă recurentă |
| B-45 | Plafonul See's de 25 mil. ca disciplină de preț | 1991.txt, prezentat ca greșeală: "our dumb insistence on a $25 million price" (1991) | 3: 1991, 2007, 50y | Ilustrare punctuală |
| B-46 | Și cele mai bune afaceri pot fi supraplătite | 1996.txt: "pay too much for even the best of businesses" (1996) | 7: 1983, 1996, 2014, 2015, 2016, 2020, Fla98 | Regulă recurentă |
| B-47 | Coca-Cola la 50x în 1998, preț absurd | 2004.txt fără 50x; 2006 în afara corpusului: "I talked when I should have walked" (2004) | 1 parțial: 2004 | Ilustrare punctuală |
| B-48 | Marja de siguranță, mărită după incertitudine | 1992.txt; exemplul 83/80 vine din Superinvestors: "only slightly higher than its price, we're not interested in buying" (1992) | 5: 1990, 1992, 1997, 2019, Fla98 | Regulă recurentă |
| B-49 | Randamentul OE față de obligațiunea lungă | nicio regulă; sprijin conceptual: "a sensible multiple of earnings relative to then-prevailing interest rates" (2017) | 0 | Instrument al nostru |
| B-50 | Look-through: câștigurile subiacente ale participațiilor | 1991.txt (cu impozit ipotetic), ownman.txt: "the highest possible look-through earnings a decade or so from now" (1991) | 12: 1989-1994, 1996-2000, OM | Regulă recurentă |
| B-51 | Paragraf de decizie cu patru întrebări | sinteză din 1994, Fla98, M95: "making heavy use of inversion" (M95) | 0 | Instrument al nostru |
| B-52 | Lista de verificare din Almanack | lista lipsește; M95 recomandă liste: "assemble his skills into a checklist that he routinely uses" (M95) | 0 | Neconfirmat în corpus |
| B-53 | Apoi aștepți prețul | 2017.txt, 1997.txt: "That last requirement proved a barrier to virtually all deals" (2017) | 4: 1978, 1997, 1999, 2017 | Regulă recurentă |
| B-54 | Formula OE: minus creșterea anuală a capitalului de lucru | 1986.txt, doar incrementul de menținere: "If the business requires additional working capital to maintain its competitive position" (1986) | 1: 1986 | Regulă enunțată o dată |
| B-55 | Capex de menținere implicit min(capex, amortizare); Greenwald | contrazis de 1986 și 2015: "keep our businesses competitive while spending less than our depreciation charge" (2015) | 0 | Instrument al nostru |
| B-56 | ROIC incremental ΔNOPAT/Δcapital, 5 și 10 ani | 1991.txt: "compared with the incremental capital investment required to produce it" (1991) | 4: 1984, 1991, 1992, 2007 | Regulă recurentă |
| B-57 | Identitatea g = reinvestire × ROIC; marcaj la 5 puncte | formula lipsește: "can't for any extended period reinvest a large portion of their earnings" (2007) | 0 | Instrument al nostru |
| B-58 | Predictibilitate: CV al OE, ani cu pierdere, abatere | niciun prag, nimic în 1979: "earnings simply don't advance smoothly" (2002) | 0 | Instrument al nostru |
| B-59 | Categoria 2007: peste 30% și capex/vânzări ≤ 5% | 2007 fără praguri; benzi descriptive: "from 25% after-tax to more than 100%" (2010) | 0 | Instrument al nostru |
| B-60 | Supraviețuire: datorie netă/OE, EBIT/dobânzi, praguri, stres | pragurile lipsesc: "Our definition of coverage is pre-tax earnings/interest, not EBITDA/interest" (2012) | 0 pentru praguri | Instrument al nostru |
| B-61 | VI: DCF 10 ani + terminal; seturi; prag 10%; DCF invers | doar o perpetuitate ilustrativă: "Say, next, that a discount rate of 10% was used" (1991) | 0 | Instrument al nostru |
| B-62 | Marja cerută: 30-50% afacere, 15-25% franciză | niciun procent: "buy an estimated $1 of value for a very real 95 cents" (2019) | 0 | Instrument al nostru |
| B-63 | Schimbare cu impozit: (1 - t·g)(1+r2)^n < (1+r1)^n | 1989.txt, ilustrare: "this deferred tax liability is equivalent to a very large transfer tax" (1989) | 0 | Instrument al nostru |
| B-64 | Kelly fracționat, plafon 40% | „Kelly” absent; 1966 în afara corpusului: "They bet big when they have the odds" (M94) | 0 | Instrument al nostru |
| B-65 | Numerar excedentar 2%; persistență 8/10; 3 puncte | randamentele lui Buffett includ numerarul: "despite their holding large quantities of excess cash" (2015) | 0 | Instrument al nostru |
| B-66 | Fereastra de zece ani (AC-X-4, „1979”) | nimic în 1979: "a five-year rolling average to be appropriate for judging" (1984) | 0 | Instrument al nostru |

## Tabelul 2: Verdict

| ID | Atribuirea din rețetă corectă? | Unde e în produs | Verdict | Motiv |
|---|---|---|---|---|
| B-01 | Parțial: 1977 și 1978 cer preț „very attractive”, 1992 „attractive”; „sensible price” apare din 1987 | porțile 2-5; managementul lipsește din v1 (SG-074) | corectăm atribuirea | Regula e recurentă, formularea prețului nu. |
| B-02 | Parțial: ordinea da; „cad la prima poartă” doar Fla98; 1978 și 2017 arată prețul ca barieră principală | AC-X-10, AC-G5-8 | corectăm atribuirea | Ambele bariere sunt documentate. |
| B-03 | Nu: nu e regulă în corpus | lipsă (SG-093, faza 4) | retrogradăm la instrument | Practică a noastră. |
| B-04 | Da (Fla98) | lipsă; AC-G4-2 parțial | păstrăm | Enunțat o dată. |
| B-05 | Da (M94) | lipsă | păstrăm | Excludere pentru univers. |
| B-06 | Da; adăugăm 1996, 2005, 2010, 2011 | AC-G2-3, AC-DD-3 | păstrăm | Recurent, bine reflectat. |
| B-07 | Da | AC-G2-1, AC-G2-2, AC-G2-4 | păstrăm | Recurent. |
| B-08 | Nu: 1994, nu Fla98; „altfel nu cumperi” e întărirea noastră | AC-G2-3, AC-DD-3 | corectăm atribuirea | Textul spune „can usually be explained”. |
| B-09 | Nu: expresia nu e în corpus | AC-G2-4 | corectăm atribuirea | Sursa verificabilă e cercul (1996). |
| B-10 | Parțial: FCIC 2010 e în afara corpusului; în corpus: 1981, 1990, 1991, 2014, Fla98, M94 | AC-G4-2, opțional | corectăm atribuirea | Recurent în corpus, slab în produs. |
| B-11 | Nu: CA cer ROE cu datorie puțină; activele tangibile vin din 1983, 2010-2016, 2017, 2019 | AC-G3-3, AC-G5-10 | corectăm atribuirea | Măsura e corectă, sursa e alta. |
| B-12 | Parțial: 1977 da; testul explicit e din 1979 | AC-G3-6 | corectăm atribuirea | Adăugăm 1979. |
| B-13 | Da (2007) | AC-G3-7 | păstrăm | Taxonomie calitativă. |
| B-14 | Da; cifrele See's din 1972 diferă între scrisori și sunt înainte de impozit | AC-X-7, AC-G3-7 (teste) | păstrăm | Bune ca test, nu ca regulă. |
| B-15 | Da; adăugăm 1984, 1991, 2007, 2017 | AC-G3-4, AC-G3-5 | păstrăm | Recurent. |
| B-16 | Da | AC-G3-1 | păstrăm | Fidel dacă (c) rămâne medie de menținere. |
| B-17 | Da; termenul EBITDA apare din 2000 | AC-G3-1 | păstrăm | Recurent. |
| B-18 | Da | AC-G2-1, AC-G3-8 | păstrăm | Criteriu recurent. |
| B-19 | Da | AC-SV-1 | păstrăm | Recurent. |
| B-20 | Da ca exemplu, nu ca metodă | AC-SV-3, AC-SV-5 | retrogradăm la instrument | Un singur exemplu numeric. |
| B-21 | Da; adăugăm 1981 | lipsă | păstrăm | Lipsește un indicator de inflație. |
| B-22 | Da | AC-G4-1, AC-G4-3 | păstrăm | Recurent. |
| B-23 | Da | AC-G4-3 | păstrăm | Recurent. |
| B-24 | Da; M94 notează că Berkshire evită „surfing” pe tehnologie | AC-G4-3 | păstrăm | Enunțat o dată. |
| B-25 | Da | AC-G4-3, AC-G5-6 | păstrăm | Enunțat în 1991. |
| B-26 | Da | AC-G4-3, AC-G4-4 | păstrăm | Nu ar trebui să decidă singur „pică”. |
| B-27 | Da | AC-G4-3 | păstrăm | Enunțat o dată. |
| B-28 | Da | AC-G4-3 (opțional) | păstrăm | Concept enunțat o dată. |
| B-29 | Parțial: regula explicită e în 2005, 2007, Fla98 | AC-G4-1, AC-G4-3 | corectăm atribuirea | Adăugăm sursele principale. |
| B-30 | Da; adăugăm OM, 2000, 2002 | AC-MG-1..7 (faza 3) | păstrăm | Recurent. |
| B-31 | Parțial: OM declară formularea din 1983 greșită și o înlocuiește | SG-075 (faza 3), one_dollar_test | corectăm atribuirea | Formula trebuie să poarte corecția. |
| B-32 | Nu pentru 1983; prima apariție 1984; da 2011, 2016 | SG-076 (faza 3) | corectăm atribuirea | An greșit. |
| B-33 | Da | lipsă (SG-076 parțial) | păstrăm | Recurent, fără AC. |
| B-34 | Da; adăugăm 1990, 2004 | lipsă | păstrăm | Recurent, fără AC. |
| B-35 | Nu ca test de management: criteriu de angajare, citat o dată | lipsă | corectăm atribuirea | Alt context. |
| B-36 | Da; adăugăm 1980, 1985 | lipsă | păstrăm | Recurent. |
| B-37 | Sursa e în afara corpusului | lipsă | eliminăm | Anecdotă acoperită de B-25, B-36. |
| B-38 | Da; definiția exactă e în 1994 și OM | AC-G5-1 | păstrăm | Recurent. |
| B-39 | Da (2000) | AC-G5-2 | păstrăm | Explicit o dată. |
| B-40 | Da | AC-G5-3 (VI_low) | păstrăm | Recurent. |
| B-41 | Nu: nicio scrisoare nu discută prima de risc | AC-G5-2 (p = 0) | retrogradăm la instrument | Deducție, nu text. |
| B-42 | Da; adăugăm 1986, 1999, 2000, 2010 | AC-G5-3 | păstrăm | Susține intervalele. |
| B-43 | Nu: absent; pe web doar surse secundare | lipsă | eliminăm | Fără sursă primară. |
| B-44 | Da | AC-G5-6 (indirect) | păstrăm | Recurent. |
| B-45 | Nu: Buffett o numește insistență proastă (1991) și prudență greșită (50y) | lipsă | corectăm atribuirea | Sens inversat. |
| B-46 | Da; adăugăm 1983, 2014-2016 | AC-G5-8 | păstrăm | Recurent. |
| B-47 | Parțial: 2004 nu conține 50x | lipsă | corectăm atribuirea | Doar „talked when I should have walked”. |
| B-48 | Nu: 83/80 e din Superinvestors, nu din scrisoarea 1984; „după incertitudine” nu e enunțat | AC-G5-6, AC-G5-8 | corectăm atribuirea | Regula e recurentă, sursa greșită. |
| B-49 | Rețeta nu dă an; PRD citează 1991, unde testul lipsește | AC-G5-5 | retrogradăm la instrument | Verificare a noastră. |
| B-50 | Parțial: „randamentul” e al nostru; formula omite impozitul ipotetic | SG-086 (faza 3) | corectăm atribuirea | Aliniem la 1991. |
| B-51 | Sinteză a noastră | AC-DD-3 | retrogradăm la instrument | Format util. |
| B-52 | Lista nu e în corpus | lipsă | retrogradăm la instrument | Neverificabil. |
| B-53 | Da | AC-G5-9 | păstrăm | Recurent. |
| B-54 | Nu: doar incrementul de menținere, mediat în (c) | AC-G3-1, owner_earnings | corectăm atribuirea | Abaterea face OE volatil. |
| B-55 | Nu: 1986 și 2015 spun că (c) depășește de obicei amortizarea | AC-G3-2, 4.10 | retrogradăm la instrument | Implicitul contrazice scrisorile. |
| B-56 | Da; adăugăm 1991 | AC-G3-4 | păstrăm | Atenție la baza înainte de impozit. |
| B-57 | Nu: formula nu apare | AC-G3-5, 4.10 | retrogradăm la instrument | Poate penaliza afaceri de tip See's. |
| B-58 | Nu: 1979 și 1992 nu dau praguri | AC-G2-1, AC-G2-2, 4.10 | retrogradăm la instrument | Indicatori ai noștri. |
| B-59 | Nu: 2007 nu are praguri | AC-G3-7, 4.10 | retrogradăm la instrument | 30% nu e al lor. |
| B-60 | Nu: 1990 e exemplu; 2017 vorbește de levierul investitorului | AC-SV-1..4, 4.10 | retrogradăm la instrument | Definiția acoperirii e a lor, pragurile nu. |
| B-61 | Nu | AC-G5-1..4, 4.10 | retrogradăm la instrument | Structura DCF e a noastră. |
| B-62 | Nu: 1984, 1991, 1992 nu conțin procente | AC-G5-6, 4.10 | retrogradăm la instrument | Benzi propuse. |
| B-63 | Nu: 1989 ilustrează amânarea | SG-084, switch_with_tax | retrogradăm la instrument | Derivată de noi. |
| B-64 | Nu: Kelly absent | SG-087, kelly_fraction | retrogradăm la instrument | Instrument al nostru. |
| B-65 | Nu | 4.10, AC-G4-4, AC-G3-5 | retrogradăm la instrument | Praguri fără text. |
| B-66 | Nu: nimic în 1979 | AC-X-4, SG-023 | retrogradăm la instrument | Fereastră aleasă de noi. |

## Întrebări de fond

**(a) Câștigurile proprietarului (1986).** Componentele (a) și (b) sunt fidele: 1986 adaugă „depreciation, depletion, amortization, and certain other non-cash charges”, cu exemple din contabilitatea de achiziție (stocuri, impozit amânat), nu orice cheltuială fără numerar. Componenta (c) nu e fidelă: scrisoarea scade media anuală a capexului necesar menținerii poziției și volumului, iar capitalul de lucru intră doar ca increment de menținere („If the business requires additional working capital to maintain its competitive position”, incrementul intră în (c); firmele LIFO de obicei nu au nevoie de el la volum constant). Variația anuală a capitalului de lucru include creșterea și zgomotul (spike-ul a dat OE negativ la Coca-Cola în 2017). Scrisoarea avertizează „since (c) must be a guess” și citează „I would rather be vaguely right than precisely wrong”. Tot 1986 spune că de obicei (c) depășește (b), caz în care „GAAP earnings overstate owner earnings”; 2015 confirmă. Implicații: (c) e estimare (judecată, AC-X-2); OE se afișează ca interval, cu (c) între amortizarea pe cost istoric și capexul total, propagat în VI (AC-G5-3), cum cer 2000 („Using precise numbers is, in fact, foolish”) și 1999 („a range of values, rather than some pseudo-precise figure”). Implicitul min(capex, amortizare) presupune mereu cazul pe care 1986 îl tratează ca excepție.

**(b) Randamentul pe capital.** CA (1982-1991, 2014) cer „good returns on equity while employing little or no debt”: ROE, nu active tangibile. Activele tangibile nete apar în 2017 (lista „key qualities”), 2019, 2020 și în anexa din 1983: câștigul pe „unleveraged net tangible assets”, fără amortizarea fondului comercial, e cel mai bun ghid, iar achiziția se judecă la cost integral (cele două variante din AC-G3-3; vezi și 1987). „Return on equity capital” apare în 1977, testul „high earnings rate on equity capital employed” în 1979. Niciun prag numeric cerut. Cifre descriptive: See's 25% după impozit față de 11% la afacerea banală (1983); ROE de 10% era „good business” cu obligațiuni la 5% (1981, prag relativ); „only six had averaged a return on equity of over 30%” (1987, raritate); 2010-2016: „terrific economics” de la 25% după impozit și „good returns in the area of 12-20%”, singurele benzi recurente, dar descrieri, nu reguli. Cifrele din 2007 susțin măsurarea pe capitalul cerut (See's, 60% înainte de impozit în 1972), logica incrementală (See's: 32 mil. pentru circa 77 mil. profit în plus; FlightSafety: 509 mil. pentru 159 mil., circa 31% înainte de impozit, „good, but far from See's-like”) și taxonomia după capital. Nu susțin 30% (exemplul „bun” are circa 31% înainte de impozit, circa 20% după), capex/vânzări ≤ 5% sau „r + 5 puncte”; fiind înainte de impozit, testele AC-X-7 trebuie convertite la baza NOPAT.

**(c) Valoarea intrinsecă.** Definiția e recurentă: OM și 1994 („discounted value of the cash that can be taken out”), 1993, 1992 (Williams, „discounted at an appropriate interest rate”), 1989 („discounting them at prevailing interest rates”), 2000. Singura rată explicită: 2000, „which we consider to be the yield on long-term U.S. bonds”; certitudinea e o întrebare separată („How certain are you that there are indeed birds in the bush?”). „Risk premium”: zero apariții; „government bond”: 7 scrisori, niciuna despre actualizare. „Fără primă” e o deducție coerentă din 2000; practica apare doar în surse secundare (verificat pe web, nu în corpus). Pragul r = max(10%, randament + 0) din AC-G5-2 adaugă însă o primă implicită de 5-6 puncte când randamentul e 4-5%; 10% apare doar ca ipoteză ilustrativă (1991). Spreadsheet sau calculator: nimic în corpus; rezumatele secundare ale adunărilor relatează că Munger nu l-a văzut pe Buffett făcând un DCF (verificat pe web, nu în corpus). 2017 („Spreadsheets never disappoint”) critică prognozele care justifică achiziții. Scepticismul față de proiecții e recurent: CA, 1982, 1989, 1995 („Charlie and I never give them a glance”), 2002. DCF-ul cu 10 ani expliciți și creștere terminală e al nostru: singurul calcul din corpus e o perpetuitate (1991: 1 mil. cu creștere de 6%, actualizat cu 10%, face 25 mil.; fără creștere, 10 mil.), iar „ten or twenty years” (2010, 2011) e orizont calitativ. V0 nu actualiza valoarea terminală (corectat în AC-G5-1).

**(d) Marja de siguranță.** Nicio scrisoare nu dă un procent. 1992: „only slightly higher than its price, we're not interested in buying”; 1990 reia motto-ul lui Graham; 1997: prețurile au erodat marja; 2019 refuză „an estimated $1 of value for a very real 95 cents” (5% nu ajunge, dar fără prag). Exemplul 83/80 e din Superinvestors (1984), nu din scrisoarea 1984: „You don't try and buy businesses worth $83 million for $80 million”, plus podul de 30.000 de livre pentru camioane de 10.000 (verificat pe web, nu în corpus), tot fără procent. Singurul număr e al lui Graham, relatat de Munger: „one third or less of sellout value” (M94), metodă istorică. Benzile 30-50% și 15-25%, ca și marja mai mică pentru franciză, sunt instrumentul nostru (1991 nu discută marja).

**(e) Moat.** Definiții: 2007 (moat durabil, castelul atacat, cost minim sau brand, „enduring” exclude schimbarea rapidă, managerul-vedetă), 1986 (costurile GEICO), 1993 (moat în jurul castelelor economice), 1995 (castele cu moat-uri de netrecut), 1996 (scara lărgește moat-ul; Inevitabilii), Fla98 (castel, moat, duce cinstit; testul capitalului; Kodak „let that moat narrow”); 1991 definește franciza fără cuvântul moat. Recurență: „moat” în 14 surse, „castle” în 6 (1986, 1993, 1995, 1996, 2007, Fla98), „durable competitive advantage” în 7. Regula managerului-vedetă apare o singură dată (2007: „eliminates the business whose success depends on having a great manager”), cu reciproca în 1991 („franchises can tolerate mis-management”) și în tensiune cu M94 („So management matters, too”): rămâne întrebare, nu regulă decisivă.

**(f) Management.** Testul dolarului: 1983 (principiu), 1984 (regulă generală: „for every dollar retained by the corporation, at least one dollar”, pe cinci ani), OM 9: „we fail the test as I improperly formulated it”, înlocuit cu creșterea valorii contabile peste S&P și primă constantă față de valoarea contabilă; formula noastră reproduce versiunea retrasă. Răscumpărări: 1984, 1999 (fonduri peste nevoi și preț sub valoarea calculată conservator), 2011 („what is smart at one price is dumb at another”), 2016, 2018, 2019, 2022, 2023; nu 1983. Candoare: 1983 (al 12-lea principiu), OM 12, 2000 (regula rolurilor inversate), 2002 („will at some point be tempted to make up the numbers”), 2024 (de câte ori apare „mistake”). Imperativul instituțional: 1989, 1990 („the tendency of executives to mindlessly imitate the behavior of their peers”), 2004; 2017 descrie aceeași dinamică fără termen. „Integrity, intelligence and energy” apare doar în Fla98, ca regulă de angajare a lui Pete Kiewit; nu e în scrisori.

**(g) Regula celor zece ani.** Nu e regula lor: „ten years of”, „10 years of” și „decade” nu dau nicio regulă despre istoric, iar 1979 nu conține „ten” sau „decade”. „Zece ani” e orizont spre viitor: Fla98, 1996 („ten or twenty years from now”), 2010 și 2011 („look out ten or twenty years when making an acquisition”). Singura fereastră enunțată pentru trecut are cinci ani (1983, 1984, OM 9); CA cer putere de câștig constantă, fără durată. AC-X-4 e instrumentul nostru, citat greșit; îl păstrăm ca „parametru propus” și adăugăm fereastra de cinci ani.

**(h) Filtrul din 1977.** Reformulat în 1977, 1978 („priced very attractively”), 1981 (parțial), 1987, 1991 (de două ori), 1992 (citează crezul; „very attractive” devine „attractive”), 1994, 1996, 2003, 2007, 2017 (cu active tangibile și creștere internă), 2018, 2019, 2022 (parțial), Fla98. CA (1982-1991, 2014) îl redau altfel: putere de câștig constantă, ROE cu datorie mică, management existent, afacere simplă, preț. Nu apare ca filtru nici în 2013, nici în OM.

## Principii recurente care lipsesc

1. **Puterea de preț în Poarta 3.** Corpus: 1981 („an ability to increase prices rather easily”, fără pierdere de cotă sau volum), 1990, 1991 (franciza poate „regularly price its product or service aggressively”), 2014, Fla98, M94 („untapped pricing power”). Produs: doar AC-G4-2, opțional. Propunere: AC-G3-9 nou (marja brută și prețul pe unitate față de inflație pe 10 ani) și câmp obligatoriu în AC-G4-3 cu întrebarea din 1981.
2. **Compensarea în acțiuni și „profitul ajustat” nu se adaugă înapoi.** Corpus: 1992 și 1998 („If compensation isn't an expense, what is it?”), 2002, 2004, 2015, 2016 (restructurări și compensare în acțiuni), 2018. Produs: AC-G3-1 interzice „profit ajustat” ca intrare, dar „alte cheltuieli fără numerar” rămâne deschis. Propunere: AC-G3-1 restrâns la ajustările de achiziție (exemplele din 1986; 2014, 2015), cu test.
3. **Amortizarea e cost real și podeaua lui (c).** Corpus: 1986, 2001 (simulatoare de 162 mil. față de amortizare de 95 mil.), 2002, 2013, 2014 („Every dime of depreciation expense we report is a real cost”), 2015. Propunere: AC-G3-2 cu interval [amortizare pe cost istoric, capex total], marcat „estimare”.
4. **Gândirea pe acțiune și numărul de acțiuni.** Corpus: OM 4 („per-share progress”), 1982, 1983 și OM 10 (orice emisiune, inclusiv opțiuni), 2019, 2020, 2022 („When the share count goes down”). Produs: VI pe acțiune; răscumpărări în faza 3. Propunere: AC-G3-10 nou în v1: OE pe acțiune și CAGR al numărului de acțiuni pe 10 ani, informativ.
5. **Calitatea contabilă ca semnal despre management.** Corpus: 2000 (contabilitate vagă), 2002 („unintelligible footnotes usually indicate untrustworthy management”), 2007 (ipoteza de randament a pensiilor), OM 12 (fără „big bath”, fără netezire), 2016. Propunere: AC-MG-8 nou: marcaje pentru ipoteza pensiilor peste un parametru, restructurări recurente, restatări frecvente (date din AC-PR-6), „adjusted EPS” evidențiat.
6. **Băncile și asigurătorii nu se judecă prin OE și ROIC.** Corpus: float și subscriere în 44 de fișiere, de exemplu 1990, 1993, OM 7. Produs: AC-SV-5 acoperă doar supraviețuirea. Propunere: AC-X-11 nou, porțile 3 și 5 afișează „neaplicabil (financiară)” în v1.
7. **Folosirea profitului reținut, adusă în v1.** Corpus: 1984 (regula generală), 2019 („The Power of Retained Earnings”), 2020, OM 6 și 9. Produs: SG-075, faza 3, fără AC. Propunere: AC-G3-11 nou, testul dolarului informativ, cu corecția din OM.

Nu propunem: cartela cu 20 de perforări (în corpus doar M94, deci nerecurentă), look-through (există SG-086), fondul comercial (AC-G3-3), EBITDA (AC-G3-1), câștigurile disponibile proprietarilor (acoperite de OE și de conversia din AC-G3-4).

## Erori găsite

Rețeta (atribuiri și derive):

1. „Filter since 1977... sensible price”: 1977 și 1978 cer preț „very attractive”; 1992 trece la „attractive”; „sensible price” apare din 1987.
2. „Most candidates die at gate one”: doar Fla98; 1978 și 2017 arată că prețul blochează cel mai des.
3. „One paragraph (Florida 1998)”: e scrisoarea 1994, formulare descriptivă, fără „do not buy”.
4. „Too-hard pile”: expresia nu există în corpus.
5. „Pricing power first (FCIC 2010)”: sursă din afara corpusului; regula există în corpus, dar „first” vine doar din FCIC.
6. „Return on tangible capital (acquisition criteria)”: CA cer ROE cu datorie puțină; activele tangibile vin din 1983, 2010-2016, 2017, 2019.
7. „1977: judge by ROE not EPS growth”: testul explicit e în 1979.
8. „Buybacks only below intrinsic value... 1983”: 1983 nu conține răscumpărări; prima apariție e în 1984.
9. „Integrity, intelligence, energy (Kiewit rule)”: doar Fla98, regulă de angajare.
10. „See's $25m ceiling (1991)” ca disciplină de preț: 1991, 2007 și 50y o prezintă ca greșeală.
11. „Coca-Cola at 50x... 2004 letter”: 2004 nu conține 50x și nici „silly price”.
12. „Not $83m for $80m (1984)”: e articolul Superinvestors, nu scrisoarea 1984.
13. „No risk premium bolted on” și „if not obvious without a spreadsheet”: absente din corpus.
14. „Candidates come from reading 10-Ks, trade journals”: nu e regulă în corpus.
15. „Moody's without meeting management”: doar FCIC (verificat pe web).

Formulele (requirements_v0, secțiunea 5):

16. OE „minus creșterea capitalului de lucru” an de an, în loc de incrementul de menținere mediat în (c).
17. Capex de menținere min(capex, amortizare) atribuit lui 1986, care spune contrariul.
18. Testul dolarului fără corecția din OM.
19. Look-through „Σ cotă × profit net”, în loc de profitul operațional reținut minus impozitul ipotetic (1991).
20. Valoarea terminală neactualizată în v0 (corectată deja în AC-G5-1).
21. Kelly atribuit lui 1966 și M94.
22. Categoria 2007 cu praguri inexistente; testele compară cifre 2007 înainte de impozit cu un ROIC după impozit.
23. Identitatea creșterii (1992, 2000) și schimbarea cu impozit (1989): formule care nu apar în scrisori.

Ani de scrisori atașați parametrilor noștri (PRD):

24. AC-X-4: „zece ani de rapoarte; 1979”.
25. Marja 30-50% și 15-25%: „1984, 1991, 1992”.
26. Supraviețuire: „1990, 2017”.
27. Instabilitate „1992, 1979” și AC-G3-8 „1979”.
28. Persistența moat „2007, 1991”, numerarul excedentar „2017”, seturile VI „1986, 1993” și „1992, 2000”, AC-G5-5 „1991”.

Inconsistențe interne:

29. architecture.md față de PRD: seturile VI (g = min(0,5 × CAGR, 5%) și min(CAGR, 10%) față de g = 0 și min(CAGR, 8%)), fereastra categoriei (5 față de 10 ani), identitatea creșterii (CAGR NOPAT pe 5 ani față de CAGR OE pe 10 ani), conversia (CFO/profit față de OE/profit).
30. Rețeta spune că nu se adaugă primă de risc, dar pragul de 10% din AC-G5-2 adaugă una implicit.

## Concluzie pentru fundație

Fundația e solidă la nivel de principii: 29 din 66 de rânduri sunt reguli recurente, iar porțile 2-5 urmează un filtru reformulat în 15 surse. Slăbiciunea e numerică: 17 rânduri trebuie retrogradate la instrument, iar aproape fiecare prag din PRD 4.10 poartă un an de scrisoare care nu îl conține. Cele trei corecții cele mai importante:
1. OE, coloana vertebrală a motorului: (c) ca medie de menținere, cu podeaua la amortizare, fără variația anuală a capitalului de lucru și fără adăugarea compensării în acțiuni; OE afișat ca interval și marcat „estimare”.
2. Toate pragurile (30%, marjele, supraviețuirea, persistența, zece ani, 10%, DCF-ul pe 10 ani, Kelly) afișate ca „parametru propus”; coloana „Sursă metodă” devine „inspirat din (nu regulă)”, ancorată unde se poate în cifre reale (25% și 12-20% pe active tangibile, 2010-2016; acoperirea pre-tax/dobânzi, 2012-2016).
3. Corectarea atribuirilor din rețetă (filtrul 1977/1987, CA față de 2017, 1994, See's, Superinvestors, 1984 pentru răscumpărări, corecția din OM la testul dolarului) și adăugarea puterii de preț, cu sursele din corpus.

Surse web consultate (verificat pe web, nu în corpus): [Superinvestors of Graham-and-Doddsville (PDF)](https://www.lapasserelle.com/courses/advanced_finance/documents/TheSuperinvestorsofGraham-and-Doddsville-WarrenE.Buffett.pdf); [FCIC Interview of Warren Buffett, 26 mai 2010](https://ritholtz.com/2016/03/fcic-buffett/); pentru DCF și rata de actualizare doar surse secundare, de exemplu [25iq](https://25iq.com/2015/11/21/why-and-how-do-munger-and-buffett-discount-the-future-cash-flows-at-the-30-year-u-s-treasury-rate/) și [recapio](https://recapio.com/digest/ive-never-seen-warren-do-discounted-cashflows-warren-charlie-on-applying-huge-margin-of-safety-by-id).
