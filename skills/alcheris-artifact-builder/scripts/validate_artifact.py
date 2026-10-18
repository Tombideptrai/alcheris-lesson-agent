#!/usr/bin/env python3
"""Validate an Alcheris artifact definition before uploading it.

Mirrors the host contract (frontend artifactContract.js / backend
block_contract_validation_errors) and adds sizing checks for the bugs that
contract does not catch (vh-sized layouts, series colours tied to the theme).

Usage: python validate_artifact.py path/to/definition.json [more.json ...]
Exit code 1 if any file has errors. Warnings never fail the run.
"""
import json
import re
import sys

MOBILE_MODES = {"desktop_recommended", "desktop_required", "full", "simplified", "viewer"}
COMPLETION_TYPES = {"manual", "none", "on_interaction", "on_submit"}
BASELINE_EVENTS = ["block_viewed", "block_interacted", "block_completed"]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
INTERNAL_SCROLL = re.compile(r"overflow(?:-x|-y)?\s*:\s*(?:auto|scroll)\b", re.I)
VH_SIZE = re.compile(r"(?:^|[;{\s])(?:min-|max-)?height\s*:\s*[^;}]*\b100(?:d|s|l)?vh\b", re.I)
PCT_ROOT = re.compile(r"(?:html|body)[^{]*\{[^}]*(?<!-)height\s*:\s*100%", re.I)


def file_content(entry):
    return entry.get("content", "") if isinstance(entry, dict) else str(entry or "")


def check(d):
    errors, warnings = [], []
    err = lambda path, msg: errors.append(f"{path}: {msg}")
    warn = lambda msg: warnings.append(msg)

    if d.get("type") != "artifact":
        err("type", 'must be "artifact"')
    if not isinstance(d.get("title"), str) or not d["title"].strip():
        err("title", "must be a non-empty string")
    if not SEMVER.match(str(d.get("version", ""))):
        err("version", "use semantic version, e.g. 1.0.0")
    if d.get("runtime") != "html_sandbox":
        err("runtime", 'only "html_sandbox" is supported')

    app = d.get("appearance")
    if app is not None:
        if app.get("mode") not in {"inherit", "fixed"}:
            err("appearance.mode", "use inherit or fixed")
        if app.get("mode") == "inherit" and app.get("tokenVersion") != "1":
            err("appearance.tokenVersion", 'inherit needs tokenVersion "1"')

    vp = d.get("viewport")
    if vp is None:
        warn("no viewport: host defaults to square; set portrait or square explicitly")
    else:
        if vp.get("preset") not in {"square", "portrait"}:
            err("viewport.preset", "use square or portrait")
        if vp.get("scrolling") != "none":
            err("viewport.scrolling", 'must be "none"')
    if "embedHeight" in d:
        err("embedHeight", "remove it; use viewport.preset")

    files = d.get("files") or {}
    entry = d.get("entry") or "/index.html"
    if not files:
        err("files", "at least one file is required")
    if entry not in files:
        err("entry", f"{entry} not found in files")
    code = "\n".join(file_content(f) for f in files.values())
    if len(code) > 200_000:
        err("files", f"total {len(code)} chars, limit 200000")
    layout = "\n".join(file_content(f) for p, f in files.items() if p.endswith((".html", ".css")))
    if INTERNAL_SCROLL.search(layout):
        err("files", "overflow auto/scroll found; split content into steps instead")

    targets = d.get("renderTargets") or {}
    for key in ("editorBlock", "fullPanel", "playerDesktop", "playerMobile"):
        if targets.get(key) is not True:
            err(f"renderTargets.{key}", "must be true")
    if (d.get("mobileBehavior") or {}).get("mode") not in MOBILE_MODES:
        err("mobileBehavior.mode", f"one of {sorted(MOBILE_MODES)}")

    completion = (d.get("completion") or {}).get("type")
    if completion not in COMPLETION_TYPES:
        err("completion.type", f"one of {sorted(COMPLETION_TYPES)}")
    calls_submit = re.search(r"AlcherisArtifact\??\.\s*submit\s*\(", code)
    calls_complete = re.search(r"AlcherisArtifact\??\.\s*complete\s*\(", code)
    sub = d.get("submission") or {}
    if not isinstance(sub.get("enabled"), bool):
        err("submission.enabled", "must be true or false")
    if not sub.get("enabled") and sub.get("mode") not in (None, "none"):
        err("submission.mode", 'use "none" when submissions are disabled')
    if sub.get("enabled") and sub.get("storage") != "alcheris_managed":
        err("submission.storage", 'must be "alcheris_managed"')
    if sub.get("enabled") and not calls_submit:
        err("files./script.js", "submittable artifacts must call AlcherisArtifact.submit(...)")
    if completion == "on_submit" and not calls_submit:
        err("completion.type", "on_submit requires AlcherisArtifact.submit(...)")
    if completion == "manual" and not (calls_complete or calls_submit):
        err("completion.type", "manual requires AlcherisArtifact.complete(...) or submit(...)")

    events = (d.get("analytics") or {}).get("events") or []
    for ev in BASELINE_EVENTS:
        if ev not in events:
            err("analytics.events", f"missing {ev}")

    sec = d.get("security") or {}
    if sec.get("sandbox") is not True:
        err("security.sandbox", "must be true")
    for key in ("allowNetwork", "allowStorage", "allowClipboard"):
        if not isinstance(sec.get(key), bool):
            err(f"security.{key}", "must be true or false")
    if sec.get("allowNetwork") is True:
        err("security.allowNetwork", "network is disabled for artifacts")
    if sec.get("allowStorage") is not False:
        err("security.allowStorage", "must stay false")

    # Sizing heuristics: the host sizes editor/preview frames FROM the content height.
    css = "\n".join(file_content(f) for p, f in files.items() if p.endswith(".css"))
    html = "\n".join(file_content(f) for p, f in files.items() if p.endswith(".html"))
    if VH_SIZE.search(css) or VH_SIZE.search(html):
        warn("height sized with 100vh: in adaptive frames this locks the frame at its first height "
             "(big empty band / growth). Size from width (vw) instead; see references/frame-and-sizing.md")
    if PCT_ROOT.search(css):
        warn("html/body height: 100% (host overrides it to auto; layouts relying on it break)")
    if re.search(r"--c\d+\s*:\s*var\(--color-primary", css):
        warn("a data/series colour is tied to --color-primary; it can collide with other series in teacher themes")
    if not re.search(r"@media[^{]*max-width", css):
        warn("no max-width media query: check phone frames (320-383px wide, 9:16) with frame_check.html")
    if re.search(r"\beval\s*\(|new\s+Function\s*\(", code):
        warn("eval/new Function found: avoid in artifacts")
    return errors, warnings


def main(paths):
    failed = False
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        # Accept a raw definition or an .alcheris-artifact.json package.
        definition = data.get("definition", data) if isinstance(data, dict) else data
        errors, warnings = check(definition)
        size = sum(len(file_content(f)) for f in (definition.get("files") or {}).values())
        status = "FAIL" if errors else "OK"
        print(f"{status} {path} ({size} chars)")
        for e in errors:
            print(f"  error   {e}")
        for w in warnings:
            print(f"  warning {w}")
        failed |= bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
