# Mitt stöd för den muntliga redovisningen

Issam Hariri · DEVOPS25 · Torsdag 19 november 2026 kl. 14.00 digitalt

Jag fokuserar på mina tekniska val, testerna, flödet och vad kontrollerna visar. Lärarens besked är att GitHub, projektet och demonstrationsmiljön ska vara redo. Jag kan visa en tidigare slutförd Actions-körning om en livekörning tar tid. Den skriftliga redogörelsen kompletterar demonstrationen.

## Det jag har redo före starten

- Min projektbranch på [GitHub](https://github.com/issamhariri-code/devops25-ci-cd-course/tree/projekt/examination).
- En [slutförd grön körning](https://github.com/issamhariri-code/devops25-ci-cd-course/actions/runs/44071844040).
- Den [avsiktligt röda versionskontrollen](https://github.com/issamhariri-code/devops25-ci-cd-course/actions/runs/44057277021/job/133949887824).
- Den [gröna körningen efter rättningen](https://github.com/issamhariri-code/devops25-ci-cd-course/actions/runs/44058055772).
- VS Code med `app/main.py`, `tests/test_api.py`, `tests/test_service.py` och `.github/workflows/ci.yml`.
- Docker Desktop och containern `cicd-examination` från imagen `cicd-examination:1.0.1`.
- [Versionsadressen](http://127.0.0.1:8000/version), [addition](http://127.0.0.1:8000/api/add?a=100&b=5) och [API-dokumentationen](http://127.0.0.1:8000/docs).
- Rapporten och den nedladdade XML-rapporten från Actions.

Jag kontrollerar att min aktuella branch och versionsadressen stämmer innan redovisningen börjar. Om en möteslänk eller annan praktisk instruktion tillkommer lägger jag till den i min förberedelse.

## 1 Jag börjar med syftet

Jag har utgått från kursens FastAPI-mall och byggt vidare på kedjan runt den. Mitt mål är att få snabb återkoppling och kunna avgöra om en ändring är redo att gå vidare. Appen är liten så att jag kan förklara kontrollerna konkret. Jag har lagt till versionsadress, kontrollerat API-fel vid division med noll, två API-tester och leveransverifiering i Actions.

Jag visar kort README och diagrammet. Jag beskriver appens funktioner utan att gå igenom installationen.

## 2 Jag visar kedjan i koden

Jag öppnar ci.yml och följer ordningen: startregel, testjobb, sparad rapport, needs: test, bygge, containerstart, verifiering och cleanup.

Jag pekar på att needs: test är spärren mellan jobben. Build och Start använder samma image-referens med github.sha. Commit-id:t kopplar körningen till en kodversion. Appens versionsnummer är en separat etikett som jag också kontrollerar genom API:et.

Jag förklarar att runnern är GitHubs tillfälliga körmiljö. Simulerad leverans betyder här att imagen faktiskt startas och kontrolleras där, men ingen permanent publik produktionstjänst lämnas igång.

## 3 Jag visar tester och en fungerande körning

Jag visar skillnaden mellan service-testet och API-testet. Service-testet för division med noll förväntar ValueError. API-testet för samma indata förväntar HTTP 400 och rätt JSON-feltext. Jag visar hur try/except och HTTPException kopplar ihop dessa beteenden.

I den gröna körningen visar jag Lint, Test, Save test report och byggjobbet. Under Verify deployment ska kontrollerna för hälsa, addition och version ha lyckats. Jag visar även att Cleanup är grönt.

Jag visar artifacten pytest-results och förklarar vad tests, failures och errors betyder i XML-rapporten. Den rapport jag tidigare hämtade visade sju tester, noll failures och noll errors.

## 4 Jag visar ett kontrollerat fel och kedjans reaktion

Jag öppnar den redan slutförda röda körningen på commit 721d6eb. Jag förklarar att jag ändrade kontrollens förväntan till 9.9.9 medan appen fortfarande körde 1.0.1. Det var ett avsiktligt fel i verifieringens förväntan.

Jag visar att testjobbet var grönt och att bygge och start lyckades. I Verify deployment visar jag Health OK, Addition OK och AssertionError med det faktiska versionssvaret 1.0.1. Därefter visar jag att Cleanup lyckades trots felet.

Jag öppnar den gröna körningen på 53634bb och visar att en återställd förväntan gav grönt igen. Jag använder detta för att förklara varför gröna tester inte ensamma bekräftar vilken version som har startats.

Om jag får frågor om uppstartsfelet visar jag den tidigare röda körningen på 2924302 och förklarar avgränsade återförsök och att JSON läses först efter lyckad hämtning. Jag skiljer den sannolika förklaringen om uppstartstid från det som loggen faktiskt bevisade.

## 5 Jag förklarar rollback och begränsningar

Jag beskriver den genomförda lokala återställningen från 1.0.1 till den sparade imagen 1.0.0. Jag kontrollerade versionssvaret, image-id och additionens resultat. Sedan återgick jag till 1.0.1. Källkoden i projektmappen behövde inte bytas för att starta den redan byggda äldre imagen.

Om jag visar rollback live använder jag samma ordning som i övningen: stoppa containern, ta bort den, starta den sparade äldre imagen och kontrollera version och funktion. Efteråt återgår jag till 1.0.1. Jag anpassar hur mycket jag visar till den presentationslängd läraren anger.

Jag är tydlig med att rollbacken var manuell, gav ett avbrott och inte återställde data. Den äldre versionen saknar den nya felhanteringen. Det gamla rollback-skriptet är en platshållare; det var Docker-kommandona som utförde min återställning.

## 6 Jag avslutar med mina förbättringar

Jag prioriterar ett registry med spårbara images som kan återanvändas vid leverans och rollback, fler testfall, säkerhetskontroller och övervakning efter leveransen. Jag behöver även hantering av miljöer, behörigheter och data om lösningen ska användas i produktion.

Jag knyter förbättringarna till de risker jag sett i mitt projekt, till exempel fel version, otillräcklig testtäckning, uppstartstid och att runnerns image inte lagras beständigt.

## Frågor jag ska kunna besvara med egna ord

- Varför räcker inte en hälsokontroll? Den visar ett begränsat svar; jag behöver även prova relevant funktion och rätt version.
- Varför både service- och API-test? De provar olika delar av vägen från indata till svar.
- Vad gör needs: test? Bygg- och leveransjobbet får börja först när hela testjobbet lyckats.
- Varför if: always()? Rapportuppladdning och cleanup ska kunna försöka köras även efter fel. De gör inte ett tidigare fel godkänt.
- Vad är skillnaden mellan image och container? Imagen är det byggda paketet; containern är en instans som startats från det paketet.
- Vad skiljer omstart från rollback? En omstart kan använda samma version. Min rollback bytte till en sparad tidigare image.
- Vad kan jag inte lova utifrån en grön körning? Att alla funktioner, indata, säkerhetsrisker och driftproblem är täckta eller att en permanent produktionstjänst har uppdaterats.
