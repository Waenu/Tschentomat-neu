# TSCHENT-O-MAT

Preisrechner für die Familie, Chalet Tschenten, Adelboden.

## Preise oder Nächte ändern

1. Auf GitHub die Datei `einstellungen.json` öffnen.
2. Oben rechts auf den Stift (Edit) klicken.
3. Nur die Zahlen ändern, dazu `version` und `gueltigAb` anpassen.
4. Rechts oben auf «Commit changes…» und danach auf «Commit changes» klicken.
5. Nach etwa einer Minute sehen alle die neuen Werte.

| Eintrag | Bedeutung |
|---|---|
| `famPausch` | Familie pro Nacht |
| `gast` | Gast pro Nacht (eigenes Zimmer) |
| `gastZimmer` | Gast im selben Zimmer wie Sohn oder Tochter, pro Nacht |
| `famAnteil` | Familie pro Nacht, wenn Sohn oder Tochter das Zimmer mit einem Gast teilt |
| `reinigung` | Reinigung pro Aufenthalt |
| `reinigungSelbst` | Reinigung, wenn die Familie selbst reinigt und frische Wäsche mitbringt (0 = gratis) |
| `selbstReinigung` | Zeiten (jedes Jahr gleich), in denen die Familie selbst reinigen darf. Format `[["11-01","12-18"]]` (Monat-Tag von, bis). Weitere Zeiträume mit Komma anfügen |
| `sparEin` | Reduktion pro Nacht, wenn Zimmer 1 unberührt bleibt |
| `sparMaxPers` | Bis so viele Personen insgesamt kann Zimmer 1 unberührt bleiben |
| `minNaechte` / `maxNaechte` | Kleinste und grösste Anzahl Nächte |
| `maxPersonen` | Personen mit Bett |
| `iban` / `bank` | Konto für die Überweisung, wird im Ergebnis angezeigt |
| `zahlTage` | Frist in Tagen nach dem letzten Ferientag |
| `lueckeMax` | Freie Nächte zwischen zwei Belegungen bis zu dieser Zahl gelten als Lücke (Airbnb-Mindestaufenthalt minus 1) |
| `keinCheckinSonntag` | `true`: Sonntag ist bei Airbnb nie Check-in-Tag. Eine freie Strecke zwischen zwei Buchungen, die an einem Sonntag beginnt, zählt für Lücken erst ab Montag. Die Sonntagsnacht bleibt für die Familie gesperrt |
| `lueckeVorlaufTage` | Lücken ausserhalb der Selbstreinigungs-Zeiten (dort ist die Familienstaffel nicht möglich) sind für die Familie erst so viele Tage vor Beginn der Lücke buchbar, vorher gesperrt |
| `lueckeSperrMonate` | Monate (Liste), in denen Lücken für die Familie immer gesperrt sind (violett, nie freigegeben). Massgebend ist der Monat der ersten Nacht der Lücke |
| `lueckeMaxPersonen` | Ganze Lücke: höchstens so viele Personen mit Bett, zusätzlich `lueckeMaxKleinkinder` Kleinkind(er) im Kinderbettchen. Dazu: keine Gäste, nur Zimmer 2, eigene Wäsche, Reinigung 240 |
| `lueckeRabatt` | Prozent Rabatt auf die Übernachtungen, wenn die ganze Lücke gebucht wird (Reinigung bleibt gleich) |
| `hochsaisonMonate` | Ganze Monate, die jedes Jahr gelb markiert werden. Januar ist `[1]`, Februar `[2]`, mehrere zum Beispiel `[2, 7]` |
| `spitzenzeiten` | Zeiten, in denen nur zu hohen Preisen vermietet wird (zum Beispiel Skirennen). Rot markiert, ohne Familienpreis: nur «Preis auf Anfrage». Format: `[["2027-01-15","2027-01-17","Skirennen"]]` (von, bis, Name) |
| `hochsaison` | Zeiträume, die gelb markiert werden. Format: `[["2026-12-19","2027-01-03"], ["2027-02-06","2027-02-20"]]` (von, bis, beide eingeschlossen) |
| `festMinGaeste` | In den `festMonate` (Februar) sind mindestens so viele Gäste nötig, sonst gibt der Rechner keinen Preis aus. `0` = keine Vorgabe. Jetzt `0` (seit 1.10.0 ersetzt durch `festBodenWoche`) |
| `festBodenWoche` | In den `festMonate` (Februar): Mindest-Gesamtpreis pro 7 Nächte inklusive Endreinigung (bei anderen Längen anteilig). Ersetzt dort `mindestpreisWoche`. Liegt der Preis der Gäste darunter, wird der fehlende Betrag gleichmässig auf alle Personen (Familie und Gäste) verteilt, die Familie allein zahlt den Boden. Liegt er darüber, entfällt der Anteil der Familie, soweit es der Preis zulässt. `0` = aus. Jetzt `1920`; für Februar 2028 ist `1980` vorgesehen |
| `mindestpreisAbNaechte` | Die Entlastung der Familie (siehe `mindestpreisWoche`) gilt erst ab dieser Zahl Nächte. Kürzere Aufenthalte mit Gästen bleiben zu den normalen Preisen. Jetzt `4` |
| `mindestpreisWoche` | Boden pro 7 Nächte in CHF (anteilig nach Nächten, aufgerundet), nur mit Gästen. Liegt der Gesamtpreis darüber, entfällt der Anteil der Familie so weit, wie der Preis nicht unter den Boden sinkt. Reicht der Preis, zahlt die Familie nichts, sonst nur den Rest bis zum Boden. Mehr Nächte oder Gäste werden dadurch nie günstiger. `0` schaltet die Regel ab |
| `festMonate` | Monate (Liste), in denen ein Aufenthalt der Familie nie provisorisch ist, sondern fest. Der Termin wird in Airbnb gesperrt (Anfrage-Text sagt es). Jetzt `[2]` (Februar). Gilt, sobald eine Nacht des Aufenthalts in einem dieser Monate liegt |
| `minNaechteMonat` | Mindestnächte pro Monat, zum Beispiel `{ "2": 7 }`: Jeder Aufenthalt mit mindestens einer Nacht im Februar braucht 7 Nächte (28.1. bis 4.2. ist ok, 31.1. bis 2.2. nicht) |
| `provisorisch` | `true`: Aufenthalte der Familie, die mindestens eine Nacht ausserhalb der Selbstreinigungs-Zeiten haben, gelten als Termin unter Vorbehalt (siehe unten). `false` schaltet die Funktion ab |
| `airbnbVorlaufTage` | Vorlaufzeit, die in Airbnb für neue Gäste eingestellt ist (aktuell 3). Ein provisorischer Aufenthalt gilt als «praktisch sicher», wenn die Abreise innerhalb dieser Tage liegt |

