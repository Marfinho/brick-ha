import { LitElement, css, html, nothing, type TemplateResult } from "lit";
import { formatDuration, parseDay, readItems, sportIcon, toIso } from "./format";
import { getLanguage, localize } from "./localize";
import type { BrickCardConfig, BrickItem, Hass, HassEntity } from "./types";

const UNAVAILABLE = new Set(["unavailable", "unknown"]);

export class BrickTrainingCard extends LitElement {
  static override properties = {
    hass: { attribute: false },
    _config: { state: true },
    _feedback: { state: true },
  };

  declare hass?: Hass;
  declare _config?: BrickCardConfig;
  declare _feedback?: string;

  static getConfigElement(): HTMLElement {
    return document.createElement("brick-training-card-editor");
  }

  static getStubConfig(hass?: Hass): Partial<BrickCardConfig> {
    const entity =
      Object.keys(hass?.states ?? {}).find((id) => id.startsWith("sensor.brick_training_heute")) ??
      "sensor.brick_training_heute";
    const week = Object.keys(hass?.states ?? {}).find((id) =>
      id.startsWith("sensor.brick_training_woche"),
    );
    return { entity, ...(week ? { week_entity: week } : {}) };
  }

  setConfig(config: BrickCardConfig): void {
    if (!config || typeof config.entity !== "string" || !config.entity) {
      throw new Error("entity is required");
    }
    this._config = {
      show_done: true,
      show_announce_button: true,
      ...config,
    };
  }

  getCardSize(): number {
    const items = this._items(this._stateObj()).length;
    return 2 + Math.min(items, 6) + (this._config?.week_entity ? 2 : 0);
  }

  getGridOptions() {
    return { columns: 12, min_columns: 6, min_rows: 3 };
  }

  private _stateObj(): HassEntity | undefined {
    return this._config ? this.hass?.states[this._config.entity] : undefined;
  }

  private _items(stateObj: HassEntity | undefined): BrickItem[] {
    return readItems(stateObj?.attributes.items);
  }

  private _t(key: Parameters<typeof localize>[1], vars?: Record<string, string | number>) {
    return localize(this.hass, key, vars);
  }

  protected override render(): TemplateResult | typeof nothing {
    if (!this._config || !this.hass) return nothing;
    const config = this._config;
    const title = config.title ?? this._t("title");
    const stateObj = this._stateObj();

    if (!stateObj) {
      return this._shell(title, html`<p class="message" role="alert">${this._t("not_found", { entity: config.entity })}</p>`);
    }
    if (UNAVAILABLE.has(stateObj.state)) {
      return this._shell(title, html`<p class="message" role="status">${this._t("unavailable")}</p>`);
    }

    const items = this._items(stateObj);
    const visible = config.show_done === false ? items.filter((i) => i.status !== "done") : items;
    const open = Number.parseInt(stateObj.state, 10) || 0;
    const doneCount = Number(stateObj.attributes.done_count ?? 0);
    const summary = this._summary(open, doneCount);

    return this._shell(
      title,
      html`
        <div class="head">
          <div>
            <div class="date">${this._dateLabel(stateObj)}</div>
            <div class="state" role="status">${summary}</div>
          </div>
          ${this._announceButton()}
        </div>
        ${visible.length
          ? html`<ul class="items" aria-label=${title}>
              ${visible.map((item) => this._item(item))}
            </ul>`
          : nothing}
        ${this._feedback ? html`<p class="feedback" role="status">${this._feedback}</p>` : nothing}
        ${this._week()}
      `,
    );
  }

  private _shell(title: string, body: TemplateResult): TemplateResult {
    return html`<ha-card .header=${title}><div class="content">${body}</div></ha-card>`;
  }

  private _summary(open: number, doneCount: number): string {
    if (open > 0) {
      return open === 1 ? this._t("open_one") : this._t("open_many", { n: open });
    }
    return doneCount > 0 ? this._t("all_done") : this._t("nothing");
  }

