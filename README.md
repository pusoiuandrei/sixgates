# SixGates

Analizor de companii listate prin cele șase porți ale metodei Buffett-Munger: fiecare cifră trasabilă până la raportul din care vine, fiecare formulă vizibilă, faptele separate de calcule și de judecăți, fără limbaj de recomandare.

Company analyzer built on the six gates of the Buffett-Munger method: every number traceable to its filing, every formula visible, facts separated from calculations and from human judgments, no buy or sell language.

## Starea proiectului

Faza 1 (fundație) livrată la 1 noiembrie 2026. Documentele de produs sunt în `phase1/` și în documentul Claude „Analizor Buffett-Munger: cerințe și descoperire” (tab-urile PRD v1, UX, Arhitectură, Spike de date, QA). Faza 2 (versiunea 1) începe după review-ul cu product owner-ul.

## Conținut

| Director | Ce conține |
|---|---|
| `context/` | rețeta metodei (`recipe.md`) și cerințele v0 (`requirements_v0.md`), sursa de adevăr pentru echipă |
| `phase1/` | PRD v1, strategia QA și setul de aur, arhitectura (ADR-uri, model de date, API), UX (fluxuri, wireframes), raportul spike-ului și backlog-ul pentru Jira (`backlog.csv`) |
| `spike/` | spike-ul de date: extracție EDGAR și ESEF, normalizare, motor de formule pur cu teste, reconciliere la documentele primare (README în engleză) |

## Rulare rapidă

```
python3 -m pytest -q spike/tests
python3 spike/run_spike.py
```

Datele brute descărcate (`spike/data/`) nu sunt versionate; se re-descarcă din SEC EDGAR, filings.xbrl.org și FRED la rulare.

## Reguli de lucru

- Principiile de acuratețe P1 la P10 din `context/requirements_v0.md` sunt criterii de acceptare; nicio cifră fără proveniență.
- Vocabularul verdictelor este fix: trece, pică, necesită judecată, date insuficiente.
- Fără em dash sau en dash în documente și în textele interfeței.
