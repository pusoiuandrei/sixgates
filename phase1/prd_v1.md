# SixGates: PRD v1 (31 octombrie 2026)

Codename SixGates (numele românesc: de decis). Documente în română; interfața în engleză, cu română disponibilă. Metoda vine din recipe.md; anii din paranteze sunt anii scrisorilor Berkshire. P1-P10 sunt principiile de acuratețe din requirements_v0, secțiunea 2. Fazele urmează requirements_v0, secțiunea 7: 1 fundație (în curs), 2 versiunea 1, 3 proprietar, 4 univers. Etichetele „Faza 1/2/3" din harta funcționalităților (secțiunea 3 a descoperirii) înseamnă fazele 2/3/4 de aici.

## 1. Rezumat

SixGates ia orice companie listată din SUA sau UE (ESEF, inclusiv BVB) și o rulează prin porțile derivate din metoda Buffett-Munger: fiecare cifră trasabilă până la raportul din care vine, fiecare formulă vizibilă în pagină, faptele separate de calcule și de judecăți, fără limbaj de recomandare. Este pentru product owner (APT) și câțiva parteneri care fac singuri munca de citit și vor partea mecanică exactă, reproductibilă și rapidă. v1 (faza 2) livrează Poarta 2 (înțelegi afacerea), Poarta 3 (randamente pe capital), Supraviețuirea, Poarta 4 (moat, doar dovezi și judecată umană) și Poarta 5 (preț sub valoare), cu proveniență completă, jurnal de probleme de date, dosar de decizie minim (analiză înghețată și versionată, plus paragraful de decizie), export CSV și autentificare multi-utilizator simplă, în Docker Compose pe Mac Mini. Verdictele sunt exact patru: trece, pică, necesită judecată, date insuficiente; nu există scor compozit. Definiția lui „gata" pentru v1: cele 20 de companii din setul de aur (10 SUA, 7 UE, 3 BVB) sunt analizate pe toate porțile v1 cu fiecare cifră reconciliată la raport; QA recalculează independent din rapoartele brute și obține aceleași rezultate; o persoană nouă înțelege un verdict fără explicații; niciun număr fără proveniență în interfață; re-execuția unei analize înghețate dă rezultate identice.

## 2. Utilizatori și sarcini

### 2.1 Utilizatori

| Utilizator | Cine | Rol în aplicație |
|---|---|---|
| Product owner (APT) | Investitor individual; citește rapoartele el însuși și decide singur | owner: parametri globali, invitații, acceptarea excepțiilor |
| Parteneri (2-4) | Co-investitori sau parteneri de discuție; contestă judecățile | partner: analize, judecăți proprii, scenarii |
| Al doilea cititor (QA) | Recalculează independent din rapoartele brute | partner, cu export și panoul „explică" |

### 2.2 Sarcini (jobs to be done), ca rezultate

1. Când deschid un raport anual, am în câteva minute cei 10 ani de OE, ROIC tangibil și datorie reconciliați la raport, ca să petrec timpul pe citit și gândit, nu pe copiat cifre.
2. Când cred că înțeleg o afacere, sunt obligat să scriu cum arată peste 10 ani și cum poate muri, ca să aflu dacă e „prea greu" înainte să mă uit la preț.
3. Când stabilesc cât aș plăti, am un interval conservator de valoare și prețul rezultat din marja cerută, cu fiecare ipoteză la vedere, ca să aștept prețul fără precizie falsă.
4. Când discut cu partenerii, faptele, calculele și judecățile sunt separate și atribuite, ca să ne contrazicem pe judecăți, nu pe cifre.
5. Când reiau o companie după un an, găsesc analiza înghețată de atunci, ca să verific dacă faptele mai țin (v1: înghețarea; diff-ul anual în faza 3).
6. Când o cifră lipsește sau sursele diferă, văd asta explicit, ca să nu construiesc o teză pe o estimare ascunsă.

### 2.3 Cum se face azi și unde eșuează

Foi de calcul pe companie, cifre copiate manual din 10-K și rapoarte anuale (ore pe companie); definiții care variază de la o foaie la alta (OE, capex de întreținere, ROIC); fără proveniență (din ce depunere, restatată sau nu); formule ascunse în celule și rupte la copiere; teze suprascrise fără versiuni, deci greșelile nu pot fi revizuite (1989, 2024); vendori care livrează EBITDA și „profit ajustat" fără avertisment (anti-rețetă); istoric european și BVB împrăștiat în PDF-uri, ESEF cu doar 4-5 ani. Rezultat: serii de 10 ani rar complete, erori nedetectate, judecăți amestecate cu cifre, nimic reproductibil.

## 3. Scope v1 și ce nu intră

### 3.1 În v1 (faza 2)

Piețe: SUA (EDGAR) și UE prin ESEF, inclusiv BVB; univers la cerere (compania se adaugă după ticker, ISIN, CIK sau LEI). Module: Poarta 2, Poarta 3, Supraviețuire, Poarta 4 (dovezi, judecată umană), Poarta 5; proveniență pe fiecare cifră și jurnal de probleme de date; dosar de decizie minim; export CSV; autentificare multi-utilizator simplă; interfață EN cu RO; Docker Compose pe Mac Mini; import manual validat pentru istoricul pre-ESEF al celor 10 companii UE și BVB din setul de aur (secțiunea 11).

### 3.2 Nu intră în v1 (non-goals explicite)

- Niciun scor compozit, rating, stele sau clasament de companii (1993: aproximativ corect bate precis greșit; anti-rețetă: fără teatru de precizie).
- Niciun semnal de tranzacționare: termenii interziși în produs și în documente sunt „cumpără", „vinde", „buy", „sell", ca termeni întregi, iar această propoziție este singurul loc în care apar (P10: limbaj de fapte, nu de recomandări).
- Nicio prognoză de piață, macro, timing, analiză tehnică, beta sau CAPM (1994, 2014; anti-rețetă).
- Fără portofoliu (Poarta 1), fără Poarta 6 (re-subscriere anuală cu diff, condiții de ieșire, calculator de schimbare cu impozit, jurnal de greșeli), fără modulul Management: faza 3.
- Fără judecăți propuse de AI (draft de moat, extrase din proxy): faza 3; regula lor este fixată de acum (AC-X-3).
- Fără alerte și digest prin n8n, fără memoriu PDF: faza 3.
- Fără screening de univers și fără import istoric asistat la scară: faza 4.
- Fără facturare, fără aplicație nativă (doar web responsiv), fără model AI local.

## 4. Cerințe funcționale pe porți

Fiecare modul are scop, user stories și criterii de acceptare (AC) în forma Dat fiind / Când / Atunci, etichetate cu principiul și cu sursa din metodă. Pragurile numerice sunt parametri globali impliciți (4.10), propuși de PM și de validat pe setul de aur; nu sunt reguli din scrisori decât unde este indicat anul. Vocabularul verdictelor este fix: trece, pică, necesită judecată, date insuficiente (chei în cod: PASS, FAIL, NEEDS_JUDGMENT, INSUFFICIENT_DATA; interfața EN: passes, fails, needs judgment, insufficient data).

### 4.0 Reguli transversale (AC-X)

