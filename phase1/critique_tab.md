# Critică și riscuri: de ce ar putea să nu meargă

Data: 2 noiembrie 2026. Două voci: mai jos este poziția orchestratorului (cu ce sunt de acord, cu ce nu, și ce recomand să decizi), apoi raportul integral al unui auditor adversar independent, care a citit toate documentele fazei 1 și datele reale din spike fără să fi văzut produsul înainte. Niciun risc de mai jos nu e teoretic: fiecare pleacă de la un document sau de la o cifră din spike.

## Poziția orchestratorului

Verdictul meu, înainte de al auditorului: produsul merită construit, dar nu în forma din PRD v1. Nucleul (fapte din surse primare cu proveniență, reconciliate la raport; motor de formule pur, cu teste; dosar înghețat cu paragraful de dinainte de cumpărare și post-mortem) este partea din metodă pe care aproape nimeni nu o face și e ieftină. Restul (șase porți cu verdicte, aplicație multi-utilizator, judecăți AI, BVB, screening, Kelly) este unde produsul riscă să devină exact ce respinge rețeta: un spreadsheet care dă impresia de analiză. Auditorul ajunge la aceeași concluzie pe altă cale, cu dovezi pe care nu le aveam: Coca-Cola, exemplul rețetei, pică propriile reguli ale produsului pe datele reale din spike (OE cu ΔWC an de an de 4,1 miliarde față de 13,1 fără, valoare intrinsecă de 8 la 9 USD pe acțiune, datorie netă la 7,2x OE, Supraviețuire „pică”). Asta nu e un bug de date, e formula greșită, și auditul principiilor (tabul precedent) arată de ce: (c) din 1986 e o estimare medie de menținere, nu variația anuală a capitalului de lucru.

Unde sunt de acord fără rezerve, și ce schimb: formula OE și capexul de întreținere (corecția 1 din audit); precizia falsă (VI cu două cifre semnificative, grilă de sensibilitate, „prețul pe care l-aș plăti” ca judecată umană pornită de la cifre, nu ca formulă); pragul de 10% peste tot (rată pe monedă, ancorată în obligațiunea lungă); capitalul tangibil neglijabil ca stare pozitivă pentru Apple și Moody's, nu ca eroare; regula celor zece ani înmuiată la „necesită judecată (istoric scurt)”; verdictele fără nicio agregare vizibilă, ca să nu devină scor compozit; eliminarea Kelly și a probabilităților de „moarte” în trepte de 5% (rămân cele trei moduri de a muri, ca text); divergențele dintre PRD și arhitectură închise printr-un singur fișier de reguli cu test în CI; setul de aur completat cu companii care au eșuat (GE, Boeing, Intel, Kraft Heinz e deja), ca să nu calibrăm pragurile pe câștigătorii de azi; QA cu al doilea cititor uman, nu doar aritmetic; acord scris și opinie juridică înainte de primul partener; accesul doar prin Tailscale, fără port deschis pe Mac Mini.

Unde sunt parțial de acord: „prețul ultimul”. Calculul porții 5 poate rula oricând, dar interfața nu îl arată până când textele porții 2 (descrierea pe 10 ani, cele trei moduri de a muri, paragraful) sunt scrise și confirmate; recalcularea devine săptămânală, nu zilnică. Judecățile AI: le păstrez, dar „orb mai întâi”: omul scrie judecata lui înainte să vadă draftul AI, apoi vede draftul cu citări și poate revizui; altfel ancorarea e sigură. Registrul promisiunilor: îl păstrez, dar restrâns la ce am propus deja în răspunsul anterior: scrisorile anuale și secțiunea de perspective din 10-K, cel mult zece promisiuni pe companie pe an, alese de om dintre cele extrase, ghidarea trimestrială exclusă din scor; semnalele care rămân sunt abandonul tăcit și ținta mutată.

Unde nu sunt de acord: „doar CLI timp de trei luni, fără interfață”. Dosarul de decizie, judecățile atribuite și contrazicerea dintre parteneri au nevoie de un formular și de un link, nu de fișiere; fără ele, partea umană a metodei nu se întâmplă. Compromisul pe care îl recomand: nucleul primul (ingestie, motor, CLI, dosar HTML pe companie, un singur utilizator), dovedit pe 10 companii americane citite integral de tine; interfața web subțire imediat după, pentru dosar și judecăți; roluri, audit, TOTP, i18n și parteneri doar când există dosare care au intrat în decizii reale. BVB: doar ca pilot pe o companie prin ESEF (rezultatul „date insuficiente” e corect și util), importul manual industrializat amânat. Screeningul de univers și alertele push: tăiate; rămâne digestul lunar cu ce s-a schimbat în rapoartele companiilor deja analizate și starea „preț sub prețul pe care l-aș plăti”, fără notificare.

Ce îți cer să decizi: (1) scopul v1 redus: SUA, 10 companii din setul de aur, un utilizator, nucleu plus interfață subțire, UE pilot pe două companii; (2) aplicarea corecțiilor de metodă din audit înainte de orice cod de fază 2: rețeta v2, cerințele secțiunea 5, PRD 4.10 și backlog-ul regenerate dintr-un singur fișier de reguli; (3) criteriile de oprire ale auditorului (secțiunea 5 de mai jos) adoptate ca atare, cu jurnal de ore săptămânal, pentru că riscul cel mai mare nu e tehnic: e ca produsul să răspundă „nu” sau „insuficient” la aproape tot și să fie abandonat în trei luni. Dacă metoda cere inactivitate, instrumentul trebuie să facă inactivitatea confortabilă, nu să fabrice activitate.

## Raportul auditorului adversar

Autor: reviewer independent, fără implicare în construcție. Citite integral: recipe.md, requirements_v0.md, prd_v1.md, architecture.md, qa_strategy.md, ux.md, spike_report.md, plus reconciliation.md, jurnalele de probleme și backlog.csv. Numere în format românesc; referințele folosesc identificatorii din PRD, arhitectură, QA și UX.

