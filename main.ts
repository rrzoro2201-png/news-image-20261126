// The World in One Day - Thursday 26 November 2026.
// Entry program: places the finished one-page illustrated newspaper into
// the grader's output directory. The image (entry.png, 1024x1024) was
// drawn beforehand by render.py (Python 3 + Pillow, no network, no
// external assets) and is committed in this repository; this file only
// copies it where the grader looks for it.
//
// The copy keeps the graded run on pure Node stdlib: the grader runs
// `node /bot/main.ts` in a Node-only image, on a read-only copy of the
// repository, with no Python, no Pillow and no system fonts, so the
// render step lives outside the graded run.
//
// Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const source = new URL("./entry.png", import.meta.url);

try {
  mkdirSync(outDir, { recursive: true });
  copyFileSync(source, join(outDir, "entry.png"));
} catch (err) {
  console.error("could not deliver entry.png:", err.message);
  process.exit(1);
}

console.log("entry.png delivered to", join(outDir, "entry.png"));
