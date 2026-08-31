# Setup-Anleitung: Forms → OneDrive → Excel → Power Automate

Ziel: Consultant-Antworten landen automatisch in einer Excel-Tabelle auf OneDrive.
Voraussetzung: Microsoft 365 Lizenz (Forms, Power Automate, OneDrive, Excel Online, Outlook).

---

## Teil 1: OneDrive-Ablage einrichten

**Warum OneDrive statt SharePoint?**
Ohne eigene SharePoint-Site ist OneDrive for Business die einfachste Alternative.
Power Automate unterstützt OneDrive for Business als nativen Connector — kein Workaround nötig.
Hinweis: Die Datei liegt in deinem persönlichen Storage. Teile den Ordner manuell mit
deinem Vertreter, damit er bei Abwesenheit Zugriff hat.

### Schritt 1 — Ordner in OneDrive anlegen

1. Öffne **onedrive.live.com** oder OneDrive in deinem M365-Browser
2. Klicke auf `+ Neu` → **Ordner**
3. Name: `ConsultantPulse`
4. Öffne den Ordner

### Schritt 2 — Excel-Datei anlegen

1. Im Ordner `ConsultantPulse`: `+ Neu` → **Excel-Arbeitsmappe**
2. Name: `pulse_data`
3. Die Datei öffnet sich direkt in Excel Online

### Schritt 3 — Excel-Sheets und Tabellen anlegen

**Sheet 1 umbenennen:**
- Rechtsklick auf `Tabelle1` → **Umbenennen** → `WeeklyPulse`

**Sheet 2 anlegen:**
- Klicke unten auf `+` → **Umbenennen** → `MonthlyConsultant`

**Sheet 3 anlegen:**
- Wieder `+` → **Umbenennen** → `MonthlyLead`

### Schritt 4 — Tabellenstruktur in Sheet "WeeklyPulse"

> **Wichtig**: Power Automate braucht formatierte Excel-Tabellen, keine rohen Zellen.

1. Klicke auf Sheet **WeeklyPulse** → Zelle **A1**
2. Trage folgende Überschriften ein (je eine pro Spalte, A bis F):

```
A1: Timestamp
B1: ConsultantName
C1: Workload
D1: BlockerYN
E1: BlockerText
F1: CallNeeded
```

3. Markiere Zellen **A1 bis F1**
4. Menü: **Einfügen** → **Tabelle** → ☑ Tabelle hat Überschriften → **OK**
5. Tabellenname (oben links, Menü Tabellenentwurf) auf `WeeklyPulse` setzen

**Wiederhole Schritt 4 für Sheet "MonthlyConsultant":**

Spalten A bis H:
```
A1: Timestamp
B1: ConsultantName
C1: Workload
D1: Engagement
E1: Motivation
F1: Delivery
G1: SkillAlignment
H1: TaskChallenge
I1: ManagerNeeds
```
Tabellenname: `MonthlyConsultant`

**Wiederhole Schritt 4 für Sheet "MonthlyLead":**

Spalten A bis G:
```
A1: Timestamp
B1: ConsultantName
C1: Reliability
D1: Proactivity
E1: SkillFit
F1: ProjectStatus
G1: Risks
```
Tabellenname: `MonthlyLead`

**Excel Online speichert automatisch** — kein manuelles Speichern nötig.

---

## Teil 2: Microsoft Forms anlegen

Öffne in einem neuen Tab: **forms.microsoft.com**

### Form 1 — Wöchentlicher Puls (Consultant)

**3 Fragen, ca. 60 Sekunden Aufwand.**

1. Klicke auf `+ Neues Formular` → Titel: `Wöchentlicher Puls`

**Frage 1 — Workload:**
- Typ: **Bewertung**, Stufen: **5**
- Text: `How would you rate your workload this week?`
- Links: `very low`, Rechts: `overloaded`
- ☑ Erforderlich

**Frage 2 — Blocker (Ja/Nein):**
- Typ: **Auswahl**
- Text: `Is there anything currently blocking you?`
- Optionen: `Yes` und `No`
- ☑ Erforderlich

**Frage 3 — Blocker Text:**
- Typ: **Text**, mehrzeilig
- Text: `If yes: What is blocking you? (Please do not mention names or projects)`
- ☐ Nicht erforderlich

**Frage 4 — Call:**
- Typ: **Auswahl**
- Text: `Would you like a quick call with me this week?`
- Optionen: `Yes` und `No`
- ☑ Erforderlich

**Einstellungen** (Zahnrad-Symbol oben rechts):
- ☑ Anmeldung erforderlich
- ☐ Anonyme Antworten — **deaktiviert**
- ☑ Mehrfache Antworten zulassen — **aktiviert** (wöchentliche Nutzung erfordert mehrfache Antworten)

---

### Form 2 — Monatliches Self-Assessment (Consultant)

**Einmal pro Monat — hier landen auch Engagement, Motivation und Delivery.**

1. `+ Neues Formular` → Titel: `Monatliches Self-Assessment`

