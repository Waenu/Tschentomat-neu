#!/usr/bin/env python3
"""Gästenamen aus dem Google-Kalender «Gäste Tschenten» in gaeste.json übernehmen.

Regeln (mit Wänu abgesprochen):
- Titel «<Name> belegt/belegen …»: alles vor « belegt»/« belegen» ist der Name. Andere Titel werden ignoriert.
- Anreise = Starttag, Abreise = letzter angezeigter Tag (Google speichert das Ende einen Tag später).
- Eintrag aus dem Kalender kommt als Typ «airbnb», markiert mit quelle=kalender und kal=<Name>.
- Von Hand eingetragene oder in der App geänderte Einträge werden NIE überschrieben (die App entfernt die Markierung beim Speichern).
- Überschneidet sich ein Kalendereintrag mit einer bestätigten Buchung im Tschentomat, gewinnt die Buchung:
  der Kalendereintrag wird übersprungen und ein früher von uns eingetragener wieder entfernt.
- Entfernen nur bei einwandfrei gelesenem Kalender, höchstens MAX_ENTFERNEN Einträge pro Lauf.
- Nur Einträge ab heute. Vergangene Einträge werden weder neu eingetragen noch angefasst.
- Keine Änderung, wenn der Kalender nicht eindeutig gelesen werden konnte.
"""
import argparse, json, os, re, sys, urllib.request, urllib.error
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

MAX_ENTFERNEN = 3
MARKER = re.compile(r"^\s*(.+?)\s+bel(?:egt|egen)\b", re.IGNORECASE)


def kurz(n):  # wie gastKurz() in der App
    return re.sub(r"\s+", " ", re.sub(r'[<>"&]', "", str(n or "")).strip())[:30]


def lesen_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "tschentomat-sync/1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace"), None
    except urllib.error.HTTPError as e:
        return None, ("http%d" % e.code)
    except Exception as e:  # Netzwerk, Zeitüberschreitung
        return None, "netz:" + e.__class__.__name__


def entfalten(text):
    return re.sub(r"\r?\n[ \t]", "", text).replace("\r\n", "\n").split("\n")


def unesc(s):
    return s.replace("\\n", " ").replace("\\N", " ").replace("\\,", ",").replace("\\;", ";").replace("\\\\", "\\")


def ics_ereignisse(text):
    """Liste von dicts: summary, start (date|None), end (date|None), ganztags, status, rrule"""
    zeilen = entfalten(text)
    ev, cur = [], None
    for z in zeilen:
        if z == "BEGIN:VEVENT":
            cur = {}
        elif z == "END:VEVENT":
            if cur is not None:
                ev.append(cur)
            cur = None
        elif cur is not None and ":" in z:
            kopf, wert = z.split(":", 1)
            name = kopf.split(";", 1)[0].upper()
            if name == "SUMMARY":
                cur["summary"] = unesc(wert)
            elif name in ("DTSTART", "DTEND"):
                ganz = "VALUE=DATE" in kopf.upper() and "DATE-TIME" not in kopf.upper() or re.fullmatch(r"\d{8}", wert.strip()) is not None
                try:
                    d = datetime.strptime(wert.strip()[:8], "%Y%m%d").date()
                except ValueError:
                    d = None
                cur["start" if name == "DTSTART" else "end"] = d
                if name == "DTSTART":
                    cur["ganztags"] = bool(ganz)
            elif name == "STATUS":
                cur["status"] = wert.strip().upper()
            elif name == "RRULE":
                cur["rrule"] = True
    return ev


def iso(d):
    return d.isoformat()


def ueberschneidet(a1, d1, a2, d2):
    """Nächte [a, d) überschneiden sich; fehlt die Abreise, zählt eine Nacht."""
    d1 = d1 or iso(date.fromisoformat(a1) + timedelta(days=1))
    d2 = d2 or iso(date.fromisoformat(a2) + timedelta(days=1))
    return a1 < d2 and a2 < d1


