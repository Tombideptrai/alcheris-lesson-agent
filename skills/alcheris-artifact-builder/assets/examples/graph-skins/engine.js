/* Graph skins engine. Expects a global CONFIG (prepended by build.mjs). */
const C = CONFIG;
const NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("stage");
const tabsEl = document.getElementById("tabs");
const dotsEl = document.getElementById("dots");
const labelEl = document.getElementById("step-label");
const titleEl = document.getElementById("step-title");
const descEl = document.getElementById("step-desc");
const nextBtn = document.getElementById("next");
const backBtn = document.getElementById("back");

const isTrend = C.mode === "trend";
const X = C.x;
const N = X.length;
const SERIES = isTrend ? C.series : [{ key: "value", label: C.valueLabel, values: C.values }];
const COLORS = ["var(--c1)", "var(--c2)", "var(--c3)", "#c2417a", "#7c8591"];
const colorOf = (s, i) => (isTrend ? COLORS[s] : COLORS[i]);

const P = { L: 50, R: 344, T: 214, B: 386, inset: isTrend ? 26 : 30 };
const xAt = (i) => P.L + P.inset + ((P.R - P.L - 2 * P.inset) * i) / (N - 1);
const yAt = (v) => P.B - (v / C.yMax) * (P.B - P.T);
const BAR_OFFSETS = [-13, 0, 13];

let tabIndex = 0;
let step = 0;
let timers = [];
const done = new Set();

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

/* ---------- source renderers (top region) ---------- */
function sourceTable(g) {
  const rows = isTrend ? SERIES.map((s) => s.label) : [C.valueLabel];
  const firstW = isTrend ? 84 : 76;
  const colW = (340 - firstW) / N;
  const top = isTrend ? 34 : 58;
  const h = isTrend ? 30 : 40;
  const cell = (x, y, w, text, head, id) => {
    add(g, "rect", { x, y, width: w, height: h, class: `cell${head ? " head" : ""}`, ...(id ? { id } : {}) });
    add(g, "text", { x: x + w / 2, y: y + h / 2, class: `cell-text${head ? " head" : ""}` }, text);
  };
  cell(10, top, firstW, isTrend ? "Year" : "Category", true);
  X.forEach((x, i) => cell(10 + firstW + i * colW, top, colW, x, true));
  rows.forEach((r, s) => {
    const y = top + h * (s + 1);
    cell(10, y, firstW, r, true);
    SERIES[s].values.forEach((v, i) => cell(10 + firstW + i * colW, y, colW, `${v}${C.unit}`, false, `src-${s}-${i}`));
  });
}

