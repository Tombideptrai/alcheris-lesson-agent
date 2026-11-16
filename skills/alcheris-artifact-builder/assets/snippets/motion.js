/* Shared motion + scene framework for the TVM artifacts. build.mjs inlines it after CONFIG.
   - tween()/wait() are tied to a scene generation: leaving a scene freezes its animations.
   - scenes(): header, dots, Back/Next, completion. Each runner gets (api) and calls api.finish(). */
const NS = "http://www.w3.org/2000/svg";
const UI = {
  board: document.getElementById("board"), label: document.getElementById("step-label"),
  title: document.getElementById("step-title"), desc: document.getElementById("step-desc"),
  next: document.getElementById("next"), back: document.getElementById("back"), dots: document.getElementById("dots"),
};
const REDUCED = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
const track = (a, p) => window.AlcherisArtifact?.track(a, p);
const h = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v);
  }
  kids.flat().forEach((k) => k != null && n.append(k));
  return n;
};
const sv = (tag, attrs = {}, text) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text != null) n.textContent = text;
  return n;
};
const EASE = {
  out: (t) => 1 - Math.pow(1 - t, 3),
  inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  back: (t) => 1 + 2.4 * Math.pow(t - 1, 3) + 1.4 * Math.pow(t - 1, 2),
};
let GEN = 0;
function tween(dur, fn, e = EASE.out) {
  const g0 = GEN;
  return new Promise((done) => {
    if (REDUCED || dur <= 0) { if (g0 === GEN) { fn(1); done(); } return; }
    const t0 = performance.now();
    const frame = (now) => {
      if (g0 !== GEN) return;
      const t = Math.min(1, (now - t0) / dur);
      fn(e(t));
      if (t < 1) requestAnimationFrame(frame); else done();
    };
    requestAnimationFrame(frame);
  });
}
const wait = (ms) => { const g0 = GEN; return new Promise((r) => setTimeout(() => { if (g0 === GEN) r(); }, REDUCED ? 0 : ms)); };
const usd = (v, d = 2) => (v < 0 ? "−$" : "$") + Math.abs(v).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
function svgPoint(svg, evt) {
  const p = svg.createSVGPoint();
  p.x = evt.clientX; p.y = evt.clientY;
  return p.matrixTransform(svg.getScreenCTM().inverse());
}
/* count a text node from a to b */
function countTo(node, from, to, dur = 500, fmt = usd) {
  return tween(dur, (t) => { node.textContent = fmt(from + (to - from) * t); });
}
/* a quick shake for wrong moves */
function shake(node) {
  if (REDUCED || !node) return;
  node.classList.remove("shake"); void node.getBoundingClientRect(); node.classList.add("shake");
}
/* drag helper: onMove(pt), onUp(pt) in SVG units */
/* Moves and releases are followed on the whole window: on phones a finger easily leaves a
   small SVG shape (and iOS can drop pointer capture), which used to lose the release. */
function draggable(node, svg, { onDown, onMove, onUp }) {
  node.style.touchAction = "none";
  node.onpointerdown = (e) => {
    e.preventDefault();
    onDown?.(svgPoint(svg, e));
    const mv = (ev) => { ev.preventDefault(); onMove?.(svgPoint(svg, ev)); };
    const end = (ev) => {
      window.removeEventListener("pointermove", mv);
      window.removeEventListener("pointerup", end);
      window.removeEventListener("pointercancel", end);
      onUp?.(svgPoint(svg, ev));
    };
    window.addEventListener("pointermove", mv, { passive: false });
    window.addEventListener("pointerup", end);
    window.addEventListener("pointercancel", end);
  };
}

function scenes(C, runners) {
  const done = new Set();
  let i = 0;
  let completed = false;
  const api = {
    fb: null,
    say(text, kind = "") { api.fb.textContent = text; api.fb.className = `feedback${kind ? " " + kind : ""}`; },
    finish() {
      const fresh = !done.has(i);
      done.add(i); UI.next.disabled = false;
      if (fresh && i < runners.length - 1) { const k = i; autoNext(() => { if (i === k) enter(k + 1); }, api.fb?.textContent); }
      if (i === runners.length - 1 && !completed) { completed = true; window.AlcherisArtifact?.complete({ scenes: runners.length }); }
    },
    get index() { return i; },
  };
  function enter(k) {
    GEN += 1;
    cancelAuto();
    i = k;
    const cfg = C.scenes[k];
    UI.label.textContent = `${C.label} · ${k + 1} of ${runners.length}`;
    UI.title.textContent = cfg.title;
    UI.desc.textContent = cfg.desc;
    UI.back.disabled = k === 0;
    UI.dots.replaceChildren(...runners.map((_, n) => h("span", { class: n === k ? "on" : "" })));
    const last = k === runners.length - 1;
    UI.next.disabled = !done.has(k);
    UI.next.textContent = last ? "All done ✓" : cfg.next || "Next →";
    UI.next.classList.toggle("done", last);
    api.fb = h("p", { class: "feedback", "aria-live": "polite" });
    const kids = runners[k](api, cfg, done.has(k)) || [];
    UI.board.replaceChildren(...kids, api.fb);
    track("step_viewed", { step: cfg.id });
    api.start?.(); api.start = null;
  }
  UI.next.addEventListener("click", () => { if (done.has(i) && i < runners.length - 1) enter(i + 1); });
  UI.back.addEventListener("click", () => { if (i > 0) enter(i - 1); });
  enter(0);
  return api;
}
