# Brick für Home Assistant

Home-Assistant-Integration (HACS) und Lovelace-Karte für **Brick**, deinen Triathlon-Trainer.
Sie zeigt dein heutiges, morgiges und wöchentliches Training an, bietet einen Trainingskalender und
kann dir den Plan über deinen Lautsprecher ansagen.

> Die Integration nutzt ausschließlich die dokumentierte Brick-API (`/api/voice/v1/summary` und
> `/api/calendar/v1/training.ics`). Sie fragt keine Gesundheitsdaten ab, sendet keine Telemetrie und
> verwendet keine KI-/Cloud-Dienste außer deiner Brick-Instanz und dem von dir gewählten TTS.

<!-- Platzhalter für Screenshots -->
| Karte | Sensoren | Kalender |
| --- | --- | --- |
| ![Karte](docs/screenshots/card.png) | ![Sensoren](docs/screenshots/sensors.png) | ![Kalender](docs/screenshots/calendar.png) |

## Funktionen

| Entität | Beschreibung |
| --- | --- |
| `sensor.brick_training_heute` | Zustand: Zahl **offener** Einheiten heute. Attribute: `text`, `items`, `done_count`, `date` |
| `sensor.brick_training_morgen` | Wie oben für morgen |
| `sensor.brick_training_woche` | Zustand: Zahl geplanter Einheiten in den nächsten 7 Tagen. Attribute: `text`, `items` |
| `binary_sensor.brick_training_offen` | An, solange heute noch mindestens eine Einheit geplant ist |
| `calendar.brick_training` | Trainingsplan und Wettkämpfe (nur mit Kalender-Quelle) |

Ruhetage (`rest`) zählen nicht als Einheit. Der Sprechtext steht im Attribut `text` (nicht im Zustand, da
Zustände auf 255 Zeichen begrenzt sind). Services: `brick.announce` und `brick.refresh`.
Dazu kommt die Karte `brick-training-card`, die mit der Integration automatisch geladen wird.

## Installation per HACS

1. HACS → Integrationen → Menü (⋮) → **Benutzerdefinierte Repositories**.
2. Repository `https://github.com/Marfinho/brick-ha`, Kategorie **Integration** hinzufügen.
3. „Brick“ installieren und Home Assistant neu starten.

Manuell: den Ordner `custom_components/brick` nach `<config>/custom_components/brick` kopieren.

## Token in Brick erzeugen

Die Integration kann Tokens nicht selbst erzeugen. Öffne in Brick **Profil → Gekoppelte Geräte** und
erzeuge dort:

* ein Token mit Scope **voice** (Pflicht) für Training heute/morgen/Woche und die Ansage,
* optional ein Token mit Scope **calendar** für den Kalender.

Tokens beginnen mit `lht_` und werden nur **einmal** angezeigt. Ein Kalender-Token öffnet nicht den
Summary-Endpunkt und umgekehrt.

## Einrichtung

**Einstellungen → Geräte & Dienste → Integration hinzufügen → Brick**

| Feld | Bedeutung |
| --- | --- |
| Brick-URL | z. B. `https://brick.example` (mit `https://`, ohne `/` am Ende) |
| Sprachassistent-Token | Token mit Scope *voice* |
| Kalender-URL oder -Token | Optional: komplette ICS-URL (`…/training.ics?token=lht_…`) oder nur das Kalender-Token |

Beim Anlegen ruft die Integration einmal den Summary-Endpunkt ab. Bei `http://` außerhalb deines lokalen
Netzes erscheint eine Warnung, da das Token dann unverschlüsselt übertragen würde. Du kannst sie bewusst
mit erneutem Absenden bestätigen.

* **Optionen:** Abfrageintervall (Standard 15 Minuten, Minimum 5). Jeder Zyklus braucht drei Abfragen
  (heute, morgen, Woche); bei Brick gelten 30 Abfragen pro Minute je Token.
* **Neu konfigurieren:** URL und Kalender-Quelle ändern (⋮ am Eintrag → *Neu konfigurieren*).
* **Token erneuern:** Wird das Token abgelehnt (`401`), startet Home Assistant automatisch den
  Reauth-Dialog.

## Lovelace-Karte

Die Karte wird von der Integration automatisch als Ressource geladen; es ist nichts von Hand einzutragen.

