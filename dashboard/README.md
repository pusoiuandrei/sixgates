# Panoul SixGates

O vedere pe companie, generată din fișierele JSON de analiză. Funcționează cu dublu clic pe fișier (file://), fără server și fără dependențe externe.

## Cum adaugi o analiză

Calea scurtă, cu fișierul JSON emis de sesiunea de analiză (secțiunea 15 din cadru):

```
python3 dashboard/build.py --add GOOGL_2026-11-04_v1.json
```

Scriptul validează fișierul, îl pune la locul lui (`data/analyses/<TICKER>/<AAAA-LL-ZZ>_v<N>.json`, după `company.ticker`, `analysis.date` și `analysis.version`), refuză să suprascrie o versiune existentă fără `--force`, apoi reconstruiește `dashboard/data.js` și `dashboard/sixgates_dashboard.html` și afișează un rezumat (companii, versiuni, verdicte). Deschide apoi `dashboard/sixgates_dashboard.html` (un singur fișier, cu datele incluse).

Sesiunea de analiză poate face singură acești pași: repo-ul este public, deci îl clonează (`git clone --depth 1 https://github.com/pusoiuandrei/sixgates`), rulează comanda de mai sus și trimite dashboard-ul reconstruit; dacă repo-ul este atașat sesiunii cu drepturi de push, face și commit, iar istoricul se completează de la sine. Fără asta, salvezi manual JSON-ul în `data/analyses/<TICKER>/` și rulezi `python3 dashboard/build.py`.

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