### 1. Verdictul scurt

L-aș construi pe jumătate. Nucleul (ingestie din surse primare, normalizare cu jurnal de excepții, motor de formule pur, dosar înghețat) merită și există deja în spike: circa 70% din aritmetică rulează dintr-un CLI. Restul (porți cu verdicte, aplicație web multi-utilizator, judecăți AI, BVB, registru de promisiuni, screening nocturn, Kelly) nu l-aș construi acum.
Pentru cine pică: pentru un utilizator al cărui stil real de investiție diferă de metodă (tranzacții frecvente, derivate, companii listate recent, cărora regula de zece ani le răspunde „date insuficiente" înainte de orice analiză); pentru parteneri (licență de date și încadrare juridică nerezolvate); pentru UE și BVB (sursa ESEF e incompletă, istoricul e muncă manuală).
Cel mai mare motiv pentru care poate fi timp pierdut: produsul mecanizează exact partea pe care rețeta o declară nemecanizabilă (OE normalizat, capexul de întreținere, valoarea intrinsecă, categoria afacerii) și, pe datele reale din spike, dă rezultate pe care metoda le-ar respinge: Coca-Cola, exemplul rețetei, pică Supraviețuirea și „valorează" 8 la 9 USD pe acțiune.
Cel mai mare motiv pentru care poate fi valoros: o bază de fapte pe zece ani cu proveniență, reconciliată la raport, plus un dosar înghețat care te obligă la paragraful de dinainte de cumpărare și face greșelile recitibile: partea din metodă pe care aproape nimeni nu o face, și cea mai ieftină de construit.

### 2. De ce ar putea să nu meargă: modurile de eșec

#### 1. Coca-Cola, exemplul rețetei, pică propriile reguli ale produsului
**Mecanism.** AC-G3-1 fixează OE cu variația capitalului de lucru an de an, fără normalizare; 4.10 ia OE_0 pentru VI_low ca min(ultimul an, media pe 5 ani), deci ancorează valoarea pe anul anormal; AC-G5-3 pune g = 0 la CAGR negativ; AC-SV-4 cu plafonul din 4.10 (datorie netă / OE peste 5) decide „pică"; 4.10 marchează instabilitate la CV OE peste 0,5.
**Dovadă.** Spike, KO: OE FY2025 = 4.101 față de 13.107 fără ΔWC; CAGR OE -6,7%; VI 45.358 la 48.464 milioane USD, adică 7,89 la 8,94 USD pe acțiune ca „preț pe care l-aș plăti"; datorie netă / OE 7,24x (Supraviețuire: pică); CV OE 0,58 (instabilitate). Arhitectura (secțiunea 4, observația b) o semnalează, PRD-ul o lasă în formulă.
**Severitate / probabilitate.** Ridicată / ridicată (s-a întâmplat deja).
**Mitigare.** AC-G3-1: ΔWC normalizat (media pe 3 ani), afișat separat; AC-G5-3: OE_0 devine judecată obligatorie aleasă dintre candidați afișați (ultimul an, media pe 5 ani, media fără ΔWC, minimul), cu motiv; Poarta 5 „necesită judecată" când OE ultimul an diferă cu peste 30% de media pe 5 ani; AC-SV-1: datorie netă pe OE median pe 5 ani.

#### 2. Prețul primul, nu ultimul
**Mecanism.** Rețeta: „price last; most candidates die at gate one". Fluxul F1 (UX) calculează porțile 3, Supraviețuire și 5 automat la sfârșitul ingestiei (pasul 4) și le afișează pe scorecard (W1) și pe lista de companii (W8) înainte ca omul să fi scris un rând la Poarta 2. Primul lucru pe care îl vezi despre o companie nouă e „5 Price under value: fail"; AC-G5-8 recalculează verdictul zilnic, deci prețul e singura cifră care „se mișcă".
**Dovadă.** UX F1, W1, W8; AC-G5-8; rețeta: „Not: check prices as information".
**Severitate / probabilitate.** Ridicată / ridicată.
**Mitigare.** Regulă nouă AC-X-11: Poarta 5 nu se calculează și nu se afișează până când Poarta 2 are textele confirmate și clasificarea „în cerc"; până atunci porțile 3 și Supraviețuire apar ca fapte și calcule, fără verdict; recalcul săptămânal.

#### 3. Falsa precizie: VI cu două zecimale, „prețul pe care l-aș plăti" ca formulă, Kelly și probabilități de „moarte"
**Mecanism.** AC-G5-1 și 4.10 produc VI din trei parametri aleși de noi (r = 10%, g plafonat, g_terminal 2 la 3%); AC-G5-6 derivă „prețul pe care l-aș plăti" ca VI_low × (1 - marja). Valoarea terminală e 45 la 60% din VI; lățimea intervalului reflectă alegerea lui g, nu incertitudinea afacerii. Rezultatul apare cu două zecimale (W3: „52.10 to 61.80 USD"; spike: „68.87 la 78.05 USD"). Aceeași boală în faza 3: SG-087 dimensionează poziția cu Kelly din p și b inventate de utilizator, iar AC-G2-3 cere probabilități de moarte în trepte de 5% (UX F5: o zecimală). Rețeta nu conține Kelly; conține „5 la 10 afaceri, până la 40% când ești aproape sigur (1966)".
**Dovadă.** W3: g_terminal de la 2,5% la 3,0% mută VI cu 6 la 7%; PT-01: r de la 10% la 11% mută VI cu 12,5%; UT-09, PT-17. Rețeta, punctul 5: „no false precision; if not obvious without a spreadsheet, not obvious"; anti-rețeta: „no precision theatre".
**Severitate / probabilitate.** Ridicată / ridicată.
**Mitigare.** AC-G5-1: două cifre semnificative („aproximativ 50 la 60 USD"); AC-G5-3: „valoarea" este grila de sensibilitate r × g (3 × 3), nu un interval; AC-G5-6: „prețul pe care l-aș plăti" devine câmp de judecată completat de om, obligatoriu la înghețare, cu referința mecanică alături; SG-087 și probabilitățile din AC-G2-3 șterse, cele trei moduri de a muri rămân text cu „ce dovadă ar arăta că a început", dimensionarea ca regulă fixă (maxim 10 poziții, plafon 25 la 40%).

#### 4. Pragul de 10% peste tot: obligațiunea e decor, moneda e ignorată
**Mecanism.** AC-G5-2 și 4.10: r = max(10%, randament + 0). Pentru orice monedă cu obligațiunea sub 10%, r este 10% nominal; „randamentul obligațiunii lungi ca prag" din rețetă nu intră niciodată în calcul (spike: „DGS10 este referința, nu rata folosită"). În termeni reali, 10% nominal în lei e un prag mai blând decât 10% în euro dacă inflația în lei e mai mare, deci produsul favorizează sistematic emitenții BVB. Ancora „moneda listării" dă aceleiași companii două praguri (ASML pe Nasdaq și pe Euronext) și nu are sursă pentru DKK (Novo Nordisk), CHF sau GBP: arhitectura listează doar FRED, BCE, BNR.
**Dovadă.** hurdle_input.json; AC-G5-2; QA 3.
**Severitate / probabilitate.** Medie / ridicată.
**Mitigare.** 4.10: tabel de praguri pe monedă, versionat (r = max(obligațiune lungă + 3 puncte, inflație așteptată + 5 puncte)), în antet; ancora devine moneda de raportare; v1 limitat la USD, EUR, RON.

#### 5. Categoriile din 2007 ca clasificator: praguri potrivite pe două anecdote
**Mecanism.** AC-G3-7 transformă trei descrieri narative (See's, FlightSafety, companiile aeriene) în praguri (30%, r + 5, r, capex / vânzări 5%). Pragul de capex / vânzări există doar ca FlightSafety (31%) să nu iasă „excelent" (UT-03): două exemple nu calibrează nimic. Regula a patra din arhitectură (profit în creștere cu capital neschimbat = excelent) etichetează „excelent" și o afacere în dezinvestire (profit sus, capex tăiat sub amortizare): tiparul Kraft Heinz 2015 la 2017. AC-G3-8 cere „necesită judecată" când categoria pe 5 și pe 10 ani diferă, ceea ce se va întâmpla aproape mereu.
**Dovadă.** Spike: Apple „bun" FY2016 la FY2018 (capex / vânzări peste 5%), „excelent" din FY2019; Coca-Cola n/a în 4 din 10 ani; arhitectura clasifică pe 5 ani, PRD-ul pe 10.
**Severitate / probabilitate.** Medie / ridicată.
**Mitigare.** AC-G3-7 devine afișarea a trei fapte pe deceniu, fără etichetă automată: reinvestire cumulată Σ(capex - amortizare + ΔWC) față de Δprofit înainte de impozit (aritmetica See's 2007), mediana capex / vânzări, tendința capitalului; categoria e judecată umană; marcaj „posibilă dezinvestire" la capex / amortizare sub 0,8 trei ani la rând.

#### 6. ROIC tangibil nu există pentru afacerile pe care metoda le caută
**Mecanism.** AC-G3-3 împarte NOPAT la un capital tangibil care, pentru afacerile asset-light, e aproape zero sau negativ; arhitectura refuză împărțirea (corect), dar atunci poarta nu are număr și cade în „necesită judecată" pe o tehnicalitate. Definiția numerarului excedentar diferă între documente (4.10: numerar peste 2% din vânzări; spike: tot numerarul), iar diferența singură mută Apple din „semnalat" într-un ROIC de mii de procente.
**Dovadă.** Spike: Apple semnalat în 5 din 10 ani, restul „> 200% (70x)"; Moody's semnalat în 3 din 10; Coca-Cola FY2025 semnalat; QA 6 numește definiția numerarului excedentar „cea mai probabilă sursă de diferență".
**Severitate / probabilitate.** Medie / ridicată.
**Mitigare.** AC-G3-3: starea „capital tangibil necesar neglijabil" (sub 2% din vânzări) devine fapt pozitiv care îndeplinește partea cantitativă a porții 3, nu marcaj de eroare; în acest regim se afișează sume absolute („82 pe 40"), nu rapoarte; o singură definiție a numerarului excedentar, în assumption_set, cu test.

#### 7. Capex de întreținere = min(capex, amortizare) greșește optimist în ambele direcții
**Mecanism.** AC-G3-2 fixează min(capex, D&A) ca implicit. Pentru o afacere în creștere (ASML, Costco) ia D&A, care subestimează costul de înlocuire sub inflație (rețeta, 1983); pentru o afacere în restrângere (capex sub D&A) ia capexul și botează subinvestirea „întreținere". În ambele cazuri OE e umflat. Rețeta definește capexul de întreținere ca „media anuală necesară menținerii poziției competitive și a volumului": o estimare, nu o linie din raport.
**Dovadă.** Spike, KO FY2025: capex 2.112, D&A 1.050, deci 1.062 milioane de capex intră gratuit în OE; UT-14 testează doar aritmetica.
**Severitate / probabilitate.** Medie / ridicată.
**Mitigare.** AC-G3-2: implicit capexul total (cel mai conservator), cu D&A și Greenwald afișate; alegerea per companie e judecată cu motiv, obligatorie la înghețare; PT-08 rescris.

#### 8. Regula celor zece ani ca poartă dură anulează scopul UE și BVB și pedepsește tehnicalități
**Mecanism.** AC-X-4 și P8: sub 10 exerciții complete, „date insuficiente"; arhitectura (secțiunea 3, `ten_year_rule`) rupe șirul la un singur concept lipsă într-un an. Consecințe: toate cele 10 companii UE și BVB din setul de aur sunt „date insuficiente" până la import manual (PRD 11.2); LVMH are zero exerciții complete deși are 5 ani de venituri, profit și CFO (lipsește doar D&A ca etichetă standard); un exercițiu de tranziție rupe șirul pentru un deceniu; un spin-off cu istoric lung (Kenvue) e tratat ca un start-up. PRD-ul spune „ultimele 10 exerciții complete", arhitectura „consecutive": nici regula nu e aceeași.
**Dovadă.** Spike: LVMH 0, OMV Petrom 3 exerciții complete; QA 3.
**Severitate / probabilitate.** Ridicată / ridicată.
**Mitigare.** AC-X-4: 10 ani rămân ținta, dar 7 la 9 ani dau „necesită judecată (istoric scurt: n din 10)" cu lipsurile listate; un concept neesențial lipsă produce calcul parțial cu marcaj, nu ruperea șirului; exercițiul de tranziție se adună cu cel adiacent ca fapt derivat marcat; PT-10 și UT-13 se actualizează.

#### 9. Verdictele formează un scor compozit deghizat și, în faza 4, un screener cu semnal
**Mecanism.** AC-X-1 interzice scorul, dar AC-G5-6 leagă marja de verdictul porții 4, AC-G3-8 leagă poarta 3 de categorie, AC-X-10 impune precedență, iar W1 numără „2 pass, 2 needs judgment, 1 fail": un arbore de decizie cu praguri fixe e un scor sub alt nume. SG-093 (screening nocturn pe S&P 500, Stoxx 600, BVB) plus AC-G5-9 și SG-089 (alerte la preț sub prețul pe care l-aș plăti) sunt un generator de semnale, indiferent de lint.
**Dovadă.** Rețeta: „Candidates come from reading... and scuttlebutt"; „Mr. Market serves you, does not guide you"; twenty-punch card.
**Severitate / probabilitate.** Medie / ridicată.
**Mitigare.** W1 fără numărătoare; SG-093 tăiat sau redus la fapte de poarta 3 fără preț; SG-089 fără alerte de preț; metrică de succes „cel mult 20 de companii analizate în profunzime pe an".

#### 10. Produsul fabrică muncă de clasificare în locul cititului
**Mecanism.** AC-X-6 și AC-PR-7 blochează porțile până când un om închide problemele „blochează poarta" cu motiv; navigarea pe telefon (UX 2) pune două cozi cu contor în bara principală (Judgments, Issues); UX întrebarea 6 propune reconfirmarea anuală a tuturor judecăților; 4.11 cere confirmarea umană a fiecărei promisiuni extrase din 4 documente pe trimestru pe companie, adică mii de rânduri pe an: fie registru gol, fie ștampilă. Rețeta: „keep the calendar nearly empty; say no to almost everything".
**Dovadă.** Spike: circa 350 de intrări în jurnal pentru 3 companii (AAPL 151, KO 86, MCO 110), 21 de severitate ridicată.
**Severitate / probabilitate.** Ridicată / ridicată.
**Mitigare.** AC-PR-7: blochează doar „ambiguous" cu impact peste 5% pe o cifră din verdict, restul se închid automat ca informative; bara de navigare fără cozi; cel mult 7 câmpuri de judecată pe companie; registrul promisiunilor limitat la 5 promisiuni de alocare a capitalului pe an, alese de om.

#### 11. Normalizarea XBRL validată pe un an din zece; retratările și rupturile de standard tratate ca tendințe
**Mecanism.** Arhitectura 3.7 la 3.9 recunoaște 13 tipuri de excepții în doar 5 companii; companyfacts nu expune etichetele proprii și nici decimals (22 la 39 de etichete proprii pe companie). Rezolvarea cere instanța XBRL a fiecărui 10-K, deci 10 instanțe pe companie; rapoartele dinainte de mijlocul lui 2019 nu sunt inline XBRL, ci au instanța ca exhibit separat, iar metoda de reconciliere din spike (text plus fapt inline din același document) a fost validată doar pe FY2025: 36 din cele 450 de celule ale ferestrei de zece ani pentru cele 3 companii SUA. În plus, AC-PR-6 („ultima depunere câștigă") retratează doar anii din fereastra comparativă a ultimului raport, deci seria amestecă ani recenți retratați cu ani vechi pe baza originală; ASC 606 (2018), ASC 842 și IFRS 16 (2019), IFRS 17 (2023) schimbă definițiile veniturilor, pasivelor curente și datoriei în mijlocul ferestrei; arhitectura exclude leasingul din datorie în v1, deci datoria netă a retailerilor (Inditex, Costco) e subestimată. AC-PR-7 nu are tipul „schimbare de standard".
**Dovadă.** Spike, excepțiile 1, 2, 4, 8; reconciliation.md; Coca-Cola venituri FY2016 41.863 (bază veche) lângă FY2017 36.212 (retratat); QA 3: AXA, IFRS 17.
**Severitate / probabilitate.** Ridicată / ridicată.
**Mitigare.** M2 și M3 (arhitectura 10): ingestie din instanțele depunerilor pentru toți anii, companyfacts doar ca index; reconciliere automată pe fiecare an pentru 6 cifre de bază înainte de DoD; AC-PR-7: tip nou „ruptură de bază", propagat la CAGR, CV și tendințe ca „necesită verificare"; leasingul în datoria netă implicit, varianta fără leasing ca scenariu.

#### 12. ESEF, BVB și financiarele: 13 din 20 de companii din setul de aur nu pot produce verdict la porțile 3 și 5
**Mecanism.** PRD 6 declară filings.xbrl.org adevăr pentru UE, dar spike-ul arată: Germania zero, România oprită la FY2022, LVMH FY2025 și AXA FY2021 lipsă, dubluri OMV Petrom. BVB devine integral import manual (pachete de pe paginile emitenților plus PDF pentru pre-2020), cu dublă introducere (QA 13): 10 companii × 5 la 7 ani × 15 cifre = 750 la 1.050 de celule, de două ori. Din cele 3 companii BVB, una e bancă (n/a), una e IPO 2023 (insuficientă până în 2033), una (OMV Petrom) cere circa 10 ore de introducere. Separat, AC-SV-5 și PT-16 declară OE și ROIC tangibil „formula nu se aplică" pentru bănci și asigurători (WFC, BRK.B, AXA, Banca Transilvania), deși metoda a făcut cei mai mulți bani în financiare. Cu Kenvue (5 ani), 13 din 20 de companii nu au verdict la porțile 3 și 5.
**Dovadă.** Arhitectura 3 (ESEF 5 și 6), 9; QA 3.
**Severitate / probabilitate.** Ridicată / ridicată.
**Mitigare.** PRD 3.1: v1 doar SUA, plus 2 companii UE ca pilot (Novo Nordisk cu ESEF și 20-F, LVMH cu import); BVB în faza 3, după ce există o sursă programatică; pachetele ESEF de pe paginile emitenților ca sursă primară; financiarele scoase din DoD v1, cu un modul propriu (ROTCE, marjă de dobândă, credite / depozite, stres 1990) în faza 3 sau renunțare explicită.

#### 13. Poarta 5 nu a rulat niciodată pe date reale: prețul lipsește
**Mecanism.** Spike-ul nu a avut nicio sursă de preț, deci DCF invers, marja de siguranță, testul dolarului și starea „preț sub prețul pe care l-aș plăti" sunt netestate pe realitate. ADR-11 estimează 20 la 60 EUR cu „listă de prețuri de verificat la contractare"; licența „de uz personal, fără redistribuire" (PRD 5.5) e incompatibilă cu afișarea către parteneri (PRD 9, întrebarea 6). Testul dolarului (SG-075) depinde integral de capitalizări: cu multipli în creștere trece orice companie, cu multipli în scădere pică orice.
**Dovadă.** Arhitectura 8; spike: toate metricile cu preț `not_computed`; UT-05.
**Severitate / probabilitate.** Ridicată / medie.
**Mitigare.** Contractarea vendorului și un al doilea spike de prețuri (acțiuni față de pagina de copertă, curs, split-uri) înainte de orice story din SG-044; confirmare scrisă a vendorului pentru afișare multi-utilizator; testul dolarului pe toate ferestrele de 5 ani din deceniu, plus varianta fără preț (ΔOE / profit reținut).

#### 14. Citările verificate dovedesc că citatul există, nu că judecata rezultă din el; omul se ancorează pe draft
**Mecanism.** AC-X-3 și ADR-8 verifică prin potrivire de subșir; QA 8 recunoaște că întrebarea reală e relevanța și o măsoară pe un eșantion de 10% judecat de QA, adică de același model. Exemplul W5 e simptomatic: moat-ul e „dovedit" cu o frază din Item 1 al 10-K-ului („Our brands... more than 200 countries"), autodescrierea companiei; orice 10-K afirmă că are brand-uri puternice. Recall-ul (ce nu a găsit AI-ul: nota despre litigiul fiscal) nu se măsoară. W5 citează și o valoare calculată de motor ca „verified", deși ADR-8 spune că modelul nu primește cifre din motor. Apoi P3 echivalează judecata „propusă de AI și confirmată de om" cu judecata umană în regula porții; F3 oferă Confirm cu o atingere, iar a scrie propria judecată costă o jumătate de oră; după confirmare, originea AI dispare. Rețeta, mindset 5: autoritatea, dovada socială și angajamentul sunt cauze standard de misjudecată; un draft bine scris, cu citări verificate, le declanșează pe toate trei.
**Dovadă.** UX W5, F3; QA 8; ADR-8; tabelul `judgment`.
**Severitate / probabilitate.** Ridicată / ridicată (din faza 3).
**Mitigare.** ADR-8: AI-ul extrage, nu concluzionează: citate despre preț, volume, concurenți, riscuri, etichetate „ce spune compania"; câmpurile de concluzie (tip de moat, direcție, durabilitate) nu se precompletează niciodată; F3: protocol „întâi orb", draftul se dezvăluie doar după ce omul a salvat propria versiune; originea „din draft AI" rămâne vizibilă permanent în dosar și export; eșantionul de relevanță judecat de un partener; test de recall cu fapte plantate; metrică: proporția judecăților confirmate fără editare (peste 70% = ștampilă).

#### 15. Documentele fazei 1 deja diverg între ele
**Mecanism.** Patru agenți au produs patru adevăruri: VI_low cu g = 0 (PRD 4.10) față de g = min(0,5 CAGR, 5%) (arhitectura, assumption_set); plafon g_high 8% (PRD) față de 10% (arhitectura); categoria pe ROIC incremental la 10 ani (AC-G3-7) față de 5 ani (arhitectura 4); draft-uri AI în faza 3 (PRD 3.2) față de M8 în v1 (arhitectura 10); roluri owner / partner (AC-AU-2) față de admin / analyst (ADR-7); precedența „insuficiente, pică, judecată, trece" (AC-X-10) față de „insuficiente, judecată, pică / trece" (UX 1); probabilități în trepte de 5% (AC-G2-3) față de o zecimală (UX F5); verdictul porții 2 derivat (AC-G2-5) față de ales explicit (UX F5). În cod, fiecare devine un bug cu test verde.
**Dovadă.** Secțiunile citate.
**Severitate / probabilitate.** Medie / ridicată.
**Mitigare.** Un singur fișier `rules.yaml` versionat (ipoteze, praguri, precedență, id-uri de formule, roluri) din care PRD, arhitectura, UX și QA citează versiunea; test în CI care compară documentele cu fișierul; trecere de consistență a PM-ului la fiecare milestone.

#### 16. QA „independent" nu e independent; testele validează aritmetica, iar proveniența creează încredere falsă
**Mecanism.** QA și Dev sunt același model cu aceeași rețetă în context: au ales „independent" aceeași convenție de DCF, același min(capex, D&A), aceleași praguri. UT-01 la UT-25 verifică 82 / 40 = 2,05; DoD-ul „QA recalculează independent și obține aceleași rezultate" înseamnă acord cu tine însuți de două ori. W2 afișează „known-result test: See's 2007: pass" ca insignă lângă ROIC: crește încrederea exact unde riscul e în intrări. P1 garantează că cifra e în raport, nu că e cifra potrivită: Apple D&A FY2015 9.200 (note) și 11.257 (flux de numerar) au amândouă proveniență impecabilă și doar una e corectă pentru OE.
**Dovadă.** QA 1, 4; UX W2, W4; spike, excepția 1.
**Severitate / probabilitate.** Medie / ridicată.
**Mitigare.** Al doilea cititor uman (un partener) pentru 3 companii; insigna de test scoasă din interfață; teste de concept, nu doar de aritmetică („OE ultimul an sub 50% din media pe 5 ani fără marcaj = eșec"); W4 arată implicit faptele candidate concurente pentru același concept și perioadă; exercițiu lunar: QA plantează o mapare greșită și măsoară în câte zile o prinde un om.

#### 17. Scop de SaaS pentru 2 la 5 utilizatori, cu un singur întreținător și cu un cost în ore de om nescris nicăieri
**Mecanism.** v1 are 65 de story-uri, 77 din 96 „Highest" (backlog.csv): nu există prioritizare. ADR-6: șase containere pe un Mac Mini care rulează și n8n, apoi VPS; multi-utilizator, roluri, audit, TOTP, i18n, scenarii, export, copii la B2, 10 milestone-uri cu review al owner-ului, care are un rol executiv cu normă întreagă. Costul agenților care construiesc nu apare în niciun buget (ADR-11 numără doar datele). Pe o companie SUA, 6 la 13 ore de om (probleme blocante, textele porții 2, formularul porții 4 cu dovezi sursate, reconcilierea completă cerută de QA 5); UE și BVB adaugă 3 la 6 ore de introducere, de două ori. DoD-ul costă 150 la 250 de ore de om. Spike-ul face deja 70% din motor într-un CLI.
**Dovadă.** PRD 7; arhitectura 1, 7, 10; backlog.csv; QA 5, 6, 13.
**Severitate / probabilitate.** Ridicată / ridicată.
**Mitigare.** v1 = CLI (arhitectura 7 îl descrie deja) + CSV + un dosar HTML static pe companie, un singur utilizator, 10 companii SUA; web, multi-utilizator și n8n doar după 3 luni de folosire reală; PRD 8: metrică „ore de om pe companie până la înghețare", țintă sub 4 ore; reconciliere completă doar pe 5 companii, restul pe eșantion.

#### 18. Setul de aur are hindsight: câștigătorii de azi calibrează pragurile de mâine
**Mecanism.** 4.10 și AC-G3-7 spun „praguri de validat pe setul de aur", iar setul conține companii alese pentru că azi sunt recunoscute ca excelente (KO, AAPL, MCO, COST, ASML, LVMH) sau groaznice (AAL, AF). A regla pragurile ca ele să iasă în categoria știută e curve-fitting cu răspunsul în mână; nu spune nimic despre ce ar fi arătat porțile în 2015. Setul nu conține niciun „impostor" (rețeta, 1996), iar „ultima depunere câștigă" retratează datele istorice, deci o rulare punct-în-timp nu e posibilă implicit.
**Dovadă.** QA 3, matricea cazurilor; PRD 4.10.
**Severitate / probabilitate.** Medie / ridicată.
**Mitigare.** QA 3: 5 impostori (companii care arătau excelent în 2015 și au dezamăgit; candidați: GE, Intel, Boeing, Walgreens, Bayer) și o rulare punct-în-timp cu depunerile disponibile la 31 decembrie 2015, comparată cu ce s-a întâmplat; pragurile se validează pe această rulare, nu pe cea de azi.

#### 19. Abandon în câteva luni: produsul răspunde „nu" sau „insuficient" la aproape tot ce urmărește owner-ul
**Mecanism.** La r = 10% și g plafonat, toate companiile de calitate din spike pică poarta 5 cu 2 la 4x (Apple „prețul pe care l-aș plăti" 69 la 78 USD, Moody's 138 la 156, Coca-Cola 8 la 9): corect în logica rețetei, dar un instrument care spune „nu" la tot nu mai e deschis a doua lună. Dacă stilul real de investiție al utilizatorului (tranzacții frecvente, derivate, companii listate recent) e în afara metodei, conflictul apare din prima lună: regula de zece ani le răspunde „date insuficiente" înainte de orice, iar anti-rețeta exclude derivatele și industriile în schimbare rapidă. Cadența produsului (verdict zilnic, cozi de confirmări) contrazice cadența rețetei (citit, inactivitate).
**Dovadă.** Spike, secțiunile Poarta 5; AC-X-4; AC-G5-8; rețeta, cadența și anti-rețeta.
**Severitate / probabilitate.** Ridicată / ridicată.
**Mitigare.** Înainte de orice story din faza 2: rulează CLI-ul spike-ului pe 10 companii pe care le deții sau le urmărești și notează dacă vreun rezultat îți schimbă o decizie; decide explicit scopul: „disciplinează-mă" (produsul intră obligatoriu înaintea fiecărei tranzacții, iar regula de zece ani e tocmai punctul) sau „analizează ce analizez deja" (metoda nu e compatibilă, produsul nu trebuie construit).

#### 20. Încadrarea juridică și licențele nu sunt rezolvate de lint-ul de cuvinte
**Mecanism.** AC-X-9 și LN-01 interzic „buy / sell", dar AC-G5-9 afișează tuturor utilizatorilor (AC-AU-2: același spațiu de lucru) „preț sub prețul pe care l-aș plăti: da", cu alerte în faza 3: în substanță o recomandare, indiferent de vocabular. Între parteneri nu există acord scris, declinare de răspundere, regulă despre bani comuni sau remunerație; requirements 6 lasă deschis „comercialul se poate adăuga mai târziu", ceea ce ar muta produsul în zona cercetării de investiții distribuite (MAR) și a consultanței (MiFID II; în România, autorizare ASF). Licența de prețuri „uz personal, fără redistribuire" nu acoperă afișarea către terți. Nu sunt avocat: riscul e de calificare și crește cu fiecare partener.
**Dovadă.** PRD 3.2, 5.5, 9 (întrebarea 6); AC-G5-9; SG-089.
**Severitate / probabilitate.** Medie / medie.
**Mitigare.** Înainte de prima invitație: acord scris între parteneri (fără remunerație, fără bani comuni, fiecare decide singur, declinare de răspundere la autentificare), opinia unui avocat pe MiFID II / MAR, confirmarea scrisă a vendorului; „prețul pe care l-aș plăti" devine câmp per utilizator, vizibil ca „judecata lui X", nu stare a companiei; comercialul scos din documente.

#### 21. Securitate: un Mac Mini de acasă cu n8n și cheile tuturor serviciilor pe aceeași mașină
**Mecanism.** ADR-6 pune pe același Mac Mini baza, API-ul, workerul, proxy-ul și n8n (care deține deja credențiale către alte sisteme); PRD 5.4 spune „TLS prin reverse proxy", ADR-7 spune Tailscale fără port forwarding: două planuri. Partenerii pe telefon vor cere acces fără Tailscale și presiunea de a expune 443 crește; parolă plus TOTP opțional (AC-AU-3, Should); cookie de 30 de zile; cheia rclone crypt pe aceeași mașină ca datele. Pentru cineva din securitate cibernetică, un incident pe propriul instrument e și reputațional.
**Dovadă.** ADR-6, ADR-7; PRD 5.4, AC-AU-1, AC-AU-3.
**Severitate / probabilitate.** Medie / medie.
**Mitigare.** ADR-7: v1 exclusiv prin Tailscale (niciun port public pe Mac Mini); rețea Docker și secrete separate de n8n; TOTP obligatoriu sau passkeys; cheia de backup în afara mașinii; scanare de dependențe în CI; un test de penetrare înainte de prima invitație.

### 3. Unde e o idee proastă (dacă e cazul)

1. **Kelly fracționat și probabilitățile de „moarte" (SG-087, AC-G2-3): de tăiat.** Cifră precisă din intrări inventate. Alternativa: regula fixă din rețetă (5 la 10 poziții, plafon 25 la 40% la „aproape sigur") și întrebarea „pot ține prin o scădere de 50%", ca judecată da / nu.
2. **Registrul promisiunilor (4.11, SG-096): de redus la a zecea parte sau de tăiat.** Extrage mii de promisiuni pe an, măsoară managementul după ghidarea trimestrială (cultura pe care rețeta o respinge) și cere confirmare umană pe fiecare rând. Alternativa: cel mult 5 promisiuni de alocare a capitalului pe companie pe an, alese de om.
3. **Screening nocturn de univers și alertele de preț (SG-093, SG-089, AC-G5-9): de tăiat.** Un screener pe porți binare cu prag de preț e un generator de semnale; rețeta spune că ideile vin din citit. Alternativa: digest lunar cu ce s-a schimbat în rapoartele companiilor deja analizate, fără preț de piață.
4. **BVB și importul manual industrializat în v1 (SG-013 pentru 10 companii, dublă introducere): de amânat.** Sursa programatică nu există, costul e de sute de ore, rezultatul e un verdict pentru o singură companie. Alternativa: v1 doar SUA plus 2 piloți UE; BVB după ce există un OAM accesibil programatic.
5. **Aplicația web multi-utilizator pe Mac Mini ca v1 (SG-060 la SG-066, ADR-6): de redesenat.** Șase containere, roluri, audit, i18n și TOTP pentru 2 la 5 utilizatori și 20 de companii, întreținute de o singură persoană. Alternativa: CLI-ul din arhitectura 7, fixture-uri CSV și un dosar HTML static pe companie, un singur utilizator timp de 3 luni; interfața și partenerii vin dacă dosarele intră în decizii reale.

### 4. Ce ar spune Buffett și Munger despre acest tool

Pe partea de fapte, ar aproba: rețeta cere zece ani de rapoarte, câștigurile proprietarului (1986), randamentul pe capital tangibil în locul EPS-ului (1977, 2017), testul dolarului (1983), paragraful de dinainte de cumpărare și jurnalul de greșeli (punctul 6; 1989, 2024), re-estimarea anuală (2014). Un dosar înghețat care îți arată peste trei ani exact ce credeai și de ce este literal „review mistakes then fix fast".

Pe partea de calcul, ar fi sceptici cu trei formulări din propria rețetă. Punctul 5: „no false precision; approximately right beats precisely wrong (1993); if not obvious without a spreadsheet, not obvious". Un interval de VI cu două zecimale, din r = 10%, g plafonat și g_terminal 2 la 3%, e exact spreadsheet-ul fără de care lucrurile ar trebui să fie evidente. Anti-rețeta: „No precision theatre (beta, CAPM, degree-of-difficulty points)"; probabilitățile de moarte și Kelly sunt degree-of-difficulty points cu alt nume. Și 1986: capexul de întreținere e „media anuală necesară menținerii poziției competitive", o estimare a omului care cunoaște afacerea, nu min(capex, D&A).

Pe partea de judecată, Munger ar aplica lista cauzelor de misjudecată (mindset 5) chiar produsului: un draft AI cu citări verificate activează autoritatea, dovada socială și angajamentul; „right because facts and reasoning are right, not because others agree" (mindset 10) se aplică și când „ceilalți" e un model.

Pe cadență, ar observa că produsul e construit în jurul a două cozi cu contor și al unui verdict de preț recalculat zilnic, iar rețeta spune: citit patru la șase ore pe zi, calendar aproape gol, „own like a farm with no daily quote" (2013), o decizie cu adevărat bună la cinci ani (2022). Un instrument folosit de douăzeci de ori într-un deceniu nu are nevoie de aplicație pe telefon; are nevoie să fie corect de douăzeci de ori.

### 5. Criterii de oprire și de succes

Criterii de oprire (oricare înseamnă oprirea investiției de timp sau reducerea la CLI):
1. După 90 de zile de folosire: sub 5 companii cu textele porții 2 scrise de tine, din rapoarte citite integral.
2. Trei luni la rând în care orele pe probleme de date, confirmări și întreținere depășesc orele de citit rapoarte (jurnal de ore săptămânal).
3. La finalul M4 (arhitectura 10): cele 10 companii SUA nu sunt reconciliate pe toți cei 10 ani în sub 20 de ore din timpul tău; atunci UE și BVB se taie.
4. Douăsprezece luni fără nicio decizie de investiție (cumpărare, abținere sau ieșire) precedată de un dosar înghețat: produsul nu e în buclă.
5. Mai mult de două dintre contradicțiile din modul de eșec 15 reapar ca bug-uri în M4 la M6: dezvoltarea cu agenți se oprește până la review uman al codului.
6. Întreținerea cere peste 8 ore pe lună două luni la rând, sau peste 70% din judecățile AI sunt confirmate fără nicio editare (din faza 3).

Criterii de succes (la 12 luni de la prima înghețare):
1. Cel puțin 10 dosare înghețate pentru companii citite integral, cu paragraful cu patru câmpuri scris de tine, fiecare sub 4 ore de muncă în produs.
2. Cel puțin o decizie documentată schimbată de o poartă („aș fi cumpărat X; poarta Y a spus nu; iată ce s-a întâmplat"), în jurnalul de greșeli.
3. Zero diferențe neexplicate pe cele 10 companii SUA, pe toți cei 10 ani, confirmate de un al doilea cititor uman pe 3 dintre ele.
4. Cel puțin doi parteneri au scris o judecată proprie care contrazice una de-a ta (sarcina 4 din PRD 2.2).
5. Numărul tranzacțiilor tale din anul următor e mai mic decât în anul precedent (din extrasele brokerului): rețeta măsoară inactivitatea.
6. O mapare greșită plantată de QA e prinsă de un om în sub o săptămână, iar scrisoarea anuală către tine însuți e scrisă din diff-ul dosarelor, nu din memorie.

### 6. Cele 10 modificări pe care le-aș face imediat

1. OE normalizat (ΔWC pe 3 ani, afișat separat) și OE_0 ca judecată aleasă dintre candidați, în AC-G3-1, AC-G5-3 și 4.10: Coca-Cola la 45 de miliarde dovedește că formula e greșită.
2. Poarta 5 ascunsă până la confirmarea porții 2 și recalculată săptămânal, regulă nouă AC-X-11 și AC-G5-8 modificat: rețeta spune „price last", fluxul F1 spune „price first".
3. VI cu două cifre semnificative, grilă de sensibilitate r × g în locul intervalului, „prețul pe care l-aș plăti" ca judecată umană, în AC-G5-1, AC-G5-3, AC-G5-6 și W3: fără zecimale din trei parametri inventați.
4. Praguri pe monedă cu podea reală și ancoră pe moneda de raportare, în AC-G5-2 și 4.10: 10% nominal peste tot favorizează leii și face obligațiunea decor.
5. Poarta 3 cu „capital necesar neglijabil" ca stare pozitivă, randament incremental cumulat pe deceniu și categoria ca judecată, în AC-G3-3, AC-G3-7, AC-G3-8: pentru Apple și Moody's produsul nu are azi un număr.
6. Capex de întreținere implicit = capex total, cu alegerea per companie ca judecată, în AC-G3-2 și PT-08: min(capex, D&A) e optimist în ambele direcții.
7. Regula de zece ani cu „necesită judecată (istoric scurt)" la 7 la 9 ani, fără ruperea șirului la concepte neesențiale, în AC-X-4, `ten_year_rule` și PT-10: altfel UE și BVB nu au verdict.
8. Scop v1 = SUA, CLI plus dosar HTML, un singur utilizator, 10 companii; UE pilot pe 2 companii; BVB, multi-utilizator și web după 3 luni de folosire, în PRD 3.1, SG-013, SG-060 la SG-066: 65 de story-uri „Must" pentru 2 la 5 utilizatori nu e prioritizare.
9. Tăiate: Kelly, probabilitățile de moarte, registrul promisiunilor în forma actuală, screeningul nocturn și alertele de preț (SG-087, AC-G2-3, 4.11 / SG-096, SG-093, SG-089): teatru de precizie și generator de semnale.
10. Înainte de prima invitație a unui partener: acord scris, opinie juridică pe MiFID II / MAR, confirmarea licenței vendorului, Tailscale exclusiv și un test de penetrare, în PRD 9 (întrebarea 6), 5.5, ADR-6, ADR-7; plus un singur `rules.yaml` cu test în CI care închide contradicțiile din modul de eșec 15.
