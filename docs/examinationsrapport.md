# CI CD med FastAPI och Docker

Issam Hariri · DEVOPS25 · 17 november 2026

## 1 Syfte och lösning

Jag har byggt vidare på kursens FastAPI-applikation och skapat en sammanhängande CI/CD-kedja runt den. När jag pushar en ändring till min projektbranch kör GitHub Actions kodkontroller och tester. Om testjobbet lyckas bygger kedjan en Docker-image, startar en container och kontrollerar att den körande applikationen svarar rätt. En testrapport sparas så att jag kan granska resultatet efter körningen.

Syftet är att få tidig återkoppling och minska risken att en felaktig ändring går vidare i leveransen. Jag vill kunna följa en liten ändring från commit till körande applikation och se vilken kontroll som reagerar om något blir fel. Därför har jag också provat ett kontrollerat verifieringsfel och en manuell återställning till en tidigare version.

Utgångspunkten är kursmallen från cloudfactoreu/devops25-ci-cd-course. Den innehöll redan beräkningsfunktioner, fem tester, en Dockerfile och exempel på workflows. Mina ändringar omfattar versionsadressen, ett API-test för versionen, kontrollerad felhantering för division med noll och ett API-test för det felsvaret. Jag har också utökat workflow-filen med startregel för projektbranchen, sparad testrapport samt containerstart, verifiering och städning efter bygget.

Applikationen är medvetet liten. Den har addition, division, en hälsokontroll och en versionsadress. Det gör att jag kan lägga fokus på hur leveransen kvalitetssäkras och förklara vad varje steg skyddar mot. I version 1.0.1 svarar API:et med HTTP 400 och ett begripligt felmeddelande när någon försöker dividera med noll.

Leveransen sker till en tillfällig testmiljö på GitHubs runner. Jag har även byggt och kört två versioner lokalt i Docker. Projektet visar därmed en fungerande simulerad leverans och manuell rollback. Jag har avgränsat arbetet från publik produktionsdrift, databas och Kubernetes, eftersom jag först vill kunna visa och motivera den här kedjan ordentligt.

<!-- pagebreak -->

## 2 Arkitektur och arbetsflöde

Projektet finns i min egen GitHub-kopia på branchen projekt/examination. Det aktiva workflowet ligger i .github/workflows/ci.yml. Det startar vid push till projekt/examination eller main, vid pull request mot main och genom manuell start i Actions. De kontrollerade körningarna i rapporten startade automatiskt genom push.

<!-- diagram -->

Workflowet har två jobb. Det första heter test och hämtar koden, förbereder Python 3.12, installerar beroenden och kör Ruff och pytest. Pytest skriver även en JUnit-rapport till reports/pytest.xml. Uppladdningssteget sparar den som pytest-results med if: always(), så att steget försöker spara rapporten även efter ett testfel när filen har skapats. Jag har hämtat en rapport och läst sju tester, noll failures och noll errors.

Det andra jobbet heter build-image och har needs: test. Det innebär att hela testjobbet måste lyckas innan bygg- och leveransjobbet får börja. Här byggs imagen med commit-id som etikett. Samma image-referens används sedan för att starta testcontainern. Eftersom bygge och start ligger i samma jobb finns den byggda imagen tillgänglig när containern ska skapas.

Efter starten kontrollerar Verify deployment tre svar: /health ska ge status ok, additionen 100 + 5 ska ge 105 och /version ska ge 1.0.1. Hälsokontrollen har avgränsade återförsök, eftersom containerstarten inte betyder att API:et omedelbart är redo att ta emot anrop. HTTP-fel eller fel svarsinnehåll gör verifieringen röd.

Cleanup ligger sist och har if: always(). Det gör att städningen försöker stoppa och ta bort containern även efter ett verifieringsfel. Jag har observerat att detta fungerar i den avsiktligt röda körningen. När jobbet är färdigt finns ingen permanent tjänst kvar på runnern.

Jag tog bort den äldre fristående CD-mallen från projektbranchen. Den kunde startas manuellt utan testjobbet. Nu är det tydligt att projektets leveransflöde finns i ci.yml och är kopplat till godkända kontroller. Det är fortfarande en simulering i en testmiljö, inte en produktionsrelease.