function arc(cx, cy, r, a0, a1) {
  const p = (a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  const [x0, y0] = p(a0);
  const [x1, y1] = p(a1);
  return `M${cx},${cy} L${x0},${y0} A${r},${r} 0 ${a1 - a0 > Math.PI ? 1 : 0} 1 ${x1},${y1} Z`;
}

function pie(g, cx, cy, r, slices) {
  let a = -Math.PI / 2;
  slices.forEach(({ value, color, id }) => {
    const a1 = a + (value / 100) * Math.PI * 2;
    add(g, "path", { d: arc(cx, cy, r, a, a1), fill: color, class: "slice", id });
    a = a1;
  });
}

function sourcePies(g) {
  if (isTrend) {
    X.forEach((x, i) => {
      const cx = 10 + (340 / N) * (i + 0.5);
      pie(g, cx, 82, 31, SERIES.map((s, si) => ({ value: s.values[i], color: colorOf(si), id: `src-${si}-${i}` })));
      add(g, "text", { x: cx, y: 130, class: "pie-label" }, x);
    });
  } else {
    pie(g, 96, 96, 62, X.map((_, i) => ({ value: C.values[i], color: colorOf(0, i), id: `src-0-${i}` })));
    X.forEach((x, i) => {
      const y = 50 + i * 23;
      add(g, "rect", { x: 190, y: y - 6, width: 12, height: 12, rx: 3, fill: colorOf(0, i) });
      add(g, "text", { x: 210, y, class: "legend-text" }, `${x} — ${C.values[i]}${C.unit}`);
    });
  }
}

function legend(g, y) {
  const w = 340 / SERIES.length;
  SERIES.forEach((s, si) => {
    const x = 10 + w * si + w / 2 - 30;
    add(g, "line", { x1: x, y1: y, x2: x + 16, y2: y, stroke: colorOf(si), "stroke-width": 4, "stroke-linecap": "round" });
    add(g, "text", { x: x + 22, y, class: "legend-text" }, s.label);
  });
}

/* ---------- graph (bottom region) ---------- */
function buildGraph(g) {
  C.yTicks.forEach((t) => {
    add(g, "line", { x1: P.L, y1: yAt(t), x2: P.R, y2: yAt(t), class: "grid-line" });
    add(g, "text", { x: P.L - 8, y: yAt(t) + 3.5, class: "tick", "text-anchor": "end" }, `${t}${C.unit}`);
  });
  add(g, "path", { d: `M${P.L},${P.T - 6} L${P.L},${P.B} L${P.R},${P.B}`, class: "axis", pathLength: 1 });
  add(g, "text", { x: P.L - 2, y: P.T - 14, class: "axis-name" }, C.yName);
  add(g, "text", { x: P.R, y: P.B + 34, class: "axis-name", "text-anchor": "end" }, C.xName);
  X.forEach((x, i) => add(g, "text", { x: xAt(i), y: P.B + 16, class: "tick", "text-anchor": "middle" }, x));

  const barsTab = tab().source === "bars";
  const ghosts = add(g, "g", { id: "ghosts" });
  const rises = add(g, "g", { id: "rises" });
  const lines = add(g, "g", { id: "lines" });
  const dots = add(g, "g", { id: "dots-g" });

  SERIES.forEach((s, si) => {
    const pts = s.values.map((v, i) => [xAt(i) + (barsTab ? BAR_OFFSETS[si] : 0), yAt(v)]);
    if (barsTab) {
      pts.forEach(([x, y]) => add(ghosts, "rect", { x: x - 6, y, width: 12, height: P.B - y, rx: 2, fill: colorOf(si), class: "ghost" }));
    }
    if (!isTrend) {
      pts.forEach(([x, y], i) => add(rises, "rect", { x: x - 17, y, width: 34, height: P.B - y, rx: 3, fill: colorOf(si, i), class: "rise" }));
    }
    if (isTrend) {
      add(lines, "path", { d: `M${pts.map((p) => p.join(",")).join(" L")}`, class: "line", stroke: colorOf(si), pathLength: 1 });
    }
    pts.forEach(([x, y], i) => {
      const color = colorOf(si, i);
      add(dots, "circle", { cx: x, cy: y, r: isTrend ? 5 : 6, stroke: color, class: "dot", "data-src": `src-${si}-${i}` });
      if (!isTrend) add(dots, "text", { x, y: y - 11, class: "dot-value", fill: color }, `${s.values[i]}${C.unit}`);
    });
  });
}

function build() {
  svg.replaceChildren();
  const t = tab();
  const barsOnly = t.source === "bars";
  // A bar chart over time is already on the graph's axes: draw it once and
  // mark its tips in place instead of drawing a second copy below.
  svg.setAttribute("viewBox", barsOnly ? "0 140 360 300" : "0 0 360 440");
  svg.parentElement.style.setProperty("--ratio", barsOnly ? (300 / 360).toFixed(4) : (440 / 360).toFixed(4));
  svg.setAttribute("aria-label", `${t.label}: ${C.caption}`);
  if (barsOnly) {
    add(svg, "text", { x: 10, y: 156, class: "region-label" }, `${t.label} · ${C.caption}`);
    legend(svg, 174);
  } else {
    add(svg, "text", { x: 10, y: 20, class: "region-label" }, `${t.label} · ${C.caption}`);
    const src = add(svg, "g", { id: "source" });
    if (t.source === "table") sourceTable(src);
    if (t.source === "pie") sourcePies(src);
    if (isTrend) legend(svg, 172);
    add(svg, "line", { x1: 10, y1: 186, x2: 350, y2: 186, stroke: "var(--border)", "stroke-dasharray": "3 4" });
    add(svg, "text", { x: 350, y: 202, class: "region-label", "text-anchor": "end" }, isTrend ? "Line graph" : "Bar chart");
  }
  buildGraph(add(svg, "g", { id: "graph" }));
}

/* ---------- steps ---------- */
function flash(id, delay) {
  const n = document.getElementById(id);
  if (!n) return;
  n.classList.remove("flash");
  later(() => { void n.getBBox(); n.classList.add("flash"); }, delay);
}

function apply(forward) {
  clearTimers();
  const t = tab();
  const bars = t.source === "bars";
  const graph = svg.querySelector("#graph");
  graph.classList.toggle("axes-on", bars || step >= 1);
  graph.classList.toggle("axes-pulse", bars && step === 1 && forward);

  svg.querySelectorAll(".ghost").forEach((n, i) => {
    n.style.transitionDelay = forward && step === 1 ? `${i * 40}ms` : "0ms";
    n.classList.toggle("show", bars);
    n.classList.toggle("faded", step >= 3);
  });

  const dotDelay = (i) => (bars ? 0 : 450) + i * 110;
  const dots = Array.from(svg.querySelectorAll(".dot"));
  dots.forEach((n, i) => {
    const show = step >= 2;
    const delay = forward && step === 2 ? dotDelay(i) : 0;
    n.style.transitionDelay = `${delay}ms`;
    n.classList.toggle("show", show);
    if (forward && step === 2) flash(n.dataset.src, delay);
  });
  svg.querySelectorAll(".dot-value").forEach((n, i) => {
    n.style.transitionDelay = forward && step === 2 ? `${dotDelay(i) + 150}ms` : "0ms";
    n.classList.toggle("show", step >= 2);
  });

  svg.querySelectorAll(".line").forEach((n, i) => {
    n.style.transitionDelay = forward && step === 3 ? `${(bars ? 350 : 0) + i * 300}ms` : "0ms";
    n.classList.toggle("show", step >= 3);
  });
  svg.querySelectorAll(".rise").forEach((n, i) => {
    n.style.transitionDelay = forward && step === 3 ? `${i * 140}ms` : "0ms";
    n.classList.toggle("show", step >= 3);
  });
}

function renderChrome() {
  const t = tab();
  const s = t.steps[step];
  const last = step === t.steps.length - 1;
  labelEl.textContent = `${t.label} · Step ${step + 1} of ${t.steps.length}`;
  titleEl.textContent = s.title;
  descEl.textContent = s.desc;
  backBtn.disabled = step === 0;
  dotsEl.querySelectorAll("span").forEach((d, i) => d.classList.toggle("on", i === step));
  tabsEl.querySelectorAll(".tab").forEach((b, i) => {
    b.classList.toggle("active", i === tabIndex);
    b.classList.toggle("done", done.has(C.tabs[i].id));
    b.setAttribute("aria-selected", String(i === tabIndex));
  });
  nextBtn.classList.toggle("done", last);
  if (!last) nextBtn.textContent = s.next;
  else if (done.size === C.tabs.length) nextBtn.textContent = "All done ✓ Replay";
  else nextBtn.textContent = "Done ✓ Next chart →";
}

function finishTab() {
  const id = tab().id;
  if (done.has(id)) return;
  done.add(id);
  window.AlcherisArtifact?.track("chart_transformed", { source: id, target: C.target });
  if (done.size === C.tabs.length) {
    window.AlcherisArtifact?.complete({ target: C.target, transformed: Array.from(done) });
  }
  renderChrome();
}

function go(newStep, forward) {
  step = newStep;
  renderChrome();
  apply(forward);
  window.AlcherisArtifact?.track("step_viewed", { source: tab().id, step: step + 1 });
  if (step === tab().steps.length - 1) later(finishTab, 1100);
}

function openTab(i) {
  tabIndex = i;
  dotsEl.replaceChildren(...tab().steps.map(() => document.createElement("span")));
  build();
  go(0, false);
}

nextBtn.addEventListener("click", () => {
  const last = step === tab().steps.length - 1;
  if (!last) return go(step + 1, true);
  const pending = C.tabs.findIndex((t) => !done.has(t.id));
  openTab(pending === -1 ? (tabIndex + 1) % C.tabs.length : pending);
});
backBtn.addEventListener("click", () => step > 0 && go(step - 1, false));

C.tabs.forEach((t, i) => {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "tab";
  b.setAttribute("role", "tab");
  b.textContent = t.label;
  b.addEventListener("click", () => openTab(i));
  tabsEl.appendChild(b);
});

openTab(0);
