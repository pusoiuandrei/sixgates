# Arhitectura SixGates (faza 1, 31 octombrie 2026)

Document tehnic al echipei Dev pentru tab-ul de arhitectură. Respectă deciziile din secțiunea 6 a requirements_v0 și operaționalizează principiile P1 la P10. Codul spike-ului (secțiunile 3, 4 și 8) este în `spike/`, cu README în engleză.

## 1. Decizii de arhitectură

Fiecare decizie are context, decizie, alternative și consecințe; numerotarea se folosește în Jira.

### ADR-1: monorepo

Context: trei componente (serviciu Python, interfață TypeScript, infrastructură Docker), echipă mică, contracte API care se schimbă des.

Decizie: un singur repo GitHub, `sixgates`: `api/` (FastAPI, ingestie, normalizare, motor), `web/` (Next.js), `infra/` (Compose, Caddyfile), `fixtures/` (setul de aur), `docs/adr/`.

Alternative: două repo-uri cu un pachet de tipuri partajat. Respins: costul sincronizării contractelor depășește beneficiul separării la 2 la 5 utilizatori.

Consecințe: un singur CI (pytest, mypy, ruff, tsc, eslint, Playwright) și un singur tag de versiune; schema OpenAPI alimentează tipurile TypeScript, deci interfața nu poate afișa un câmp inexistent în API.

### ADR-2: serviciul Python (FastAPI) pentru ingestie, normalizare și motor

Context: sursele primare sunt XBRL (companyfacts, inline XBRL din 10-K, xBRL-JSON din ESEF); formulele cer teste cu rezultate cunoscute.

Decizie: pachetul `sixgates` cu patru module cu dependențe într-un singur sens: `ingest` (descărcare, stocare brută, manifest) → `normalize` (hartă de concepte, selecție pe exercițiu, suprascrieri per emitent, jurnal de probleme) → `engine` (funcții pure, versionate, fără I/O) → `api`. Procesele `api` (uvicorn) și `worker` (planificatorul) rulează același cod în două containere. Biblioteca XBRL: `edgartools` pentru EDGAR (instanțe inline XBRL, documente) și parsare proprie a xBRL-JSON pentru ESEF; Arelle doar ca validator opțional al pachetelor ESEF.

Alternative: Arelle ca unic parser (greu, lent, API instabil); ETL în SQL, unde logica de selecție ar fi mai greu de testat.

Consecințe: motorul nu știe de baza de date; orice calcul se reproduce dintr-un CSV (secțiunea 7); `mypy --strict` pe `engine` și `normalize`.

### ADR-3: interfața în Next.js

Context: aplicație web responsivă, EN cu RO, client subțire al API-ului, întreținere pe termen lung.

Decizie: Next.js (App Router, TypeScript, Tailwind, `output: "standalone"`), `next-intl` pentru i18n, TanStack Table. Justificare în cinci linii: (1) cel mai mare ecosistem și cea mai bogată documentație, deci cel mai ușor de întreținut sau de predat; (2) se găzduiește singur în Docker, fără Vercel; (3) i18n și rutare mature, necesare din prima zi; (4) componente de tabel, formular și dialog standard și accesibile; (5) regula care îl ține „plictisitor”: interfața nu accesează baza de date și nu are logică de domeniu în server actions, ci doar apeluri către FastAPI cu tipuri generate din OpenAPI.

Alternative: SvelteKit (mai puțin cod, bundle mai mic, ecosistem mai mic). Respins la limită: simplitatea nu compensează riscul de ecosistem pentru un produs care trebuie să trăiască ani.

Consecințe: componente server doar pentru schelet și autentificare; ecranele cu cifre sunt componente client; proveniența vine în același răspuns cu cifra.

### ADR-4: PostgreSQL ca unic depozit

Decizie: PostgreSQL 16 cu trei scheme: `core` (entity, filing, filing_text, fact, concept_map, concept_override, price, assumption_set), `analysis` (derived_value, judgment, analysis, scenario, user) și `ops` (ingestion_run, data_issue, download_manifest, ai_usage, audit_log). Textul rapoartelor pentru citări stă în `filing_text` (nu pe disc), ca o singură copie de rezervă să conțină totul; fișierele brute stau în `raw/` cu sha256 în `download_manifest`, deci sunt verificabile și regenerabile.

Alternative: SQLite (fără utilizatori concurenți); DuckDB (inutil la acest volum).

Consecințe: migrații Alembic; indexuri pe `(entity_id, canonical_concept, period_end)`; toate ștergerile sunt logice (`superseded_by`, `resolved_at`).

### ADR-5: planificatorul de joburi: APScheduler în containerul worker

Context: joburi puține și previzibile: ingestie nocturnă, verificarea zilnică a noilor depuneri, prețuri săptămânale, FRED zilnic, draft-uri AI la cerere, copii de rezervă.

Decizie: APScheduler într-un proces `worker` separat, cu starea rulărilor în `ops.ingestion_run` și lacăte consultative PostgreSQL (`pg_advisory_lock`) ca un job să nu ruleze de două ori. Fără Redis, fără broker.

Alternative: Celery plus Redis (robust, dar încă două procese de monitorizat pentru 2 la 5 utilizatori); container cron (simplu, dar fără stare, reîncercări sau declanșare din interfață). APScheduler păstrează același cod, permite `POST /ingest` din API și istoric în baza de date.

Consecințe: joburi idempotente; fiecare job scrie un rând în `ingestion_run`; pe VPS pot rula doi workeri fără conflict.

### ADR-6: Docker Compose pe Mac Mini și pe VPS

Decizie: un `docker-compose.yml` de bază cu `db` (postgres:16), `api`, `worker`, `web`, `proxy` (Caddy) și `backup`, plus două fișiere de suprapunere:

| Serviciu | Mac Mini | VPS |
|---|---|---|
| proxy | Caddy cu TLS intern, acces doar din rețeaua locală și Tailscale | Caddy cu Let's Encrypt, doar 80/443 expuse |
| db | volum local, 2 GB RAM | volum local, 4 GB RAM |
| backup | pg_dump zilnic pe disc extern plus rclone către B2 | același script |
| resurse | fără limite | limite de memorie pe container |

Imagini `linux/arm64` și `linux/amd64`, fără dependențe de macOS; n8n rămâne în afara rețelei Compose și apelează API-ul prin HTTP (faza 2). Mutarea pe VPS = `pg_dump`, copierea `raw/`, `docker compose up`.

### ADR-7: secrete și autentificare

Decizie: conturi create de administrator (fără înregistrare publică), parole Argon2id, sesiuni în cookie `HttpOnly; Secure; SameSite=Strict` cu expirare 30 de zile, limită de încercări; roluri `admin` (utilizatori, ingestie) și `analyst`. Nicio rută fără sesiune, inclusiv API-ul. Secretele (chei EODHD, Claude, FRED, parola bazei) stau într-un `.env` necomis montat ca Docker secrets; rotația este o schimbare de fișier și un restart. Pe Mac Mini accesul din afara casei se face prin Tailscale, nu prin port forwarding; pe VPS, Caddy cu TLS și opțional o listă de IP-uri permise.

Alternative: OAuth cu Google (dependență externă pentru 5 utilizatori); Caddy basic auth (nu știe de utilizatori). Consecințe: fiecare judecată și analiză înghețată poartă `author_user_id`; `ops.audit_log` reține cine a confirmat ce.

