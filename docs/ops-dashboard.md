# Ops-Anleitung: Dashboard einrichten und betreiben

Ziel: Das consultant-pulse Dashboard auf einem neuen Rechner einrichten
und nach jeder Erhebungsperiode mit echten Daten aktualisieren.

Voraussetzung: Git, Python 3.12+, Node.js 18+ installiert.

---

## Teil 1: Einrichtung (einmalig)

### Schritt 1 — Repository klonen

```bash
git clone https://github.com/JohnHapke/consultant_pulse.git
cd consultant_pulse
```

### Schritt 2 — Python-Umgebung einrichten

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Schritt 3 — Frontend-Dependencies installieren

```bash
cd frontend
npm install
cd ..
```

### Schritt 4 — Consultant-Map anlegen

Die Datei `config/consultant_map.yaml` enthält die echten Namen und ist gitignored.
Sie wird **nicht** aus dem Repository geladen — du erhältst sie per E-Mail oder Teams.

Lege sie manuell an:

```bash
# Windows: mit Editor öffnen
notepad config\consultant_map.yaml

# Mac/Linux:
nano config/consultant_map.yaml
```

Format:

```yaml
consultants:
  - id: C01
    name: Max Mustermann              # Form 3: pre-filled name (exakt wie in Power Automate Flow 4)
    email: max.mustermann@firma.de    # Form 1+2: M365-E-Mail-Adresse des Consultants
  - id: C02
    name: Erika Muster
    email: erika.muster@firma.de
  # ... bis C17
```

> **Warum beides?**
> Forms 1 + 2 werden vom Consultant selbst ausgefüllt — Power Automate erfasst dabei
> die M365-E-Mail-Adresse als Identifier.
> Form 3 wird vom Project Lead ausgefüllt — der Consultant-Name ist per URL vorausgefüllt
> (Power Automate Flow 4). Der Aggregator sucht daher je nach Formular entweder
> nach E-Mail oder nach Name — beide müssen in der YAML stehen.
>
> Die Reihenfolge der Einträge ist irrelevant.
> Diese Datei wird einmalig angelegt und nur bei Teamveränderungen angepasst.

---

## Teil 2: Wöchentliche Aktualisierung

### Schritt 1 — Excel von OneDrive herunterladen

1. Öffne OneDrive → Ordner `ConsultantPulse`
2. Lade `pulse_data.xlsx` herunter
3. Speichere sie lokal, z.B. unter `~/Downloads/pulse_data.xlsx`

### Schritt 2 — Aggregator ausführen

```bash
source venv/bin/activate        # Windows: venv\Scripts\activate

python backend/src/aggregator.py \
  --excel ~/Downloads/pulse_data.xlsx \
  --consultant-map config/consultant_map.yaml \
  --week 2026-W17 \
  --output frontend/public/data
```

> Ersetze `2026-W17` durch die aktuelle ISO-Woche.
> Format: `YYYY-WNN` — z.B. `2026-W17` für Woche 17 im Jahr 2026.
> Die aktuelle Wochennummer: [whatweek.com](https://whatweek.com) oder
> in Excel: `=ISOWEEKNUM(HEUTE())`

### Schritt 3 — Dashboard starten

```bash
cd frontend
npm run serve
```

Browser öffnet sich auf `http://localhost:8080`.

---

## Teil 3: Monatliche Aktualisierung

Identisch zu Teil 2 — nur `--week` durch `--month` ersetzen:

```bash
python backend/src/aggregator.py \
  --excel ~/Downloads/pulse_data.xlsx \
  --consultant-map config/consultant_map.yaml \
  --month 2026-04 \
  --output frontend/public/data
```

> Format: `YYYY-MM` — z.B. `2026-04` für April 2026.

Danach `npm run serve` wie gehabt.

---

## Teil 4: Kollege einrichten (einmalig)

Dein Vertreter richtet sich das Dashboard identisch ein (Schritte 1–4 aus Teil 1).
Zusätzlich:

- **consultant_map.yaml**: Per E-Mail oder Teams schicken — nicht über GitHub
- **Excel**: Zugriff auf den freigegebenen OneDrive-Ordner `ConsultantPulse` einrichten
  (OneDrive → Ordner → Teilen → Personen mit Link)

Dein Vertreter führt danach bei Bedarf selbst Schritt 2–3 aus Teil 2 aus.

---

## Häufige Fehlerquellen

| Problem | Ursache | Lösung |
|---|---|---|
| `MapperError: Unknown consultant` | Name in Excel stimmt nicht mit `consultant_map.yaml` überein | Namen in der YAML exakt an M365-Anzeigenamen anpassen |
| `AggregatorError: No weekly entries` | Falsche Woche angegeben oder keine Einträge in diesem Zeitraum | ISO-Woche prüfen, Timestamps in Excel kontrollieren |
| `ModuleNotFoundError` | venv nicht aktiviert | `source venv/bin/activate` ausführen |
| Dashboard zeigt alte Daten | Browser-Cache | F5 oder Strg+Shift+R (Hard Refresh) |
| `bool_true/false` Mismatch | Forms schreibt `Ja`/`Nein` statt `Yes`/`No` | `config/fields.yaml` → `bool_true`/`bool_false` anpassen |
