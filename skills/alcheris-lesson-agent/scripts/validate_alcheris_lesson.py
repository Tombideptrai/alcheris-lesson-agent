#!/usr/bin/env python3
"""Validate an Alcheris lesson for common AI-agent mistakes."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request


CUSTOM_FIELD_TYPES = {
    "instructions",
    "short_text",
    "long_text",
    "choice",
    "checklist",
    "file_upload",
}

CUSTOM_INSPECTOR_TYPES = {"text", "textarea", "number", "boolean", "choice"}
CUSTOM_MOBILE_MODES = {"native", "simplified", "viewer", "desktop_recommended", "desktop_required"}
CUSTOM_SUBMISSION_MODES = {
    "none",
    "draft_only",
    "submit_required",
    "draft_and_submit",
    "teacher_review_required",
    "score_required",
}
CUSTOM_COMPLETION_TYPES = {
    "manual",
    "on_interaction",
    "on_submit",
    "score_threshold",
    "teacher_reviewed",
    "all_required_fields_valid",
    "checkpoint_passed",
}
CUSTOM_BASELINE_EVENTS = {"block_viewed", "block_interacted", "block_completed"}
CUSTOM_OPTIONAL_EVENTS = {
    "draft_saved",
    "attempt_started",
    "attempt_submitted",
    "answer_changed",
    "feedback_viewed",
    "hint_used",
    "score_changed",
    "desktop_required_seen",
}
HEADING_TYPES = {"h1", "h2", "h3", "h4", "h5", "h6"}
BEAT_ACTIVITY_TYPES = {
    "quiz", "cloze", "sequence", "flashcard", "snippet", "coding", "data-lab",
    "interaction", "canvas", "mindmap", "comparison", "essay", "custom_activity", "artifact", "checkpoint",
}

CUSTOM_ALLOWED_EVENTS = CUSTOM_BASELINE_EVENTS | CUSTOM_OPTIONAL_EVENTS
CUSTOM_EMITS = {"submitted", "completed", "score_changed"}
CUSTOM_SIGNALS = {"submission_status", "score", "completion_status"}
ARTIFACT_MOBILE_MODES = {"full", "viewer", "simplified", "desktop_recommended", "desktop_required"}
ARTIFACT_COMPLETION_TYPES = {"none", "manual", "on_interaction", "on_submit"}
ARTIFACT_RUNTIME = "html_sandbox"
ARTIFACT_MAX_INLINE_BYTES = 200 * 1024


def request_json(method: str, url: str, token: str | None = None, payload: dict | None = None) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: HTTP {exc.code}: {body}") from exc


def authenticate(base_url: str, username: str, password: str) -> str:
    data = request_json("POST", f"{base_url}/api/token/", payload={"username": username, "password": password})
    return data["access"]


def has_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def strip_html(value: str) -> str:
    return re.sub(r"<[^>]*>", " ", value).strip()


def lexical_json_has_text(value) -> bool:
    if isinstance(value, dict):
        text = value.get("text")
        if has_text(text):
            return True
        return any(lexical_json_has_text(item) for item in value.values())
    if isinstance(value, list):
        return any(lexical_json_has_text(item) for item in value)
    return False


def rich_text_has_visible_content(content: dict) -> bool:
    if has_text(content.get("text")):
        return True
    if has_text(content.get("html")) and has_text(strip_html(content.get("html", ""))):
        return True
    return lexical_json_has_text(content.get("json"))


def option_has_text(option) -> bool:
    if has_text(option):
        return True
    if isinstance(option, dict):
        return any(has_text(option.get(key)) for key in ("text", "label", "value"))
    return False


def contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def block_label(page_index: int, block_index: int, block: dict) -> str:
    return f"page {page_index + 1}, block {block_index + 1} ({block.get('type', 'unknown')})"


def normalize_right_panel_mode(mode: str | None) -> str:
    if mode == "ielts":
        return "exam"
    if mode == "leetcode":
        return "ui-project"
    return mode or "standard"


def is_json_compatible(value) -> bool:
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(is_json_compatible(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and is_json_compatible(item) for key, item in value.items())
    return False


def artifact_file_content(file_data) -> str | None:
    if isinstance(file_data, str):
        return file_data
    if isinstance(file_data, dict):
        content = file_data.get("content", file_data.get("code", ""))
        return content if isinstance(content, str) else None
    return None


def validate_custom_activity(content: dict, label: str, warnings: list[str], errors: list[str]) -> None:
    if not isinstance(content, dict):
        errors.append(f"{label}: custom_activity content must be an object")
        return
    if not is_json_compatible(content):
        errors.append(f"{label}: custom_activity content must contain only JSON-compatible values")

    if content.get("type") != "custom_activity":
        errors.append(f"{label}: custom_activity content.type must be custom_activity")
    if not has_text(content.get("title")):
        errors.append(f"{label}: custom_activity needs a title")
    if not re.match(r"^\d+\.\d+\.\d+$", str(content.get("version") or "")):
        errors.append(f"{label}: custom_activity version should use semantic format like 1.0.0")

    fields = content.get("fields") or []
    if not isinstance(fields, list) or not fields:
        errors.append(f"{label}: custom_activity needs at least one field")
        fields = []
    field_ids: set[str] = set()
    for fi, field in enumerate(fields):
        if not isinstance(field, dict):
            errors.append(f"{label}, field {fi + 1}: field must be an object")
            continue
        field_id = field.get("id")
        field_type = field.get("type")
        if not has_text(field_id):
            errors.append(f"{label}, field {fi + 1}: field id is required")
        elif field_id in field_ids:
            errors.append(f"{label}, field {fi + 1}: duplicate field id {field_id}")
        else:
            field_ids.add(field_id)
        if field_type not in CUSTOM_FIELD_TYPES:
            errors.append(f"{label}, field {fi + 1}: unsupported custom_activity field type {field_type}")
        if not has_text(field.get("label")):
            errors.append(f"{label}, field {fi + 1}: field label is required")
        if field_type in {"choice", "checklist"}:
            options = field.get("options") or []
            if not isinstance(options, list) or not any(option_has_text(option) for option in options):
                errors.append(f"{label}, field {fi + 1}: choice/checklist fields need non-empty options")

    targets = content.get("renderTargets") or {}
    if targets.get("editorBlock") is not True:
        errors.append(f"{label}: renderTargets.editorBlock must be true")
    if targets.get("playerDesktop") is not True:
        errors.append(f"{label}: renderTargets.playerDesktop must be true")
    if targets.get("playerMobile") is not True:
        errors.append(f"{label}: renderTargets.playerMobile must be true")

    mobile = content.get("mobilePlayer") or {}
    if mobile.get("mode") not in CUSTOM_MOBILE_MODES:
        errors.append(f"{label}: mobilePlayer.mode is required and must be supported")
    if mobile.get("layout") != "single_column":
        errors.append(f"{label}: mobilePlayer.layout must be single_column")
    if not has_text(mobile.get("behavior")):
        errors.append(f"{label}: mobilePlayer.behavior is required")

    inspector = content.get("inspector") or {}
    properties = inspector.get("properties")
    if not isinstance(properties, list):
        errors.append(f"{label}: inspector.properties must be a list")
    else:
        seen_props: set[str] = set()
        for pi, prop in enumerate(properties):
            if not isinstance(prop, dict):
                errors.append(f"{label}, inspector property {pi + 1}: property must be an object")
                continue
            prop_id = prop.get("id")
            if not has_text(prop_id):
                errors.append(f"{label}, inspector property {pi + 1}: property id is required")
            elif prop_id in seen_props:
                errors.append(f"{label}, inspector property {pi + 1}: duplicate property id {prop_id}")
            else:
                seen_props.add(prop_id)
            if prop.get("type") not in CUSTOM_INSPECTOR_TYPES:
                errors.append(f"{label}, inspector property {pi + 1}: unsupported property type {prop.get('type')}")
            if not has_text(prop.get("label")):
                errors.append(f"{label}, inspector property {pi + 1}: label is required")

    submission = content.get("submission") or {}
    enabled = submission.get("enabled")
    mode = submission.get("mode")
    if not isinstance(enabled, bool):
        errors.append(f"{label}: submission.enabled must be true or false")
    if mode not in CUSTOM_SUBMISSION_MODES:
        errors.append(f"{label}: submission.mode is required and must be supported")
    if enabled is False and mode != "none":
        errors.append(f"{label}: submission.mode must be none when submission.enabled is false")
    if enabled is True and submission.get("storage") != "alcheris_managed":
        errors.append(f"{label}: submission.storage must be alcheris_managed")

    completion = content.get("completion") or {}
    if completion.get("type") not in CUSTOM_COMPLETION_TYPES:
        errors.append(f"{label}: completion.type is required and must be supported")

    events = (content.get("analytics") or {}).get("events") or []
    if not isinstance(events, list):
        errors.append(f"{label}: analytics.events must be a list")
    else:
        missing = sorted(CUSTOM_BASELINE_EVENTS - set(events))
        if missing:
            errors.append(f"{label}: analytics.events missing baseline events {missing}")
        for event in events:
            if event not in CUSTOM_ALLOWED_EVENTS:
                warnings.append(f"{label}: analytics event {event} is not in the custom_activity contract")

    interactions = content.get("interactions") or {}
    for signal in interactions.get("emits") or []:
        if signal not in CUSTOM_EMITS:
            warnings.append(f"{label}: unsupported emitted signal {signal}")
    for signal in interactions.get("providesSignals") or []:
        if signal not in CUSTOM_SIGNALS:
            warnings.append(f"{label}: unsupported provided signal {signal}")


def validate_artifact(content: dict, label: str, warnings: list[str], errors: list[str]) -> None:
    if not isinstance(content, dict):
        errors.append(f"{label}: artifact content must be an object")
        return
    if not is_json_compatible(content):
        errors.append(f"{label}: artifact content must contain only JSON-compatible values")

    if content.get("type") != "artifact":
        errors.append(f"{label}: artifact content.type must be artifact")
    if not has_text(content.get("title")):
        errors.append(f"{label}: artifact needs a title")
    if not re.match(r"^\d+\.\d+\.\d+$", str(content.get("version") or "")):
        errors.append(f"{label}: artifact version should use semantic format like 1.0.0")
    if content.get("runtime") != ARTIFACT_RUNTIME:
        errors.append(f"{label}: artifact runtime must be {ARTIFACT_RUNTIME}")

    files = content.get("files") or {}
    if not isinstance(files, dict) or not files:
        errors.append(f"{label}: artifact files must be a non-empty object")
        files = {}
    else:
        total_size = 0
        for path, body in files.items():
            if not has_text(path) or not str(path).startswith("/"):
                errors.append(f"{label}: artifact file path {path!r} must start with /")
            body_text = artifact_file_content(body)
            if body_text is None:
                errors.append(f"{label}: artifact file {path!r} must be text or an object with text content")
                continue
            total_size += len(body_text.encode("utf-8"))
            if "<script src=" in body_text.lower():
                warnings.append(f"{label}: artifact file {path!r} references an external script; prefer bundled code and keep network off")
        if total_size > ARTIFACT_MAX_INLINE_BYTES:
            errors.append(f"{label}: artifact inline files exceed {ARTIFACT_MAX_INLINE_BYTES} bytes")

    entry = content.get("entry")
    if not has_text(entry) or entry not in files:
        errors.append(f"{label}: artifact entry must point to an existing file")

    targets = content.get("renderTargets") or {}
    for target in ("editorBlock", "fullPanel", "playerDesktop", "playerMobile"):
        if targets.get(target) is not True:
            errors.append(f"{label}: renderTargets.{target} must be true")

    mobile = content.get("mobileBehavior") or {}
    if mobile.get("mode") not in ARTIFACT_MOBILE_MODES:
        errors.append(f"{label}: mobileBehavior.mode is required and must be supported")
    if mobile.get("mode") == "full" and mobile.get("layout") == "fixed":
        warnings.append(f"{label}: artifact is marked mobile full but layout is fixed")

    submission = content.get("submission") or {}
    enabled = submission.get("enabled")
    mode = submission.get("mode")
    if not isinstance(enabled, bool):
        errors.append(f"{label}: submission.enabled must be true or false")
    if mode not in CUSTOM_SUBMISSION_MODES:
        errors.append(f"{label}: submission.mode is required and must be supported")
    if enabled is False and mode != "none":
        errors.append(f"{label}: submission.mode must be none when submission.enabled is false")
    if enabled is True and submission.get("storage") != "alcheris_managed":
        errors.append(f"{label}: submission.storage must be alcheris_managed")

    completion = content.get("completion") or {}
    if completion.get("type") not in ARTIFACT_COMPLETION_TYPES:
        errors.append(f"{label}: completion.type is required and must be supported")

    events = (content.get("analytics") or {}).get("events") or []
    if not isinstance(events, list):
        errors.append(f"{label}: analytics.events must be a list")
    else:
        missing = sorted(CUSTOM_BASELINE_EVENTS - set(events))
        if missing:
            errors.append(f"{label}: analytics.events missing baseline events {missing}")
        for event in events:
            if event not in CUSTOM_ALLOWED_EVENTS:
                warnings.append(f"{label}: analytics event {event} is not in the artifact contract")

    security = content.get("security") or {}
    if security.get("sandbox") is not True:
        errors.append(f"{label}: security.sandbox must be true")
    if security.get("allowStorage") is not False:
        errors.append(f"{label}: security.allowStorage must be false")
    for flag in ("allowNetwork", "allowClipboard"):
        if not isinstance(security.get(flag), bool):
            errors.append(f"{label}: security.{flag} must be true or false")


def validate_block(block: dict, page_index: int, block_index: int, warnings: list[str], errors: list[str]) -> None:
    btype = block.get("type")
    content = block.get("content") or {}
    label = block_label(page_index, block_index, block)

    if btype in {"text", "paragraph", "h1", "h2", "h3", "h4", "h5", "h6", "quote"}:
        if not rich_text_has_visible_content(content):
            errors.append(f"{label}: text-like block has no visible text in content.text, content.html, or content.json")
    elif btype == "callout":
        if not has_text(content.get("text")):
            errors.append(f"{label}: callout has empty content.text")
    elif btype == "accordion":
        if not has_text(content.get("title")) or not has_text(content.get("body")):
            errors.append(f"{label}: accordion needs title and body")
    elif btype == "image":
        if not has_text(content.get("url")):
            errors.append(f"{label}: image has empty url")
        if not has_text(content.get("altText")):
            warnings.append(f"{label}: image should include altText")
    elif btype == "table":
        headers = content.get("headers") or []
        rows = content.get("rows") or []
        if not headers or not rows:
            errors.append(f"{label}: table needs non-empty headers and rows")
        elif any(not has_text(cell) for cell in headers):
            warnings.append(f"{label}: table has an empty header")
    elif btype == "video":
        if not has_text(content.get("url")):
            errors.append(f"{label}: video has empty url")
    elif btype == "gallery":
        if not content.get("slides"):
            warnings.append(f"{label}: gallery has no slides")
    elif btype == "embed":
        if not has_text(content.get("embedUrl")):
            errors.append(f"{label}: embed needs embedUrl")
    elif btype == "pdf":
        if not has_text(content.get("url")) and not has_text(content.get("fileUrl")):
            warnings.append(f"{label}: pdf should include a document url")
    elif btype == "quiz":
        questions = content.get("questions") or []
        if not questions:
            errors.append(f"{label}: quiz has no questions")
        for qi, q in enumerate(questions):
            qtype = q.get("type") or "multiple_choice"
            options = q.get("options") or []
            if not has_text(q.get("question")):
                errors.append(f"{label}, question {qi + 1}: empty question")

            if qtype in {"multiple_choice", "multiple_select"}:
                if len([o for o in options if option_has_text(o)]) < 2:
                    errors.append(f"{label}, question {qi + 1}: fewer than 2 non-empty options")

            if qtype == "multiple_choice":
                correct = q.get("correctAnswerIndex")
                if not isinstance(correct, int) or correct < 0 or correct >= len(options):
                    errors.append(f"{label}, question {qi + 1}: invalid correctAnswerIndex")
            elif qtype == "multiple_select":
                correct_indices = q.get("correctAnswerIndices") or []
                if not correct_indices:
                    errors.append(f"{label}, question {qi + 1}: multiple_select needs correctAnswerIndices")
                for correct in correct_indices:
                    if not isinstance(correct, int) or correct < 0 or correct >= len(options):
                        errors.append(f"{label}, question {qi + 1}: invalid correctAnswerIndices entry")
            elif qtype == "short_answer":
                if not has_text(q.get("correctShortAnswer")):
                    errors.append(f"{label}, question {qi + 1}: short_answer needs correctShortAnswer")
            elif qtype == "cloze":
                question = q.get("question") or ""
                if "[" not in question or "]" not in question:
                    errors.append(f"{label}, question {qi + 1}: cloze question needs bracketed answers")
            else:
                warnings.append(f"{label}, question {qi + 1}: unknown question type {qtype}")

            if not has_text(q.get("explanation")):
                warnings.append(f"{label}, question {qi + 1}: add explanation")
    elif btype == "flashcard":
        if not has_text(content.get("title")) or not has_text(content.get("instructions")):
            warnings.append(f"{label}: flashcard should include learner-facing title and instructions")
        cards = content.get("cards") or []
        if not cards:
            errors.append(f"{label}: flashcard deck has no cards")
        for ci, card in enumerate(cards):
            if not has_text(card.get("front")) or not has_text(card.get("back")):
                errors.append(f"{label}, card {ci + 1}: front and back are required")
            if has_text(card.get("front")) and card.get("front", "").strip().lower() in {"question 1", "question 2", "overview question 1", "overview question 2", "overview question 3"}:
                warnings.append(f"{label}, card {ci + 1}: front is too generic for self-study")
    elif btype == "sequence":
        if not has_text(content.get("title")) or not has_text(content.get("instructions")):
            warnings.append(f"{label}: sequence should include learner-facing title and instructions")
        items = content.get("items") or []
        if len(items) < 2:
            errors.append(f"{label}: sequence needs at least 2 items")
        for ii, item in enumerate(items):
            text = item.get("text") if isinstance(item, dict) else item
            if not has_text(text):
                errors.append(f"{label}, item {ii + 1}: empty sequence item")
    elif btype == "cloze":
        if not has_text(content.get("title")) or not has_text(content.get("instructions")):
            warnings.append(f"{label}: cloze should include learner-facing title and instructions")
        text = content.get("text")
        if not has_text(text) or "[" not in text or "]" not in text:
            errors.append(f"{label}: cloze needs text with bracketed answers")
        elif "/" not in text:
            warnings.append(f"{label}: consider accepted alternatives such as [rose/increased/climbed]")
        if not (content.get("wordBank") or []):
            warnings.append(f"{label}: cloze has no wordBank; add draggable words (with distractors) so learners see a word list")
    elif btype == "essay":
        if not has_text(content.get("prompt")):
            errors.append(f"{label}: essay needs a prompt")
        if not isinstance(content.get("minWords"), int) or content.get("minWords", 0) <= 0:
            warnings.append(f"{label}: essay should include positive minWords")
    elif btype == "custom_activity":
        validate_custom_activity(content, label, warnings, errors)
    elif btype == "artifact":
        validate_artifact(content, label, warnings, errors)
    elif btype == "data-lab":
        if not content.get("cells"):
            errors.append(f"{label}: data-lab needs cells")
    elif btype == "interaction":
        mode = content.get("mode")
        if mode not in {"graph", "distribution", "equation", "embed"}:
            warnings.append(f"{label}: interaction should use mode graph, distribution, equation, or embed")
        elif mode == "graph":
            series = content.get("series")
            if isinstance(series, list) and series:
                for si, s in enumerate(series):
                    pts = (s or {}).get("points") or []
                    if not isinstance(pts, list) or len(pts) < 2:
                        errors.append(f"{label}: interaction graph series {si + 1} needs at least 2 points")
                    elif any(not isinstance(p, dict) or p.get("value") is None or not has_text(p.get("label")) for p in pts):
                        errors.append(f"{label}: interaction graph series {si + 1} points need label and value")
            else:
                data = content.get("graphData") or []
                if not isinstance(data, list) or len(data) < 2:
                    errors.append(f"{label}: interaction graph needs graphData (or series) with at least 2 points")
                elif any(not isinstance(p, dict) or p.get("value") is None or not has_text(p.get("label")) for p in data):
                    errors.append(f"{label}: interaction graph points need label and value")
        elif mode == "distribution":
            if content.get("statMean") is None or content.get("statStdDev") is None:
                errors.append(f"{label}: interaction distribution needs statMean and statStdDev")
        elif mode == "equation":
            if not has_text(content.get("mathExpression")):
                errors.append(f"{label}: interaction equation needs mathExpression")
            if content.get("gameMode") and not (content.get("targets") or []):
                warnings.append(f"{label}: interaction equation gameMode needs targets")
        elif mode == "embed":
            if not has_text(content.get("embedUrl")):
                errors.append(f"{label}: interaction embed needs embedUrl")
    elif btype == "illustration":
        scenes = content.get("scenes") or []
        if not isinstance(scenes, list) or not scenes:
            errors.append(f"{label}: illustration needs at least one scene")
        for si, scene in enumerate(scenes):
            if not isinstance(scene, dict) or not (scene.get("layers") or []):
                errors.append(f"{label}, scene {si + 1}: illustration scene needs layers")
    elif btype == "comparison":
        ctype = content.get("compareType")
        pairs = {
            "image": ("beforeImage", "afterImage"),
            "code": ("beforeCode", "afterCode"),
            "text": ("beforeText", "afterText"),
        }
        if ctype not in pairs:
            errors.append(f"{label}: comparison needs compareType image, code, or text")
        else:
            before_key, after_key = pairs[ctype]
            if not has_text(content.get(before_key)) or not has_text(content.get(after_key)):
                errors.append(f"{label}: comparison ({ctype}) needs {before_key} and {after_key}")
    elif btype == "canvas":
        if not (content.get("paths") or content.get("images")):
            warnings.append(f"{label}: canvas has no paths or images to display")
    elif btype == "mindmap":
        nodes = content.get("nodes") or []
        if not isinstance(nodes, list) or not nodes:
            warnings.append(f"{label}: mindmap has no nodes")
    elif btype == "checkpoint":
        if not has_text(content.get("label")):
            warnings.append(f"{label}: checkpoint should include a visible label")


def validate_lesson(lesson: dict) -> tuple[list[str], list[str], dict]:
    warnings: list[str] = []
    errors: list[str] = []
    pages = lesson.get("pages") or []
    summary = {"pages": []}
    has_image = False
    has_interaction_graph = False
    has_chart = False
    has_interaction = False
    mc_indices = []
    active_blocks = {
        "quiz",
        "cloze",
        "sequence",
        "flashcard",
        "essay",
        "custom_activity",
        "artifact",
        "coding",
        "data-lab",
        "interaction",
        "checkpoint",
        "illustration",
        "canvas",
        "mindmap",
        "comparison",
    }
    active_count = 0

    if not pages:
        errors.append("lesson has no pages")

    for pi, page in enumerate(pages):
        blocks = sorted(page.get("blocks") or [], key=lambda b: (b.get("panel", ""), b.get("order", 0)))
        left = [b for b in blocks if b.get("panel") == "leftPanel"]
        right = [b for b in blocks if b.get("panel") == "rightPanel"]
        mode = normalize_right_panel_mode(page.get("rightPanelMode"))
        layout = page.get("layout") or "split"
        summary["pages"].append({
            "title": page.get("title"),
            "layout": layout,
            "rightPanelMode": mode,
            "left": [b.get("type") for b in left],
            "right": [b.get("type") for b in right],
        })

        if layout == "split":
            if not left:
                errors.append(f"page {pi + 1}: split page has empty left panel")
            if not right:
                errors.append(f"page {pi + 1}: split page has empty right panel")
            right_activities = [b for b in right if b.get("type") in BEAT_ACTIVITY_TYPES]
            left_headings = [b for b in left if b.get("type") in HEADING_TYPES]
            if len(right_activities) > 1 and not left_headings:
                warnings.append(
                    f"page {pi + 1}: split page has {len(right_activities)} right-panel activities but no left-panel headings; "
                    "mobile beats will chunk the left panel blindly - add one heading per teaching point (see references/alcheris-learning-beats.md)"
                )

        if mode != "standard":
            right_types = [b.get("type") for b in right]
            allowed = {
                "essay": {"essay"},
                "exam": {"quiz"},
                "code-practice": {"coding"},
                "ui-project": {"coding"},
                "data-lab": {"data-lab"},
                "illustration": {"illustration"},
                "artifact": {"artifact"},
            }.get(mode)
            if allowed and any(t not in allowed for t in right_types):
                warnings.append(f"page {pi + 1}: rightPanelMode {mode} has non-workspace block types {right_types}")
            if mode in {"essay", "exam", "data-lab", "code-practice", "ui-project", "illustration", "artifact"} and len(right) != 1:
                warnings.append(f"page {pi + 1}: full-panel mode {mode} should usually have exactly one right-panel block")
        elif len(right) == 1:
            right_type = right[0].get("type")
            suggested_modes = {
                "quiz": "exam",
                "essay": "essay",
                "data-lab": "data-lab",
                "illustration": "illustration",
                "artifact": "artifact",
                "coding": "code-practice or ui-project",
            }
            if right_type in suggested_modes:
                warnings.append(f"page {pi + 1}: standard mode has one {right_type} workspace; consider rightPanelMode {suggested_modes[right_type]}")

        for bi, block in enumerate(blocks):
            if block.get("type") == "image":
                has_image = True
            if block.get("type") == "interaction" and (block.get("content") or {}).get("mode") == "graph":
                has_interaction_graph = True
            if block.get("type") == "interaction":
                has_interaction = True
            if block.get("type") == "chart":
                has_chart = True
            if block.get("type") in active_blocks:
                active_count += 1
            if block.get("type") == "quiz":
                for q in (block.get("content") or {}).get("questions", []):
                    if (q.get("type") or "multiple_choice") == "multiple_choice" and isinstance(q.get("correctAnswerIndex"), int):
                        mc_indices.append(q["correctAnswerIndex"])
            validate_block(block, pi, bi, warnings, errors)

    lesson_text = json.dumps(lesson, ensure_ascii=False).lower()
    chart_like = contains_any(lesson_text, ("chart", "graph", "table", "trend"))
    trend_writing_like = chart_like and contains_any(lesson_text, ("writing", "introduction", "overview", "overall", "response", "paragraph"))

    if chart_like and not (has_image or has_interaction_graph or has_chart or has_interaction):
        warnings.append("chart/data lesson appears to need a visual stimulus (image, chart, or interaction) but none was found")

    if trend_writing_like and has_image and not has_interaction_graph:
        warnings.append(
            "trend lesson uses a static chart image; consider an interaction graph (mode graph, slider reveal) so learners "
            "uncover the trend before writing - see references/alcheris-interactive-blocks.md"
        )

    if any(word in lesson_text for word in ("writing", "essay", "response", "paragraph")) and not any(word in lesson_text for word in ("vocabulary", "language bank", "useful language", "rubric", "checklist", "criteria")):
        warnings.append("writing/response lesson should include a language bank, rubric, checklist, or criteria section")

    if trend_writing_like and contains_any(lesson_text, ("introduction", "paraphrase")):
        intro_requirements = {
            "chart form": ("chart form", "line graph", "bar chart", "table", "pie chart", "mixed chart", "display"),
            "topic/unit": ("unit", "measured", "billions", "minutes", "percentage", "percent", "number of", "amount of"),
            "categories": ("category", "categories", "group", "groups", "types", "variables"),
            "place/time": ("place", "where", "scope", "time period", "between", "from", "to", "years", "months", "days", "period"),
            "trend exclusions": ("do not analyze", "do not mention rises", "no trends", "save", "overview", "body paragraph"),
        }
        missing_intro = [name for name, terms in intro_requirements.items() if not contains_any(lesson_text, terms)]
        if missing_intro:
            warnings.append("trend-writing introduction lesson should explicitly teach: " + ", ".join(missing_intro))

    if trend_writing_like and contains_any(lesson_text, ("overview", "overall")):
        overview_requirements = {
            "increase/decrease decisions": ("increase", "decrease", "rise", "fall", "return", "stable", "fluctuat"),
            "highest/lowest overall": ("highest", "lowest", "dominant", "remain lower", "remain higher"),
            "strongest change": ("strongest", "fastest", "sharpest", "dramatic", "biggest change", "most significant"),
            "grouping": ("group", "together", "similar", "contrast"),
            "exact-figure exclusion": ("no exact", "without exact", "save", "body paragraph", "supporting figures"),
        }
        missing_overview = [name for name, terms in overview_requirements.items() if not contains_any(lesson_text, terms)]
        if missing_overview:
            warnings.append("trend-writing overview lesson should explicitly teach: " + ", ".join(missing_overview))

    if len(mc_indices) >= 4:
        counts = {}
        for idx in mc_indices:
            counts[idx] = counts.get(idx, 0) + 1
        top_idx, top_n = max(counts.items(), key=lambda kv: kv[1])
        if top_n / len(mc_indices) >= 0.8:
            letter = "ABCDEFGH"[top_idx] if 0 <= top_idx < 8 else str(top_idx)
            warnings.append(
                f"{top_n}/{len(mc_indices)} multiple-choice answers are at position {letter} (index {top_idx}); "
                "shuffle each question's options so the correct answer is distributed across positions"
            )

    if active_count == 0:
        errors.append("lesson has no active learning blocks")
    summary["active_blocks"] = active_count
    summary["has_image"] = has_image
    return warnings, errors, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Alcheris lesson for render and pedagogy issues.")
    parser.add_argument("lesson_id")
    parser.add_argument("--base-url", default=os.getenv("ALCHERIS_URL", "http://localhost:8000"))
    parser.add_argument("--username", default=os.getenv("ALCHERIS_EMAIL") or os.getenv("ALCHERIS_USERNAME"))
    parser.add_argument("--password", default=os.getenv("ALCHERIS_PASSWORD"))
    args = parser.parse_args()

    if not args.username or not args.password:
        print("Set ALCHERIS_EMAIL/ALCHERIS_USERNAME and ALCHERIS_PASSWORD, or pass credentials via env.", file=sys.stderr)
        return 2

    base_url = args.base_url.rstrip("/")
    token = authenticate(base_url, args.username, args.password)
    lesson = request_json("GET", f"{base_url}/api/lessons/{args.lesson_id}/", token=token)
    warnings, errors, summary = validate_lesson(lesson)

    print(json.dumps({"summary": summary, "warnings": warnings, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