def abgleichen(gaeste, buchungen, ereignisse, heute):
    """Gibt (neue Liste, Meldungen) zurück. gaeste: Liste von dicts."""
    meld = []
    bestaetigt = [b for b in buchungen if b.get("status") != "abgelehnt" and b.get("arr") and b.get("dep")]
    ziel = {}   # arr -> dict(name, dep)
    for e in ereignisse:
        t = e.get("summary", "")
        if e.get("status") == "CANCELLED":
            continue
        if not e.get("start"):
            continue
        if e.get("rrule"):
            meld.append("Übersprungen (wiederkehrend): " + t)
            continue
        if not e.get("ganztags"):
            if MARKER.match(t):
                meld.append("Übersprungen (nicht ganztägig): " + t)
            continue
        m = MARKER.match(t)
        if not m:
            continue   # kein Gast-Eintrag
        name = kurz(m.group(1))
        if not name:
            continue
        arr = iso(e["start"])
        dep = None
        if e.get("end") and e["end"] - timedelta(days=1) > e["start"]:
            dep = iso(e["end"] - timedelta(days=1))
        if (dep or arr) < heute:
            continue   # vergangen
        if arr in ziel:
            meld.append("Doppelter Anreisetag %s, nur der erste zählt: %s" % (arr, t))
            continue
        ziel[arr] = {"name": name, "dep": dep}

    neu = [dict(x) for x in gaeste]
    entfernen = []

    for arr, z in sorted(ziel.items()):
        bu = next((b for b in bestaetigt if ueberschneidet(arr, z["dep"], b["arr"], b["dep"])), None)
        vorh = [x for x in neu if x.get("arr") == arr]
        if bu:
            meld.append("Übersprungen (bestätigte Buchung von %s %s bis %s): %s" % (bu.get("name"), bu["arr"], bu["dep"], z["name"]))
            continue
        if vorh:
            x = vorh[0]
            if x.get("quelle") == "kalender" and x.get("name") == x.get("kal") and x.get("typ") == "airbnb":
                aend = []
                if x.get("name") != z["name"]:
                    x["name"] = z["name"]; x["kal"] = z["name"]; aend.append("Name")
                if (x.get("dep") or None) != z["dep"]:
                    if z["dep"]:
                        x["dep"] = z["dep"]
                    else:
                        x.pop("dep", None)
                    aend.append("Abreise")
                if aend:
                    meld.append("Aktualisiert (%s): %s %s" % (", ".join(aend), z["name"], arr))
            else:
                meld.append("Übersprungen (Anreisetag %s ist schon von Hand eingetragen: %s): %s" % (arr, x.get("name"), z["name"]))
            continue
        e = {"arr": arr}
        if z["dep"]:
            e["dep"] = z["dep"]
        e.update({"name": z["name"], "typ": "airbnb", "quelle": "kalender", "kal": z["name"]})
        neu.append(e)
        meld.append("Neu: %s, %s bis %s" % (z["name"], arr, z["dep"] or "?"))

    # Früher von uns eingetragene Einträge prüfen: gelöscht im Kalender oder jetzt Tschentomat-Buchung?
    for x in list(neu):
        if x.get("quelle") != "kalender" or x.get("name") != x.get("kal") or x.get("typ") != "airbnb":
            continue
        if (x.get("dep") or x.get("arr")) < heute:
            continue
        grund = None
        if x["arr"] not in ziel:
            grund = "nicht mehr im Kalender"
        elif any(ueberschneidet(x["arr"], x.get("dep"), b["arr"], b["dep"]) for b in bestaetigt):
            grund = "jetzt bestätigte Buchung im Tschentomat"
        if grund:
            entfernen.append((x, grund))
    if entfernen:
        if len(entfernen) > MAX_ENTFERNEN:
            meld.append("WARNUNG: %d Einträge wären zu entfernen, das ist mehr als %d pro Lauf. Es wird nichts entfernt, bitte prüfen." % (len(entfernen), MAX_ENTFERNEN))
        else:
            for x, g in entfernen:
                neu.remove(x)
                meld.append("Entfernt (%s): %s %s" % (g, x.get("name"), x.get("arr")))

    neu.sort(key=lambda x: x.get("arr", ""))
    return neu, meld


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ics", help="ICS-Datei statt URL (Test)")
    ap.add_argument("--gaeste", default="gaeste.json")
    ap.add_argument("--buchungen", default="buchungen.json")
    ap.add_argument("--heute", help="YYYY-MM-DD (Test)")
    ap.add_argument("--dry", action="store_true", help="nichts schreiben")
    a = ap.parse_args()
    heute = a.heute or datetime.now(ZoneInfo("Europe/Zurich")).date().isoformat()

    if a.ics:
        text = open(a.ics, encoding="utf-8").read()
    else:
        url = os.environ.get("GAESTE_ICAL", "").strip()
        if not url:
            print("::notice::Secret GAESTE_ICAL ist nicht gesetzt, nichts zu tun.")
            return 0
        text, fehler = lesen_url(url)
        if fehler:
            if fehler.startswith("http4"):
                print("::error::Kalender nicht lesbar (%s). Ist die geheime Adresse noch gültig? Es wurde nichts geändert." % fehler)
                return 1
            print("::warning::Kalender vorübergehend nicht lesbar (%s). Es wurde nichts geändert." % fehler)
            return 0
    if "BEGIN:VCALENDAR" not in text or "END:VCALENDAR" not in text:
        print("::error::Antwort ist kein Kalender. Es wurde nichts geändert.")
        return 1

    roh = open(a.gaeste, encoding="utf-8").read()
    daten = json.loads(roh)
    gaeste = daten["gaeste"] if isinstance(daten, dict) and isinstance(daten.get("gaeste"), list) else None
    if gaeste is None:
        print("::error::gaeste.json hat ein unerwartetes Format. Es wurde nichts geändert.")
        return 1
    try:
        buch = json.load(open(a.buchungen, encoding="utf-8")).get("buchungen", [])
    except Exception:
        print("::error::buchungen.json nicht lesbar. Es wurde nichts geändert.")
        return 1

    neu, meld = abgleichen(gaeste, buch, ics_ereignisse(text), heute)
    for m in meld:
        print(m)
    if neu == gaeste:
        print("Keine Änderung.")
        return 0
    if a.dry:
        print("(Testlauf, nichts geschrieben)")
        return 0
    daten["gaeste"] = neu
    open(a.gaeste, "w", encoding="utf-8").write(json.dumps(daten, indent=2, ensure_ascii=False) + "\n")
    print("gaeste.json aktualisiert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
