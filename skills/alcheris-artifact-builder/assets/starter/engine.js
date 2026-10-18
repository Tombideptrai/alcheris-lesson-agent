/* Stepper engine. build.mjs prepends `const CONFIG = {...}`.
   Shell (tabs, step copy, Back/Next, dots, check steps, completion) is generic.
   Replace the SCENE section with your own drawing; keep the hooks:
     buildScene(tab)           draw everything for a tab, hidden; read VIEW.w/VIEW.h
     applyStep(tab, step, fwd) show what this step reveals (fwd = moving forward)

   Optional per-step check (config): { title, desc, check: { prompt,
     options: ["...", ...], answer: <index>, hints: { <index>: "..." }, explain } }
   Next stays locked until the learner picks the answer or presses "Show me".

   Optional CONFIG.fitDrawing = true: the drawing's height follows the stage's
   real shape (no letterbox on phones) and the scene is redrawn on resize
   without replaying animations. Scenes must lay out from VIEW.h. */
const C = CONFIG;
const NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("stage");
const stageEl = svg.parentElement;
const tabsEl = document.getElementById("tabs");
const dotsEl = document.getElementById("dots");
const labelEl = document.getElementById("step-label");
const titleEl = document.getElementById("step-title");
const descEl = document.getElementById("step-desc");
const nextBtn = document.getElementById("next");
const backBtn = document.getElementById("back");
const checkEl = document.getElementById("check");
const checkPrompt = document.getElementById("check-prompt");
const checkOptions = document.getElementById("check-options");
const checkFeedback = document.getElementById("check-feedback");

let tabIndex = 0;
let step = 0;
let timers = [];
const done = new Set();
const solved = new Set(); // "tab:step" keys of checks already answered

const el = (tag, attrs = {}, text) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text !== undefined) n.textContent = text;
  return n;
};
const add = (parent, tag, attrs, text) => parent.appendChild(el(tag, attrs, text));
const later = (fn, ms) => timers.push(window.setTimeout(fn, ms));
const clearTimers = () => { timers.forEach(clearTimeout); timers = []; };
const tab = () => C.tabs[tabIndex];
const stepKey = () => `${tab().id}:${step}`;

/* ---------- SCENE (replace) ---------- */
// Keep text 10-12px in viewBox units so it stays readable at 0.8 scale.
const VIEW = { w: 360, h: 440 };
const COLORS = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)", "var(--c5)"];

function buildScene() {
  svg.setAttribute("viewBox", `0 0 ${VIEW.w} ${VIEW.h}`);
  // With fitDrawing the stage shape drives VIEW.h; otherwise the drawing's
  // aspect drives the stage height through --ratio.
  if (!C.fitDrawing) stageEl.style.setProperty("--ratio", (VIEW.h / VIEW.w).toFixed(4));
  const base = VIEW.h - 60;
  const room = base - 80;
  const n = C.values.length;
  const slot = 280 / n;
  add(svg, "path", { d: `M40,${base} L320,${base}`, class: "axis", pathLength: 1 });
  C.values.forEach((item, i) => {
    const cx = 40 + slot * (i + 0.5);
    const h = (item.value / C.max) * room;
    add(svg, "rect", { x: cx - 26, y: base - h, width: 52, height: h, rx: 4, fill: COLORS[i % COLORS.length], class: "bar" });
    add(svg, "text", { x: cx, y: base - h - 10, class: "value" }, String(item.value));
    add(svg, "text", { x: cx, y: base + 22, class: "label" }, item.label);
  });
}

function applyStep(_tab, s, forward) {
  svg.querySelector(".axis").classList.toggle("show", s >= 1);
  svg.querySelectorAll(".value").forEach((n) => n.classList.add("show"));
  svg.querySelectorAll(".bar").forEach((n, i) => {
    n.style.transitionDelay = forward && s === 2 ? `${i * 150}ms` : "0ms";
    n.classList.toggle("show", s >= 2);
  });
}
/* ---------- end SCENE ---------- */

function currentCheck() {
  return tab().steps[step].check || null;
}

function renderCheck() {
  const check = currentCheck();
  checkEl.hidden = !check;
  if (!check) return;
  const answered = solved.has(stepKey());
  checkPrompt.textContent = check.prompt;
  checkFeedback.textContent = answered ? (check.explain || "") : "";
  checkOptions.replaceChildren(...check.options.map((label, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = label;
    if (answered && i === check.answer) b.classList.add("right");
    b.disabled = answered;
    b.addEventListener("click", () => answer(i));
    return b;
  }));
  if (!answered) {
    const reveal = document.createElement("button");
    reveal.type = "button";
    reveal.className = "reveal";
    reveal.textContent = "Show me";
    reveal.addEventListener("click", () => answer(check.answer, true));
    checkOptions.appendChild(reveal);
  }
}

