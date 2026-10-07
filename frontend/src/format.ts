import { localize } from "./localize";
import type { BrickItem, Hass } from "./types";

const SPORT_ICONS: Record<string, string> = {
  run: "mdi:run",
  bike: "mdi:bike",
  swim: "mdi:swim",
  strength: "mdi:dumbbell",
  mobility: "mdi:yoga",
  walk: "mdi:walk",
  brick: "mdi:weight-lifter",
  cross_training: "mdi:weight-lifter",
  rest: "mdi:sleep",
};

export function sportIcon(sport: string): string {
  return SPORT_ICONS[sport] ?? "mdi:heart-pulse";
}

/** "1 Std 20", "45 Min", "2 Std". Leer bei fehlender Dauer. */
export function formatDuration(hass: Hass | undefined, minutes: number): string {
  if (!Number.isFinite(minutes) || minutes <= 0) return "";
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  if (h === 0) return localize(hass, "minutes", { m });
  if (m === 0) return localize(hass, "hours", { h });
  return localize(hass, "hour_min", { h, m });
}

/** ISO-Datum (YYYY-MM-DD) ohne Zeitzonen-Verschiebung. */
export function parseDay(iso: string): Date | undefined {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!match) return undefined;
  return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]), 12);
}

export function toIso(date: Date): string {
  const p = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${p(date.getMonth() + 1)}-${p(date.getDate())}`;
}

export function readItems(value: unknown): BrickItem[] {
  if (!Array.isArray(value)) return [];
  return value.filter(
    (item): item is BrickItem =>
      typeof item === "object" && item !== null && "sport" in item,
  );
}