## Belegung aus Airbnb

- Die Datei `belegt.json` wird alle 3 Stunden automatisch aus dem Airbnb-Kalender erzeugt (Reiter «Actions», «Belegung aktualisieren»). Nicht von Hand ändern.
- Der Airbnb-Link steht nur als geheimer Eintrag `AIRBNB_ICAL` unter Settings, Secrets and variables, Actions.
- Von Hand starten: Reiter «Actions», «Belegung aktualisieren», «Run workflow».

## Bestätigung in der App

- Die Kinder senden die Anfrage per WhatsApp. Der Text enthält einen Link (`?b=Name_Anreise_Abreise_…`).
- Auf dem Handy der Eltern (GitHub-Token gespeichert, Schlüssel `tm_token` im Browser, nur dort) landet der Link unter «Offen». Knöpfe: Bestätigen, Ablehnen, «Fest machen» (bei provisorischen Terminen), Bescheid vermerken.
- Gespeichert wird in `buchungen.json` (wird von der App über die GitHub-API geschrieben, nicht von Hand ändern ausser zum Löschen von Testeinträgen). Felder pro Eintrag: `name`, `arr`, `dep`, `selbst`, `pers`, optional `status` (`"abgelehnt"`), `bescheid`, `prov` (`true` = provisorisch).
- Das Token läuft nach einem Jahr ab (aktuell ca. Oktober 2027) und muss dann neu erstellt werden.

