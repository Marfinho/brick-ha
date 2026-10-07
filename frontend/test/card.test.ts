import { beforeAll, describe, expect, it, vi } from "vitest";
import type { BrickCardConfig, Hass, HassEntity } from "../src/types";

type Card = HTMLElement & {
  hass?: Hass;
  setConfig(c: BrickCardConfig): void;
  getCardSize(): number;
  updateComplete: Promise<boolean>;
};

const ITEMS = [
  { sport: "bike", title: "Grundlagen Z2", durationMin: 80, status: "planned", date: "2026-10-07" },
  { sport: "run", title: "Lockerer Lauf", durationMin: 45, status: "done", date: "2026-10-07" },
];

function entity(state: string, attributes: Record<string, unknown> = {}): HassEntity {
  return { entity_id: "sensor.brick_training_heute", state, attributes };
}

function makeHass(states: Record<string, HassEntity>, language = "de"): Hass {
  return { states, language, callService: vi.fn().mockResolvedValue(undefined) };
}

async function mount(
  hass: Hass,
  config: Partial<BrickCardConfig> = {},
): Promise<{ card: Card; root: ShadowRoot }> {
  const card = document.createElement("brick-training-card") as Card;
  card.setConfig({ type: "custom:brick-training-card", entity: "sensor.brick_training_heute", ...config });
  card.hass = hass;
  document.body.append(card);
  await card.updateComplete;
  return { card, root: card.shadowRoot as ShadowRoot };
}

beforeAll(async () => {
  await import("../src/index");
});