```yaml
type: custom:brick-training-card
entity: sensor.brick_training_heute
week_entity: sensor.brick_training_woche   # optional: 7-Tage-Streifen
title: Training                            # optional
show_done: true                            # erledigte Einheiten zeigen (Standard: true)
show_announce_button: true                 # Knopf „Ansagen“ (Standard: true)
announce:                                  # Box für den Knopf
  media_player: media_player.kueche
  tts_entity: tts.home_assistant_cloud
```

Der Knopf „Ansagen“ erscheint nur, wenn `announce.media_player` gesetzt ist. Die Karte hat einen visuellen
Editor, verwendet nur Theme-Variablen (hell und dunkel) und ist auf Deutsch und Englisch verfügbar.
Sie macht keine externen Anfragen.

## Services

### `brick.announce`

Ruft frische Daten ab und spricht den Plan.

```yaml
action: brick.announce
data:
  day: today            # today | tomorrow | week
  detail: normal        # short | normal (normal: mit Form und Wettkampf-Countdown)
  media_player: [media_player.kueche]
  tts_entity: tts.home_assistant_cloud
  volume: 0.5           # optional, 0 bis 1
  restore_volume: true  # Standard: true
```

Die Lautstärke wird gesetzt, `tts.speak` (Sprache `de`) aufgerufen, bis zum Ende der Ausgabe gewartet
(mit Timeout) und die alte Lautstärke wiederhergestellt. Ist Brick nicht erreichbar, sagt die Box:
„Das Training konnte gerade nicht abgerufen werden.“

**Alexa (Alexa Media Player):** Statt `tts_entity` den Notify-Dienst angeben:

```yaml
action: brick.announce
data:
  notify_service: notify.alexa_media_echo_kueche
  media_player: [media_player.echo_kueche]   # optional, für Lautstärke und Ziel
```

> ⚠️ *Alexa Media Player* ist eine **inoffizielle** Integration, die die Alexa-Weboberfläche nutzt. Amazon
> kann sie jederzeit ändern oder sperren; dann fällt die Alexa-Ansage aus. Ein Alexa-Skill ist nicht Teil
> dieses Projekts.

### `brick.refresh`

Aktualisiert sofort, höchstens alle 30 Sekunden (zu frühe Aufrufe werden übersprungen).

## Automationsbeispiel: Morgenansage

```yaml
automation:
  - alias: Brick Morgenansage
    triggers:
      - trigger: time
        at: "07:15:00"
    conditions:
      - condition: state
        entity_id: binary_sensor.brick_training_offen
        state: "on"
    actions:
      - action: brick.announce
        data:
          day: today
          detail: normal
          media_player: [media_player.kueche]
          tts_entity: tts.home_assistant_cloud
          volume: 0.45
```

## Fehlersuche

| Problem | Lösung |
| --- | --- |
| „Das Token wurde abgelehnt“ | Token muss Scope *voice* haben, darf nicht widerrufen sein und ist ein Token, kein Kalender-Token. Neu erzeugen und Reauth durchführen. |
| „Brick ist nicht erreichbar“ | URL mit `https://`, ohne Slash am Ende; ist Brick von Home Assistant aus erreichbar (DNS, Firewall, Zertifikat)? |
| Sensoren „nicht verfügbar“ | Siehe *Einstellungen → System → Protokolle*. Bei `429` wartet die Integration die von Brick genannte Zeit ab. |
| Kalender fehlt | Er wird nur angelegt, wenn bei der Einrichtung eine Kalender-URL/-Token angegeben ist (nachträglich über *Neu konfigurieren*). |
| Karte lädt nicht | Browser-Cache leeren (Strg+F5). Die Karte wird als `/brick_static/brick-training-card.js` ausgeliefert. |
| Keine Ansage | Prüfe `tts_entity` und Lautsprecher; bei Alexa: *Alexa Media Player* eingerichtet? Zeit für Start und Ende der Ausgabe ist begrenzt (10 s bzw. 2 min). |

Diagnosedaten (*Gerät → Diagnose herunterladen*) enthalten keine Tokens oder URLs. Tokens werden nie
geloggt.

## Entwicklung

```bash
# Python
pip install -r requirements_test.txt
ruff check . && ruff format --check . && mypy && pytest

# Karte (TypeScript + Lit)
cd frontend
npm ci
npm run typecheck && npm test && npm run build   # schreibt custom_components/brick/dist/brick-training-card.js
```

Die Build-Ausgabe ist eingecheckt, damit HACS ohne Build funktioniert; die CI prüft, dass sie zum Quelltext passt.

Lizenz: MIT