<!-- pagebreak -->

## 3 Tekniska val

Jag valde att behålla FastAPI-appen från kursmallen. Beräkningarna är enkla att förstå, vilket gör det lätt att avgöra om ett test eller ett API-svar är korrekt. Jag kan till exempel kontrollera att 100 + 5 blir 105 och samtidigt skilja mellan att en adress svarar och att funktionen ger rätt resultat.

Jag använder tester på två nivåer. Service-testerna anropar beräkningsfunktionerna direkt. API-testerna går genom FastAPI med TestClient och kontrollerar HTTP-svar och JSON-innehåll. De två nivåerna täcker olika delar av samma funktionalitet.

| Testnivå | Antal | Vad jag kontrollerar |
| --- | --- | --- |
| Service | 3 | Addition, division och ValueError vid division med noll |
| API | 4 | Hälsa, addition, versionssvar och HTTP 400 vid division med noll |

Mitt nya feltest visade först att API-anropet avbröts av ValueError innan testets HTTP-kontroll nåddes. Jag lade sedan till try/except i API-funktionen och översatte det fångade felet till HTTPException med status 400. Beräkningsfunktionen fortsätter att signalera ValueError. På det sättet får klienten ett kontrollerat svar, samtidigt som service-testets förväntan fortfarande gäller. De fem ursprungliga testerna och mina två nya tester passerar tillsammans.

Ruff ger återkoppling om de kodregler och syntaxproblem som verktyget kontrollerar. Pytest provar beteendet som jag har beskrivit i testerna. Ett giltigt Python-uttryck kan fortfarande räkna fel, så jag behöver båda typerna av kontroll. Vilka stilregler Ruff granskar beror på konfigurationen.

Docker ger mig ett paket med appen, Python och beroendena. Jag använder samma requirements.txt vid installation i testjobbet och i Dockerbygget. Imagen körs sedan som container. Versionsadressen visar appens valda versionsnummer, medan image-etiketten i Actions knyter bygget till en commit. Det är två olika identiteter som jag behöver hålla ihop.

Jag valde GitHub-hosted runner för att kunna köra kedjan utan en egen permanent byggserver. Min lokala dator och GitHubs runner är separata miljöer. Den automatiska körningen fortsätter på GitHub när koden är pushad, även om jag stänger VS Code. Jag har behållit lösningen enkel och lagt fokus på beroenden mellan stegen och kontroller av den app som faktiskt startas.

<!-- pagebreak -->

## 4 Testning och resultat

Den lokala testsviten gav sju godkända tester efter felhanteringen och versionsändringen till 1.0.1. Ruff godkände också koden. En beroendevarning från Starlette och AnyIO fanns i testutskriften. Den var skild från testfel och gjorde inte körningen underkänd.

I den första fulla Actions-körningen lyckades tester, bygge och containerstart, men hälsokontrollen fick Connection reset by peer. Python försökte därefter läsa ett JSON-svar som inte hade kommit fram. Uppstartstid var en möjlig förklaring; loggen bevisade inte hela grundorsaken. Jag utökade återförsöken till att hantera anslutningsavbrottet och lät curl skriva svaret till en fil innan Python läste det. Nästa körning blev grön. I en senare körning syntes samma anslutningsfel följt av Health OK, vilket visade att återförsöket fungerade.

Jag provade sedan versionskontrollen genom att ändra dess förväntan till 9.9.9 medan appen och API-testet behöll 1.0.1. Testerna, bygget och containerstarten lyckades. Loggen visade Health OK och Addition OK, men versionsjämförelsen gav AssertionError med appens faktiska svar 1.0.1. Verifieringen stoppade jobbet och Cleanup lyckades ändå. När jag återställde förväntan till 1.0.1 blev hela kedjan grön igen. Felet låg alltså avsiktligt i kontrollens förväntan, inte i en ändrad appversion.