describe("brick-training-card", () => {
  it("zeigt offene Einheiten mit Icon, Dauer und Status-Chip", async () => {
    const hass = makeHass({
      "sensor.brick_training_heute": entity("1", { items: ITEMS, done_count: 1, date: "2026-10-07" }),
    });
    const { root } = await mount(hass);
    expect(root.querySelector(".state")?.textContent).toBe("1 Einheit offen");
    const items = root.querySelectorAll("li.item");
    expect(items).toHaveLength(2);
    expect((items[0].querySelector("ha-icon") as HTMLElement & { icon?: string }).icon).toBe("mdi:bike");
    expect(items[0].querySelector(".duration")?.textContent).toBe("1 Std 20");
    expect(items[0].querySelector(".chip")?.textContent?.trim()).toBe("offen");
    expect(items[1].classList.contains("done")).toBe(true);
    expect(items[1].querySelector(".duration")?.textContent).toBe("45 Min");
    expect(items[1].querySelector(".chip")?.textContent?.trim()).toBe("erledigt");
    expect(root.querySelector(".date")?.textContent).toContain("Oktober");
  });

  it("zählt mehrere offene Einheiten", async () => {
    const hass = makeHass({
      "sensor.brick_training_heute": entity("2", { items: ITEMS, done_count: 0, date: "2026-10-07" }),
    });
    const { root } = await mount(hass);
    expect(root.querySelector(".state")?.textContent).toBe("2 Einheiten offen");
  });

  it("zeigt 'Alles erledigt'", async () => {
    const hass = makeHass({
      "sensor.brick_training_heute": entity("0", { items: [ITEMS[1]], done_count: 1, date: "2026-10-07" }),
    });
    const { root } = await mount(hass);
    expect(root.querySelector(".state")?.textContent).toBe("Alles erledigt");
  });

  it("zeigt 'Heute ist nichts geplant' bei leerem Plan", async () => {
    const hass = makeHass({
      "sensor.brick_training_heute": entity("0", { items: [], done_count: 0, date: "2026-10-07" }),
    });
    const { root } = await mount(hass);
    expect(root.querySelector(".state")?.textContent).toBe("Heute ist nichts geplant");
    expect(root.querySelectorAll("li.item")).toHaveLength(0);
  });

  it("blendet erledigte Einheiten bei show_done=false aus", async () => {
    const hass = makeHass({
      "sensor.brick_training_heute": entity("1", { items: ITEMS, done_count: 1, date: "2026-10-07" }),
    });
    const { root } = await mount(hass, { show_done: false });
    expect(root.querySelectorAll("li.item")).toHaveLength(1);
  });

  it.each(["unavailable", "unknown"])("zeigt eine Meldung bei %s", async (state) => {
    const hass = makeHass({ "sensor.brick_training_heute": entity(state) });
    const { root } = await mount(hass);
    expect(root.querySelector(".message")?.textContent).toContain("nicht verfügbar");
    expect(root.querySelector("li")).toBeNull();
  });

  it("meldet eine fehlende Entität", async () => {
    const { root } = await mount(makeHass({}));
    expect(root.querySelector(".message")?.textContent).toContain("sensor.brick_training_heute");
  });

  it("lokalisiert nach hass.language", async () => {
    const hass = makeHass(
      { "sensor.brick_training_heute": entity("0", { items: [], date: "2026-10-07" }) },
      "en",
    );
    const { root } = await mount(hass);
    expect(root.querySelector(".state")?.textContent).toBe("Nothing planned today");
  });

  it("Ansagen-Knopf ruft brick.announce auf", async () => {
    const hass = makeHass({
      "sensor.brick_training_heute": entity("1", { items: ITEMS, done_count: 1, date: "2026-10-07" }),
    });
    const { root } = await mount(hass, {
      announce: { media_player: "media_player.kueche", tts_entity: "tts.cloud" },
    });
    const button = root.querySelector("button.announce") as HTMLButtonElement;
    expect(button.textContent).toContain("Ansagen");
    button.click();
    await Promise.resolve();
    expect(hass.callService).toHaveBeenCalledWith("brick", "announce", {
      day: "today",
      media_player: ["media_player.kueche"],
      tts_entity: "tts.cloud",
    });
  });

  it("versteckt den Knopf ohne Box oder bei show_announce_button=false", async () => {
    const hass = makeHass({
      "sensor.brick_training_heute": entity("1", { items: ITEMS, date: "2026-10-07" }),
    });
    expect((await mount(hass)).root.querySelector("button.announce")).toBeNull();
    const second = await mount(hass, {
      show_announce_button: false,
      announce: { media_player: "media_player.kueche" },
    });
    expect(second.root.querySelector("button.announce")).toBeNull();
  });

  it("rendert den 7-Tage-Streifen mit hervorgehobenem Heute", async () => {
    const hass = makeHass({
      "sensor.brick_training_heute": entity("1", { items: ITEMS, date: "2026-10-07" }),
      "sensor.brick_training_woche": {
        entity_id: "sensor.brick_training_woche",
        state: "2",
        attributes: {
          items: [
            ...ITEMS,
            { sport: "swim", title: "Technik", durationMin: 45, status: "planned", date: "2026-10-09" },
          ],
        },
      },
    });
    const { root } = await mount(hass, { week_entity: "sensor.brick_training_woche" });
    const days = root.querySelectorAll("ol.week li.day");
    expect(days).toHaveLength(7);
    expect(days[0].classList.contains("today")).toBe(true);
    expect(days[0].querySelectorAll(".dot")).toHaveLength(2);
    expect((days[2].querySelector(".dot") as HTMLElement & { icon?: string }).icon).toBe("mdi:swim");
    expect(days[1].querySelectorAll(".dot")).toHaveLength(0);
  });

  it("verlangt eine Entität und liefert eine Kartengröße", async () => {
    const { card } = await mount(makeHass({}));
    expect(() => card.setConfig({ type: "x" } as BrickCardConfig)).toThrow();
    expect(card.getCardSize()).toBeGreaterThan(0);
  });

  it("registriert sich in window.customCards", () => {
    const cards = (window as unknown as { customCards: { type: string }[] }).customCards;
    expect(cards.filter((c) => c.type === "brick-training-card")).toHaveLength(1);
  });

  it("liefert Stub-Konfiguration und Editor-Element", async () => {
    const ctor = customElements.get("brick-training-card") as unknown as {
      getStubConfig(h?: Hass): BrickCardConfig;
      getConfigElement(): HTMLElement;
    };
    const stub = ctor.getStubConfig(
      makeHass({ "sensor.brick_training_heute": entity("0") }),
    );
    expect(stub.entity).toBe("sensor.brick_training_heute");
    expect(ctor.getConfigElement().tagName.toLowerCase()).toBe("brick-training-card-editor");
  });
});
