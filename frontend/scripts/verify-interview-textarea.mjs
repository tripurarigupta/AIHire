/**
 * Renders the real InterviewActiveView with react-dom/server to prove the
 * textarea reflects the `draft` prop instead of stale local state.
 *
 * Uses rolldown (Vite 8's bundler) to handle JSX, since this project has no
 * esbuild dependency.
 *
 * Run: node scripts/verify-interview-textarea.mjs
 */
import { readFileSync, mkdirSync, unlinkSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { build } from "rolldown";
import { renderToStaticMarkup } from "react-dom/server";
import { createElement } from "react";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SRC = join(ROOT, "src/components/ui/InterviewActiveView.jsx");
const source = readFileSync(SRC, "utf8");

// Bundle to a temp file *inside* the project so Node can still resolve
// `react` / `react-dom` from ./node_modules.
const tmpDir = join(ROOT, "node_modules", ".cache");
mkdirSync(tmpDir, { recursive: true });
const tmp = join(tmpDir, `interview-view-${process.pid}.mjs`);
await build({
  input: SRC,
  external: ["react", "react/jsx-runtime", "react-dom"],
  output: { file: tmp, format: "esm" },
});

const { default: ActiveView } = await import(pathToFileURL(tmp).href);
unlinkSync(tmp);

const questions = [
  { id: "q1", question: "Explain JWT auth.", category: "technical", target_skill: "jwt" },
  { id: "q2", question: "Explain N+1 queries.", category: "technical", target_skill: "django" },
  { id: "q3", question: "Tell us about a conflict.", category: "behavioral", target_skill: "teamwork" },
];

let failures = 0;
const check = (name, cond, detail = "") => {
  if (cond) console.log(`  PASS  ${name}`);
  else { console.log(`  FAIL  ${name} ${detail}`); failures++; }
};

// Mirror InterviewPage's own state handling: the parent owns `draft` and resets
// it when advancing to the next question. We pass answered=0 since we only
// test the UI behavior, not answer persistence (that's covered by
// verify-interview-state.mjs).
const renderFor = (current, draft, answered = 0) =>
  renderToStaticMarkup(
    createElement(ActiveView, {
      questions, current, draft, onDraftChange: () => { },
      onNext: () => { }, loading: false, answered,
    })
  );

const textareaValue = (html) => {
  const m = html.match(/<textarea[^>]*>([\s\S]*?)<\/textarea>/);
  return m ? m[1] : null;
};

console.log("\n=== 1. Question 1 shows the answer being typed ===");
const typed = renderFor(0, "my typed answer for q1");
check("textarea renders the draft prop", textareaValue(typed) === "my typed answer for q1", String(textareaValue(typed)));
check("shows question 1 heading", typed.includes("Explain JWT auth"));

console.log("\n=== 2. Advancing resets the textarea (the reported bug) ===");
const q2 = renderFor(1, "");
check("textarea is cleared for question 2", textareaValue(q2) === "", JSON.stringify(textareaValue(q2)));
check("previous answer is NOT shown on question 2", !q2.includes("my typed answer for q1"));
check("shows question 2 heading", q2.includes("Explain N+1 queries"));
check("header shows Question 2 of 3", q2.includes("Question 2 of 3"));

console.log("\n=== 3. Restoring a previously stored answer works ===");
const restored = renderFor(2, "stored answer from earlier");
check("textarea shows restored answer", textareaValue(restored) === "stored answer from earlier");
check("question 3 heading shown", restored.includes("Tell us about a conflict"));

console.log("\n=== 4. Answering is optional: skip affordances are present ===");
const blankMid = renderFor(1, "", 1);
check("blank answer offers 'Skip'", blankMid.includes("Skip →"));
check("answers optional hint shown", blankMid.includes("Optional"));
check("no answer does not block progress", blankMid.includes("No answer entered"));
check("answered counter shown", blankMid.includes("1 of 3 answered"));

const typedMid = renderFor(1, "some answer", 2);
check("typed answer advances instead of skipping", typedMid.includes("Next Question"));
check("typed answer confirmed", typedMid.includes("Answer saved."));

console.log("\n=== 5. Submit controls (user asked to remove Finish Early) ===");
const mid = renderFor(1, "", 1);
check("Finish Early is NOT offered", !mid.includes("Finish Early"));
check("skip button offered on blank non-last question", mid.includes("Skip →"));

const last = renderFor(2, "", 1);
check("last question says 'Submit Interview'", last.includes("Submit Interview"));
check("no 'Finish Early' on the last question", !last.includes("Finish Early"));

console.log("\n=== 6. No Finish Early anywhere ===");
const blankZero = renderFor(1, "", 0);
check("no 'Finish Early' on blank 2nd, zero answered", !blankZero.includes("Finish Early"));
check("no 'Finish Early' on blank 2nd, one answered", !blankMid.includes("Finish Early"));
check("no 'Finish Early' on typed mid", !typedMid.includes("Finish Early"));
check("no 'Finish Early' on last question", !last.includes("Finish Early"));
check("skip button on blank non-last (zero answered)", blankZero.includes("Skip →"));
check("skip button on blank non-last (one answered)", blankMid.includes("Skip →"));
check("typed answer advances instead of skipping", typedMid.includes("Next Question"));

console.log("\n=== 7. Component no longer duplicates state ===");
check("component no longer uses useState", !/useState/.test(source), "found useState in source");
check("textarea is bound to the draft prop", /value=\{draft \?\? ""\}/.test(source));

console.log("\n" + "=".repeat(60));
if (failures) { console.log(`RESULT: ${failures} FAILED`); process.exit(1); }
console.log("RESULT: all textarea checks passed.");