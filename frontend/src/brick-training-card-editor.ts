import { LitElement, html, nothing, type TemplateResult } from "lit";
import { localize, type Key } from "./localize";
import type { BrickCardConfig, Hass } from "./types";

interface FormData {
  entity?: string;
  week_entity?: string;
  title?: string;
  show_done?: boolean;
  show_announce_button?: boolean;
  media_player?: string;
  tts_entity?: string;
}

const SCHEMA = [
  { name: "entity", required: true, selector: { entity: { domain: "sensor", integration: "brick" } } },
  { name: "week_entity", selector: { entity: { domain: "sensor", integration: "brick" } } },
  { name: "title", selector: { text: {} } },
  { name: "show_done", selector: { boolean: {} } },
  { name: "show_announce_button", selector: { boolean: {} } },
  { name: "media_player", selector: { entity: { domain: "media_player" } } },
  { name: "tts_entity", selector: { entity: { domain: "tts" } } },
] as const;

const LABELS: Record<string, Key> = {
  entity: "editor_entity",
  week_entity: "editor_week_entity",
  title: "editor_title",
  show_done: "editor_show_done",
  show_announce_button: "editor_show_announce",
  media_player: "editor_media_player",
  tts_entity: "editor_tts_entity",
};

export class BrickTrainingCardEditor extends LitElement {
  static override properties = {
    hass: { attribute: false },
    _config: { state: true },
  };

  declare hass?: Hass;
  declare _config?: BrickCardConfig;

  setConfig(config: BrickCardConfig): void {
    this._config = config;
  }

  protected override render(): TemplateResult | typeof nothing {
    if (!this._config) return nothing;
    const c = this._config;
    const data: FormData = {
      entity: c.entity,
      week_entity: c.week_entity,
      title: c.title,
      show_done: c.show_done ?? true,
      show_announce_button: c.show_announce_button ?? true,
      media_player: c.announce?.media_player,
      tts_entity: c.announce?.tts_entity,
    };
    return html`<ha-form
      .hass=${this.hass}
      .data=${data}
      .schema=${SCHEMA}
      .computeLabel=${(s: { name: string }) => localize(this.hass, LABELS[s.name] ?? "title")}
      @value-changed=${this._changed}
    ></ha-form>`;
  }

  private _changed = (ev: CustomEvent<{ value: FormData }>): void => {
    ev.stopPropagation();
    const v = ev.detail.value;
    const config: BrickCardConfig = {
      type: this._config?.type ?? "custom:brick-training-card",
      entity: v.entity ?? "",
    };
    if (v.week_entity) config.week_entity = v.week_entity;
    if (v.title) config.title = v.title;
    config.show_done = v.show_done ?? true;
    config.show_announce_button = v.show_announce_button ?? true;
    if (v.media_player || v.tts_entity) {
      config.announce = {
        ...(v.media_player ? { media_player: v.media_player } : {}),
        ...(v.tts_entity ? { tts_entity: v.tts_entity } : {}),
      };
    }
    this._config = config;
    this.dispatchEvent(
      new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true }),
    );
  };
}