### ADR-8: Claude API pentru draft-uri cu citări verificate

Context: decizia 6: AI propune din rapoarte cu citări verificate automat, omul confirmă; AI nu poate trece o poartă.

Decizie: modulul `ai_drafts` are un singur tip de apel: pentru (`entity_id`, poartă, câmp) construiește contextul din `filing_text` (10-K, DEF 14A sau raportul ESEF, text curat cu offseturi stabile), cere modelului JSON `{claims: [{text, quotes: [{filing_id, quote}]}]}` la temperatură 0, cu prompt caching pe textul raportului. Verificarea: fiecare `quote` trebuie să se regăsească prin potrivire exactă de subșir în `filing_text` (după normalizarea spațiilor albe și a ghilimelelor tipografice); la potrivire se înregistrează `char_start`, `char_end`, `verified = true`. Draftul se salvează ca `judgment` cu `ai_draft = true` și `status = propus_de_AI` numai dacă toate citările sunt verificate; altfel nu se salvează, iar eșecul intră în `data_issue` (info, cu citările eșuate). Un `judgment` cu `status = propus_de_AI` nu intră niciodată în verdictul unei porți; confirmarea de către om creează o versiune nouă cu `ai_draft = false` și autor, păstrând citările.

Consecințe: `ops.ai_usage` reține tokeni și cost pe apel, cu plafon lunar; modelul nu primește cifre calculate de motor.

### ADR-9: observabilitate

Decizie: jurnale structurate JSON (`structlog`) cu `run_id`, `entity_id`, `filing_id` pe fiecare linie, rotație prin driverul Docker `json-file`; tabelele `ops.ingestion_run` și `ops.data_issue` sunt afișate în interfață (pagina companiei și o pagină de administrare), conform P9. Fără Prometheus în v1; `GET /health` verifică baza, ultima rulare reușită și vechimea prețurilor. Fiecare cifră se urmărește până la rularea care a produs-o prin `fact.run_id`.

### ADR-10: copii de rezervă

Decizie: `pg_dump --format=custom` zilnic la 03:00, 30 de zile local și 12 luni lunar; `rclone crypt` către Backblaze B2 sau Hetzner Storage Box; `raw/` sincronizat săptămânal. Test de restaurare lunar, documentat, care verifică și că o analiză înghețată se recalculează identic (secțiunea 7).

### ADR-11: estimare de cost (plafon 200 EUR pe lună)

| Element | Furnizor | Cost lunar | Observații |
|---|---|---|---|
| Rapoarte SUA | SEC EDGAR | 0 EUR | User-Agent cu contactul real al proprietarului, sub 10 cereri pe secundă |
| Rapoarte UE și BVB | filings.xbrl.org | 0 EUR | acoperire parțială, secțiunea 3 |
| Randamente | FRED, BCE, BNR | 0 EUR | chei gratuite |
| Prețuri și acțiuni în circulație, inclusiv BVB | EOD Historical Data | 20 la 60 EUR | listă de prețuri de verificat la contractare; licență personală |
| Fundamentale pentru verificare încrucișată | EODHD sau FMP | 0 la 40 EUR | doar divergențe afișate |
| Claude API | Anthropic | 10 la 40 EUR | estimare mai jos |
| Găzduire | Mac Mini, apoi VPS (Hetzner CX32 sau similar) | 0, apoi 10 la 20 EUR | |
| Copii de rezervă | B2 sau Storage Box | 2 la 5 EUR | sub 50 GB |
| Total | | 35 la 165 EUR | sub plafon și la VPS |

Estimarea Claude pe companie: un 10-K are 80 la 150 de mii de tokeni; 3 la 5 draft-uri pe același context cu prompt caching costă 0,8 la 2 EUR pe companie și rulare la prețuri de clasă Sonnet; la 20 de companii cu re-subscriere anuală rezultă 10 la 40 EUR pe lună, cu plafon de 50 EUR în `ops.ai_usage`.

## 2. Modelul de date

Modelul operaționalizează P1 (proveniență), P2 (formulă vizibilă), P3 (fapt, calcul, judecată separate), P4 (lipsă marcată), P5 (ipoteze fixate, modificare = scenariu) și P6 (reproductibilitate). Trei tipuri de rânduri nu se amestecă niciodată: `fact` (din raport), `derived_value` (din formulă), `judgment` (om sau AI confirmat de om).

| Tabel | Rol | Câmpuri cheie |
|---|---|---|
| entity | emitentul | cik, lei, isin, ticker, market, name, fiscal_year_end, fiscal_year_convention, reporting_standard, currency |
| filing | raportul primar | accession sau esef_id, form, period_end, filed_at, source_url, raw_sha256, primary_document |
| filing_text | textul curat pentru citări | filing_id, text, normalization_version |
| fact | o cifră așa cum a fost depusă | entity_id, canonical_concept, source_concept, period_start, period_end, is_instant, value, unit, decimals, filing_id, frame, extracted_at, run_id, is_restated, superseded_by, selected |
| concept_map | regula de normalizare | canonical_concept, standard, candidates (ordine), fallbacks, components, absent_ok, notes, version |
| concept_override | excepția per emitent | entity_id, canonical_concept, fiscal_year_from, fiscal_year_to, source_concept, reason, evidence_filing_id, author_user_id |
| derived_value | rezultatul unei formule | entity_id, formula_id, formula_version, engine_version, period_end, value, unit, input_fact_ids[], assumption_set_id, assumptions_snapshot, computed_at, status, flags[] |
| judgment | text de om sau draft AI | entity_id, gate, field, text, author_user_id, ai_draft, citations (jsonb), status, version, supersedes_id |
| analysis | dosarul înghețat | entity_id, version, frozen_at, fact_snapshot_hash, derived_snapshot, judgments_snapshot, verdicts, author_user_id, engine_version, assumption_set_id |
| scenario | ipoteze modificate | analysis_id, overrides (jsonb), results (jsonb), author_user_id; nu scrie niciodată în derived_value |
| data_issue | jurnalul problemelor | entity_id, severity, concept, period_end, description, detected_at, run_id, resolved_at, resolution |
| price | cotația | entity_id, date, close, currency, source, shares_outstanding, fetched_at |
| assumption_set | ipotezele fixe | name, version, values (jsonb), valid_from, notes |
| ingestion_run, user | rulări și conturi | source, started_at, finished_at, status, facts_written, issues_written; email, password_hash, role |

Statusurile `derived_value`: `ok`, `missing_input`, `not_applicable`, `flagged` (motiv în `flags`), `not_computed` (de exemplu fără sursă de preț). Statusurile `judgment`: `propus_de_AI`, `confirmat`, `respins`. `fact.selected` este adevărat pentru valoarea cea mai recent depusă a perioadei; cele vechi au `superseded_by` și rămân în tabel.

