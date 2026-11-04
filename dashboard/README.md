# Panoul SixGates

O vedere pe companie, generată din fișierele JSON de analiză. Funcționează cu dublu clic pe fișier (file://), fără server și fără dependențe externe.

## Cum adaugi o analiză

1. Salvează JSON-ul produs de sesiunea de analiză în `data/analyses/<TICKER>/<AAAA-LL-ZZ>_v<N>.json` (de exemplu `data/analyses/KO/2026-11-04_v1.json`).
2. Rulează `python3 dashboard/build.py`. Scriptul validează câmpurile minime, scrie `dashboard/data.js` și `dashboard/sixgates_dashboard.html` și afișează un rezumat (companii, versiuni, verdicte).
3. Deschide `dashboard/sixgates_dashboard.html` (un singur fișier, cu datele incluse).

Alternativ, în pagină: „Importă JSON” (unul sau mai multe fișiere, sau text lipit). Importurile stau în localStorage-ul browserului; „Exportă tot” descarcă toate analizele ca o listă JSON, „Șterge importurile” le golește. La aceeași cheie (ticker, dată, versiune), datele incluse în build au prioritate. `index.html` merge și fără `data.js`: atunci arată doar importurile.

## Istoric

Fiecare versiune este un fișier separat. Nu suprascrie un fișier vechi: o analiză nouă sau o judecată nouă înseamnă `_v2`, `_v3` și așa mai departe. Când o companie are mai multe versiuni, antetul arată un selector și blocul „diferențe față de versiunea anterioară” (verdictele porților și decizia pre-analizei care s-au schimbat). O versiune cu `status: "frozen"` este un dosar înghețat.

## Reguli

- Nicio cifră fără sursă. Ce lipsește apare ca „lipsă”, nu ca zero și nu estimat.
- Registre, marcate pe fiecare secțiune: [F] fapt din raport, [C] calcul din formulă vizibilă, [J] judecată a omului cu autor și dată, [AI] draft propus de AI, neconfirmat.
- Verdicte: trece, pică, necesită judecată, date insuficiente, plus „închisă” pentru poarta 5 până la textele porții 2. Fără scor compozit, fără stele, fără medie.
- Pragurile sunt parametri propuși (instrumente ale noastre, nu reguli ale lui Buffett sau Munger).
- Fără limbaj de recomandare. Aritmetică cu surse și judecăți atribuite, nu sfat de investiții.

## Glosar

Butonul „Glosar” deschide lista completă de termeni (OE, ROIC, K1 la K7, registre, verdicte, documente SEC și altele), cu căutare. Termenii subliniați cu puncte din pagină deschid glosarul direct la definiția lor.