**Frage 1 — Workload (Monatlicher Rückblick):**
- Typ: **Bewertung**, Stufen: 5
- Text: `How would you rate your average workload this month?`
- Links: `very low`, Rechts: `overloaded`
- ☑ Erforderlich

**Frage 2 — Engagement:**
- Typ: **Bewertung**, Stufen: 5
- Text: `How engaged have you felt in your work this month?`
- Links: `barely engaged`, Rechts: `highly engaged`
- ☑ Erforderlich

**Frage 3 — Motivation:**
- Typ: **Bewertung**, Stufen: 5
- Text: `How motivated are you for your current tasks?`
- Links: `not at all`, Rechts: `highly motivated`
- ☑ Erforderlich

**Frage 4 — Delivery:**
- Typ: **Bewertung**, Stufen: 5
- Text: `How well did you deliver what was planned this month?`
- Links: `barely delivered`, Rechts: `fully delivered`
- ☑ Erforderlich

**Frage 5 — Skill Alignment:**
- Typ: **Bewertung**, Stufen: 5
- Text: `How well do you feel your skills are being used in your current project?`
- Links: `completely misaligned`, Rechts: `perfectly aligned`
- ☑ Erforderlich

**Frage 6 — Task Challenge:**
- Typ: **Bewertung**, Stufen: 5
- Text: `Are your current tasks challenging you at the right level?`
- Links: `clearly underchallenged`, Rechts: `clearly overwhelmed`
- ☑ Erforderlich

**Frage 7 — Manager Needs:**
- Typ: **Text**, mehrzeilig
- Text: `Is there anything you need from me as your manager?`
- ☐ Nicht erforderlich

**Einstellungen** (Zahnrad-Symbol oben rechts):
- ☑ Anmeldung erforderlich
- ☐ Anonyme Antworten — **deaktiviert**
- ☑ Mehrfache Antworten zulassen — **aktiviert** (monatliche Nutzung erfordert mehrfache Antworten)

---

### Form 3 — Project Lead Report

1. `+ Neues Formular` → Titel: `Project Lead Report`

**Frage 1 — Consultant Name:**
- Typ: **Text**
- Text: `Which consultant are you filling this form for?`
- ☑ Erforderlich

**Frage 2 — Reliability:**
- Typ: **Bewertung**, Stufen: 5
- Text: `How reliably does the consultant deliver their tasks?`
- Links: `rarely`, Rechts: `consistently reliable`
- ☑ Erforderlich

**Frage 3 — Proactivity:**
- Typ: **Bewertung**, Stufen: 5
- Text: `How proactively does the consultant contribute on their own initiative?`
- Links: `little self-initiative`, Rechts: `highly proactive`
- ☑ Erforderlich

**Frage 4 — Skill Fit:**
- Typ: **Bewertung**, Stufen: 5
- Text: `How well does the consultant's skill profile match the project requirements?`
- Links: `poor fit`, Rechts: `excellent fit`
- ☑ Erforderlich

**Frage 5 — Project Status:**
- Typ: **Bewertung**, Stufen: 5
- Text: `How do you rate the current project status?`
- Links: `critical`, Rechts: `very good`
- ☑ Erforderlich

**Frage 6 — Risks:**
- Typ: **Text**, mehrzeilig
- Text: `Are there any risks or need for escalation?`
- ☐ Nicht erforderlich

**Einstellungen** (Zahnrad-Symbol oben rechts):
- ☑ Anmeldung erforderlich
- ☐ Anonyme Antworten — **deaktiviert**
- ☑ Mehrfache Antworten zulassen — **aktiviert** (PLs füllen das Form für mehrere Consultants aus)

---

## Teil 3: Power Automate — Forms mit Excel verbinden

Öffne in einem neuen Tab: **make.powerautomate.com**

Du erstellst drei Flows — einen pro Formular. Die Logik ist identisch,
nur Formular und Excel-Tabelle wechseln.

---

### Flow 1 — Wöchentlicher Puls → WeeklyPulse

**Flow erstellen:**
1. Linke Leiste: **Erstellen**
2. Wähle: **Automatisierter Cloud-Flow**
3. Name: `Form1 WeeklyPulse → Excel`
4. Trigger: `Microsoft Forms — Wenn eine neue Antwort übermittelt wird` → **Erstellen**

**Trigger konfigurieren:**
- `Formular-ID`: Wähle `Wöchentlicher Puls`

**Schritt 1 hinzufügen:**
- `Microsoft Forms — Antwortdetails abrufen`
- Formular-ID: `Wöchentlicher Puls`
- Antwort-ID: Dynamisch → `Antwort-ID` (aus Trigger)

**Schritt 2 hinzufügen:**
- `Excel Online (Business) — Zeile zu Tabelle hinzufügen`

**Excel-Verbindung konfigurieren:**
- `Ort`: **OneDrive for Business**
- `Dokumentbibliothek`: `OneDrive`
- `Datei`: Navigiere zu `ConsultantPulse/pulse_data.xlsx`
- `Tabelle`: `WeeklyPulse`

**Spalten zuordnen:**

