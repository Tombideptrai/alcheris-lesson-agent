/* Auto-advance, shared by every TVM artifact (build.mjs inlines it before the engine).
   autoNext(go, text): after a step is FRESHLY completed, wait long enough to read `text`
   (the feedback just shown), then call go(). The Next button fills like a progress bar
   while waiting; tapping it skips ahead. cancelAuto() is called on every step change. */
let AUTO = null;
function readMs(text) {
  const words = String(text || "").trim().split(/\s+/).filter(Boolean).length;
  return Math.max(1800, Math.min(5000, 1300 + words * 230));
}
function cancelAuto() {
  if (!AUTO) return;
  clearTimeout(AUTO.timer);
  AUTO.btn?.classList.remove("auto");
  AUTO = null;
}
function autoNext(go, text) {
  cancelAuto();
  const btn = document.getElementById("next");
  const ms = readMs(text);
  if (btn) { btn.style.setProperty("--auto-ms", `${ms}ms`); btn.classList.remove("auto"); void btn.offsetWidth; btn.classList.add("auto"); }
  const timer = setTimeout(() => { if (AUTO && AUTO.timer === timer) { cancelAuto(); go(); } }, ms);
  AUTO = { timer, btn };
}
