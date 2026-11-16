/* Height reporter shared by every TVM artifact. The host sizes adaptive frames from a
   ResizeObserver, which can stay silent when the block is revealed late or the tab is in
   the background. We also tell the bridge our height whenever the board changes. */
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
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