## Termine unter Vorbehalt (provisorisch)

- Idee: Lücken füllen, die sonst leer blieben, ohne den Termin in Airbnb zu sperren. Ein Airbnb-Gast hat immer Vorrang, die Familie muss dann räumen oder gar nicht erst gehen. Normale Kosten.
- Gilt automatisch für alle Aufenthalte, die mindestens eine Nacht ausserhalb der Selbstreinigungs-Zeiten (`selbstReinigung`) haben. Reine Staffel-Aufenthalte (März/April, Oktober bis 18. Dezember) sind fest und werden in Airbnb gesperrt.
- Kalender: gestreifter Balken mit Umriss. Rote Umrandung = Konflikt, ein Airbnb-Gast hat inzwischen eine dieser Nächte gebucht. Grüner Haken im weissen Kreis = «praktisch sicher» (Abreise innert `airbnbVorlaufTage`, es kann kaum noch jemand buchen).
- Der Balken ist im sicheren Teil voll, im unsicheren schraffiert. Sicher sind alle Nächte vor «heute plus `airbnbVorlaufTage`», denn ein neuer Airbnb-Gast kann frühestens dann einchecken. Der volle Teil wächst jeden Tag. Liegt die Abreise innerhalb dieser Frist, ist der ganze Balken voll und das Häkchen erscheint. Anfrage, Hilfe und Warnung nennen das Datum («praktisch sicher am …»).
- Bei provisorischen Terminen lassen sich die Knöpfe «Per WhatsApp senden» und «Anfrage kopieren» erst nach dem Pflicht-Häkchen «Ich habe das Risiko verstanden» benutzen. Der Anfragetext enthält dann den Satz, dass das Risiko bestätigt wurde.
- «Fest machen» in der Bestätigungsliste entfernt die Markierung. Danach den Termin in Airbnb sperren.
- Provisorische Nächte sind für andere Familienmitglieder im Kalender belegt, zählen aber nicht für die Lückenberechnung.

## Hilfe im Kalender

Der schwebende «?»-Knopf (nur sichtbar, solange der Kalender im Bild ist) schaltet die Hilfe ein. Danach erklärt ein Tipp auf einen Tag, warum er so aussieht. Die Hilfe merkt sich ihren Zustand im Browser (`tm_hilfe`). Ausführliche Erklärungen stehen in der App unter «Anleitung», «Begriffe».

## Versionen und Rückkehr

- Bis 3.99 wurde in 0.01-Schritten gezählt, danach 1.0.0: letzte Stelle = kleine Änderung, mittlere = grössere Funktion, erste = grundlegender Umbau.
- Ältere Stände liegen als Branches auf GitHub: `stand-3.93` (vor der Kalender-Hilfe) und `stand-1.3.1` (vor den provisorischen Terminen). Zurück: `index.html` aus dem Branch übernehmen.

## Testmodus

Die App mit `?heute=2027-01-18` öffnen (zum Beispiel `https://waenu.github.io/Tschentomat/?heute=2027-01-18`): Sie rechnet dann so, als wäre dieser Tag heute. Oben erscheint eine rote Leiste mit ◀ und ▶ (ein Tag zurück oder vor) und «Echt». Es wird nichts gespeichert, ausser du bestätigst etwas auf dem Elterntelefon (das schreibt echt in `buchungen.json`). Für die Kinder ist der Modus nirgends sichtbar.
