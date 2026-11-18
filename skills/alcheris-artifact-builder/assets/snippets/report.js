/* Height reporter. The host sizes adaptive frames from a ResizeObserver, which can stay
   silent when the block is revealed late or the tab is in the background. We also tell the
   bridge our height whenever the board changes. Include it last in every artifact. */
(() => {
  let timer = null;
  const send = () => {
    const hgt = Math.ceil(document.querySelector(".artifact")?.getBoundingClientRect().height || 0);
    if (hgt > 0) window.AlcherisArtifact?.resize?.(hgt);
  };
  const soon = () => { clearTimeout(timer); timer = setTimeout(send, 60); };
  const start = () => {
    const root = document.querySelector(".artifact");
    if (!root) return;
    new MutationObserver(soon).observe(root, { childList: true, subtree: true });
    [30, 400, 1500].forEach((ms) => setTimeout(send, ms));
  };
  window.addEventListener("resize", soon);
  // The guided player can mount the frame at 0px wide and widen it later without a resize
  // event reaching us (background tabs skip rendering steps). At 0px the content measures far
  // too tall, so poll the width and re-report when it changes.
  let lastW = -1;
  setInterval(() => {
    const w = document.documentElement.clientWidth;
    if (w !== lastW) { lastW = w; if (w > 0) soon(); }
  }, 500);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