| Kontrollerad körning | Commit | Resultat |
| --- | --- | --- |
| [Första fulla kedjan](https://github.com/issamhariri-code/devops25-ci-cd-course/actions/runs/43895495089) | 2924302 | Röd hälsokontroll |
| [Korrigerad uppstartskontroll](https://github.com/issamhariri-code/devops25-ci-cd-course/actions/runs/43897535571) | bc44598 | Grön kedja |
| [Avsiktlig versionsavvikelse](https://github.com/issamhariri-code/devops25-ci-cd-course/actions/runs/44057277021) | 721d6eb | Röd versionskontroll |
| [Återställd versionsförväntan](https://github.com/issamhariri-code/devops25-ci-cd-course/actions/runs/44058055772) | 53634bb | Grön kedja |
| [Aktuell projektkedja](https://github.com/issamhariri-code/devops25-ci-cd-course/actions/runs/44071844040) | 1d2a24e | Grön efter borttagen CD-mall |

Jag utförde också en manuell lokal rollback. Jag stoppade containern för 1.0.1 och startade den sparade imagen 1.0.0. Versionsadressen visade 1.0.0 och additionen svarade med HTTP 200 och resultat 105. Containerns image-id matchade den sparade äldre imagen. Källkoden låg samtidigt kvar på 1.0.1. Jag återgick därefter till imagen 1.0.1 och bekräftade versionen igen. Det visade ett verkligt byte mellan två sparade appversioner; övningen utgick inte från någon faktisk incident i 1.0.1.

<!-- pagebreak -->

## 5 Reflektion och förbättringar

För mig har arbetet gjort skillnaden tydlig mellan en grön testsvit och en verifierad leverans. Ett API-test provar koden som finns i testmiljön. Efter containerstart behöver jag också kontrollera den app som faktiskt körs. Hälsa och korrekt addition kan passera även när fel version har startats. Därför fyller versionskontrollen en egen funktion i kedjan.

Jag har också sett att återkopplingen behöver gå att använda för nästa beslut. I uppstartsfelet behövde jag börja vid det första anslutningsfelet och skilja det från det efterföljande JSON-felet. I versionsövningen behövde jag läsa vilket värde appen faktiskt gav. Commit, körlogg och sparad rapport gör det möjligt att följa ändringen och förklara vad som hände.

Testerna täcker bara de fall som finns beskrivna. Projektet har ingen fullständig kontroll av alla indata, belastning eller säkerhet. Verifieringen efter start kontrollerar hälsa, en addition och versionen. Den visar användbara grundegenskaper men garanterar inte att alla funktioner fungerar. Nästa steg i testningen skulle vara fler gränsfall och ett API-test för vanlig division.

Den lokala rollbacken var manuell och gav ett avbrott när containern byttes. Den återställde ingen beständig data. Version 1.0.0 saknar dessutom den nya felhanteringen för division med noll, så en återgång kan återinföra äldre begränsningar. I en verklig incident behöver jag därför välja tidigare version utifrån vilka funktioner verksamheten behöver. Det ursprungliga rollback-skriptet i kursmallen är fortfarande en platshållare; det var Docker-kommandona som utförde min verifierade återställning.

För en produktionsmiljö skulle jag först spara den byggda imagen i ett registry och använda en beständig image-identitet vid leverans och återställning. CI-byggets image används på den tillfälliga runnern. Jag skulle också låsa och uppdatera beroenden och basimage mer kontrollerat, lägga till säkerhetskontroller och införa övervakning efter leveransen. Versionsnumret i appen och verifieringens förväntan ändras nu manuellt och behöver hållas konsekventa.

Jag skulle även behöva tydligare hantering av miljöer, behörigheter och eventuella releasegodkännanden, samt en plan för data och driftavbrott vid återställning. I den här lösningen har jag kunnat prova grundkedjan i små ändringar, se vad som stoppar flödet och verifiera både fungerande och felaktiga förlopp. Det ger mig ett konkret underlag för att motivera hur jag vill utveckla kedjan vidare.

Underlag: [mitt projekt](https://github.com/issamhariri-code/devops25-ci-cd-course/tree/projekt/examination), [kursmallen](https://github.com/cloudfactoreu/devops25-ci-cd-course), kursens projektuppgift och bedömningsstöd samt körningarna ovan. Rapportens upplägg följer dag 1, PDF-sidor 24–26, och redovisningspunkterna i dag 6, PDF-sida 33. Hanteringen av återförsök och utfil stöds av [curl-dokumentationen](https://curl.se/docs/manpage.html#--retry-all-errors).
