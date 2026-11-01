# Analizor Buffett-Munger: cerințe și descoperire (v0, 31 octombrie 2026)

Document de produs al utilizatorului (product owner: APT). Principiile pe care le operaționalizează sunt în recipe.md. Limba documentelor de produs: română, cu diacritice, fără cratime lungi (em dash). Limba interfeței: engleză ca limbă principală, română disponibilă.

## 1. Viziunea
Un instrument care ia orice companie listată și o trece prin cele șase teste din rețetă, cu fiecare cifră trasabilă până la raportul financiar din care vine, cu formula vizibilă și cu judecățile umane separate clar de fapte. Rezultatul: verdict pe fiecare poartă (trece, pică, necesită judecată, date insuficiente), interval de valoare intrinsecă estimat conservator, „prețul pe care l-aș plăti" și un dosar de decizie versionat.
Pentru cine: investitorul care face el însuși munca de citit și vrea partea mecanică corectă, reproductibilă și rapidă.
Ce nu este: nu este un screener cu scor compozit; nu dă sfaturi de cumpărare; nu înlocuiește cititul rapoartelor; nu prezice piața.

## 2. Principiile de acuratețe (nenegociabile, devin criterii de acceptare)
1. Proveniență pe fiecare cifră (sursa, perioada fiscală, eticheta XBRL sau pagina, data extragerii, link). O cifră fără proveniență nu se afișează.
2. Formula vizibilă, în pagină, cu intrările; fiecare formulă are test automat cu rezultat cunoscut.
3. Fapte separate de judecăți: fapt (din raport), calcul (din formulă), judecată (om, sau propusă de AI și confirmată de om). O judecată nu trece o poartă singură.
4. Niciun substitut tăcut: lipsă sau „necesită verificare", fără estimări sau interpolări nemarcate.
5. Ipoteze conservatoare, fixate și vizibile; orice modificare = „scenariu", nu „valoare".
6. Reproductibilitate: analize versionate cu date și surse înghețate.
7. Sursa primară bate vendorul (EDGAR, ESEF adevăr; vendori pentru prețuri și verificare încrucișată; divergențe afișate).
8. Zece ani sau marcat: fără zece ani, poarta nu trece, afișează „date insuficiente".
9. Erorile sunt vizibile: jurnal al problemelor de date pe companie.
10. Limbaj de fapte, nu de recomandări (fără „cumpără/vinde").

## 3. Harta funcționalităților (module, ce calculează softul, ce cere de la om, faza)
- Poarta 2 (înțelegi afacerea): stabilitatea pe 10 ani a veniturilor, marjelor și câștigurilor proprietarului ca indiciu; omul scrie descrierea pe 10 ani (obligatoriu), 3 moduri de a muri cu probabilități, paragraful de motivare. Faza 1.
- Poarta 3 (randamente pe capital): ROIC tangibil 10 ani, ROIC incremental 5/10 ani, câștigurile proprietarului, capex/vânzări, conversie în numerar, identitatea creșterii, categoria excelent/bun/groaznic cu praguri explicite. Faza 1.
- Supraviețuire: datorie netă/OE, acoperirea dobânzilor, scadențe, test de stres definit de utilizator. Faza 1.
- Poarta 4 (moat): dovezi cantitative (persistența ROIC, marja brută, preț vs inflație unde există), tendințe pe 5 ani, listă de surse de moat cu dovezi; omul decide tipul, direcția, durabilitatea; cotă de piață și retenție introduse cu sursă. Faza 1 dovezi, faza 2 draft AI cu citări.
- Management: testul dolarului pe 5 ani, preț mediu al răscumpărărilor vs valoare, evoluția numărului de acțiuni, deprecieri de achiziții, proprietatea insiderilor și compensația din proxy (extrase AI cu citare). Faza 2.
- Poarta 5 (preț sub valoare): DCF pe OE cu ipoteze fixe și vizibile, DCF invers, randamentul câștigurilor vs obligațiune, marja cerută după categorie, „prețul pe care l-aș plăti", alertă. Faza 1.
- Poarta 6 (păstrezi cât țin faptele): dosar de decizie versionat, re-subscriere anuală cu diff, declanșatoare de vânzare, calculator de schimbare cu impozit, jurnal de greșeli. Faza 2.
- Poarta 1 (portofoliu): poziții, cost, look-through, concentrare, Kelly fracționat cu plafon 40%. Faza 2.
- Cadența: digest săptămânal/lunar al schimbărilor în afaceri, memento anual, alerte de preț prin n8n (email, Slack). Faza 2-3.
- Screening de univers: rulare nocturnă a porților 3 și 5 pe S&P 500, Stoxx 600, BVB. Faza 3.
- Export: CSV (faza 1), memoriu PDF pe companie (faza 2).

## 4. Surse de date
- SEC EDGAR XBRL companyfacts (API și export în bloc): SUA, standardizat din 2009; gratuit; 10 cereri/s; etichete proprii la unele companii, cere normalizare cu validare și jurnal de excepții.
- SEC EDGAR documente (10-K, 10-Q, DEF 14A, 13F): text; extragere AI cu citare obligatorie.
- filings.xbrl.org (ESEF, XBRL International): emitenți UE inclusiv România, din exercițiul 2020-2021; gratuit, API JSON; doar 4-5 ani istoric; IFRS cu extensii; istoricul anterior din PDF, validat manual.
- BVB și rapoartele emitenților români: fără API pentru fundamentale; import asistat, 20-30 emitenți prioritari.
- FRED: Treasury 10 și 30 ani, inflație SUA; gratuit, cheie API.
- BCE Data Portal, BNR: randamente euro și lei, cursuri.
- Prețuri: EOD Historical Data (global, inclusiv BVB) sau Polygon (SUA); comercial; licență de uz personal.
- Yahoo Finance: neoficial, doar verificare manuală.
- Vendori de fundamentale (Financial Modeling Prep, EODHD, Intrinio): verificare încrucișată, nu adevăr.
- Morningstar, GuruFocus: fără API; cel mult link extern.
- Nu se obțin fiabil: cota de piață, volumul fizic, retenția, puterea de preț directă; rămân judecăți cu dovezi.

## 5. Formulele motorului (fiecare cu sursa și test cu rezultat cunoscut)
- OE = profit net + amortizări/deprecieri + alte cheltuieli fără numerar, minus capex de întreținere, minus creșterea capitalului de lucru (1986). Capex de întreținere: implicit min(capex, amortizare); alternativ Greenwald; ambele afișate, alegerea marcată.
- ROIC tangibil = NOPAT / (capital de lucru net + imobilizări nete + alte active operaționale, minus numerar excedentar); NOPAT = profit operațional × (1 minus rata efectivă). Fond comercial exclus pentru calitate, inclus în varianta „pe prețul plătit" (1983, 2017).
- ROIC incremental = ΔNOPAT/Δcapital investit pe 5 și 10 ani (2007).
- Identitatea creșterii: g = rata de reinvestire × ROIC, comparat cu creșterea observată (1992, 2000).
- ROE pe capital de început de an, lângă creșterea EPS, cu avertisment (1977).
- Predictibilitate: coeficient de variație al OE pe 10 ani, ani cu pierdere, abaterea veniturilor de la trend; praguri de validat; fără stele.
- Categoria afacerii (2007): excelent ROIC incremental >30% și capex/vânzări mic; bun între costul capitalului +5 puncte și 30%; groaznic sub costul capitalului cu capital în creștere; praguri de validat pe setul de aur.
- Supraviețuire: datorie netă/OE; EBIT/dobânzi; scadențe 5 ani; test de stres definit de utilizator (1990, 2017).
- VI = Σ OE_t/(1+r)^t pe 10 ani + OE_11/(r − g_terminal); r = randamentul obligațiunii lungi + prima aleasă (implicit prag total 10%); g primii ani ≤ CAGR istoric OE; g_terminal 2-3%; rezultat ca interval (1992, 2000).
- DCF invers: g care egalează prețul (2000).
- Marja de siguranță: preț/VI; cerută 30-50% pentru afacere, 15-25% pentru franciză; prețul pe care l-aș plăti = VI × (1 − marja).
- Randamentul câștigurilor (OE/preț) vs randamentul la 10 ani (FRED/BCE/BNR).
- Testul dolarului: Δcapitalizare 5 ani / profituri reținute 5 ani ≥ 1, cu avertisment și varianta pe 10 ani (1983).
- Răscumpărări: preț mediu plătit vs VI la acea dată (2011, 2016).
- Look-through: Σ cotă × profit net (1990, 1991).
- Schimbare cu impozit: se ține dacă (1 − t·g)(1+r2)^n < (1+r1)^n (1989).
- Dimensionare: f = (p − (1−p)/b) × fracție (0,25-0,5), plafon 40% (1966, Munger 1994).

## 6. Decizii luate la 31 octombrie 2026
- Utilizatori: product owner plus câțiva parteneri; multi-utilizator simplu de la început, fără facturare; comercialul se poate adăuga mai târziu.
- Piețe v1: SUA plus UE (ESEF), inclusiv BVB; istoricul european pre-2020 prin import validat.
- Adevărul datelor: surse primare (EDGAR, ESEF); vendori doar pentru prețuri și verificare încrucișată.
- Buget date: până la 200 EUR/lună: prețuri și acțiuni în circulație de la un vendor global cu BVB (EODHD sau similar), plus un vendor de fundamentale exclusiv pentru verificare încrucișată automată.
- Judecăți calitative: AI propune din rapoarte cu citări verificate automat, omul confirmă; AI nu poate trece o poartă; draftul rămâne marcat „propus de AI".
- Model AI: doar Claude API; fără model local (Ollama a fost eliminat).
- Formă: aplicație web responsivă (telefon și desktop).
- Găzduire: primele iterații local sau pe Mac Mini (M4, 24 GB, rulează deja n8n), apoi VPS/cloud. Consecință: totul containerizat de la început (Docker Compose, PostgreSQL, fără dependențe macOS), mutarea = copiere.
- Stivă: Python (FastAPI, Arelle sau edgartools, PostgreSQL) pentru ingestie și motorul de formule; TypeScript (Next.js sau SvelteKit) pentru interfață; planificator de joburi.
- Cod: GitHub, repo nou (contul GitHub al utilizatorului: pusoiuandrei; organizație de decis); backlog și QA în Jira, proiect separat.
- Rămân pe recomandări implicite: limba (EN principal, RO disponibil), portofoliu real în faza 2, alerte prin n8n în faza 2, screening de univers în faza 3, univers la cerere în v1.
- Definiția lui „gata" pentru v1 (propusă, de confirmat): 20 de companii din setul de aur (10 SUA, 7 UE, 3 BVB) trec prin toate cele șase porți cu fiecare cifră reconciliată la raport; QA recalculează independent din rapoartele brute și obține aceleași rezultate; o persoană nouă înțelege un verdict fără explicații; niciun număr fără proveniență în interfață.

## 7. Echipa de agenți și procesul
- PM: PRD, criterii de acceptare, prioritizare, jurnal de decizii; poate bloca o cerință care contrazice secțiunea 2.
- UX: fluxuri, wireframes telefon și desktop, limbaj vizual fapt/calcul/judecată, stări „date insuficiente"; poate bloca un ecran cu cifră fără proveniență.
- Dev: arhitectură (ingestie cu normalizare XBRL, motor de formule pur, API, interfață), ADR-uri, cod cu teste, jurnal de excepții; poate bloca o sursă necitabilă la nivel de cifră.
- QA: independent de Dev, nu vede codul înainte de a scrie testele; strategie, set de aur, al doilea cititor, raport „trece/nu trece"; poate bloca orice.
- Straturi de QA: teste unitare cu rezultate din scrisori (See's 1972/2007, FlightSafety, aritmetica 1989, Wells Fargo 1990); reconciliere la raport cu toleranță de rotunjire; al doilea cititor; teste de proprietate; regresie pe setul de aur; verificarea citărilor AI; teste UI și de înțelegere; prospețime și integritate a datelor.
- Faze: 0 descoperire (făcută); 1 fundație (PRD v1, fluxuri și wireframes, arhitectură și spike de date pe 5 companii reconciliate manual, strategia de test și setul de aur; ieșire: review cu product owner); 2 versiunea 1 (porțile 2, 3, 4 dovezi, 5 și supraviețuirea, SUA plus UE, proveniență completă, export CSV; ieșire: definiția lui „gata", raport QA trece); 3 proprietar (management, dosar versionat, portofoliu, alerte n8n, PDF); 4 univers (screening nocturn, import istoric UE și BVB).
- Gata la nivel de story: cod + teste + proveniență verificată în interfață + criterii de acceptare bifate de PM + semnătura QA.

## 8. Riscuri
Normalizarea XBRL (etichete proprii); istoric european sub 10 ani; date BVB fără API; licențe de date; falsa precizie a DCF; AI care inventează judecăți; construit prea mult (v1 = porțile 3 și 5 impecabile pe 20 de companii); zonă reglementată (fără „cumpără/vinde"); derivă față de metodă (secțiunea 2 ca listă de verificare la fiecare review).
