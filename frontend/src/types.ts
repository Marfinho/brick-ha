/** Minimale Typen der Home-Assistant-Frontend-API (keine externen Imports). */

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
}

export interface Hass {
  states: Record<string, HassEntity | undefined>;
  language: string;
  locale?: { language: string };
  callService(
    domain: string,
    service: string,
    data?: Record<string, unknown>,
  ): Promise<unknown>;
}

export interface AnnounceConfig {
  media_player?: string;
  tts_entity?: string;
}

export interface BrickCardConfig {
  type: string;
  entity: string;
  week_entity?: string;
  title?: string;
  show_done?: boolean;
  show_announce_button?: boolean;
  announce?: AnnounceConfig;
}

export interface BrickItem {
  sport: string;
  title: string;
  durationMin: number;
  status: "planned" | "done" | string;
  date: string;
}

export interface LovelaceCard extends HTMLElement {
  hass?: Hass;
  setConfig(config: BrickCardConfig): void;
  getCardSize(): number;
}