```sql
CREATE TABLE core.entity (
  id              bigserial PRIMARY KEY,
  cik             text UNIQUE,            -- SUA
  lei             text UNIQUE,            -- ESEF
  isin            text,
  ticker          text,
  market          text NOT NULL,          -- 'NASDAQ', 'NYSE', 'XPAR', 'BVB'
  name            text NOT NULL,
  fiscal_year_end text NOT NULL,          -- 'MM-DD'
  fiscal_year_convention text NOT NULL DEFAULT 'end_year',
  reporting_standard text NOT NULL,       -- 'us-gaap' | 'ifrs-full'
  currency        char(3) NOT NULL
);

CREATE TABLE core.filing (
  id              bigserial PRIMARY KEY,
  entity_id       bigint NOT NULL REFERENCES core.entity,
  filing_key      text NOT NULL UNIQUE,   -- accession SEC sau fxo_id ESEF
  form            text NOT NULL,          -- '10-K', '10-K/A', 'DEF 14A', 'ESEF-AR', 'MANUAL'
  period_end      date NOT NULL,
  filed_at        date NOT NULL,
  source_url      text NOT NULL,
  primary_document text,
  raw_sha256      char(64) NOT NULL
);

CREATE TABLE core.fact (
  id              bigserial PRIMARY KEY,
  entity_id       bigint NOT NULL REFERENCES core.entity,
  canonical_concept text,                 -- NULL dacă nu intră în hartă
  source_concept  text NOT NULL,          -- eticheta XBRL așa cum a fost depusă
  period_start    date,                   -- NULL pentru instant
  period_end      date NOT NULL,
  is_instant      boolean NOT NULL,
  fiscal_year     smallint,
  value           numeric(24,4) NOT NULL,
  unit            text NOT NULL,          -- 'USD', 'EUR', 'RON', 'shares'
  decimals        smallint,
  filing_id       bigint NOT NULL REFERENCES core.filing,
  frame           text,
  extracted_at    timestamptz NOT NULL,
  run_id          bigint NOT NULL,
  selected        boolean NOT NULL DEFAULT false,
  is_restated     boolean NOT NULL DEFAULT false,
  superseded_by   bigint REFERENCES core.fact,
  UNIQUE (entity_id, source_concept, unit, period_start, period_end, filing_id)
);
CREATE INDEX fact_lookup ON core.fact (entity_id, canonical_concept, period_end) WHERE selected;

CREATE TABLE core.concept_map (
  canonical_concept text NOT NULL,
  standard        text NOT NULL,
  kind            text NOT NULL,          -- 'duration' | 'instant'
  candidates      text[] NOT NULL,        -- sinonime, în ordine de prioritate
  fallbacks       text[] NOT NULL DEFAULT '{}',
  components      text[][] NOT NULL DEFAULT '{}',
  absent_ok       boolean NOT NULL DEFAULT false,
  notes           text,
  version         smallint NOT NULL,
  PRIMARY KEY (canonical_concept, standard, version)
);

CREATE TABLE analysis.derived_value (
  id              bigserial PRIMARY KEY,
  entity_id       bigint NOT NULL REFERENCES core.entity,
  formula_id      text NOT NULL,
  formula_version text NOT NULL,
  engine_version  text NOT NULL,
  period_end      date,
  value           numeric(24,6),
  unit            text NOT NULL,
  input_fact_ids  bigint[] NOT NULL,
  assumption_set_id bigint REFERENCES core.assumption_set,
  assumptions_snapshot jsonb NOT NULL,
  computed_at     timestamptz NOT NULL,
  status          text NOT NULL CHECK (status IN ('ok','missing_input','not_applicable','flagged','not_computed')),
  flags           text[] NOT NULL DEFAULT '{}',
  detail          jsonb NOT NULL DEFAULT '{}'
);

CREATE TABLE analysis.judgment (
  id              bigserial PRIMARY KEY,
  entity_id       bigint NOT NULL REFERENCES core.entity,
  gate            smallint NOT NULL CHECK (gate BETWEEN 1 AND 6),
  field           text NOT NULL,
  text            text NOT NULL,
  author_user_id  bigint,                 -- NULL doar pentru draft AI
  ai_draft        boolean NOT NULL,
  citations       jsonb NOT NULL,         -- [{filing_id, quote, char_start, char_end, verified}]
  status          text NOT NULL CHECK (status IN ('propus_de_AI','confirmat','respins')),
  version         smallint NOT NULL DEFAULT 1,
  supersedes_id   bigint REFERENCES analysis.judgment,
  created_at      timestamptz NOT NULL DEFAULT now(),
  CHECK (ai_draft = false OR status <> 'confirmat')
);

CREATE TABLE analysis.analysis (
  id              bigserial PRIMARY KEY,
  entity_id       bigint NOT NULL REFERENCES core.entity,
  version         smallint NOT NULL,
  frozen_at       timestamptz NOT NULL,
  fact_snapshot_hash char(64) NOT NULL,   -- sha256 peste faptele selectate, serializate canonic
  derived_snapshot jsonb NOT NULL,
  judgments_snapshot jsonb NOT NULL,
  verdicts        jsonb NOT NULL,         -- {gate: 'trece'|'pică'|'necesită judecată'|'date insuficiente'}
  engine_version  text NOT NULL,
  assumption_set_id bigint NOT NULL REFERENCES core.assumption_set,
  author_user_id  bigint NOT NULL,
  UNIQUE (entity_id, version)
);
```

Valorile setului de ipoteze v1: `hurdle_rate` 0,10; `terminal_growth` 0,02 la 0,03; `explicit_years` 10; `growth_cap_high` 0,10; `growth_cap_low` 0,05; `growth_low_fraction` 0,5; `margin_business` 0,30 la 0,50; `margin_franchise` 0,15 la 0,25; `cost_of_capital` 0,10; `excellent_incremental_roic` 0,30; `good_spread_over_cost` 0,05; `low_capex_to_sales` 0,05; `maintenance_capex_method` `min_capex_da` (alternativa `greenwald` afișată); `other_noncash_added_back` fals; `tax_rate_clamp` 0 la 0,5. Orice valoare diferită la calcul creează un `scenario`, niciodată un `derived_value`.

## 3. Ingestia și normalizarea XBRL

### SEC EDGAR companyfacts (SUA)