function answer(i, revealed = false) {
  const check = currentCheck();
  const correct = i === check.answer;
  window.AlcherisArtifact?.track(revealed ? "check_revealed" : "check_answered", { tab: tab().id, step: step + 1, choice: i, correct });
  if (!correct) {
    const b = checkOptions.children[i];
    b.classList.add("wrong");
    checkFeedback.textContent = (check.hints && check.hints[i]) || "Not quite. Look at the drawing again.";
    return;
  }
  solved.add(stepKey());
  renderCheck();
  renderChrome();
}

function renderChrome() {
  const t = tab();
  const s = t.steps[step];
  const last = step === t.steps.length - 1;
  const locked = Boolean(s.check) && !solved.has(stepKey());
  labelEl.textContent = C.tabs.length > 1 ? `${t.label} · Step ${step + 1} of ${t.steps.length}` : `Step ${step + 1} of ${t.steps.length}`;
  titleEl.textContent = s.title;
  descEl.textContent = s.desc;
  backBtn.disabled = step === 0;
  nextBtn.disabled = locked;
  dotsEl.querySelectorAll("span").forEach((d, i) => d.classList.toggle("on", i === step));
  tabsEl.querySelectorAll(".tab").forEach((b, i) => {
    b.classList.toggle("active", i === tabIndex);
    b.classList.toggle("done", done.has(C.tabs[i].id));
    b.setAttribute("aria-selected", String(i === tabIndex));
  });
  nextBtn.classList.toggle("done", last && !locked);
  if (locked) nextBtn.textContent = "Answer to continue";
  else if (!last) nextBtn.textContent = s.next || "Next →";
  else if (done.size === C.tabs.length) nextBtn.textContent = "All done ✓ Replay";
  else nextBtn.textContent = C.tabs.length > 1 ? "Done ✓ Next →" : "Done ✓";
  if (last && !locked) later(finishTab, 900);
}

function finishTab() {
  const id = tab().id;
  if (done.has(id)) return;
  done.add(id);
  window.AlcherisArtifact?.track("tab_finished", { tab: id });
  // Guided flow waits for this: without complete()/submit() the learner is stuck.
  if (done.size === C.tabs.length) window.AlcherisArtifact?.complete({ finished: Array.from(done) });
  renderChrome();
}

function go(newStep, forward) {
  clearTimers();
  step = newStep;
  renderCheck();
  renderChrome();
  applyStep(tab(), step, forward);
  window.AlcherisArtifact?.track("step_viewed", { tab: tab().id, step: step + 1 });
}

function redraw() {
  svg.replaceChildren();
  buildScene(tab());
  applyStep(tab(), step, false); // no replayed animation
}

function openTab(i) {
  tabIndex = i;
  dotsEl.replaceChildren(...tab().steps.map(() => document.createElement("span")));
  svg.replaceChildren();
  buildScene(tab());
  go(0, false);
}

nextBtn.addEventListener("click", () => {
  if (nextBtn.disabled) return;
  if (step < tab().steps.length - 1) return go(step + 1, true);
  const pending = C.tabs.findIndex((t) => !done.has(t.id));
  openTab(pending === -1 ? (tabIndex + 1) % C.tabs.length : pending);
});
backBtn.addEventListener("click", () => step > 0 && go(step - 1, false));

if (C.tabs.length > 1) {
  C.tabs.forEach((t, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "tab";
    b.setAttribute("role", "tab");
    b.textContent = t.label;
    b.addEventListener("click", () => openTab(i));
    tabsEl.appendChild(b);
  });
}

// Match the drawing to the stage's real shape. The stage height comes from CSS
// (width-based), so this never feeds back into the frame size.
function fitDrawing() {
  const r = stageEl.getBoundingClientRect();
  if (!r.width || !r.height) return;
  const h = Math.max(240, Math.round(VIEW.w * (r.height / r.width)));
  if (Math.abs(h - VIEW.h) > 2) { VIEW.h = h; redraw(); }
}
if (C.fitDrawing) {
  if (typeof ResizeObserver === "function") new ResizeObserver(fitDrawing).observe(stageEl);
  window.addEventListener("resize", fitDrawing);
  fitDrawing();
}

openTab(0);
