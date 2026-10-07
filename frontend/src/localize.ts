import type { Hass } from "./types";

const STRINGS = {
  de: {
    title: "Brick Training",
    open_one: "1 Einheit offen",
    open_many: "{n} Einheiten offen",
    all_done: "Alles erledigt",
    nothing: "Heute ist nichts geplant",
    status_open: "offen",
    status_done: "erledigt",
    announce: "Ansagen",
    announced: "Ansage gestartet",
    announce_failed: "Ansage fehlgeschlagen",
    unavailable: "Brick ist gerade nicht verfügbar.",
    not_found: "Entität {entity} nicht gefunden.",
    week: "Nächste 7 Tage",
    hour_min: "{h} Std {m}",
    hours: "{h} Std",
    minutes: "{m} Min",
    editor_entity: "Entität „Training heute“",
    editor_week_entity: "Entität „Training Woche“ (optional)",
    editor_title: "Titel",
    editor_show_done: "Erledigte Einheiten anzeigen",
    editor_show_announce: "Knopf „Ansagen“ anzeigen",
    editor_media_player: "Lautsprecher für die Ansage",
    editor_tts_entity: "TTS-Dienst für die Ansage",
  },
  en: {
    title: "Brick Training",
    open_one: "1 session open",
    open_many: "{n} sessions open",
    all_done: "All done",
    nothing: "Nothing planned today",
    status_open: "open",
    status_done: "done",
    announce: "Announce",
    announced: "Announcement started",
    announce_failed: "Announcement failed",
    unavailable: "Brick is currently unavailable.",
    not_found: "Entity {entity} not found.",
    week: "Next 7 days",
    hour_min: "{h} h {m}",
    hours: "{h} h",
    minutes: "{m} min",
    editor_entity: "\"Training today\" entity",
    editor_week_entity: "\"Training week\" entity (optional)",
    editor_title: "Title",
    editor_show_done: "Show completed sessions",
    editor_show_announce: "Show \"Announce\" button",
    editor_media_player: "Speaker for the announcement",
    editor_tts_entity: "TTS service for the announcement",
  },
} as const;

export type Key = keyof (typeof STRINGS)["de"];

export function getLanguage(hass?: Hass): "de" | "en" {
  const lang = hass?.locale?.language ?? hass?.language ?? "en";
  return lang.toLowerCase().startsWith("de") ? "de" : "en";
}

export function localize(
  hass: Hass | undefined,
  key: Key,
  vars: Record<string, string | number> = {},
): string {
  let text: string = STRINGS[getLanguage(hass)][key];
  for (const [name, value] of Object.entries(vars)) {
    text = text.replaceAll(`{${name}}`, String(value));
  }
  return text;
}
