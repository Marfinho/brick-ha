import { beforeAll, describe, expect, it } from "vitest";
import type { BrickCardConfig, Hass } from "../src/types";

type Editor = HTMLElement & {
  hass?: Hass;
  setConfig(c: BrickCardConfig): void;
  updateComplete: Promise<boolean>;
};

beforeAll(async () => {
  await import("../src/index");
});

async function mount(config: BrickCardConfig): Promise<{ editor: Editor; form: HTMLElement & { data: Record<string, unknown>; schema: { name: string }[]; computeLabel(s: { name: string }): string } }> {
  const editor = document.createElement("brick-training-card-editor") as Editor;
  editor.hass = { states: {}, language: "de", callService: async () => undefined };
  editor.setConfig(config);
  document.body.append(editor);
  await editor.updateComplete;
  const form = editor.shadowRoot?.querySelector("ha-form") as never;
  return { editor, form };
}

describe("brick-training-card-editor", () => {
  it("rendert ein Formular mit Entity-Pickern und deutschen Labels", async () => {
    const { form } = await mount({
      type: "custom:brick-training-card",
      entity: "sensor.brick_training_heute",
      announce: { media_player: "media_player.kueche" },
    });
    expect(form).not.toBeNull();
    expect(form.data.entity).toBe("sensor.brick_training_heute");
    expect(form.data.media_player).toBe("media_player.kueche");
    expect(form.data.show_done).toBe(true);
    expect(form.schema.map((s) => s.name)).toContain("week_entity");
    expect(form.computeLabel({ name: "title" })).toBe("Titel");
  });

  it("feuert config-changed mit verschachteltem announce-Objekt", async () => {
    const { editor, form } = await mount({
      type: "custom:brick-training-card",
      entity: "sensor.brick_training_heute",
    });
    const received: BrickCardConfig[] = [];
    editor.addEventListener("config-changed", (e) =>
      received.push((e as CustomEvent<{ config: BrickCardConfig }>).detail.config),
    );
    form.dispatchEvent(
      new CustomEvent("value-changed", {
        detail: {
          value: {
            entity: "sensor.brick_training_heute",
            week_entity: "sensor.brick_training_woche",
            title: "Training",
            show_done: false,
            show_announce_button: true,
            media_player: "media_player.kueche",
            tts_entity: "tts.cloud",
          },
        },
      }),
    );
    expect(received).toEqual([
      {
        type: "custom:brick-training-card",
        entity: "sensor.brick_training_heute",
        week_entity: "sensor.brick_training_woche",
        title: "Training",
        show_done: false,
        show_announce_button: true,
        announce: { media_player: "media_player.kueche", tts_entity: "tts.cloud" },
      },
    ]);
  });
});
