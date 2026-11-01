# Audit C: cumpărare, deținere, vânzare, netransferabil, exemplul Coca-Cola

Data: 2 noiembrie 2026. Obiect: secțiunile „How to buy”, „How to own”, „How to sell”, „What is not transferable” din context/recipe.md și faptele din scrisori ale exemplului Coca-Cola, verificate pe corpusul din /home/claude/corpus/txt; apoi regulile instituționale Berkshire și discursurile Munger, pentru principii recurente care lipsesc.

Metodă și convenții:
- grep -n -i cu context pe tot corpusul; fiecare frază verbatim de mai jos a fost verificată automat (spații normalizate) în fișierul indicat.
- Un an înseamnă fișierul <an>.txt. OM = Owner's Manual (1996, actualizat); FL98 = Florida 1998; USC94, HV95 = discursurile lui Munger; VI = valoare intrinsecă; OE = câștigurile proprietarului.
- Recurența numără documente distincte; textele de 50 de ani sunt în 2014.txt și se numără o dată; raportul anual 2024 nu se numără separat de scrisoarea 2024.
- O singură căutare web, pentru regula de 40% (C-09), care alimentează SG-087: [scrisoarea parteneriatului din 20 ianuarie 1966](https://buffett-knowledge-map.pages.dev/partnership/1966_01_20).

## Partea 1. Regulile din rețetă față de corpus

### Tabelul 1. Dovezi

| ID | Principiul | Dovezi găsite | Recurență | Clasificare |
|---|---|---|---|---|
| C-01 | Prețul ultimul; nu justifică o afacere mai slabă | 1977 (prețul, al patrulea criteriu), 1979, 1989, 1999, 2014 (planul lui Munger): "a comfortable business at a questionable price, we much prefer the latter" (1999) | 5 (1977, 1979, 1989, 1999, 2014) | Regulă recurentă |
| C-02 | Aștepți mingea ideală, ca Ted Williams | 1994 (zona preferată), 1997 (77 de celule; nu poți fi eliminat), 2025 (Abel): "waiting for the fat pitch would mean a trip to the Hall" (1997) | 3 (1994, 1997, 2025) | Regulă recurentă |
| C-03 | Cartela cu 20 de perforări | doar USC94, unde Munger redă prelegerile lui Buffett; absentă din scrisori și din FL98: "giving you a ticket with only 20 slots in it" (USC94, 1994) | 1 (USC94) | Regulă enunțată o dată |
| C-04 | Cumperi pe pesimism, nu din contrarianism | 1990, 1997 (articolul Forbes din 1979), 2008, 2013, OM (scăderea pieței e o veste bună), plus frica și lăcomia (1986, 2004, 2006): "It's optimism that is the enemy of the rational buyer." (1990) | 8 (1986, 1990, 1997, 2004, 2006, 2008, 2013, OM) | Regulă recurentă |
| C-05 | Afaceri excelente cu o problemă temporară, rezolvabilă | 1980 (GEICO, ca AmEx în 1964), 1989, 1990 (Wells Fargo), USC94; Apple și „10-14x” lipsesc: "a marvelous business encounters a one-time huge, but solvable, problem" (1989) | 4 (1980, 1989, 1990, USC94) | Regulă recurentă |
| C-06 | Evaluezi prețul, nu alegi momentul | 1992, 1994, 1997, 1999, 2013, 2014: "We try to price, rather than time, purchases." (1994) | 6 (1992, 1994, 1997, 1999, 2013, 2014) | Regulă recurentă |
| C-07 | Verificare agregată: dobânzi, profituri față de PIB | 1999 leagă profiturile de PIB și trimite la articolul Fortune; 2001 trimite la articolul din 10 decembrie; metafora gravitației lipsește: "We see the growth in corporate profits as being largely tied" (1999) | 1 indirectă (1999) | Neconfirmat în corpus (articolele Fortune din 1999 și din 10 decembrie 2001) |
| C-08 | Concentrare: 5-10 afaceri bine înțelese | 1978, 1984, 1988, 1993 (cinci până la zece companii), USC94, 1996, FL98 (șase afaceri ajung), 2025: "if you are a know-something investor" (1993) | 8 (1978, 1984, 1988, 1993, USC94, 1996, FL98, 2025) | Regulă recurentă |
| C-09 | Până la 40% într-o idee aproape sigură | corpusul are doar faptul AmEx de la mijlocul anilor 1960: "we put about 40% of Buffett Partnership Ltd.'s capital into the stock" (1994); regula însăși, cu condițiile ei, e în scrisoarea parteneriatului din 20 ianuarie 1966 (verificat pe web, nu în corpus) | 1 ilustrare (1994); regula: 1 sursă externă | Neconfirmat în corpus |
| C-10 | Cumperi mai mult la scădere, dacă teza ține | 1987 (recunoașterea întârziată e o șansă), 1990, 1994, OM (bucăți suplimentare din afacerile deținute); 2011 (IBM) privește răscumpărările emitentului: "pick up many more shares at the new, panic prices" (1990) | 4 (1987, 1990, 1994, OM) | Regulă recurentă |
| C-11 | Nu media în jos într-o afacere în declin | 1979 spune altceva, iar 1989 (țigara aruncată) la fel; nicio regulă de mediere: "conclude that turnarounds seldom turn" (1979) | 0 ca formulare | Instrument al nostru |
| C-12 | Fără bani împrumutați | OM 7, 1996 (inversare: fără împrumuturi mari), FL98 (LTCM), 2010, 2014, 2017 (tabelul celor patru scăderi), 2019: "borrowed money has no place in the investor's tool kit" (2014) | 7 (OM, 1996, FL98, 2010, 2014, 2017, 2019) | Regulă recurentă |
| C-13 | Numerarul: prețul capacității de a acționa, nu prognoză | 2008 (angajament public) până la 2025 (numerarul nu înseamnă retragere): "to always run Berkshire with more than ample cash" (2008) | 9 (2008, 2009, 2010, 2013, 2017, 2021, 2022, 2024, 2025) | Regulă recurentă |
| C-14 | Când nimic nu trece testele, aștepți | 1986, 1997, 2002, 2003 (poziția implicită: titluri de stat pe termen scurt), 2024, 2025: "pay off debt and stockpile funds" (1986) | 6 (1986, 1997, 2002, 2003, 2024, 2025) | Regulă recurentă |
| C-15 | Numerarul e loc de parcare, nu casă | 2008, despre agățarea de numerar: "is almost certainly a terrible policy if continued for long" (2008); 1998, 2004, 2024; „loc de parcare” apare doar în 1985-1987, despre arbitraj și obligațiuni | 4 (1998, 2004, 2008, 2024) | Regulă recurentă |
| C-16 | Locul implicit al capitalului: activele productive | 2011, 2024, 2025 (afaceri productive înaintea titlurilor de stat): "is our third category: investment in productive assets" (2011) | 3 (2011, 2024, 2025) | Regulă recurentă |
| C-17 | Cumperi doar ce poți ține la scădere de 50% | 2014 (trei scăderi de circa 50%), 2017 (37-59%), 2019 (doar fără împrumut și cu emoțiile stăpânite): "major drops in the market, perhaps of 50% magnitude or even greater" (2019) | 3 (2014, 2017, 2019) | Regulă recurentă |
| C-18 | Fond indexat S&P 500 ieftin, cumpărat eșalonat | 1993 (investiție periodică), 1996, FL98, 2004, 2013 (testamentul 90/10), 2014, 2016, 2017 (pariul): "90% in a very low-cost S&P 500 index fund" (2013) | 8 (1993, 1996, FL98, 2004, 2013, 2014, 2016, 2017) | Regulă recurentă |
| C-19 | Deții ca pe o fermă, fără cotație zilnică | 1987, 1993 (bursa închisă un an sau doi), OM 1 (fermă deținută cu familia), 2013: "I have yet to see a quotation for either my farm" (2013) | 4 (1987, 1993, OM, 2013) | Regulă recurentă |
| C-20 | Urmărești doar economia afacerii și managementul | 1987 (deții cât timp randamentul, managementul și prețul sunt în regulă), 1996, 2025 (ajustare la schimbări fundamentale): "you need only monitor whether these qualities are being preserved" (1996) | 3 (1987, 1996, 2025) | Regulă recurentă |
| C-21 | Câștiguri look-through maxime peste un deceniu | 1989-2000 (11 scrisori), OM; definiția Berkshire scade impozitul ipotetic pe profitul nedistribuit (1990, 1991): "the highest possible look-through earnings a decade or so from now" (1991) | 12 (1989-1994, 1996-2000, OM) | Regulă recurentă |
| C-22 | Lași câștigătorii; nu tai florile, nu uzi buruienile | 1987 (nu vindem pentru că a crescut), 1988 (metafora îi aparține lui Peter Lynch), 2022, 2023: "likens such behavior to cutting the flowers and watering the weeds" (1988) | 4 (1987, 1988, 2022, 2023) | Regulă recurentă |
| C-23 | Buruienile își pierd importanța în timp | 2022 (Coca-Cola și AmEx față de o investiție stagnantă): "The weeds wither away in significance as the flowers bloom." (2022) | 1 (2022) | Regulă enunțată o dată |
| C-24 | Folosești amânarea impozitului | 1989 (avantaj real, dar nu motivul strategiei), OM (impozite amânate fără dobândă), USC94: "the governmental tax system gives you an extra 1, 2 or 3" (USC94) | 3 (1989, OM, USC94) | Regulă recurentă |
| C-25 | Aritmetica 1989: 692.000 față de 25.000 USD | 1989: 1 USD, 20 de dublări, impozit 34%; o singură plată la final lasă circa 692.000 USD (impozit circa 356.500), plata la fiecare dublare lasă circa 25.250 USD (impozit circa 13.000): "doubled 20 times during the 20 years" (1989) | 1 (1989) | Ilustrare punctuală |
| C-26 | Ignori costul de achiziție | nicio frază în corpus; costul contează pentru impozitul de transfer (1989) | 0 | Instrument al nostru |
| C-27 | Ignori prognoze, politică, dobânzi, comentatori | 1992, 1994, 1996 (rata de scont, comentatorii), 2013, 2014, 2019: "We will continue to ignore political and economic forecasts" (1994) | 6 (1992, 1994, 1996, 2013, 2014, 2019) | Regulă recurentă |
| C-28 | Răscumpărări sub VI în loc de dividende; testul dolarului | testul dolarului: 1983, 1984, OM 9, 2014 (Munger), 2025; răscumpărări: 1984, 1985, 1999, 2011 (două condiții), 2012, 2016, 2018, 2021-2023, 2025; 1983 nu conține răscumpărări: "Continuing shareholders are hurt unless shares are purchased below intrinsic value." (2011) | 14 (1983, 1984, 1985, 1999, 2011, 2012, 2014, 2016, 2018, 2021, 2022, 2023, 2025, OM) | Regulă recurentă |
| C-29 | Reestimezi valoarea intrinsecă o dată pe an | OM leagă revizuirea de dobânzi și de prognozele fluxurilor, nu de calendar: "an estimate that must be changed if interest rates move" (OM) | 0 pentru cadența anuală | Instrument al nostru |
| C-30 | Volatilitatea nu este risc | 1993 (adeptul beta), FL98, 2011, 2014: "Volatility is far from synonymous with risk." (2014) | 4 (1993, FL98, 2011, 2014) | Regulă recurentă |
| C-31 | „Pentru totdeauna”, implicit, pentru afaceri și manageri remarcabili | 1986-1987 (deținerile permanente; deții nedefinit cât timp randamentul, managementul și prețul sunt în regulă), 1988 (doar afaceri și manageri remarcabili), 2023, 2025: "our favorite holding period is forever" (1988) | 5 (1986, 1987, 1988, 2023, 2025) | Regulă recurentă |
| C-32 | Vinzi când ai greșit, fără amânare | 2005 (momentul să acționezi e acum), 2014 (Tesco, vândut prea încet), 2024 (context: decizii despre oameni): "The cardinal sin is delaying the correction of mistakes" (2024) | 3 (2005, 2014, 2024) | Regulă recurentă |
| C-33 | Vinzi la deteriorare structurală, nu ciclică | 1991 face distincția, dar nu vinde (regula deținerilor permanente); vânzarea la deteriorare: 1987 (randament prospectiv nesatisfăcător), 2014 (Tesco: cotă și marje în scădere), 2025: "significantly adjust a holding if we see fundamental changes" (2025) | 3 (1987, 2014, 2025) | Regulă recurentă |
| C-34 | Vinzi când managementul își pierde integritatea | 1987 (condiție de deținere), 2014 (Tesco, după răcirea față de management); 1989 privește alegerea partenerilor: "management is competent and honest, and the market does not overvalue" (1987) | 2 (1987, 2014) | Regulă enunțată o dată |
| C-35 | Vinzi la preț mult peste valoare sau pentru alternativă | 1987 (două motive separate: supraevaluarea; o idee mai ieftină sau mai bine înțeleasă), 2003-2004 (deținerile mari, printre care Coca-Cola), 2014 (prețul ridicat face din investiție speculație); excepție: deținerile permanente (1986, 1987): "In such a case, we will sell our holdings." (1987) | 4 (1987, 2003, 2004, 2014) | Regulă recurentă |
| C-36 | Vinzi când ai nevoie de bani; dimensionezi dinainte | analog Berkshire: 1987 (vânzări doar pentru pierderi extraordinare), 2014 (fără nevoi mari de numerar pe termen scurt): "manage our affairs so that sales are never required" (1987) | 0 pentru individ; 2 analoage | Instrument al nostru |
| C-37 | Nu vinzi pentru scădere, prognoză, profit, durată, apreciere | 1987 (apreciere, durată, maxima profitului luat), 1996 (rata de scont, comentatorii), OM (nici panică, nici doliu), 2013 (nu vinzi la vești proaste): "we do not sell holdings just because they have appreciated" (1987) | 4 (1987, 1996, OM, 2013) | Regulă recurentă |
| C-38 | Media în jos doar pentru afaceri solide, la panică | aceleași surse ca C-10: "buy more of a good thing at a bargain price" (1987) | 4 (duplicat al C-10) | Regulă recurentă |
| C-39 | Omisiunile costă mai mult decât faptele (Disney 1966) | 1983, 1989, 1991, FL98, 2008, 2014 (Munger: Walmart); Disney: cumpărat în 1966, vândut în 1967 la 48 (1995): "our most egregious mistakes fall in the omission, rather than the commission" (1991) | 6 (1983, 1989, 1991, FL98, 2008, 2014) | Regulă recurentă |
| C-40 | Filiale controlate: fără „gin rummy” | 1983 (principiile), OM 11 (precizare: doar afacerile controlate, nu titlurile), 2011, 2014 (Munger), 2024: "gin rummy managerial behavior (discard your least promising business at each turn)" (OM) | 5 (1983, OM, 2011, 2014, 2024) | Regulă recurentă |
| C-41 | Floatul de asigurări: pârghie ieftină, netransferabilă | OM 7, 1991 și 1993 (costul floatului, adesea sub zero, față de obligațiunile de stat pe termen lung), 2017: "two low-cost, non-perilous sources of leverage" (OM); 1,6-1,7x vine din Buffett's Alpha, în afara corpusului | 4 (OM, 1991, 1993, 2017) | Netransferabil |
| C-42 | Capital permanent, fără retrageri | 2017 (floatul nu poate fi retras), USC94: "We didn't have any clients who could fire us at Berkshire" (USC94) | 2 (USC94, 2017) | Netransferabil |
| C-43 | Fluxul de tranzacții și reputația | 1990 și 2014 (criteriile: confidențialitate, răspuns în cinci minute), 2008 (condiții inaccesibile pe piețe normale), 2024, 2025: "big investment opportunities can be confidentially shared with us" (2025) | 5 (1990, 2008, 2014, 2024, 2025) | Netransferabil |
| C-44 | Dimensiunea mică avantajează individul | 1992 (capitalul mare, o ancoră), 1994 (minimum 100 milioane USD pe idee), 1999, 2001, 2025, USC94: "a good $10 million idea could do wonders for us" (2001) | 6 (1992, 1994, 1999, 2001, 2025, USC94) | Regulă recurentă |
| C-45 | Doi Buffett: parteneriatul și calitatea din 1972 | 1989 (țigara aruncată), 2014 (1972, See's, planul lui Munger): "It took Charlie Munger to break my cigar-butt habits" (2014); 31,6% pe an în 1957-1968 vine din scrisorile parteneriatului, în afara corpusului | 2 (1989, 2014) | Netransferabil |
| C-46 | Abel CEO; aceleași reguli în scrisoarea din 2026 | 2025: concentrare, răbdare, răscumpărări sub VI estimată conservator, testul dolarului, bilanțul ca activ strategic; data de 1 ianuarie 2026 nu apare: "will not pay dividends so long as more than one dollar" (2025) | 1 (2025); repetă OM 3 și 9, iar restul are 3+ surse (C-08, C-13, C-14, C-28) | Regulă recurentă |
| C-47 | Prima cumpărare Coca-Cola: 1988 | 1988 (cumpărări majore), 1989 (14.172.500 acțiuni la sfârșitul lui 1988): "Only in the summer of 1988 did my brain finally establish contact" (1989) | 2 (1988, 1989) | Ilustrare punctuală |
| C-48 | Ultima cumpărare Coca-Cola: 1994 | 2003, 2010 (1995 e anul de după finalizare), 2022 (august 1994), 2023: "we last changed our position in Coca-Cola in 1994" (2003) | 4 (2003, 2010, 2022, 2023) | Ilustrare punctuală |
| C-49 | 400 milioane acțiuni, cost 1,3 miliarde; 7%, apoi 9,3% | tabelele 2012-2021 și 2025 (cost 1.299 milioane USD); 7,0% (1990, 1991), 7,8% (1994), 9,3% (31 decembrie 2025): "completed its seven-year purchase of the 400 million shares of Coca-Cola" (2022) | 12 (2012-2022, 2025) | Ilustrare punctuală |
| C-50 | Greșeala: nevânzarea la 50x în 1998 | 2003 și 2004 admit nevânzarea deținerilor mari în marea bulă (Coca-Cola e printre ele, dar nu e numită ca greșeală); 1999 alege explicit păstrarea; 50x și 1998 lipsesc: "I talked when I should have walked." (2004) | 2 generice (2003, 2004) | Neconfirmat în corpus (adunarea din 2006 sau presa) |
| C-51 | Multiplii exemplului: 15x, 7% plus 15%, 2% pe an | niciun multiplu în corpus; FL98 spune doar că prețul din 1987 era deja bun: "even though it was selling at a pretty good price" (FL98) | 0 | Neconfirmat în corpus (literatură secundară, calcul propriu) |
| C-52 | Faptele din 2025-2026: dividende, volume, valoare | „în afara corpusului”; reper în corpus la 31 decembrie 2025: 9,3%, valoare de piață 27.964 milioane USD, dividende 2025 de 816 milioane USD (2025) | 0 | Neconfirmat în corpus |

### Tabelul 2. Verdict

| ID | Atribuirea din rețetă corectă? | Unde e în produs | Verdict | Motiv |
|---|---|---|---|---|
| C-01 | da (nesursat; de adăugat 1977, 1999) | ordinea porților: Poarta 5 ultima; AC-G5-6 depinde de Poarta 4 | păstrăm | regulă stabilă, deja reflectată în arhitectura porților |
| C-02 | da (de adăugat 1994) | AC-G5-8, AC-G5-9 | păstrăm | prețul pe care l-aș plăti este zona de lovit |
| C-03 | nu (1990 și 1996, citați la „mindset”, nu o conțin; sursa: USC94) | lipsă | corectăm atribuirea | metaforă didactică, o apariție, relatată de Munger |
| C-04 | da (lipsește avertismentul din același paragraf) | lipsă; doar starea din AC-G5-9 | păstrăm | adăugăm: contrarianismul e la fel de nechibzuit ca turma (1990) |
| C-05 | nu (Apple 2016 și 10-14x lipsesc; AmEx 1964 și GEICO 1976 corecte: 1980, 1989) | lipsă; indirect AC-G2-3 (moduri de a muri) | corectăm atribuirea | în scrisori Apple ilustrează răscumpărările, nu o problemă temporară |
| C-06 | da | AC-G5-8; 3.2 (fără timing) | păstrăm | verbatim 1994, repetat în cinci scrisori |
| C-07 | da (în afara corpusului; 1999 și 2001 trimit la articole) | exclus intenționat (3.2) | păstrăm | doar context; produsul exclude corect macro |
| C-08 | da | SG-087 (faza 3) | păstrăm | concentrarea e regula; cifra 5-10 apare doar în 1993 |
| C-09 | da (verificat pe web, nu în corpus: 20 ianuarie 1966) | SG-087; requirements §5 (Kelly, plafon 40%) | retrogradăm la instrument | regulă a parteneriatului, enunțată o dată; Kelly nu apare în corpus |
| C-10 | nu (1990 corect; 2011 privește răscumpărările IBM) | lipsă; doar AC-G5-9 | corectăm atribuirea | înlocuim 2011 cu 1987 și OM |
| C-11 | nu (1979: redresările rareori reușesc) | parțial: AC-G4-3, direcția „se îngustează” | corectăm atribuirea | reformulăm ca regula din 1979 |
| C-12 | da (de adăugat OM 7, 2010, 2019; LTCM e în FL98) | lipsă pentru investitor; Supraviețuirea vizează datoria companiei | păstrăm | cea mai repetată regulă de risc din corpus |
| C-13 | da | lipsă (Poarta 1, faza 3) | păstrăm | completăm cu pragul fixat dinainte (Partea 2) |
| C-14 | da | implicit: fără „trece” la Poarta 5 nu apare nicio stare | păstrăm | nu cere mecanism separat |
| C-15 | nu (metafora lipsește din 2008; „loc de parcare” în 1985-1987, alt sens) | lipsă | corectăm atribuirea | ideea rămâne, citată din 2008 și 2024 |
| C-16 | da | lipsă | păstrăm | confirmată de 2024 și 2025 |
| C-17 | da (nesursat; de adăugat 2014, 2017, 2019) | lipsă (Poarta 1) | păstrăm | în scrisori regula este: fără împrumut, emoții sub control |
| C-18 | da | lipsă; nicio comparație cu indexul | păstrăm | completăm cu comparația pe 5 ani (Partea 2) |
| C-19 | da (de adăugat 1987, 1993, OM 1) | parțial: AC-G5-8 recalculează zilnic, util doar la cumpărare | păstrăm | ecranul de deținere nu pune cotația în prim-plan |
| C-20 | da | SG-082, AC-MG-7 (faza 3) | păstrăm | 1987 adaugă a treia condiție: prețul nu e supraevaluat |
| C-21 | da | SG-086 (faza 3); requirements §5 | păstrăm | formula din requirements omite impozitul ipotetic |
| C-22 | nu (anul corect; metafora e a lui Peter Lynch) | parțial: SG-083 | corectăm atribuirea | Buffett citează metafora, nu o inventează |
| C-23 | da | lipsă | păstrăm | corolar ilustrativ, nu regulă separată |
| C-24 | da (lipsește precizarea din 1989) | SG-084 (faza 3) | păstrăm | motivul deținerii lungi sunt relațiile, nu impozitul |
| C-25 | da (25.250 rotunjit la 25.000) | AC-X-7 (test cu rezultat cunoscut) | păstrăm | cifrele se verifică exact |
| C-26 | nu (nesursat, convenție proprie) | contrazice SG-084 și SG-086, unde costul intră în impozit | retrogradăm la instrument | corect: costul nu contează, cu excepția impozitului |
| C-27 | da (nesursat; de adăugat 1992, 1994, 2014) | 3.2; AC-X-9 | păstrăm | aliniat cu P10 |
| C-28 | nu (1983 conține testul dolarului, nu răscumpărări) | SG-075, SG-076 (faza 3) | corectăm atribuirea | OM 9 reformulează testul pe 5 ani; 2011 cere și lichiditate |
| C-29 | nu („2014” susține doar volatilitatea) | SG-091 (atribuit 2014), SG-082 | retrogradăm la instrument | OM leagă revizuirea de dobânzi și fluxuri, nu de calendar |
| C-30 | da | 3.2 (fără beta); AC-X-1 | păstrăm | verbatim 2014, susținut de 1993 și 2011 |
| C-31 | da (lipsesc condițiile din 1987 și excepția deținerilor permanente) | SG-081, SG-082 (faza 3) | păstrăm | adăugăm cele trei condiții din 1987 |
| C-32 | da (de adăugat 2005, 2014) | AC-DD-3 (câmpul „ce m-ar contrazice”), SG-083 | păstrăm | Tesco (2014) e cazul de portofoliu |
| C-33 | nu (în 1991 Buffett nu vinde) | AC-G4-3, AC-G4-4 (direcția); SG-083 | corectăm atribuirea | sursele vânzării: 1987, 2014, 2025 |
| C-34 | nu (1989 privește alegerea partenerilor) | AC-MG-1..7, SG-083 (faza 3) | corectăm atribuirea | două surse; rămâne judecată umană |
| C-35 | nu (2004 corect, dar fără 50x; 2006 în afara corpusului; lipsește 1987) | SG-083, SG-084; intervalul VI (AC-G5-3) | corectăm atribuirea | 1987 dă două motive separate, rețeta le cere simultan |
| C-36 | nu (nesursat) | lipsă (Poarta 1) | retrogradăm la instrument | reformulăm: nicio vânzare nu trebuie să fie forțată (1987, 2014) |
| C-37 | nu (1987 acoperă doar aprecierea și durata) | lipsă ca protecție explicită | corectăm atribuirea | scăderea și comentatorii: 1996, 2013, OM |
| C-38 | da (duplicat) | lipsă | eliminăm | comasăm cu C-10 |
| C-39 | nu (Disney a fost o vânzare prematură; 2008 nu compară costurile) | SG-083 (doar greșelile comise) | corectăm atribuirea | exemplu corect: Walmart (2014) sau 1989 |
| C-40 | da | nu se aplică (filiale controlate) | păstrăm | OM 11 limitează regula la afacerile controlate |
| C-41 | da (în afara corpusului; corpusul compară cu obligațiunile pe termen lung) | exclus intenționat | păstrăm | corpusul confirmă pârghia ieftină |
| C-42 | da (nesursat; de adăugat 2017, USC94) | exclus intenționat | păstrăm | echivalentul pentru individ e corect |
| C-43 | da (nesursat) | exclus intenționat | păstrăm | confirmat de criterii și de Abel |
| C-44 | da (nesursat; de adăugat 1994, 2001) | exclus intenționat (context) | păstrăm | observație repetată de Buffett și Abel |
| C-45 | da (31,6% în afara corpusului; 1972 confirmat) | exclus intenționat | păstrăm | marcăm cifra ca externă |
| C-46 | da (data numirii lipsește din corpus) | context | păstrăm | toate cele cinci reguli apar la Abel |
| C-47 | da | setul de spike (PRD §9, întrebarea 4) | păstrăm | 1988 și 1989 concordă |
| C-48 | da | setul de spike | păstrăm | 2003, 2010 și 2022 concordă |
| C-49 | da (7% e aproximativ: 7,0-7,8%) | setul de spike | păstrăm | cost exact: 1.299 milioane USD |
| C-50 | nu (nici Coca-Cola la 50x, nici 1998 nu apar) | context | corectăm atribuirea | citat generic 2003-2004; remarca de epocă e din 1999 |
| C-51 | nu (nesursat) | context | corectăm atribuirea | marcat ca estimare externă, cu metoda |
| C-52 | în afara corpusului | prețul doar prin AC-G5-7 | păstrăm | marcat „în afara corpusului”, de verificat la sursă |

## Partea 2. Regulile instituționale ale Berkshire și Munger: ce lipsește

Am parcurs cele 15 principii din OM, criteriile de achiziție (1982-1991 și 2014), scrisoarea lui Abel (2025), cele două texte de 50 de ani (2014), USC94 și HV95. Candidații de mai jos sunt principii generale, repetate, care lipsesc din rețetă sau din produs.

| Principiul | Dovezi (fișier, an, frază) | Recurență | De ce contează pentru produs | Plasare propusă |
|---|---|---|---|---|
| P-01. Analiza pe două piste și lista de verificare psihologică | USC94 (interesele raționale, apoi influențele subconștiente), HV95 (25 de tendințe folosite ca listă): "I now use a kind of two-track analysis" (USC94) | 2 (USC94, HV95) | dosarul separă faptele de judecăți (P3), dar nu verifică judecata însăși | rețetă: „How to buy”, pas înainte de decizie; PRD: AC-DD-4 nou, listă bifată cu zece tendințe din HV95 (stimulente, inconsecvență, efectul de posesie, reacția la pierdere, dovada socială etc.), judecată atribuită, fără efect pe verdict |
| P-02. Cauți activ dovezile care te contrazic | HV95 (Darwin), 1989 și 2014 (gândacul: veștile proaste vin în serie), 2008 (de două ori): "should have caused me to re-examine my thinking and promptly take action" (2008) | 4 (1989, HV95, 2008, 2014) | câmpul „ce m-ar contrazice” (AC-DD-3) rămâne text nefolosit; declanșatoarele fixe din ux.md (ROIC sub prag doi ani) sunt instrumente ale noastre | rețetă: „How to sell”; PRD: în AC-DD-3, câmpul 4 se leagă de 1-3 fapte măsurabile alese de utilizator, comparate automat la re-subscriere (SG-082), afișate ca fapte |
| P-03. Post-mortem la interval fix, inclusiv pentru abțineri | 1989, 1991 (autopsiile ajută și investitorii), 2000 (Washington Post, la trei ani), 2014, 2024 (16 mențiuni ale greșelii), OM 12: "reality is honestly compared to the original projections" (2014) | 6 (1989, 1991, 2000, 2014, 2024, OM) | omisiunile rămân invizibile fără registru (1991); SG-083 nu are AC | rețetă: „The cadence”, la 3 ani; PRD: AC în SG-083: la 3 ani de la fiecare versiune înghețată, cu decizie sau abținere, diff automat între ipoteze și fapte |
| P-04. Timpul ajută afacerea excelentă și o penalizează pe cea mediocră | 1989, USC94 (randamentul acțiunii converge spre cel al afacerii), FL98, 2010 (Coca-Cola): "Time is the friend of the wonderful business" (1989) | 4 (1989, USC94, FL98, 2010) | justifică deținerea lungă doar pentru categoriile „excelent” și „bun” | rețetă: „How to own”, prima frază; PRD: notă în Poarta 6 (faza 3) lângă categoria din AC-G3-7, fără verdict |
| P-05. Emisiunea de acțiuni doar pentru valoare egală; emisiunile repetate, semnal de alarmă | OM 10, criteriile de achiziție (1982-1992), 2014 (Buffett și Munger), 2016 (General Re): "never invested in companies that are hell-bent on issuing shares" (2014) | 12 sau mai multe | creșterea OE totale poate ascunde diluarea; produsul acoperă doar răscumpărările (SG-076) | rețetă: „How to buy”; PRD: AC-G3 nou în v1: CAGR al acțiunilor diluate pe 10 ani, cu marcaj la pragul din 4.10, fără verdict singur |
| P-06. Măsori pe acțiune | OM 3 (din 1983), 2011, 2025 (de trei ori): "we measure by per-share progress" (OM) | 4 (1983, OM, 2011, 2025) | OE, ROIC și identitatea creșterii (AC-G3-5) sunt pe total companie | rețetă: „How to own”; PRD: în AC-G3-1 și AC-G3-5, serie OE pe acțiune diluată lângă total |
| P-07. Rezervă minimă de lichiditate fixată dinainte | 2008, 2009, 2010 (minim 10, uzual 20 miliarde USD), 2011 (nicio răscumpărare sub 20), 2013-2015, 2018 (20), 2021 (30), 2022, 2025: "$10 billion is our absolute minimum" (2011) | 11 (2008-2011, 2013-2015, 2018, 2021, 2022, 2025) | fără prag, numerarul devine prognoză; rețeta nu are prag | rețetă: „How to buy”; PRD: Poarta 1 (faza 3), parametru „rezervă minimă” setat de owner, afișat ca fapt lângă AC-G5-9 |
| P-08. Testul bursei închise: orizont minim asumat la cumpărare | 1987, 1993, 1996, OM 1, 2014 (minimum cinci ani pentru acțiunile Berkshire): "If you aren't willing to own a stock for ten years" (1996) | 5 (1987, 1993, 1996, OM, 2014) | AC-DD-3 cere descrierea la 10 ani, nu angajamentul de deținere | rețetă: „How to buy”; PRD: al cincilea câmp în AC-DD-3 (aș păstra-o cu bursa închisă cinci ani? da sau nu, cu motiv) |
| P-09. Stimulentele explică comportamentul | USC94, HV95 (prima tendință), 1985 (opțiuni la valoarea reală), 2006 (stimulente legate de rezultatele controlabile), 2023: "what determines the behavior are incentives for the decision-maker" (USC94) | 5 (1985, USC94, HV95, 2006, 2023) | managementul e judecat fără date despre remunerare | rețetă: „How to own”; PRD: SG-077 ridicat la Must în faza 3, cu extrase citate (AC-X-3) |
| P-10. Te compari cu indexul pe ferestre de cinci ani | 1983, OM 9 și 15, 2013, 2016, 2017 (pariul): "not less than a five-year test as a rough yardstick" (1983) | 5 (1983, OM, 2013, 2016, 2017) | funcția-obiectiv din rețetă cere comparația; produsul nu o are | rețetă: „How to own”; PRD: Poarta 1 (faza 3), randament rulant pe 5 ani față de S&P 500 cu dividende, după costuri, ca fapt |
| P-11. Inactivitatea ca politică | 1990, 1996, 2002, 2023 (somnul lui Rip Van Winkle), USC94: "Lethargy bordering on sloth remains the cornerstone of our investment style" (1990) | 5 (1990, USC94, 1996, 2002, 2023) | recalcularea zilnică (AC-G5-8) poate încuraja activitatea | rețetă: „How to own”; UX: numărul de decizii pe an și rulajul, ca fapte (Poarta 1); cartela de 20 (C-03) opțională |
| P-12. Filtrul reputațional și social | 2010 (reputația), 2025 (Salomon; criteriile de alocare): "Avoid businesses that undermine the fabric of society or could jeopardize" (2025) | 2 (2010, 2025) | nou ca filtru de investiție în 2025; rețeta are doar „fără risc reputațional” | rețetă: „How to buy”; PRD: câmp opțional de judecată în Poarta 4 sau Management, fără efect pe verdict |

Verificate, dar acoperite sau respinse:
- Acoperite: rețeaua de modele (USC94, HV95; rețeta, mindset 15); inversarea (1996, 2009, HV95; AC-G2-3 și Supraviețuirea; rețeta citează doar USC 2007 și Almanack, din afara corpusului); „gin rummy” (C-40, dar anti-rețeta trebuie să spună „doar afaceri controlate”); CEO-ul ca responsabil de risc (2022, 2025; AC-X-3); criteriile de achiziție (porțile 2-5); refuzul rapid (FL98, 2014, 2025; AC-G2-4).
- Respinse: „the big money is in the waiting”, „sit on your ass”, „it's not supposed to be easy” lipsesc din corpus și nu se citează; echivalentele din corpus sunt USC94 (câteva investiții mari, apoi aștepți) și 1990 (letargia).

## Partea 3. Erori găsite

1. Disney 1966 dat ca eroare de omisiune (C-39): 1995 arată cumpărarea din 1966 și vânzarea din 1967 ("In 1967 I sold out at 48 per share.", 1995); este o vânzare prematură. Omisiuni documentate: Walmart (Munger, 2014) și cumpărările „servite pe tavă” (1989).
2. Vânzarea la deteriorare structurală atribuită ziarelor din 1991 (C-33): în 1991 Buffett constată scăderea valorii, dar nu vinde, invocând regula deținerilor permanente ("investee holdings that we have classified as permanent", 1991). Sursele vânzării: 1987, 2014 (Tesco), 2025.
3. Vânzarea pe criteriul managementului atribuită lui 1989 (C-34): 1989 descrie cu cine intri în afaceri; vânzarea apare în 1987 (condiție de deținere) și 2014 (Tesco).
4. Regula (4) de vânzare (C-35): sursa explicită, 1987, lipsește; rețeta cere simultan supraevaluarea și o folosință mai bună, deși 1987 le dă ca motive separate; „2006 meeting” e în afara corpusului. Rețeta omite și excepția deținerilor permanente, nevândute nici la supraevaluare (1986, 1987); 2003 și 2004 regretă aceeași atitudine pentru deținerile mari din marea bulă: chiar lecția Coca-Cola.
5. SG-083 („Condiții de ieșire: 1989, 1991, 2004, 2024”) moștenește erorile 2-4; surse corecte: 1987, 2003-2004, 2014, 2024, 2025.
6. „Remarca din 1998” despre Coca-Cola la 50x (C-50): nu există în scrisori; remarca de epocă este din 1999 (afacerile arată mai bine decât acțiunile lor, iar Buffett alege să păstreze); admiterea greșelii vine în 2003 și 2004, fără multiplu.
7. Răscumpărări „(1983)” (C-28): 1983 nu are niciun pasaj despre răscumpărări; regula apare în 1984. Testul dolarului „pe 5 ani rulant” din 1983 e declarat formulat greșit în OM 9, care dă testul corectat (câștigul valorii contabile față de S&P și prima constantă față de valoarea contabilă); requirements §5 și SG-075 folosesc varianta retrasă. Lipsește și prima condiție din 2011: lichiditate suficientă.
8. Atribuiri punctuale greșite: „parking place” (C-15) nu e în 2008, ci în 1985-1987, despre arbitraj și obligațiuni; 2011 (C-10) descrie răscumpărările IBM, nu cumpărări suplimentare; 1979 (C-11) spune că redresările rareori reușesc, nu că nu se mediază în jos; Apple și „10-14x” (C-05) lipsesc; florile și buruienile (C-22) sunt metafora lui Peter Lynch; cartela de 20 (C-03) lipsește din 1990 și 1996; „(2014)” acoperă doar volatilitatea, iar SG-091 a preluat-o greșit pentru reestimarea anuală (C-29).
9. Deriva de accent: aritmetica 1989 (C-25) omite precizarea că deținerea lungă nu a fost aleasă pentru impozit; pesimismul (C-04) omite avertismentul despre contrarianism; formula look-through din requirements §5 (C-21) omite impozitul ipotetic (1990, 1991).
10. Plafonul de 40% și Kelly (C-09): regula din 1966 e reală, dar enunțată o dată și în afara corpusului; Kelly nu apare nicăieri, deci SG-087 și requirements §5 nu pot invoca USC94 pentru formulă.
11. „Abel CEO from 1 Jan 2026” (C-46): data nu apare în corpus; scrisoarea e semnată la 28 februarie 2026.

## Concluzie pentru fundație

Cele trei corecturi cele mai importante pentru secțiunile auditate:
1. Rescrie „How to sell” pe sursele reale: 1987 (trei condiții de deținere; vânzarea la supraevaluare și schimbul pe o idee mai ieftină sau mai bine înțeleasă, ca motive separate), 2005, 2014 (Tesco), 2024, 2025; elimină 1989 și 1991 ca surse de vânzare; numește excepția deținerilor permanente și regretul din 2003-2004; corectează SG-083 și înlocuiește Disney cu Walmart.
2. Separă regulile de instrumente: plafonul de 40% cu Kelly, reestimarea anuală, „ignori costul” (cu excepția impozitului), „vinzi când ai nevoie de bani” și declanșatoarele fixe din ux.md se marchează „instrument al nostru”, cu sursa reală alături (1966 pe web, OM, 1987, 2014).
3. Corectează alocarea capitalului: 1983 rămâne doar pentru testul dolarului, în forma reformulată din OM 9 (SG-075, requirements §5); răscumpărările se citează din 1984, 2011 (lichiditate plus discount), 2012, 2016. Din Partea 2 intră primele în produs câmpurile de infirmare (P-02) și post-mortemul la 3 ani (P-03).