  private _dateLabel(stateObj: HassEntity): string {
    const iso = String(stateObj.attributes.date ?? "");
    const day = parseDay(iso);
    if (!day) return "";
    return day.toLocaleDateString(getLanguage(this.hass), {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
  }

  private _item(item: BrickItem): TemplateResult {
    const done = item.status === "done";
    const duration = formatDuration(this.hass, item.durationMin);
    return html`
      <li class="item ${done ? "done" : ""}">
        <ha-icon class="sport" .icon=${sportIcon(item.sport)} aria-hidden="true"></ha-icon>
        <span class="title">${item.title}</span>
        ${duration ? html`<span class="duration">${duration}</span>` : nothing}
        <span class="chip ${done ? "chip-done" : "chip-open"}">
          ${done ? this._t("status_done") : this._t("status_open")}
        </span>
      </li>
    `;
  }

  private _week(): TemplateResult | typeof nothing {
    const weekId = this._config?.week_entity;
    if (!weekId) return nothing;
    const weekState = this.hass?.states[weekId];
    if (!weekState || UNAVAILABLE.has(weekState.state)) return nothing;

    const byDate = new Map<string, BrickItem[]>();
    for (const item of readItems(weekState.attributes.items)) {
      byDate.set(item.date, [...(byDate.get(item.date) ?? []), item]);
    }
    const todayIso =
      String(this._stateObj()?.attributes.date ?? "") || toIso(new Date());
    const start = parseDay(todayIso) ?? new Date();
    const lang = getLanguage(this.hass);

    const days = Array.from({ length: 7 }, (_, offset) => {
      const date = new Date(start.getFullYear(), start.getMonth(), start.getDate() + offset, 12);
      return { date, iso: toIso(date), items: byDate.get(toIso(date)) ?? [] };
    });

    return html`
      <ol class="week" aria-label=${this._t("week")}>
        ${days.map((day) => {
          const label = day.date.toLocaleDateString(lang, { weekday: "long", day: "numeric", month: "long" });
          const isToday = day.iso === todayIso;
          return html`
            <li class="day ${isToday ? "today" : ""}" aria-label=${label} aria-current=${isToday ? "date" : nothing}>
              <span class="dow">${day.date.toLocaleDateString(lang, { weekday: "short" })}</span>
              <span class="dom">${day.date.getDate()}</span>
              <span class="dots">
                ${day.items.map(
                  (item) => html`<ha-icon
                    class="dot ${item.status === "done" ? "dot-done" : ""}"
                    .icon=${sportIcon(item.sport)}
                    title=${item.title}
                  ></ha-icon>`,
                )}
              </span>
            </li>
          `;
        })}
      </ol>
    `;
  }

  private _announceButton(): TemplateResult | typeof nothing {
    const config = this._config;
    if (!config || config.show_announce_button === false) return nothing;
    if (!config.announce?.media_player) return nothing;
    return html`<button class="announce" type="button" @click=${this._announce}>
      <ha-icon icon="mdi:bullhorn" aria-hidden="true"></ha-icon>
      <span>${this._t("announce")}</span>
    </button>`;
  }

  private _announce = async (): Promise<void> => {
    const announce = this._config?.announce;
    if (!announce?.media_player || !this.hass) return;
    try {
      await this.hass.callService("brick", "announce", {
        day: "today",
        media_player: [announce.media_player],
        ...(announce.tts_entity ? { tts_entity: announce.tts_entity } : {}),
      });
      this._feedback = this._t("announced");
    } catch {
      this._feedback = this._t("announce_failed");
    }
    window.setTimeout(() => {
      this._feedback = undefined;
    }, 4000);
  };

  static override styles = css`
    .content {
      padding: 0 16px 16px;
      color: var(--primary-text-color);
    }
    .head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
    }
    .date {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s, 0.875rem);
    }
    .state {
      font-size: var(--ha-font-size-xl, 1.25rem);
      font-weight: 500;
    }
    .message {
      margin: 0;
      color: var(--secondary-text-color);
    }
    .items,
    .week {
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 0;
      border-top: 1px solid var(--divider-color);
    }
    .sport {
      color: var(--primary-color);
      flex: none;
    }
    .title {
      flex: 1;
      min-width: 0;
      overflow-wrap: anywhere;
    }
    .duration {
      color: var(--secondary-text-color);
      white-space: nowrap;
    }
    .chip {
      flex: none;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: var(--ha-font-size-s, 0.8125rem);
      border: 1px solid var(--primary-color);
      color: var(--primary-text-color);
    }
    .chip-done {
      border-color: var(--divider-color);
      color: var(--secondary-text-color);
    }
    .item.done .title,
    .item.done .duration {
      text-decoration: line-through;
    }
    .item.done {
      opacity: 0.65;
    }
    .announce {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      flex: none;
      padding: 8px 14px;
      border: 0;
      border-radius: 18px;
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      font: inherit;
      cursor: pointer;
    }
    .announce:focus-visible,
    .announce:hover {
      outline: 2px solid var(--primary-text-color);
      outline-offset: 2px;
    }
    .feedback {
      margin: 8px 0 0;
      color: var(--secondary-text-color);
    }
    .week {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      gap: 4px;
      margin-top: 12px;
    }
    .day {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
      padding: 6px 2px;
      border-radius: 8px;
      border: 1px solid var(--divider-color);
      min-width: 0;
    }
    .day.today {
      border-color: var(--primary-color);
      background: var(--secondary-background-color);
      font-weight: 600;
    }
    .dow {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s, 0.75rem);
    }
    .dots {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      min-height: 16px;
    }
    .dot {
      --mdc-icon-size: 16px;
      color: var(--primary-color);
    }
    .dot-done {
      color: var(--secondary-text-color);
      opacity: 0.6;
    }
  `;
}
