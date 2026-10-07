import { BrickTrainingCard } from "./brick-training-card";
import { BrickTrainingCardEditor } from "./brick-training-card-editor";

if (!customElements.get("brick-training-card")) {
  customElements.define("brick-training-card", BrickTrainingCard);
}
if (!customElements.get("brick-training-card-editor")) {
  customElements.define("brick-training-card-editor", BrickTrainingCardEditor);
}

interface CustomCardEntry {
  type: string;
  name: string;
  description: string;
  preview?: boolean;
  documentationURL?: string;
}
const w = window as unknown as { customCards?: CustomCardEntry[] };
w.customCards = w.customCards ?? [];
if (!w.customCards.some((card) => card.type === "brick-training-card")) {
  w.customCards.push({
    type: "brick-training-card",
    name: "Brick Training",
    description: "Heutiges Training und 7-Tage-Übersicht aus Brick / Today's training and 7-day overview from Brick",
    preview: false,
    documentationURL: "https://github.com/Marfinho/brick-ha",
  });
}