- **AC-X-1** (P10, P3; 1993): Dat fiind orice poartă / Când se afișează verdictul / Atunci este exact una din cele patru valori; nu există verdict agregat pe companie, scor numeric sau stele.
- **AC-X-2** (P3): Dat fiind o valoare afișată / Când se randează / Atunci este marcată, vizual și în API, ca fapt, calcul sau judecată; o judecată nu are niciodată aspectul unui fapt.
- **AC-X-3** (P3; decizie 31 octombrie 2026): Dat fiind o judecată generată prin Claude API / Când se salvează / Atunci poartă originea „propus de AI" și cel puțin o citare verbatim (document, identificator de depunere, pagină sau secțiune, textul exact), verificată automat ca existentă în textul documentului, altfel draftul este respins; Când un om o confirmă / Atunci devine „confirmat de <utilizator>", cu data; până la confirmare poarta nu poate fi „trece" și rămâne „necesită judecată". Prima judecată AI se livrează în faza 3; modelul de date o suportă din v1.
- **AC-X-4** (P8; cadența: zece ani de rapoarte; 1979): Dat fiind sub 10 exerciții fiscale complete pentru un concept cerut de o poartă / Când se calculează poarta / Atunci verdictul este „date insuficiente", seria arată „N/10 ani", anii disponibili rămân vizibili ca informație, iar lipsa este în jurnalul de probleme; fereastra este formată din ultimele 10 exerciții complete; un exercițiu de tranziție nu se anualizează, se marchează.
- **AC-X-5** (P4): Dat fiind un concept lipsă într-un an, fără etichetă standard și fără mapare validată / Când se calculează / Atunci celula arată „lipsă", calculele dependente arată „necesită verificare", nu se interpolează, nu se completează din vendor, iar jurnalul primește o intrare.
- **AC-X-6** (P7, P9): Dat fiind un fapt primar și valoarea vendorului de verificare / Când diferă peste toleranța de rotunjire / Atunci se afișează valoarea primară cu marcajul „divergență", ambele valori și sursele în panoul de proveniență, plus intrare în jurnal; la divergență materială (4.10), poarta care folosește faptul este „date insuficiente" până când un utilizator închide intrarea cu motiv; valoarea vendorului nu intră în nicio formulă.
- **AC-X-7** (P2): Dat fiind orice formulă / Când se livrează / Atunci are identificator, versiune, test automat cu rezultat cunoscut (See's 1972/2007 și FlightSafety: 2007; aritmetica impozitului: 1989; Wells Fargo: 1990) și este afișată în pagină cu intrările ei.
- **AC-X-8** (P5): Dat fiind un parametru fix (prag r, marje, praguri de categorie, scenariu de stres) / Când un utilizator îl modifică / Atunci rezultatul se salvează ca „scenariu", cu autor și dată, fără să înlocuiască „valoarea"; parametrii globali se schimbă doar de owner, versionat, cu efect pe analizele noi.
- **AC-X-9** (P10): Dat fiind textele interfeței în EN și RO / Când rulează lint-ul din CI / Atunci nu conțin termenii din 3.2, cu excepția paginii care explică regula.
- **AC-X-10** (P3, P4, P8; propus de PM): Dat fiind o poartă evaluată / Când mai multe verdicte s-ar aplica / Atunci precedența este: date insuficiente (regula de 10 ani, concept lipsă necesar, divergență materială deschisă, import în validare), apoi pică (eșec pe calcule sau judecată umană de respingere), apoi necesită judecată (judecată lipsă, draft AI neconfirmat, dovezi în dezacord cu judecata, zonă gri), apoi trece.

### 4.1 Poarta 2: înțelegi afacerea

Scop: a răspunde „pot spune cum arată afacerea peste zece ani?" cu indicii din cifre și judecată scrisă obligatorie (1992, Florida 1998).

User stories:
- Ca investitor, vreau stabilitatea pe 10 ani a veniturilor, marjelor și OE, ca să am un indiciu obiectiv dacă afacerea e supusă schimbării constante (1992).
- Ca investitor, vreau să fiu obligat să scriu descrierea pe 10 ani, trei moduri de a muri și paragraful de motivare, și să clasific compania în „în cerc", „prea greu", „în afară", ca să nu sar peste gândit (1996).

Criterii de acceptare:
- **AC-G2-1** (P2, P8; 1992, 1996, 2007): Dat fiind 10 exerciții fiscale / Când se deschide poarta / Atunci se afișează CAGR venituri pe 10 ani, abaterea maximă a veniturilor față de trendul liniar, marja operațională minimă și maximă, coeficientul de variație al OE și numărul anilor cu pierdere, fiecare cu formula și faptele de intrare.
- **AC-G2-2** (P5; 1992, 1979): Dat fiind indicatorii / Când unul depășește pragul de instabilitate din 4.10 / Atunci apare „indiciu de instabilitate", cu valoarea și pragul; indiciul nu decide singur verdictul.
- **AC-G2-3** (P3; 1992, Florida 1998, Munger 2007, 1993): Dat fiind formularul / Când lipsește descrierea pe 10 ani, oricare dintre cele trei moduri de a muri (cu probabilitate în trepte de 5%, marcată „estimare personală") sau paragraful de motivare / Atunci verdictul este „necesită judecată" și câmpurile lipsă sunt listate.
- **AC-G2-4** (P3; 1996): Dat fiind formularul complet / Când utilizatorul alege „prea greu" sau „în afară" / Atunci verdictul este „pică", cu motivul afișat ca judecată, cu autor.
- **AC-G2-5** (P3, P8; 1992, Florida 1998): Dat fiind formularul complet, alegerea „în cerc" și 10 ani de date / Când nu există indiciu de instabilitate, sau există și utilizatorul l-a bifat ca tratat în paragraf / Atunci verdictul este „trece"; altfel „necesită judecată". Orice text păstrează istoricul cu autor și dată (P6).

### 4.2 Poarta 3: randamente pe capital

Scop: a măsura dacă afacerea câștigă randamente mari pe capital tangibil puțin, pe un record de 10 ani (1977, 2007, 2017).

User stories:
- Ca investitor, vreau câștigurile proprietarului după definiția din 1986, cu capexul de întreținere vizibil, ca să nu mă bazez pe EPS sau EBITDA.
- Ca investitor, vreau ROIC tangibil pe 10 ani și ROIC incremental pe 5 și 10 ani, ca să văd ce câștigă capitalul nou, nu doar cel vechi (2007).
- Ca investitor, vreau categoria excelent / bun / groaznic cu praguri explicite și identitatea creșterii, ca să compar cu See's și FlightSafety și să deosebesc creșterea din reinvestire de cea din achiziții (2007, 1992, 2000).

Criterii de acceptare:
- **AC-G3-1** (P2; 1986): Dat fiind faptele anuale / Când se calculează OE / Atunci OE = profit net + deprecieri și amortizări + alte cheltuieli fără numerar - capex de întreținere - creșterea capitalului de lucru, pe fiecare din cei 10 ani, fiecare intrare legată de un fact id; EBITDA și „profit ajustat" nu apar nicăieri ca intrare (anti-rețetă).
- **AC-G3-2** (P4, P5; 1986): Dat fiind capexul total și amortizarea / Când se calculează capexul de întreținere / Atunci se afișează ambele metode (implicit min(capex, amortizare); alternativ Greenwald) cu rezultatele lor, metoda folosită este marcată, iar schimbarea ei este scenariu.
- **AC-G3-3** (P2, P4; 1977, 1983, 2017): Dat fiind NOPAT = profit operațional × (1 - rata efectivă de impozit) și capitalul investit tangibil (capital de lucru net + imobilizări nete + alte active operaționale - numerar excedentar) / Când se calculează ROIC / Atunci apare seria pe 10 ani fără fond comercial (calitate) și varianta cu fond comercial („pe prețul plătit"), ambele cu formule; o rată efectivă în afara intervalului 0-50% marchează anul „necesită verificare" și nu se înlocuiește tăcut.
- **AC-G3-4** (P2; 2007, 1986): Dat fiind seriile NOPAT și capital investit / Când se calculează indicatorii complementari / Atunci apar ROIC incremental = ΔNOPAT / Δcapital investit pe 5 și 10 ani (la Δcapital ≤ 0 se afișează „capital în scădere", fără valoare), capex / vânzări și conversia în numerar (OE / profit net), pe 10 ani și ca mediană.
- **AC-G3-5** (P2; 1992, 2000): Dat fiind rata de reinvestire (Δcapital investit / NOPAT) și ROIC / Când se calculează identitatea creșterii / Atunci g implicit = rata de reinvestire × ROIC apare lângă CAGR OE pe 10 ani, cu diferența în puncte; peste pragul din 4.10 apare marcajul „creștere neexplicată de reinvestire: verifică achiziții, modificări contabile, levier", fără a decide verdictul.
- **AC-G3-6** (P2; 1977): Dat fiind capitalul propriu de început de an / Când se afișează ROE / Atunci stă lângă creșterea EPS, cu avertismentul că EPS singur nu măsoară nimic; capitalul propriu negativ este marcat și ROE nu se calculează.
- **AC-G3-7** (P2, P5; 2007): Dat fiind ROIC incremental pe 10 ani și capex / vânzări / Când se atribuie categoria / Atunci: excelent = ROIC incremental peste 30% și capex / vânzări sub pragul „mic"; bun = între r + 5 puncte și 30%; groaznic = sub r, cu capital investit în creștere; între r și r + 5 puncte = nedeterminat; pragurile sunt afișate lângă categorie; testele reproduc See's 2007 (excelent), FlightSafety (bun) și un caz „groaznic".
- **AC-G3-8** (P3, P8; 2007, 1979): Dat fiind categoria / Când se evaluează verdictul / Atunci: date insuficiente sub 10 ani; trece dacă excelent sau bun și cel mult un an cu pierdere în 10; pică dacă groaznic; necesită judecată dacă nedeterminat, dacă pe 5 și pe 10 ani categoria diferă, dacă identitatea creșterii are marcaj sau dacă metoda de capex de întreținere schimbă categoria.

### 4.3 Supraviețuire

Scop: a verifica, prin inversare, că datoria nu poate ruina afacerea într-un an prost (1990, 2014, 2017).

User stories:
- Ca investitor, vreau datoria netă raportată la OE, acoperirea dobânzilor și scadențele pe 5 ani, ca să văd dacă afacerea are datorie puțină sau deloc și dacă refinanțarea poate deveni o problemă.
- Ca investitor, vreau să definesc un test de stres și să văd dacă afacerea rămâne pe linia de plutire, ca să știu ce m-ar ruina (Munger 2007).

Criterii de acceptare:
- **AC-SV-1** (P2; 2014; criteriile de achiziție: datorie puțină sau deloc): Dat fiind datoria financiară, numerarul și OE / Când se calculează / Atunci datorie netă / OE apare pe ultimul an și pe minimul OE din 10 ani (conservator), iar EBIT / dobânzi pe 10 ani, cu formule și intrări.
- **AC-SV-2** (P1, P4): Dat fiind scadențele pe 5 ani / Când nu sunt etichetate în XBRL (frecvent în ESEF) / Atunci câmpul arată „lipsă" și poate fi completat manual cu sursa (document, pagină), marcat „intrare umană cu sursă"; nu se estimează.
- **AC-SV-3** (P5, P3; 1990, 2017): Dat fiind scenariul de stres (scăderea OE în procente și durata; pentru financiare: procent de credite neperformante × severitate) / Când rulează / Atunci se afișează, după șoc, EBIT / dobânzi, anii de OE necesari rambursării datoriei nete și acoperirea scadențelor pe 2 ani din numerar plus OE stresat; scenariul implicit este fix și vizibil (4.10) și singurul care decide verdictul; scenariile utilizatorilor se salvează cu autor și se afișează alături; testul formulei reproduce exemplul Wells Fargo 1990.
- **AC-SV-4** (P3, P8): Dat fiind indicatorii / Când se evaluează verdictul / Atunci: date insuficiente sub 10 ani de OE sau fără dobânzi și datorie; pică dacă în cazul de bază EBIT / dobânzi < 1 sau datorie netă / OE depășește plafonul dur; necesită judecată dacă baza trece dar stresul implicit nu, sau dacă scadențele lipsesc; trece dacă baza și stresul implicit trec pragurile din 4.10.
- **AC-SV-5** (P4; 1990): Dat fiind o companie marcată financiară (judecată cu sursă) / Când se afișează modulul / Atunci indicatorii nefinanciari arată „neaplicabil (financiară)", nu sunt ascunși, iar testul de stres folosește forma 1990, cu portofoliul de credite introdus cu sursă.

### 4.4 Poarta 4: moat (dovezi)

Scop: a strânge dovezi cantitative că randamentele mari au rezistat atacurilor și a forța judecata explicită despre tip, direcție și durabilitate (2007, 1991).

User stories:
- Ca investitor, vreau persistența ROIC și tendința marjei brute pe 5 ani, ca să văd dacă castelul a rezistat (2007).
- Ca investitor, vreau să răspund explicit la testul de franciză (1991) și la testul capitalului (Florida 1998) și să notez direcția, nu doar nivelul, ca să nu confund o afacere bună cu un moat și să prind deteriorarea structurală (1991).
- Ca investitor, vreau să introduc cota de piață, retenția și prețul față de inflație cu sursă, ca să am dovezi, nu impresii (FCIC 2010).

Criterii de acceptare:
- **AC-G4-1** (P2, P8; 2007, FCIC 2010, 1991): Dat fiind 10 ani de ROIC tangibil, venituri și cost al vânzărilor / Când se calculează dovezile / Atunci apar numărul anilor cu ROIC ≥ r, ROIC minim și median, marja brută și marja operațională pe 10 ani și tendința lor pe 5 ani în puncte (mediana ultimilor 5 ani față de precedenții 5), cu formule.
- **AC-G4-2** (P1, P4; FCIC 2010): Dat fiind cota de piață, retenția sau prețul mediu pe unitate față de inflație / Când sunt introduse / Atunci fiecare valoare cere sursa (document, pagină sau link, data) și este marcată „intrare umană cu sursă"; fără sursă nu se salvează și câmpul contează ca incomplet; inflația vine din FRED, BCE sau BNR cu proveniență.
- **AC-G4-3** (P3; 2007, 1991, Florida 1998, 1996): Dat fiind formularul de judecată / Când se completează / Atunci conține: sursele moat-ului bifate (cost scăzut, brand, scară în cost / informație / dovadă socială, val lung, altul), fiecare cu dovadă și sursă; testul de franciză 1991 (necesar sau dorit; fără substitut apropiat; preț nereglementat) cu da / nu / necunoscut; testul capitalului 1998 (un rival capabil, cu o sumă foarte mare, ar putea lua afacerea: da / nu); „are nevoie de manager-vedetă" 2007 (da / nu); direcția (se lărgește / stabil / se îngustează, 1991); durabilitatea estimată (5 / 10 / 20+ ani); inevitabil sau impostor 1996 (opțional). În v1 originea fiecărui câmp este „om"; structura acceptă „propus de AI" din faza 3 fără migrare (AC-X-3).
- **AC-G4-4** (P3, P8; 2007, 1991, Florida 1998): Dat fiind dovezile și formularul / Când se evaluează verdictul / Atunci: date insuficiente sub 10 ani; necesită judecată dacă formularul este incomplet; pică dacă testul capitalului este „da" sau nu este bifată nicio sursă de moat; trece dacă formularul este complet, testul capitalului este „nu", există cel puțin o sursă cu dovadă, direcția nu este „se îngustează", iar persistența și tendința marjei brute ating pragurile din 4.10; altfel necesită judecată (dovezile și judecata nu concordă).

### 4.5 Poarta 5: preț sub valoare

Scop: a compara prețul cu un interval conservator de valoare intrinsecă și a fixa prețul pe care l-aș plăti (1992, 2000, 1984).

User stories:
- Ca investitor, vreau VI ca interval din DCF pe OE cu ipoteze fixe și vizibile, și DCF invers, ca să nu mă păcălesc cu precizie falsă și să văd ce creștere presupune prețul de azi (1993, 2000).
- Ca investitor, vreau randamentul OE față de obligațiunea la 10 ani, ca să am verificarea simplă din 1991.
- Ca investitor, vreau prețul pe care l-aș plăti din marja cerută după categorie, ca să aștept prețul, nu să-l urmăresc (1994).

Criterii de acceptare:
- **AC-G5-1** (P2, P5; 1992, 2000): Dat fiind OE_0 și parametrii / Când se calculează VI / Atunci VI = Σ(t = 1..10) OE_0 × (1 + g)^t / (1 + r)^t + [OE_11 / (r - g_terminal)] / (1 + r)^10, cu valoarea terminală actualizată la prezent (corecție față de formula din descoperire, secțiunea 11), afișată cu toate intrările și cu test cu rezultat cunoscut.
- **AC-G5-2** (P5; 1992, 2000; rețeta: pragul este obligațiunea lungă, fără primă de risc pe companie): Dat fiind randamentul obligațiunii lungi din FRED, BCE sau BNR, după moneda listării / Când se stabilește r / Atunci r = max(prag minim global, randament + primă fixă globală), identic pentru toate companiile, versionat, modificabil pe companie doar ca scenariu.
- **AC-G5-3** (P5; 1992, 2000, 1993): Dat fiind cele două seturi fixe de parametri din 4.10 / Când se afișează VI / Atunci apare ca interval [VI_low, VI_high] pe acțiune, cu fiecare set vizibil; g pe anii 1-10 nu depășește CAGR istoric OE pe 10 ani; la CAGR negativ, g = 0 și apare marcajul „OE în scădere".
- **AC-G5-4** (P2; 2000): Dat fiind capitalizarea / Când se calculează DCF invers / Atunci se afișează g pe 10 ani care egalează prețul, cu ceilalți parametri din setul VI_low, lângă CAGR istoric; fără soluție în intervalul -20% la +50% apare „în afara intervalului".
- **AC-G5-5** (P2; 1991): Dat fiind OE_0 și capitalizarea / Când se afișează randamentul / Atunci OE_0 / capitalizare apare lângă randamentul obligațiunii la 10 ani în moneda listării, cu data și proveniența ambelor și cu diferența în puncte; nu produce verdict singur.
- **AC-G5-6** (P5; 1984, 1991, 1992): Dat fiind verdictul Poarta 4 și testul de franciză / Când se alege marja / Atunci franciză (15-25%) doar dacă Poarta 4 este „trece" și testul de franciză 1991 are trei „da", altfel afacere (30-50%); prețul pe care l-aș plăti = interval [VI_low × (1 - marja maximă), VI_low × (1 - marja minimă)] pe acțiune, cu formula vizibilă.
- **AC-G5-7** (P1, P7): Dat fiind prețul de închidere, acțiunile în circulație și cursul / Când se calculează capitalizarea / Atunci toate trei sunt fapte vendor cu proveniență (vendor, data valorii, data extragerii); acțiunile vendor se verifică cu pagina de copertă a ultimei depuneri, iar o diferență peste pragul din 4.10 este divergență; conversia valutară folosește cursul BCE sau BNR de la data prețului; acestea sunt singurele fapte vendor acceptate în formule, impus prin test.
- **AC-G5-8** (P3, P5, P8, P10): Dat fiind prețul și intervalul / Când se evaluează verdictul / Atunci: date insuficiente sub 10 ani de OE, fără preț din ultimele 7 zile de tranzacționare sau fără randament; trece dacă prețul ≤ VI_low × (1 - marja maximă); necesită judecată dacă prețul este între acest nivel și VI_low × (1 - marja minimă); pică peste; verdictul poartă data prețului și se recalculează zilnic; textul verdictului nu conține nicio formulare de acțiune.
- **AC-G5-9** (P10; cadența săptămânală: watchlist cu intervalul de valoare și prețul pe care l-aș plăti): Dat fiind lista de companii / Când prețul zilei este sub prețul pe care l-aș plăti / Atunci apare starea „preț sub prețul pe care l-aș plăti: da", cu data, în aplicație; v1 nu trimite notificări.
- **AC-G5-10** (propus de PM; rețeta, punctul 5, verificări încrucișate; 1983): Dat fiind ROIC tangibil median pe 10 ani și capitalizarea / Când se afișează poarta / Atunci apare multiplul capitalului tangibil plătit (capitalizare / capital investit tangibil) lângă ROIC, fără verdict. Justificare: verificarea e în rețetă, folosește intrări deja calculate și nu cere ingestie nouă.

### 4.6 Proveniență și jurnal de probleme de date

Scop: fiecare cifră are drum înapoi până la raport; fiecare problemă de date este vizibilă (P1, P9).

User stories:
- Ca investitor, vreau să ating orice cifră și să văd sursa, perioada, eticheta, data extragerii și linkul, ca să verific în 30 de secunde.
- Ca investitor, vreau jurnalul problemelor de date pe companie, ca să știu ce nu e sigur înainte să judec.

Criterii de acceptare:
- **AC-PR-1** (P1): Dat fiind un fapt / Când se ingerează / Atunci are: sursa (EDGAR, ESEF, import manual), entitatea (CIK, LEI, ISIN), perioada fiscală (început, sfârșit, exercițiu, tip anual sau instant), conceptul (etichetă XBRL standard sau extensie, ori pagina din PDF), documentul (identificator de depunere, data depunerii), unitatea, scara și precizia, data și ora extragerii, link către document; un fapt fără oricare dintre acestea este respins la ingestie.
- **AC-PR-2** (P1, P7): Dat fiind un fapt vendor (preț, acțiuni, curs, randament) / Când se ingerează / Atunci are vendorul, endpointul, data valorii, data extragerii și tipul „vendor"; motorul respinge faptele vendor pentru orice alt concept (test automat).
- **AC-PR-3** (P2, P6): Dat fiind un calcul / Când se afișează / Atunci listează identificatorul și versiunea formulei, fact id-urile de intrare, parametrii cu versiune, rezultatul și unitatea; endpointul „explică" întoarce arborele complet, iar interfața îl deschide din orice cifră.
- **AC-PR-4** (P4, P9): Dat fiind o etichetă proprie a companiei / Când se mapează la un concept standard / Atunci maparea este în tabelul versionat (companie, interval de perioade, autor, justificare) și generează o intrare în jurnal; fără mapare, conceptul este „lipsă" (AC-X-5).
- **AC-PR-5** (P1, P7): Dat fiind un import manual / Când se încarcă șablonul CSV / Atunci fiecare celulă are document, pagină, cifra exact ca în raport, unitate și scară, altfel validatorul respinge rândul; faptele intră în verdicte doar după semnătura unui al doilea cititor; până atunci poarta arată „date insuficiente (import în validare)".
- **AC-PR-6** (P1, P9; propus de PM): Dat fiind aceeași combinație (entitate, concept, perioadă) în mai multe depuneri / Când valorile diferă peste rotunjire / Atunci faptul implicit vine din ultima depunere, originalul rămâne vizibil cu marcajul „restatat", cu intrare în jurnal; analizele înghețate păstrează fact id-ul folosit atunci.
- **AC-PR-7** (P9): Dat fiind o problemă de date / Când se creează / Atunci are companie, tip (concept lipsă, mapare extensie, divergență vendor, restatare, unitate sau scară, exercițiu fiscal schimbat, capital propriu negativ, rată de impozit în afara intervalului, import în validare, altele), severitate (blochează poarta, avertisment, informativ), stare (deschis, acceptat cu motiv, rezolvat), autor și date; este vizibilă pe pagina companiei și filtrabilă; o intrare „blochează poarta" deschisă face poarta „date insuficiente" (AC-X-10).
- **AC-PR-8** (P1): Dat fiind interfața / Când rulează testul UI din CI / Atunci fiecare valoare numerică afișată poartă o referință de proveniență și panoul se deschide; build-ul eșuează la prima cifră fără referință.

### 4.7 Dosar de decizie minim

Scop: a îngheța analiza și paragraful de decizie, ca să poată fi recitite și reproduse peste ani (P6; rețeta, punctul 6; Florida 1998).

User stories:
- Ca investitor, vreau să înghețăm analiza ca versiune numerotată și să scriu paragraful de decizie cu cele patru întrebări, ca să recitesc exact ce știam și ce credeam și să nu decid fără el.
- Ca partener, vreau să văd cine a scris fiecare judecată și când, ca să discutăm pe fapte.

Criterii de acceptare:
- **AC-DD-1** (P6): Dat fiind o analiză / Când se îngheață / Atunci versiunea N conține fact id-urile și valorile, versiunile parametrilor și formulelor, judecățile cu autori, verdictele, textele și data prețului; este imuabilă; o nouă înghețare este N+1; lista versiunilor este vizibilă.
- **AC-DD-2** (P6): Dat fiind o versiune înghețată / Când este re-executată / Atunci valorile și verdictele sunt identice (test automat pe setul de aur); o re-execuție cu date curente creează un draft nou și nu suprascrie nimic.
- **AC-DD-3** (P3, P10; Florida 1998; rețeta, punctul 6): Dat fiind paragraful de decizie / Când se îngheață analiza / Atunci cele patru câmpuri sunt completate (cum arată afacerea peste 10 ani; de ce ține moat-ul; ce plătesc față de cât valorează; ce m-ar contrazice), altfel înghețarea este refuzată, cu câmpul lipsă afișat; paragraful este judecată cu autor și dată; dosarul arată verdictele pe porți, intervalul VI, prețul pe care l-aș plăti și judecățile atribuite, fără nicio formulare de acțiune; diff-ul anual, condițiile de ieșire și calculatorul cu impozit sunt în faza 3.

### 4.8 Export CSV

Scop: a scoate analiza cu proveniență completă pentru al doilea cititor și pentru arhivă (P1, P6).

User story: Ca al doilea cititor, vreau exportul complet al unei versiuni, ca să recalculez în afara aplicației.

Criterii de acceptare:
- **AC-EX-1** (P1, P6): Dat fiind o versiune de analiză / Când se exportă / Atunci rezultă facts.csv (toate coloanele de proveniență), calculations.csv (formula, versiune, fact id-uri de intrare, valoare), judgments.csv (câmp, valoare, autor, dată, origine, citări), verdicts.csv, issues.csv și metadata.csv (versiune, data exportului, versiuni de parametri), UTF-8, separator virgulă, șiruri între ghilimele, date ISO 8601, numere nerotunjite; două exporturi ale aceleiași versiuni înghețate sunt identice.
- **AC-EX-2** (licențe): Dat fiind exportul / Când conține date vendor / Atunci include doar prețul, acțiunile și cursul folosite în analiză, la data lor, nu istoricul de prețuri și nu valorile vendorului de fundamentale (doar marcajul de divergență și procentul).

### 4.9 Autentificare multi-utilizator simplă

Scop: conturi pentru owner și parteneri, fără acces public, judecăți atribuite (decizie 31 octombrie 2026).

User story: Ca owner, vreau să invit parteneri și să văd cine a schimbat ce, ca să discutăm pe judecăți atribuite.

Criterii de acceptare:
- **AC-AU-1**: Dat fiind aplicația / Când un vizitator neautentificat cere orice pagină, API, export sau document / Atunci primește doar ecranul de autentificare; nu există înregistrare liberă; conturile se creează doar prin invitația owner-ului; parolă de minimum 12 caractere, stocată cu argon2id; sesiunile expiră (14 zile de inactivitate, 30 de zile absolut); 5 încercări eșuate în 15 minute blochează temporar, cu jurnalizare.
- **AC-AU-2**: Dat fiind rolurile owner și partner / Când un partner încearcă parametri globali, invitații, aprobarea mapărilor sau acceptarea problemelor / Atunci este refuzat; toți utilizatorii văd același spațiu de lucru, iar fiecare judecată poartă autorul.
- **AC-AU-3** (Should): Dat fiind un utilizator / Când activează TOTP / Atunci autentificarea cere codul; owner-ul poate impune TOTP pentru toți.
- **AC-AU-4** (P6): Dat fiind orice modificare de judecată, parametru global, mapare sau stare a unei probleme / Când se salvează / Atunci jurnalul de audit reține cine, când, valoarea înainte și după; vizibil pentru owner.

### 4.10 Parametri impliciți v1

Propuși de PM, de validat pe setul de aur; modificabili doar de owner, versionat; nu sunt reguli din scrisori.

| Parametru | Implicit | Sursă metodă | Principiu |
|---|---|---|---|
| Prag r | max(10%, randament obligațiune lungă + p), p = 0 | 1992, 2000 | P5 |
| Set VI_low | OE_0 = min(OE ultimul an, media 5 ani); g = 0; g_terminal 2% | 1986, 1993 | P5 |
| Set VI_high | OE_0 = OE ultimul an; g = min(CAGR OE 10 ani, 8%); g_terminal 3% | 1992, 2000 | P5 |
| Marja cerută | afacere 30-50%; franciză 15-25% | 1984, 1991, 1992 | P5 |
| Categorie | excelent peste 30% și capex / vânzări ≤ 5%; bun r + 5 la 30%; groaznic sub r cu capital în creștere | 2007 | P2 |
| Numerar excedentar | numerar peste 2% din vânzări | 2017 (capital tangibil necesar operării) | P5 |
| Identitatea creșterii | marcaj la diferență peste 5 puncte | 1992, 2000 | P2 |
| Instabilitate (Poarta 2) | ≥ 2 ani cu pierdere în 10; CV OE peste 0,5; abatere venituri peste 20% într-un an | 1992, 1979 | P5 |
| Supraviețuire | trece: datorie netă / OE ≤ 2 și EBIT / dobânzi ≥ 8; pică: datorie netă / OE peste 5 sau EBIT / dobânzi sub 1; stres implicit OE -50% timp de 2 ani; financiare 10% neperformante × 30% severitate | 1990, 2017 | P5 |
| Persistența moat | ROIC ≥ r în cel puțin 8 din 10 ani; marja brută pe 5 ani nu scade cu peste 3 puncte | 2007, 1991 | P2 |
| Toleranțe | rotunjire 0,5% relativ sau o unitate de precizie; divergență materială peste 5%; acțiuni vendor față de depunere peste 1% | P7 | P7 |
| Capex de întreținere | min(capex, amortizare); alternativ Greenwald | 1986 | P4 |

## 5. Cerințe non-funcționale

### 5.1 Proveniență și reproductibilitate

Documentele brute (JSON companyfacts, pachete ESEF, PDF-urile importurilor) se stochează local, cu hash, ca linkurile să nu depindă de sursă; formulele și parametrii sunt versionați semantic; o analiză înghețată se re-execută identic ani mai târziu din datele stocate (AC-DD-2); rotunjirea se face doar la afișare, valorile se păstrează cu precizia raportată.

### 5.2 Auditabilitate

Fiecare valoare derivată listează fact id-urile de intrare și versiunea formulei (AC-PR-3); endpointul „explică" este în API-ul intern și folosit de QA; jurnalul de audit (AC-AU-4) și jurnalul de probleme (AC-PR-7) sunt exportabile.

### 5.3 Performanță (ținte propuse)

| Operațiune | Țintă |
|---|---|
| Pagina unei companii din fapte în cache | sub 2 s desktop, sub 3 s telefon pe 4G (p95); motorul sub 500 ms |
| Prima ingestie SUA (companyfacts, index de depuneri, verificare încrucișată) | sub 2 minute |
| Prima ingestie ESEF (4-5 ani) | sub 5 minute |
| Validarea unui șablon de import manual | sub 10 s |
| Reîmprospătarea zilnică a prețurilor pentru 200 de companii | sub 10 minute, în limitele vendorului |
| Export CSV; re-execuția unei analize înghețate | sub 5 s fiecare |

### 5.4 Securitate (desfășurare mică, multi-utilizator)

Conturi doar prin invitație, fără pagină publică (AC-AU-1); TLS prin reverse proxy; secretele (chei EODHD, FRED, Claude, parola bazei) doar în variabile de mediu sau Docker secrets, niciodată în repo, cu scanare de secrete în CI; cheile vendor nu ajung în client; jurnal de audit; backup zilnic criptat, cu test de restaurare lunar; imagini Docker fixate pe versiune și actualizări lunare de dependențe; către Claude API se trimit doar extrase din documente publice, fără date personale; jurnalele nu conțin secrete.

### 5.5 Licențe de date

EDGAR: User-Agent declarat cu numele aplicației și e-mail de contact, cel mult 10 cereri pe secundă, preferință pentru exporturile în bloc și cache local. filings.xbrl.org: gratuit, atribuire, cache local. EODHD sau similar: licență de uz personal, fără redistribuire; prețurile se afișează doar utilizatorilor autentificați și nu se exportă ca istoric (AC-EX-2); acoperirea partenerilor de confirmat (secțiunea 9). Vendorul de fundamentale: doar verificare încrucișată, valorile nu se afișează ca adevăr și nu se exportă. Yahoo Finance: doar verificare manuală, fără scraping automat. FRED: cheie gratuită, atribuire; BCE și BNR: publice. Morningstar și GuruFocus: cel mult link extern.

### 5.6 Portabilitate

Docker Compose cu PostgreSQL, fără dependențe macOS; întâi Mac Mini (M4, 24 GB, rulează deja n8n), apoi VPS; mutarea înseamnă copierea volumelor și a fișierului de mediu; procedura de mutare se testează o dată înainte de raportul QA v1.

### 5.7 Observabilitate

Jurnal de ingestie pe rulare (sursă, companie, documente, concepte mapate, excepții), păstrat 12 luni; jurnalul de probleme de date în baza de date și în interfață; pagină de stare a joburilor (ultimul succes, durată, erori, cereri consumate pe vendor); la job eșuat, e-mail simplu în v1, n8n din faza 3.

### 5.8 Buget

Plafon 200 EUR pe lună pentru date (vendor global de prețuri cu BVB plus vendor de fundamentale pentru verificare); consumul se afișează în pagina de administrare; costul Claude API este separat (secțiunea 9).

## 6. Date și surse (scurt)

| Piață | Adevăr | Verificare încrucișată | Prețuri, acțiuni, macro | Intrare umană cu sursă |
|---|---|---|---|---|
| SUA | EDGAR XBRL companyfacts și documentele 10-K, 10-Q, DEF 14A | vendor de fundamentale | EODHD sau similar; FRED | scadențe lipsă, cotă de piață, retenție, preț față de inflație |
| UE (ESEF) din 2020-2021 | filings.xbrl.org (IFRS cu extensii) | vendor de fundamentale | EODHD; BCE | la fel, plus scadențe (rar etichetate) |
| UE înainte de 2020 | import manual validat din PDF | al doilea cititor | EODHD; BCE | tot istoricul, cu pagină |
| BVB | rapoartele emitenților, import manual validat (ESEF unde există) | al doilea cititor | EODHD; BNR | tot istoricul, cu pagină |

Reguli: sursa primară bate vendorul (P7); vendorul intră în formule doar pentru preț, acțiuni, curs și randamente (AC-PR-2); ce nu se obține fiabil (cotă de piață, volum fizic, retenție, putere de preț) rămâne judecată cu dovezi. Detaliile de ingestie, normalizare și model de date sunt în arhitectura Dev (ADR-urile din SG-002), nu aici.

## 7. Backlog pe faze

Faza 1 fundație (în curs), faza 2 versiunea 1, faza 3 proprietar, faza 4 univers. Prioritate: Must, Should, Could. Story-urile din fazele 3 și 4 primesc AC la începutul fazei lor.

| ID | Story | Faza | Prioritate | Acceptare |
|---|---|---|---|---|
| SG-001 | Epic: Fundație (arhitectură, spike de date, strategie de test, wireframes) | 1 | Must | review de fază |
| SG-002 | ADR-uri: stivă, Docker Compose, PostgreSQL, model fapt / calcul / judecată | 1 | Must | AC-PR-1..3 |
| SG-003 | Spike de date: 5 companii reconciliate manual (3 SUA, 1 UE, 1 BVB) | 1 | Must | AC-PR-1, AC-PR-5 |
| SG-004 | Tabel de normalizare XBRL v0 cu jurnal de excepții | 1 | Must | AC-PR-4 |
| SG-005 | Strategia de test, setul de aur (20 de companii), toleranțe | 1 | Must | secțiunea 8 |
| SG-006 | Fluxuri și wireframes telefon / desktop; limbaj vizual fapt / calcul / judecată; stări „date insuficiente" | 1 | Must | AC-X-1, AC-X-2, AC-X-4 |
| SG-007 | Repo GitHub, CI cu teste, lint de vocabular, scanare de secrete | 1 | Must | AC-X-9 |
| SG-008 | Review de fază 1 cu product owner | 1 | Must | secțiunea 9 închisă |
| SG-009 | Epic: Ingestie și normalizare | 2 | Must | AC-PR-1..6 |
| SG-010 | Adăugare companie la cerere (ticker, ISIN, CIK, LEI) | 2 | Must | AC-PR-1 |
| SG-011 | Ingestie EDGAR companyfacts și index de depuneri, stocare brută locală | 2 | Must | AC-PR-1 |
| SG-012 | Ingestie ESEF din filings.xbrl.org (IFRS cu extensii) | 2 | Must | AC-PR-1, AC-PR-4 |
| SG-013 | Import manual validat: șablon CSV, validator, semnătura celui de-al doilea cititor | 2 | Must | AC-PR-5 |
| SG-014 | Normalizare cu tabel de mapare versionat și excepții în jurnal | 2 | Must | AC-PR-4, AC-X-5 |
| SG-015 | Prețuri, acțiuni în circulație, cursuri, randamente (EODHD, FRED, BCE, BNR) | 2 | Must | AC-G5-7, AC-PR-2 |
| SG-016 | Verificare încrucișată automată cu vendorul de fundamentale | 2 | Must | AC-X-6 |
| SG-017 | Politica de restatări | 2 | Should | AC-PR-6 |
| SG-018 | Marcaj financiară / nefinanciară cu sursă | 2 | Should | AC-SV-5 |
| SG-019 | Epic: Motor de formule și proveniență | 2 | Must | AC-X-4..8, AC-PR-3 |
| SG-020 | Model de proveniență (fact, calc, judgment) cu id-uri și versiuni | 2 | Must | AC-PR-1..3 |
| SG-021 | Motor de formule pur, versionat, teste cu rezultat cunoscut | 2 | Must | AC-X-7 |
| SG-022 | Parametri globali versionați; scenariu față de valoare | 2 | Must | AC-X-8 |
| SG-023 | Regula celor 10 ani, stările „date insuficiente", precedența verdictelor | 2 | Must | AC-X-4, AC-X-5, AC-X-10 |
| SG-024 | Endpoint și panou „explică" | 2 | Must | AC-PR-3 |
| SG-025 | Epic: Poarta 2, înțelegi afacerea | 2 | Must | AC-G2-1..5 |
| SG-026 | Indicatori de stabilitate pe 10 ani și indiciul de instabilitate | 2 | Must | AC-G2-1, AC-G2-2 |
| SG-027 | Intrări umane obligatorii: descriere 10 ani, 3 moduri de a muri, paragraf, clasificare | 2 | Must | AC-G2-3, AC-G2-4 |
| SG-028 | Verdict Poarta 2 și istoricul textelor | 2 | Must | AC-G2-5 |
| SG-029 | Epic: Poarta 3, randamente pe capital | 2 | Must | AC-G3-1..8 |
| SG-030 | OE 1986 cu capex de întreținere în două metode | 2 | Must | AC-G3-1, AC-G3-2 |
| SG-031 | ROIC tangibil 10 ani, cu și fără fond comercial | 2 | Must | AC-G3-3 |
| SG-032 | ROIC incremental 5 / 10, identitatea creșterii, capex / vânzări, conversie | 2 | Must | AC-G3-4, AC-G3-5 |
| SG-033 | ROE pe capital de început lângă EPS, cu avertisment | 2 | Should | AC-G3-6 |
| SG-034 | Categoria 2007 și verdictul Poarta 3 | 2 | Must | AC-G3-7, AC-G3-8 |
| SG-035 | Epic: Supraviețuire | 2 | Must | AC-SV-1..5 |
| SG-036 | Datorie netă / OE, EBIT / dobânzi, scadențe cu intrare umană | 2 | Must | AC-SV-1, AC-SV-2 |
| SG-037 | Test de stres: scenariu implicit, scenarii utilizator, forma 1990 | 2 | Must | AC-SV-3 |
| SG-038 | Verdict supraviețuire | 2 | Must | AC-SV-4, AC-SV-5 |
| SG-039 | Epic: Poarta 4, moat (dovezi) | 2 | Must | AC-G4-1..4 |
| SG-040 | Persistența ROIC, marje și tendințe pe 5 ani | 2 | Must | AC-G4-1 |
| SG-041 | Intrări umane cu sursă: cotă de piață, retenție, preț față de inflație | 2 | Should | AC-G4-2 |
| SG-042 | Formular de judecată: surse de moat, teste 1991 / 1998 / 2007, direcție | 2 | Must | AC-G4-3 |
| SG-043 | Verdict Poarta 4 | 2 | Must | AC-G4-4 |
| SG-044 | Epic: Poarta 5, preț sub valoare | 2 | Must | AC-G5-1..10 |
| SG-045 | DCF pe OE cu ipoteze fixe, interval VI | 2 | Must | AC-G5-1..3 |
| SG-046 | DCF invers | 2 | Must | AC-G5-4 |
| SG-047 | Randamentul OE față de obligațiunea la 10 ani | 2 | Must | AC-G5-5 |
| SG-048 | Marja cerută, prețul pe care l-aș plăti, verdict | 2 | Must | AC-G5-6, AC-G5-8 |
| SG-049 | Stare „preț sub prețul pe care l-aș plăti" în aplicație | 2 | Should | AC-G5-9 |
| SG-050 | Multiplul capitalului tangibil plătit lângă ROIC (propus de PM) | 2 | Could | AC-G5-10 |
| SG-051 | Epic: Proveniență în interfață și jurnal de probleme | 2 | Must | AC-PR-7, AC-PR-8 |
| SG-052 | Panou de proveniență pe orice cifră | 2 | Must | AC-PR-1, AC-PR-3 |
| SG-053 | Jurnal de probleme de date pe companie, stări, blocarea porții | 2 | Must | AC-PR-7 |
| SG-054 | Test UI: nicio cifră fără proveniență | 2 | Must | AC-PR-8 |
| SG-055 | Marcare vizuală fapt / calcul / judecată | 2 | Must | AC-X-2 |
| SG-056 | Epic: Dosar de decizie minim și export | 2 | Must | AC-DD-1..3, AC-EX-1..2 |
| SG-057 | Înghețare versionată și re-execuție identică | 2 | Must | AC-DD-1, AC-DD-2 |
| SG-058 | Paragraful de decizie cu patru câmpuri | 2 | Must | AC-DD-3 |
| SG-059 | Export CSV cu proveniență | 2 | Must | AC-EX-1, AC-EX-2 |
| SG-060 | Epic: Autentificare, securitate, desfășurare | 2 | Must | AC-AU-1..4, secțiunea 5 |
| SG-061 | Conturi prin invitație, roluri, sesiuni, limitare la autentificare | 2 | Must | AC-AU-1, AC-AU-2 |
| SG-062 | TOTP opțional | 2 | Should | AC-AU-3 |
| SG-063 | Jurnal de audit | 2 | Must | AC-AU-4 |
| SG-064 | Docker Compose pe Mac Mini, TLS, secrete, backup și restaurare testată | 2 | Must | 5.4, 5.6 |
| SG-065 | Pagină de stare a joburilor, jurnale de ingestie, consum vendori | 2 | Must | 5.7, 5.8 |
| SG-066 | Interfață EN / RO cu vocabular fix și lint de termeni interziși | 2 | Must | AC-X-1, AC-X-9 |
| SG-067 | Epic: QA v1 | 2 | Must | secțiunea 8 |
| SG-068 | Regresie automată pe setul de aur | 2 | Must | secțiunea 8 |
| SG-069 | Al doilea cititor: recalcul independent din rapoarte brute | 2 | Must | secțiunea 8 |
| SG-070 | Teste de proprietate: fără substituții tăcute, fără cifre fără sursă | 2 | Must | AC-X-5, AC-PR-8 |
| SG-071 | Test de înțelegere cu utilizator nou | 2 | Must | secțiunea 8 |
| SG-072 | Teste de prospețime și integritate a datelor | 2 | Should | 5.7 |
| SG-073 | Raport QA „trece / nu trece" pentru v1 | 2 | Must | secțiunea 1 |
| SG-074 | Epic: Management | 3 | Must | AC de scris |
| SG-075 | Testul dolarului pe 5 și 10 ani (1983) | 3 | Must | AC de scris |
| SG-076 | Răscumpărări: preț mediu plătit față de VI la acea dată; evoluția acțiunilor (2011, 2016) | 3 | Must | AC de scris |
| SG-077 | Deprecieri de achiziții; insideri și compensație din proxy, extrase AI cu citare | 3 | Should | AC-X-3 |
| SG-078 | Epic: Judecăți propuse de AI | 3 | Must | AC-X-3 |
| SG-079 | Verificator de citări verbatim | 3 | Must | AC-X-3 |
| SG-080 | Draft AI pentru moat cu citări | 3 | Must | AC-X-3, AC-G4-3 |
| SG-081 | Epic: Poarta 6, păstrezi cât țin faptele | 3 | Must | AC de scris |
| SG-082 | Re-subscriere anuală cu diff (1996, 2014) | 3 | Must | AC de scris |
| SG-083 | Condiții de ieșire (1989, 1991, 2004, 2024) și jurnal de greșeli (1989, 2008) | 3 | Must | AC de scris |
| SG-084 | Calculator de schimbare cu impozit (1989) | 3 | Should | AC-X-7 |
| SG-085 | Epic: Poarta 1, portofoliu | 3 | Must | AC de scris |
| SG-086 | Poziții, cost, look-through (1990, 1991) | 3 | Must | AC de scris |
| SG-087 | Concentrare și dimensionare fracționată cu plafon 40% (1966, Munger 1994) | 3 | Should | AC de scris |
| SG-088 | Epic: Cadență, alerte, PDF | 3 | Should | AC de scris |
| SG-089 | Alerte de preț și digest prin n8n | 3 | Should | AC-G5-9 |
| SG-090 | Memoriu PDF pe companie | 3 | Should | AC-DD-3 |
| SG-091 | Memento anual de re-estimare (2014) | 3 | Could | AC de scris |
| SG-092 | Epic: Univers | 4 | Should | AC de scris |
| SG-093 | Screening nocturn porțile 3 și 5 pe S&P 500, Stoxx 600, BVB | 4 | Should | AC-G3-8, AC-G5-8 |
| SG-094 | Import istoric asistat UE și BVB la scară | 4 | Should | AC-PR-5 |
| SG-095 | Jurnal de calitate a datelor pe univers | 4 | Could | AC-PR-7 |

## 8. Metrici de succes v1

| Metrică | Țintă | Cum se măsoară |
|---|---|---|
| Reconciliere set de aur | 20 din 20 companii, zero diferențe neexplicate față de raport (toleranța din 4.10) | raport QA, al doilea cititor |
| Proveniență | 100% din cifrele afișate au proveniență | test UI din CI (AC-PR-8) |
| Formule testate | 100% din formule cu test cu rezultat cunoscut, zero eșecuri | CI |
| Reproductibilitate | re-execuția celor 20 de analize înghețate dă rezultate identice | test automat (AC-DD-2) |
| Înțelegere | 3 din 3 utilizatori noi explică corect un verdict în sub 10 minute, fără ajutor | test de utilizare, UX |
| Substituții tăcute | zero | teste de proprietate |
| Limbaj | zero termeni interziși în interfață | lint din CI (AC-X-9) |
| Performanță | țintele din 5.3 atinse la p95 | măsurători pe Mac Mini |
| Buget | sub 200 EUR pe lună în primele 3 luni | pagina de administrare |

## 9. Întrebări deschise pentru product owner

| Nr | Întrebare | Implicit propus (se lucrează cu el până la răspuns) |
|---|---|---|
| 1 | Parametrii VI: prag r, plafonul lui g, g_terminal, baza OE_0 | tabelul 4.10: r = max(10%, obligațiune), g ≤ min(CAGR, 8%), terminal 2-3%, OE_0 conservator |
| 2 | Pragurile de supraviețuire și scenariul de stres implicit | datorie netă / OE ≤ 2, EBIT / dobânzi ≥ 8, OE -50% timp de 2 ani; financiare 10% × 30% (1990) |
| 3 | Pragurile categoriei 2007 și ce înseamnă capex / vânzări „mic" | 30%, r + 5, r; capex / vânzări ≤ 5% |
| 4 | Confirmarea definiției lui „gata" restrânse la porțile v1 și compoziția setului de aur | DoD din secțiunea 1; spike pe 5 companii: Coca-Cola, Apple, Moody's, un emitent ESEF german, un emitent BVB cu ESEF; QA propune lista de 20 |
| 5 | Politica de restatări | ultima depunere implicit, originalul vizibil (AC-PR-6) |
| 6 | Licența vendorului de prețuri acoperă partenerii? | se verifică termenii înainte de prima invitație; până atunci o singură desfășurare privată, fără export de istoric |
| 7 | Bugetul Claude API, în afara plafonului de date | plafon soft 50 EUR pe lună, afișat în administrare; în v1 consumul este zero |
| 8 | Maparea verdictului Poarta 5 pe interval și atribuirea marjei de franciză | AC-G5-6 și AC-G5-8 |

## 10. Jurnal de decizii

| Data | Decizie | Origine |
|---|---|---|
| 31 octombrie 2026 | Utilizatori: product owner plus câțiva parteneri; multi-utilizator simplu de la început, fără facturare; comercialul mai târziu | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Piețe v1: SUA plus UE (ESEF), inclusiv BVB; istoricul european pre-2020 prin import validat | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Adevărul datelor: surse primare (EDGAR, ESEF); vendori doar pentru prețuri și verificare încrucișată | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Buget date până la 200 EUR pe lună: vendor global de prețuri și acțiuni cu BVB, plus vendor de fundamentale exclusiv pentru verificare automată | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Judecăți calitative: AI propune din rapoarte cu citări verificate automat, omul confirmă; AI nu poate trece o poartă; draftul rămâne „propus de AI" | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Model AI: doar Claude API; fără model local | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Formă: aplicație web responsivă (telefon și desktop) | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Găzduire: local sau Mac Mini, apoi VPS; totul containerizat de la început (Docker Compose, PostgreSQL) | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Stivă: Python (FastAPI, Arelle sau edgartools, PostgreSQL) pentru ingestie și motor; TypeScript (Next.js sau SvelteKit) pentru interfață; planificator de joburi | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Cod: GitHub, repo nou (organizația de decis); backlog și QA în Jira, proiect separat | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | Implicite: interfață EN principal și RO; portofoliu în faza 3; alerte n8n în faza 3; screening în faza 4; univers la cerere în v1 | requirements_v0, secțiunea 6 |
| 31 octombrie 2026 | DoD v1 propusă: 20 de companii din setul de aur reconciliate; QA recalculează independent; verdict înțeles de o persoană nouă; nicio cifră fără proveniență | requirements_v0, secțiunea 6 (de confirmat) |
| 31 octombrie 2026 | Fazele se numerotează după secțiunea 7; etichetele „Faza 1/2/3" din harta funcționalităților sunt fazele 2/3/4 | propus de PM |
| 31 octombrie 2026 | DoD v1 restrânsă la porțile v1 (2, 3, 4 dovezi, 5, Supraviețuire), plus reproductibilitatea analizelor înghețate | propus de PM |
| 31 octombrie 2026 | Vocabular fix al verdictelor cu chei de cod și echivalente EN; precedența: date insuficiente, pică, necesită judecată, trece | propus de PM |
| 31 octombrie 2026 | Formula VI cu valoarea terminală actualizată la prezent | propus de PM (corecție) |
| 31 octombrie 2026 | r = max(prag minim 10%, obligațiune lungă + primă fixă), global, niciodată pe companie | propus de PM |
| 31 octombrie 2026 | Import manual validat minim în v1 pentru cele 10 companii UE și BVB din setul de aur; tooling la scară în faza 4 | propus de PM |
| 31 octombrie 2026 | Dosar minim v1 = înghețare versionată plus paragraful cu patru câmpuri; restul Poarta 6 în faza 3 | propus de PM |
| 31 octombrie 2026 | Alerta Poarta 5 în v1 = stare în aplicație, fără notificări | propus de PM |
| 31 octombrie 2026 | Faptele vendor intră în formule doar pentru preț, acțiuni, curs și randamente | propus de PM |
| 31 octombrie 2026 | Politica de restatări: ultima depunere implicit, originalul vizibil, diferența în jurnal | propus de PM |
| 31 octombrie 2026 | Verificare suplimentară: multiplul capitalului tangibil plătit lângă ROIC (Could) | propus de PM |
| 31 octombrie 2026 | Parametrii numerici din 4.10 sunt implicite de validat pe setul de aur, nu reguli din scrisori | propus de PM |

## 11. Conflicte semnalate

Am verificat harta funcționalităților și documentul de descoperire față de P1-P10 și față de rețetă. Trei puncte contrazic principiile sau se contrazic între ele; le-am rezolvat în acest PRD fără a redeschide deciziile din secțiunea 6 și le supun confirmării.

1. **Definiția lui „gata" cere „toate cele șase porți", dar v1 nu conține Poarta 1, Poarta 6 și Management** (faza 3, secțiunea 7). Luată literal, v1 nu poate fi niciodată „gata". Rezolvare: DoD v1 = porțile 2, 3, 4 (dovezi), 5 și Supraviețuirea; DoD era „propusă, de confirmat", deci nu este decizie închisă (întrebarea 4).
2. **P8 (zece ani sau marcat) și DoD (7 UE plus 3 BVB reconciliate) față de secțiunea 7, care pune „import istoric UE și BVB" în faza 4.** ESEF are 4-5 ani; fără import în v1, cele 10 companii europene ar fi „date insuficiente" pe toate porțile și DoD ar fi imposibilă. Rezolvare: import manual validat minim în faza 2 (SG-013), doar pentru setul de aur; tooling-ul asistat la scară rămâne în faza 4. Decizia din secțiunea 6 („istoricul european pre-2020 prin import validat") se respectă.
3. **Formula VI din secțiunea 5 nu actualizează valoarea terminală**: „+ OE_11/(r - g_terminal)" adună o valoare de la anul 10 la valori prezente, ceea ce la r = 10% umflă termenul terminal de circa 2,6 ori și contrazice P5 (conservator) și P2 (formule testate). Rezolvare: AC-G5-1 împarte valoarea terminală la (1 + r)^10; QA scrie testul cu rezultat cunoscut; Dev confirmă.

Cele mai apropiate cazuri verificate, fără conflict:
- **Pragul r = obligațiune + primă** (secțiunea 5) față de rețetă („fără primă de risc adăugată", 1992, 2000): nu e conflict dacă prima este unică, globală și fixă, un prag minim, nu o primă pe companie; riscul pe companie rămâne în marja cerută după categorie (1984, 1992). AC-G5-2 impune asta.
- **„3 moduri de a muri cu probabilități"** față de anti-rețetă (fără teatru de precizie, 1993): probabilitățile rămân, dar în trepte de 5%, marcate „estimare personală", și nu intră în niciun calcul în v1 (în faza 3 doar în dimensionare, cu fracție și plafon).
- **„Alertă" la Poarta 5 în v1** față de „alerte prin n8n" în faza 3 și P10: în v1 este o stare factuală în aplicație („preț sub prețul pe care l-aș plăti: da / nu"), fără notificări și fără formulare de acțiune.
- **Numerotarea fazelor** diferă între secțiunea 3 („Faza 1/2/3") și secțiunea 7 (fazele 2/3/4); PRD-ul folosește secțiunea 7.