| Spalte | Dynamischer Wert |
|---|---|
| Timestamp | Ausdruck: `utcNow()` |
| ConsultantName | `Angezeigter Name des Befragten` |
| Workload | Frage 1 |
| BlockerYN | Frage 2 |
| BlockerText | Frage 3 |
| CallNeeded | Frage 4 |

**Speichern und testen** — Flow testen, Testantwort abschicken, Zeile in Excel prüfen.

---

### Flow 2 — Monatliches Self-Assessment → MonthlyConsultant

Identisch zu Flow 1 — nur diese Unterschiede:

- Flow-Name: `Form2 MonthlyConsultant → Excel`
- Trigger-Formular: `Monatliches Self-Assessment`
- Excel-Tabelle: `MonthlyConsultant`
- Spalten: Timestamp, ConsultantName, Workload (F1), Engagement (F2), Motivation (F3), Delivery (F4), SkillAlignment (F5), TaskChallenge (F6), ManagerNeeds (F7)

---

### Flow 3 — Project Lead Report → MonthlyLead

Identisch zu Flow 1 — nur diese Unterschiede:

- Flow-Name: `Form3 MonthlyLead → Excel`
- Trigger-Formular: `Project Lead Report`
- Excel-Tabelle: `MonthlyLead`
- Spalten: Timestamp, ConsultantName, Reliability, Proactivity, SkillFit, ProjectStatus, Risks

---

### Flow 4 — Monatlicher Versand der PL-Links (Scheduler)

Dieser Flow läuft automatisch am 1. eines Monats und schickt jedem Project Lead
personalisierte Links für jeden seiner Consultants.

**Flow erstellen:**
1. **Erstellen** → **Geplanter Cloud-Flow**
2. Name: `Monthly PL Report Versand`
3. Startdatum: nächster 1. des Monats
4. Wiederholen: alle **1 Monat**

**Schritt 1 — Variable definieren:**
- `Variablen — Variable initialisieren`
- Name: `ConsultantList`, Typ: **Array**
- Wert (Ausdruck):

```json
[
  {"name": "Max Mustermann", "pl_email": "pl.name@firma.de"},
  {"name": "Erika Muster",   "pl_email": "pl.name@firma.de"},
  {"name": "John Doe",       "pl_email": "andere.pl@firma.de"}
]
```

> Trage hier alle 17 Consultants mit dem E-Mail ihrer jeweiligen PLs ein.
> Diese Liste pflegst du manuell — sie enthält PII, daher nur in Power Automate,
> nie im Code-Repository.

**Schritt 2 — Loop:**
- `Steuerung — Auf jeden anwenden` → Variable `ConsultantList`

**Schritt 3 — E-Mail (innerhalb des Loops):**
- `Outlook — E-Mail senden (V2)`
- `An`: `items('Auf_jeden_anwenden')?['pl_email']`
- `Betreff`: `Monatliches Feedback erbeten`
- `Text`: Formular-Link mit vorausgefülltem Consultant-Namen

**Formular-Link mit vorausgefülltem Namen:**
1. forms.microsoft.com → Form 3 → `Teilen` → `Vorausfüll-Link`
2. Testweise ausfüllen → Link kopieren
3. Ersetze den eingetragenen Namen durch: `items('Auf_jeden_anwenden')?['name']`

---

## Überblick: Was automatisch passiert

```
Jede Woche (manuell per E-Mail oder Teams-Nachricht versenden):
  Consultant öffnet Form 1-Link (3 Fragen, 60 Sek.)
  → Power Automate Flow 1 → neue Zeile in WeeklyPulse (OneDrive)

Jeden Monat (manuell versenden):
  Consultant öffnet Form 2-Link (7 Fragen, 5 Min.)
  → Power Automate Flow 2 → neue Zeile in MonthlyConsultant (OneDrive)

Jeden Monat (am 1., automatisch):
  Power Automate Flow 4 → E-Mail an PLs mit personalisiertem Form 3-Link
  PL öffnet Link → füllt Formular aus
  → Power Automate Flow 3 → neue Zeile in MonthlyLead (OneDrive)

Danach (manuell, wenn alle geantwortet haben):
  Python-Aggregator liest pulse_data.xlsx
  → anonymisiert → aggregiert → schreibt JSON
  → React Dashboard zeigt Ergebnisse
```

---

## Häufige Fehlerquellen

| Problem | Ursache | Lösung |
|---|---|---|
| Excel-Spalten erscheinen nicht in Power Automate | Tabelle nicht als Tabelle formatiert | Schritt 4 wiederholen, Tabellenname prüfen |
| "Angezeigter Name" ist leer | Form erlaubt anonyme Antworten | Einstellungen → Anmeldung erforderlich aktivieren |
| Flow findet Excel-Datei nicht | Falscher OneDrive-Pfad | Datei neu über Ordner-Symbol auswählen |
| Testzeile hat leere Spalten | Falsche Frage im Dynamischen Inhalt gewählt | Fragentext im Dropdown genau prüfen |
| OneDrive-Connector fehlt | Fehlende Verbindung | Power Automate → Verbindungen → OneDrive for Business hinzufügen |