1. Descărcare: `companyfacts/CIK##########.json` și `submissions/CIK##########.json`, cu antetul `User-Agent` conținând numele și adresa reală de contact a proprietarului (politica de acces echitabil a SEC) și cel mult 5 cereri pe secundă. Fișierul brut merge în `raw/sec/` cu sha256 în `download_manifest`; o schimbare de hash declanșează reprocesarea.
2. Index: din `submissions` se rețin 10-K și 10-K/A cu `accession`, `filingDate`, `reportDate`, `primaryDocument`.
3. Selecția anuală: doar formularele 10-K și 10-K/A; durate de 340 la 380 de zile (exerciții de 52 sau 53 de săptămâni; Apple FY2017 are 371 de zile) sau instante la data de închidere. Câmpurile `fy` și `fp` descriu depunerea, nu faptul: un 10-K din 2024 conține comparativele din 2023 și 2022 cu `fy = 2024`. Eticheta exercițiului se obține din harta „data de închidere → fy al depunerii în care acea dată a fost perioada focală”; discrepanțele față de anul calendaristic se jurnalizează.
4. Duplicate între depuneri: pentru același (etichetă, unitate, perioadă) câștigă valoarea cea mai recent depusă; cele vechi primesc `superseded_by`. Dacă valoarea diferă dincolo de precizia comună (Moody's a trecut în 2019 de la 0,1 milioane la 1 milion, deci 4.204,1 și 4.204 sunt aceeași cifră), faptul nou este `is_restated` și ambele valori intră în `data_issue`. `frame` se reține, dar nu decide selecția.
5. Harta de concepte: sinonime în ordine de prioritate; dacă mai multe sinonime există în același exercițiu, câștigă cel mai recent depus, iar o diferență dincolo de rotunjire marchează valoarea `ambiguous` (severitate ridicată). Fără sinonime, se folosesc etichete de rezervă mai largi sau mai înguste (`ProfitLoss` pentru `NetIncomeLoss`), notate; apoi suma componentelor, cu `partial_sum` la componentă absentă. Nimic nu se interpolează.
6. ASC 606: `RevenueFromContractWithCustomerExcludingAssessedTax` este primul sinonim, urmat de `Revenues`, `SalesRevenueNet`, `SalesRevenueGoodsNet`. Momentul diferă pe emitent: Apple a trecut la eticheta nouă în 10-K-ul FY2019 (FY2017 și FY2018 retratate sub ea), Moody's în FY2018, Coca-Cola niciodată (`Revenues`). Schimbarea de etichetă între exerciții se jurnalizează.
7. Etichete proprii: companyfacts nu expune etichetele proprii (`ko:`, `aapl:`, `mco:`) și nici `decimals`. Un concept absent devine `lipsă` plus `data_issue`; rezolvarea este un rând în `concept_override` către o etichetă din instanța inline XBRL a 10-K-ului (de unde se citește și `decimals`), cu motiv și raport-dovadă. Spike-ul a găsit 22 (Apple), 39 (Coca-Cola) și 35 (Moody's) etichete proprii fără dimensiuni la data bilanțului.
8. Reutilizarea unei etichete pentru linii diferite: Apple a folosit `DepreciationDepletionAndAmortization` pentru amortizarea imobilizărilor corporale din note (9.200 în FY2015) și, din 10-K-ul FY2018, pentru linia completă din fluxul de numerar (11.257 în FY2015, sub altă etichetă). „Ultimul raport câștigă” nu rezolvă singur cazul; verificarea de ambiguitate îl semnalează și suprascrierea îl rezolvă cu dovada din situația fluxurilor de numerar.
9. Splituri: comparativele retratate doar în rapoartele ulterioare amestecă numărul de acțiuni dinainte și după split (Apple: 5,25 miliarde în FY2017, 20 de miliarde în FY2018). Salturile peste 1,5x marchează seria pe acțiune inutilizabilă până la o tabelă de factori de split cu sursă.

### ESEF prin filings.xbrl.org (UE, inclusiv România)

1. Listare: `GET /api/entities/{LEI}/filings` (JSON:API) dă `fxo_id`, `period_end`, `country`, `published`, `json_url`, `report_url`, `package_url`, `sha256`. Un emitent poate avea mai multe depuneri pentru același exercițiu (versiuni lingvistice, al doilea OAM pentru listări secundare: OMV Petrom apare sub RO și GB); faptele sunt identice, dar fiecare depunere este un `filing` separat și duplicatele se jurnalizează.
2. Descărcare: xBRL-JSON (OIM) de la `json_url`; raportul XHTML de la `report_url` pentru text și citări; pachetul doar pentru validarea cu Arelle.
3. Parsare OIM: se rețin faptele numerice fără dimensiuni explicite (totalurile din situațiile primare); perioadele OIM se termină la miezul nopții următoare (`2025-01-01T00:00:00` înseamnă 31 decembrie 2024); `decimals` este disponibil; moneda emitentului nu se convertește niciodată.
4. Harta `ifrs-full`: aceeași mecanică. Specific ESEF: etichetarea obligatorie acoperă situațiile primare așa cum le prezintă emitentul, deci liniile metodei apar des ca extensii proprii (LVMH: profit operațional, amortizare, investiții operaționale, costul datoriei nete; OMV Petrom: investiții în imobilizări) sau lipsesc (LVMH nu etichetează `ProfitLossBeforeTax`; se afișează identitatea profit plus impozit, marcată `derived_identity`). Prefixul extensiilor se schimbă de la an la an (`omvpetromsa` în 2021, `omvpetrom` în 2022), deci suprascrierile se potrivesc pe numele local. Semnul poate fi inconsecvent între ani (LVMH a raportat interesele minoritare cu semn opus în comparativele din 2024 față de 2023).
5. Istoric: filings.xbrl.org începe cu exercițiul 2020 sau 2021 (primul raport conține comparativul anului anterior): LVMH are 4 depuneri (FY2021 la FY2024), deci 5 exerciții; OMV Petrom doar FY2021 și FY2022, deci 3 exerciții. Anii anteriori intră prin import manual validat (PDF), ca `fact` cu `filing.form = 'MANUAL'`, `source_url` către PDF și validare cu doi cititori, marcate vizibil în interfață.
6. Specific BVB: la 31 octombrie 2026, filings.xbrl.org listează 39 de emitenți români cu 115 depuneri, toate pentru FY2021 și FY2022; nimic pentru FY2023 și FY2024 (Franța are 194 și 192 de depuneri pentru acei ani, Olanda 116 și 121, Germania zero în toți anii). OMV Petrom, Romgaz, Transgaz, Electrica, Nuclearelectrica, BRD și Transelectrica sunt prezente; Hidroelectrica (listată în 2023) lipsește. Concluzie: sursa ESEF se completează cu pachetele ESEF publicate de emitenți pe paginile de relații cu investitorii sau pe BVB, importate manual în `raw/` (același parser), și cu import validat din PDF pentru anii dinainte de 2020. Un OAM românesc cu acces programatic rămâne de verificat (secțiunea 9).

### Randamente și prețuri

FRED: seria DGS10 (CSV sau API cu cheie), stocată ca serie zilnică; ultima valoare este referința pentru prag (4,98% la 29 octombrie 2026 în spike). BCE Data Portal pentru randamentul euro pe 10 ani, BNR pentru lei și cursuri, toate ca serii cu sursă și dată. Prețuri: EODHD (EOD, acțiuni în circulație, inclusiv BVB) în `price`; prețul este singura cifră care nu vine din raport și este etichetat ca atare. Vendorul de fundamentale servește doar comparația automată: divergențele peste 1% devin `data_issue`, fără să schimbe vreo valoare.

### Harta de concepte v1

| Concept canonic | us-gaap (prioritate) | ifrs-full | Regulă și observații |
|---|---|---|---|
| revenue | RevenueFromContractWithCustomerExcludingAssessedTax, Revenues, SalesRevenueNet, SalesRevenueGoodsNet | Revenue, RevenueFromContractsWithCustomers | sinonime; ASC 606 la momente diferite |
| operating_income | OperatingIncomeLoss | ProfitLossFromOperatingActivities | ESEF: des extensie (LVMH) |
| pretax_income | IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest, ...MinorityInterestAndIncomeLossFromEquityMethodInvestments | ProfitLossBeforeTax | ESEF: identitate marcată dacă lipsește |
| income_tax | IncomeTaxExpenseBenefit | IncomeTaxExpenseContinuingOperations | |
| net_income | NetIncomeLoss; rezervă ProfitLoss | ProfitLossAttributableToOwnersOfParent; rezervă ProfitLoss | partea societății-mamă |
| d_and_a | DepreciationDepletionAndAmortization, DepreciationAndAmortization, DepreciationAmortizationAndAccretionNet; componente Depreciation + AmortizationOfIntangibleAssets | DepreciationAndAmortisationExpense, AdjustmentsForDepreciationAndAmortisationExpense; rezervă variantele cu deprecieri de valoare | ESEF: des lipsă sau amestecată |
| capex | PaymentsToAcquirePropertyPlantAndEquipment, PaymentsToAcquireProductiveAssets, PaymentsForCapitalImprovements | PurchaseOfPropertyPlantAndEquipmentIntangibleAssets...; componente PP&E + necorporale | ieșire pozitivă |
| cfo | NetCashProvidedByUsedInOperatingActivities; rezervă ...ContinuingOperations | CashFlowsFromUsedInOperatingActivities; rezervă CashFlowsFromUsedInOperations | |
| cash | CashAndCashEquivalentsAtCarryingValue; rezervă varianta cu numerar restricționat | CashAndCashEquivalents | strict |
| st_investments | componente (ShortTermInvestments sau OtherShortTermInvestments) + (MarketableSecuritiesCurrent sau AvailableForSaleSecuritiesCurrent sau MarketableSecurities) | CurrentFinancialAssetsAtFairValueThroughProfitOrLoss, OtherCurrentFinancialAssets | absent acceptat, semnalat |
| st_borrowings | NotesAndLoansPayable, NotesAndLoansPayableCurrent, ShortTermBorrowings, DebtCurrent; rezervă CommercialPaper | ShorttermBorrowings, CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings | Coca-Cola: patru etichete în zece ani |
| ltd_current | LongTermDebtCurrent, LongTermDebtAndCapitalLeaseObligationsCurrent | CurrentPortionOfLongtermBorrowings | |
| debt_long | LongTermDebtNoncurrent, LongTermDebtAndCapitalLeaseObligations; rezervă LongTermDebt | LongtermBorrowings, NoncurrentPortionOfNoncurrentBorrowings | leasingul IFRS 16 neinclus în v1 |
| interest_expense | InterestExpense, InterestExpenseBorrowings, InterestExpenseNonoperating; rezervă InterestExpenseDebt | InterestExpense; rezervă FinanceCosts | Apple nu mai raportează din FY2024 |
| equity | StockholdersEquity; rezervă varianta cu interese minoritare | EquityAttributableToOwnersOfParent; rezervă Equity | Moody's negativ FY2015 la FY2017 |
| goodwill, intangibles | Goodwill; IntangibleAssetsNetExcludingGoodwill cu componente trademarks + franchise rights + other | Goodwill; IntangibleAssetsOtherThanGoodwill | Apple nu mai raportează din FY2018; Coca-Cola sumă parțială din FY2024 |
| current_assets, current_liabilities | AssetsCurrent, LiabilitiesCurrent | CurrentAssets, CurrentLiabilities; rezervă variantele „other than held for sale” | |
| ppe_net | PropertyPlantAndEquipmentNet, varianta cu active din leasing financiar | PropertyPlantAndEquipment | |
| diluted_shares | WeightedAverageNumberOfDilutedSharesOutstanding | AdjustedWeightedAverageShares; rezervă WeightedAverageShares | ESEF: rar etichetat (OMV Petrom lipsă) |
| dividends_paid | PaymentsOfDividendsCommonStock, PaymentsOfDividends, varianta cu echivalente de dividend | DividendsPaidToEquityHoldersOfParentClassifiedAsFinancingActivities, DividendsPaidClassifiedAsFinancingActivities | |
| share_repurchases | PaymentsForRepurchaseOfCommonStock | PaymentsToAcquireOrRedeemEntitysShares | ESEF: des doar în situația capitalurilor |

### Cum se produce „date insuficiente”

Regula este funcția pură `ten_year_rule`, cu test. Un exercițiu este „complet” dacă toate conceptele necesare porții 3 (revenue, operating_income, pretax_income, income_tax, net_income, d_and_a, capex, cfo, cash, current_assets, current_liabilities, ppe_net) au status `ok`, `partial_sum`, `ambiguous` sau `derived_identity`, nu `missing`. Dacă cel mai lung șir de exerciții complete consecutive este sub 10, porțile 3 și 5 primesc verdictul „date insuficiente”, iar interfața afișează anii compleți și conceptele lipsă din anii incompleți. Un singur concept lipsă într-un an rupe șirul; `ambiguous` și `partial_sum` lasă poarta să se calculeze, dar apar cu avertisment lângă cifră. În spike: Apple, Coca-Cola și Moody's au 15 la 17 exerciții complete; LVMH zero (amortizarea lipsește în toți anii); OMV Petrom trei.

## 4. Motorul de formule

Principii: funcții pure, fără I/O, intrări tipate (`Fact(value, fact_id, unit)`), ieșire `Result(formula_id, version, value, unit, status, flags, inputs, detail)`. Versiunea formulei este semantică; orice schimbare de aritmetică incrementează versiunea majoră; motorul are propria versiune. Reguli: nicio împărțire la un capital tangibil nepozitiv (`flagged`, valoare nulă); unități diferite nu se amestecă (`unit_mismatch`); monede diferite nu se convertesc; ipotezele vin din `assumption_set`; orice valoare diferită creează un scenariu. Pseudocodul de mai jos este cel implementat în `spike/formulas.py` și testat.

```
maintenance_capex(capex, d_and_a, method):
  min_capex_da:  min(capex, d_and_a)                      # implicit, flag method:min_capex_da
  greenwald:     max(capex - ppe_to_sales_avg * max(delta_revenue, 0), 0)
  ambele variante se calculează și se afișează; alegerea este marcată

owner_earnings = net_income + d_and_a + other_noncash - maintenance_capex - delta_ncwc
  other_noncash lipsește în v1 (flag other_noncash:not_added_back)
  delta_ncwc lipsă în primul an disponibil (flag, nu se scade nimic)

ncwc = (current_assets - cash - st_investments) - (current_liabilities - st_borrowings - ltd_current)
tangible_invested_capital = ncwc + ppe_net (+ other_operating_assets, neincluse în v1)
  <= 0  -> status flagged, non_positive_tangible_capital
capital_on_price_paid = tangible_invested_capital + goodwill + intangibles

effective_tax_rate = income_tax / pretax_income; pretax <= 0 -> flagged; clamp 0..0,5 cu flag
nopat = operating_income * (1 - effective_tax_rate)
tangible_roic_t = nopat_t / tangible_invested_capital_(t-1)      # capital de început de an
incremental_return(n) = (nopat_t - nopat_(t-n)) / (capital_t - capital_(t-n)), n in {5, 10}
  delta_capital <= 0 -> flagged capital_did_not_grow, ambele delte afișate
reinvestment_rate = (capex - d_and_a + delta_ncwc) / nopat
growth_identity: g_implicit = reinvestment_rate * tangible_roic, lângă CAGR NOPAT observat pe 5 ani
capex_to_sales = capex / revenue; cash_conversion = cfo / net_income
net_debt = st_borrowings + ltd_current + debt_long - cash - st_investments
net_debt_to_oe = net_debt / owner_earnings (OE <= 0 -> flagged)
interest_coverage = operating_income / interest_expense
predictability = coeficient de variație al OE pe fereastră, ani cu pierdere
business_category_2007(incremental_roic_5y, capex_to_sales):
  > 30% și capex/vânzări < 5%                       -> excelent
  >= costul capitalului + 5 puncte                  -> bun   (FlightSafety: 31%, dar capital-intensiv)
  < costul capitalului                              -> groaznic
  profit în creștere cu capital neschimbat/scăzut   -> excelent (profit în creștere fără capital suplimentar)
  praguri marcate thresholds_to_validate

dcf_value(oe0, g, r, g_term, N) = sum_{t=1..N} oe0 (1+g)^t / (1+r)^t
                                + oe0 (1+g)^N (1+g_term) / (r - g_term) / (1+r)^N
intrinsic_value_range: jos = dcf(oe, min(0,5 CAGR, 5%), r, 2%, 10); sus = dcf(oe, min(CAGR, 10%), r, 3%, 10)
  CAGR negativ sau necunoscut -> g = 0 pe ambele căi, flag growth:none_assumed; OE <= 0 -> flagged
reverse_dcf: g astfel încât dcf(oe, g, r, g_term_mediu, 10) = capitalizarea (bisecție); fără preț -> not_computed
margin_of_safety = 1 - price / VI_jos; price_i_would_pay = VI_jos * (1 - marja), interval pe marja categoriei
one_dollar_test(5 ani) = (capitalizare_t - capitalizare_(t-5)) / sum(net_income - dividends_paid); fără preț -> not_computed
tax_deferral_1989(principal, n, t) = principal + (principal 2^n - principal)(1 - t)  vs  principal (2 - t)^n
switch_with_tax: se ține dacă (1 - t g)(1 + r2)^n < (1 + r1)^n
kelly_fraction = max(0, min((p - (1-p)/b) * fracție, 0,40))
```

Două observații din spike care cer o decizie a PM, nu o ipoteză a Dev: (a) formula VI din requirements_v0 secțiunea 5 scrie termenul terminal nediscontat; implementarea îl discontează cu `(1+r)^N`, altfel valoarea terminală ar fi de 2,6 ori mai mare la r = 10%; (b) termenul ΔWC an de an face OE volatil (Coca-Cola FY2017 negativ din reorganizarea îmbuteliatorilor, FY2024 și FY2025 cu variații de peste 50%); varianta fără ΔWC se calculează și se afișează, iar o regulă de normalizare (medie pe 3 ani) este de decis în faza 2.

## 5. API

Toate rutele cer sesiune; răspunsurile poartă `engine_version` și `assumption_set`. Prefix `/api/v1`.

| Rută | Metodă | Rol |
|---|---|---|
| /auth/login, /auth/logout, /auth/me | POST, POST, GET | sesiune |
| /entities?q= | GET | căutare după nume, ticker, CIK, LEI, ISIN |
| /entities/{id} | GET | fișa emitentului, ultima rulare, probleme deschise |
| /entities/{id}/ingest | POST | declanșează ingestia (admin), întoarce run_id |
| /entities/{id}/facts?concept=&from=&to= | GET | fapte canonice cu proveniență completă |
| /entities/{id}/derived?period= | GET | valori derivate cu intrări, formulă, versiune, status |
| /entities/{id}/gates | GET | verdictele pe porți cu motivele |
| /entities/{id}/judgments | GET, POST, PATCH | judecăți cu versiuni; confirmare sau respingere |
| /entities/{id}/judgments/ai-draft | POST | draft AI pentru (gate, field) |
| /entities/{id}/analyses | GET, POST | listă și îngheț |
| /analyses/{id}/diff/{other_id} | GET | diferențe fapte, derivate, judecăți, verdicte |
| /analyses/{id}/scenarios | GET, POST | scenarii cu ipoteze modificate |
| /entities/{id}/issues | GET, PATCH | jurnalul problemelor, rezolvare |
| /entities/{id}/export.csv?what=facts\|derived | GET | export CSV |
| /runs, /health | GET | rulări și stare |

Cele trei rute importante, cu forme:

```
GET /api/v1/entities/42/facts?concept=revenue&from=2016&to=2025
200 {
  "entity": {"id": 42, "name": "Apple Inc.", "cik": "0000320193", "currency": "USD"},
  "facts": [{
    "fact_id": 918223, "canonical_concept": "revenue",
    "source_concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    "fiscal_year": 2025, "period_start": "2024-09-29", "period_end": "2025-09-27",
    "value": 416161000000, "unit": "USD", "decimals": -6, "status": "ok",
    "filing": {"id": 5531, "form": "10-K", "accession": "0000320193-25-000079", "filed_at": "2025-10-31",
               "source_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm"},
    "frame": "CY2025", "extracted_at": "2026-10-31T21:05:16Z", "run_id": 77,
    "is_restated": false, "superseded": [{"fact_id": 901100, "value": 416161000000, "accession": "..."}],
    "issues": []
  }]
}

GET /api/v1/entities/42/gates
200 {
  "engine_version": "0.1.0", "assumption_set": {"name": "v1-default", "version": 1},
  "ten_year_rule": {"status": "ok", "complete_years": [2011, "...", 2025]},
  "gates": {
    "3": {"verdict": "necesită judecată",
          "evidence": [{"formula_id": "tangible_roic", "version": "1.0.0", "period_end": "2025-09-27",
                        "value": null, "status": "flagged", "flags": ["non_positive_tangible_capital"],
                        "input_fact_ids": [918223, 918300, 918311], "detail": {"nopat": 1.12e11, "capital": -2.2e9}}],
          "judgments_required": ["category_confirmation"]},
    "5": {"verdict": "necesită judecată",
          "evidence": [{"formula_id": "intrinsic_value_range", "version": "1.0.0", "value": 1.377e12,
                        "detail": {"low": 1.377e12, "high": 1.934e12, "g_low": 0.036, "g_high": 0.072, "rate": 0.10}},
                       {"formula_id": "margin_of_safety", "status": "not_computed", "flags": ["no_price_source"]}]}
  }
}

POST /api/v1/entities/42/judgments/ai-draft
{"gate": 4, "field": "moat_sources", "filings": [5531], "language": "en"}
202 {"judgment_id": 1203, "status": "propus_de_AI", "ai_draft": true, "text": "...",
     "citations": [{"filing_id": 5531, "quote": "...", "char_start": 48211, "char_end": 48377, "verified": true}],
     "usage": {"input_tokens": 118000, "output_tokens": 2100, "cost_eur": 0.41}}
422 {"error": "citation_not_verified", "failed_quotes": [{"filing_id": 5531, "quote": "..."}], "issue_id": 9981}
```

## 6. Interfața

Fiecare cifră afișată este un obiect, nu un număr: `{value, unit, kind, fact_ids | derived_id, status, flags}`. Componenta `Figure` redă valoarea și, la atingere, deschide cardul de proveniență, care cere `GET /facts?ids=` și arată eticheta XBRL exactă așa cum a fost depusă, perioada, raportul (formular, dată, link către documentul primar la SEC sau filings.xbrl.org), data extragerii, dacă este retratată și ce valoare a înlocuit, problemele deschise. Pentru o valoare derivată, cardul arată formula cu versiunea, intrările (fiecare cu propriul card) și ipotezele.

Separarea fapt, calcul, judecată este structurală: atributele `data-kind="fact|calc|judgment"` și `data-status` pe fiecare element, cu stiluri distincte (fapt: fond neutru și link; calcul: contur punctat și semnul formulei; judecată: fond cald cu autorul sau eticheta „propus de AI”). Testele Playwright verifică că nu există un element cu cifră fără `data-kind` și fără `fact_ids` sau `derived_id` (regula UX de blocare). Stările `lipsă`, `semnalat`, `date insuficiente` și `necalculat (fără preț)` au componente proprii. i18n: EN principal, RO disponibil, chei în `web/messages/{en,ro}.json`, inclusiv statusurile; identificatorii de concepte și formule rămân în engleză. Mobile first: tabelele pe 10 ani se afișează pe telefon ca liste pe an cu 3 la 5 cifre și pe desktop ca tabele; nimic nu se ascunde pe telefon. Ecranele sunt ale agentului UX.

## 7. Testabilitate pentru QA

- CLI fără interfață și fără bază de date: `python -m sixgates.engine run --facts fixtures/aapl/annual.csv --assumptions v1-default --out metrics.csv` ia fapte canonice dintr-un CSV (formatul `out/annual_us.csv` din spike) și produce toate valorile derivate cu formulă, versiune, intrări și status. QA poate construi CSV-ul manual din rapoarte și compara.
- Setul de aur: `fixtures/<ticker>/` conține faptele brute descărcate (cu sha256), CSV-ul canonic așteptat și `expected_metrics.csv`; testele de regresie rulează pipeline-ul pe faptele brute și compară byte cu byte. Orice diferență este fie un bug, fie o schimbare de versiune declarată.
- Rezultate cunoscute din scrisori: `tests/test_formulas.py` (See's 1972 și 2007, FlightSafety, aritmetica 1989, inegalitatea schimbării cu impozit, regula de zece ani cu 9 ani, capitalul tangibil nepozitiv, monotonia DCF în rata de discont, DCF cu formă închisă, DCF invers care recuperează creșterea); 22 de teste trec în spike.
- Versiuni expuse: `GET /health` și fiecare răspuns poartă `engine_version`; fiecare `Result` poartă `formula_id` și `version`; un test compară hash-ul codului sursă al fiecărei funcții cu versiunea declarată, deci o formulă nu se poate schimba fără incrementarea versiunii.
- Reproducere identică a unei analize înghețate: `analysis` reține `fact_snapshot_hash` (sha256 peste faptele selectate serializate canonic: JSON sortat, numere ca text decimal), `assumption_set_id` și `engine_version`; `sixgates analysis replay --id 17` recalculează din faptele cu `id` în instantaneu, cu imaginea Docker etichetată cu versiunea motorului, și compară hash-ul rezultatului cu cel stocat; testul lunar de restaurare rulează aceeași comandă.
- Verificarea citărilor AI: fixture cu un text de raport și draft-uri cu citări corecte, trunchiate și inventate; testul cere respingerea ultimelor două.

## 8. Raportul spike-ului de date

Detalii în `spike/out/spike_report.md` și `spike/out/reconciliation.md`.

### Ce s-a extras

| Companie | Sursă | Exerciții | Fapte brute | Observație |
|---|---|---|---|---|
| Apple (CIK 320193) | companyfacts, 10-K FY2025 | FY2009 la FY2025 (17), fereastră FY2016 la FY2025 | 1.095 | 52/53 săptămâni; split 4:1 în 2020 |
| Coca-Cola (CIK 21344) | companyfacts, 10-K FY2025 | FY2009 la FY2025 (17) | 1.382 | patru etichete pentru împrumuturile pe termen scurt |
| Moody's (CIK 1059556) | companyfacts, 10-K FY2025 | FY2009 la FY2025 (17) | 1.224 | capital propriu negativ FY2015 la FY2017 |
| LVMH (LEI IOG4E947OATN0KJYSD45) | filings.xbrl.org, 4 depuneri | FY2020 la FY2024 (5) | 1.180 | amortizarea doar ca extensie amestecată; EUR |
| OMV Petrom (LEI 549300UKYDM6L8HEPU79) | filings.xbrl.org, 6 depuneri pentru 2 exerciții | FY2020 la FY2022 (3) | 1.386 | nimic după FY2022; RON |

FRED DGS10: 4,98% la 29 octombrie 2026. Motor: 22 de teste trec. Regula de zece ani: trece pentru cele trei companii SUA, „date insuficiente” pentru LVMH și OMV Petrom.

### Ce s-a reconciliat

| Document | Cifre | Potriviri | Nepotriviri | Neverificate |
|---|---|---|---|---|
| Apple 10-K FY2025 (text și iXBRL) | 12 | 12 (3 cu semn de prezentare) | 0 | 0 |
| Coca-Cola 10-K FY2025 | 12 | 12 (3 cu semn de prezentare) | 0 | 0 |
| Moody's 10-K FY2025 | 12 | 12 (3 cu semn de prezentare) | 0 | 0 |
| LVMH raport ESEF FY2024 (XHTML, franceză) | 8 | 8 | 0 | 0 |
| OMV Petrom raport ESEF FY2022 (XHTML, română) | 8 | 7 | 0 | 1 (fond comercial inexistent) |

„Semn de prezentare” înseamnă că fluxul de numerar afișează ieșirile între paranteze, iar elementul XBRL este o plată pozitivă prin definiția taxonomiei. Toate cele 51 de cifre au fost confirmate și de faptul inline XBRL din același document, ceea ce validează metoda de producție (instanța depunerii, nu doar companyfacts).

### Ce a eșuat sau nu s-a putut face

| Pas | Rezultat | Motiv și consecință |
|---|---|---|
| Prețuri și capitalizare | eșuat | EODHD și Polygon cer cheie (401), stooq blocat, Yahoo limitat (429); DCF invers, marja de siguranță și testul dolarului rămân `not_computed` |
| Istoric BVB pe filings.xbrl.org | parțial | doar FY2021 și FY2022 pentru toți cei 39 de emitenți români; Hidroelectrica absentă |
| LVMH: amortizare | lipsă | doar extensia care amestecă provizioane, amortizare și deprecieri; OE și regula de zece ani nu se pot calcula |
| LVMH: profit înainte de impozit | derivat | neetichetat; afișat ca identitate marcată |
| OMV Petrom: împrumuturi | lipsă | nicio linie `Borrowings` etichetată separat; datoria netă necalculabilă |
| Apple: cheltuieli cu dobânzile FY2024 și FY2025 | lipsă | compania nu le mai prezintă; acoperirea dobânzilor necalculabilă |
| Interval VI pentru LVMH și OMV Petrom | neaplicat | regula de zece ani; OE pentru Petrom există (9.420 milioane RON în FY2022), poarta nu trece |

### Excepțiile de normalizare găsite

| Nr. | Excepție | Exemplu | Tratament |
|---|---|---|---|
| 1 | aceeași etichetă standard pentru linii diferite în rapoarte diferite | Apple DepreciationDepletionAndAmortization: 9.200 (note, FY2015) vs 11.257 (flux de numerar) | verificare de ambiguitate plus suprascriere per emitent cu dovadă |
| 2 | companyfacts fără etichete proprii și fără decimals | Coca-Cola „Loans and notes payable” FY2015 la FY2016, „Other intangible assets” FY2024 la FY2025 | lipsă marcată; rezolvare din instanța inline XBRL |
| 3 | o linie sub mai multe etichete în timp | Coca-Cola împrumuturi pe termen scurt: 4 etichete în 10 ani; ASC 606 la momente diferite | sinonime cu prioritate, cel mai recent depus câștigă, jurnal |
| 4 | split retratat doar în rapoartele ulterioare | Apple acțiuni diluate 5,25 miliarde (FY2017) vs 20 de miliarde (FY2018) | detecție de salt, tabelă de factori de split |
| 5 | retratări reale între rapoarte | Coca-Cola venituri FY2017: 35.410 apoi 36.212; FY2018: 31.856 apoi 34.300 | ultimul câștigă, ambele în jurnal, `is_restated` |
| 6 | schimbare de precizie confundabilă cu retratare | Moody's 4.204,1 vs 4.204 | comparație la precizia comună; doar info |
| 7 | linie inexistentă vs concept lipsă; etichete de rezervă | Moody's fără hârtie comercială în majoritatea anilor; LongTermDebt total în FY2020 | `absent_ok` la severitate joasă, niciodată zero tăcut; rezervă notată |
| 8 | conceptele metodei doar ca extensii ESEF, cu prefix instabil | LVMH profit operațional, investiții, costul datoriei; Petrom investiții (`omvpetromsa` apoi `omvpetrom`) | suprascrieri pe nume local |
| 9 | concept neetichetat în ESEF | LVMH ProfitLossBeforeTax; Petrom acțiuni diluate; ambele fără achiziții de acțiuni proprii în flux | identitate marcată sau lipsă |
| 10 | semn inconsecvent între ani în ESEF | LVMH interese minoritare FY2022 și FY2023: -667 în raportul 2023, +667 în 2024 | retratare jurnalizată; regulă de semn de confirmat |
| 11 | depuneri duplicate și două OAM-uri | OMV Petrom RO-0, RO-1, GB-0 pentru același an | un `filing` per depunere, duplicate jurnalizate |
| 12 | 52 sau 53 de săptămâni; monedă și scară | Apple FY2017 cu 371 de zile; Petrom în RON cu decimals -3; LVMH cu separatori de spațiu | durată 340 la 380 de zile; fără conversie; parsare după formatul inline XBRL |
| 13 | capital propriu negativ și capital tangibil nepozitiv sau neglijabil | Moody's capital propriu -1.225 milioane în FY2016; Apple capital tangibil negativ FY2021, FY2023 la FY2025; ROIC de zeci de ori la Apple și Moody's | ROIC semnalat, nu calculat; „> 200%, capital tangibil neglijabil”; categoria „profit în creștere fără capital suplimentar” |

## 9. Riscuri tehnice și decizii amânate

| Risc sau decizie | Impact | Propunere |
|---|---|---|
| Istoric UE și BVB sub zece ani din ESEF | porțile 3 și 5 rămân „date insuficiente” pentru companiile UE fără import manual | importul validat din PDF devine un flux de produs (doi cititori, marcare vizibilă) în faza 4; până atunci verdictul rămâne „date insuficiente” |
| BVB fără depuneri ESEF după FY2022 pe filings.xbrl.org | fără sursă automată pentru BVB | import manual al pachetelor ESEF de pe paginile emitenților; de verificat accesul programatic la OAM-ul românesc (decizie amânată) |
| Fără sursă de preț în spike | jumătate din poarta 5 necalculată | contractarea EODHD este primul pas al fazei 2; până atunci preț introdus manual cu sursă și dată, marcat ca intrare manuală |
| Etichete proprii și reutilizarea etichetelor | cifre greșite dacă prioritatea decide singură | ambiguitatea blochează la severitate ridicată; suprascrierile cer dovadă; reconcilierea la raport pentru cel mai recent an intră în definiția lui „gata” |
| Amortizarea lipsă în ESEF | OE necalculabil pentru emitenți ca LVMH | import din note ca fapt manual validat; de decis dacă se acceptă extensia emitentului cu avertisment |
| Leasing IFRS 16 și ASC 842 în datorie | datoria netă subestimată pentru retaileri și lux | decizie amânată: v1 exclude leasingul din datorie și îl afișează separat; de validat cu product owner |
| Termenul ΔWC în OE | OE volatil, VI instabilă | decizie PM: normalizare pe 3 ani sau afișarea ambelor variante |
| Formula VI cu termen terminal nediscontat în requirements_v0 | supraevaluare de 2,6x dacă se implementează literal | confirmare PM a versiunii discontate (implementată) |
| Praguri ale categoriilor 2007 | clasificări discutabile (FlightSafety la 31%) | validare pe setul de aur în faza 2, cu PM și QA |
| Costul API Claude la screening (faza 3) | depășirea plafonului | plafon lunar în `ops.ai_usage`; draft-uri doar la cerere în v1 |
| Un singur întreținător | risc operațional | runbook-uri, test de restaurare lunar, imagini etichetate |

## 10. Plan de implementare pentru faza 2 (v1)

| Nr. | Milestone | Demonstrabil la final |
|---|---|---|
| M1 | Schelet: monorepo, Compose pe Mac Mini, PostgreSQL cu migrații, autentificare, CI | autentificare pe telefon, `/health` verde, un utilizator creat de admin |
| M2 | Ingestie SUA: companyfacts și submissions pentru 10 companii din setul de aur; `filing`, `fact`, `data_issue`, `ingestion_run` | pagina companiei arată faptele canonice pe 10 ani cu cardul de proveniență și jurnalul problemelor |
| M3 | Instanța depunerii: inline XBRL din 10-K pentru etichete proprii și decimals; `concept_override`; reconciliere automată la ultimul 10-K | reconcilierea celor 10 companii SUA afișată în produs, pe cifră |
| M4 | Motorul și poarta 3: motor versionat, CLI pentru QA, setul de aur cu teste din scrisori, verdictul porții 3 și supraviețuirea | poarta 3 cu verdict și formula vizibilă pe fiecare cifră; QA rulează CLI-ul pe CSV-uri proprii |
| M5 | Poarta 5 și prețuri: EODHD, `price`, VI ca interval, DCF invers, randamentul câștigurilor vs FRED, „prețul pe care l-aș plăti”, scenarii | poarta 5 completă pentru companiile SUA; un scenariu cu prag diferit nu schimbă valoarea |
| M6 | ESEF: filings.xbrl.org pentru 7 companii UE și 3 BVB, parser OIM, suprascrieri pe extensii, import manual validat marcat | companii UE cu fapte, proveniență către XHTML și verdict „date insuficiente” explicat; una cu istoric manual completat |
| M7 | Porțile 2 și 4 (dovezi) și judecăți: CRUD cu versiuni, dovezile cantitative pentru moat, separarea fapt, calcul, judecată în interfață | o analiză completă pe o companie, cu judecățile omului și verdicte pe toate porțile |
| M8 | Draft-uri AI cu citări verificate: `filing_text`, apelul Claude, verificarea prin subșir, `ai_usage` | un draft „propus de AI” cu citări verificate, confirmat de om; un draft cu citare inventată respins |
| M9 | Analiză înghețată, diff, export CSV, copii de rezervă și restaurare | două versiuni ale aceleiași analize comparate; export CSV; restaurare cu recalculare identică |
| M10 | Definiția lui „gata”: 20 de companii (10 SUA, 7 UE, 3 BVB) prin toate porțile, QA recalculează independent, mutarea pe VPS testată | raport QA „trece”, demonstrație pe telefon cu o persoană nouă, aceeași aplicație pe VPS |

Ordinea respectă riscul: surse primare și reconciliere înainte de formule, formule înainte de interfața bogată, AI la final. Fiecare milestone se încheie cu o revizuire față de secțiunea 2 din requirements_v0.
