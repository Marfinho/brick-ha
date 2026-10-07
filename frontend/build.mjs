// Bündelt die Karte zu einer einzigen Datei, die in die Integration eingecheckt wird.
import { build } from "esbuild";

await build({
  entryPoints: ["src/index.ts"],
  outfile: "../custom_components/brick/dist/brick-training-card.js",
  bundle: true,
  format: "esm",
  target: "es2021",
  minify: true,
  legalComments: "none",
  charset: "utf8",
  logLevel: "info",
});
