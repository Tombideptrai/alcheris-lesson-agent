# Artifact definition contract

The editor (`artifactContract.js`) and the backend (`block_contract_validation_errors`) both validate this. A rejected save writes nothing and returns `block_contract_errors` with the field path. `scripts/validate_artifact.py` mirrors these rules.

## Template

```json
{
  "type": "artifact",
  "title": "Every trend graph is a line graph",
  "version": "1.0.0",
  "runtime": "html_sandbox",
  "entry": "/index.html",
  "description": "One sentence for the teacher's artifact library.",
  "appearance": { "mode": "inherit", "tokenVersion": "1" },
  "viewport": { "preset": "portrait", "scrolling": "none" },
  "renderTargets": { "editorBlock": true, "fullPanel": true, "playerDesktop": true, "playerMobile": true },
  "mobileBehavior": { "mode": "full", "layout": "responsive", "minWidth": 320 },
  "completion": { "type": "manual" },
  "submission": { "enabled": false, "mode": "none", "storage": "alcheris_managed" },
  "analytics": { "events": ["block_viewed", "block_interacted", "block_completed"] },
  "security": { "sandbox": true, "allowNetwork": false, "allowStorage": false, "allowClipboard": false },
  "files": {
    "/index.html": { "type": "text/html", "content": "…" },
    "/styles.css": { "type": "text/css", "content": "…" },
    "/script.js": { "type": "application/javascript", "content": "…" }
  }
}
```

The host inlines every `.css` file and every `.js` file into the entry HTML. `<link rel=stylesheet>` and `<script src>` tags are stripped, so they only matter for local preview.

## Rules

| Field | Rule |
|---|---|
| `type` | `"artifact"` |
| `title` | non-empty string |
| `version` | semver `x.y.z` |
| `runtime` | `"html_sandbox"` |
| `entry` | must exist in `files` (default `/index.html`) |
| `files` | at least one; total under 200 KB |
| `appearance.mode` | `inherit` (needs `tokenVersion: "1"`) or `fixed` |
| `viewport.preset` | `square` or `portrait`; `scrolling` must be `"none"`; no `embedHeight` |
| HTML/CSS | no `overflow(-x\|-y): auto\|scroll` anywhere |
| `renderTargets.*` | all four `true` |
| `mobileBehavior.mode` | `full`, `simplified`, `viewer`, `desktop_recommended`, `desktop_required` |
| `completion.type` | `manual`, `none`, `on_interaction`, `on_submit` |
| `manual` completion | code must call `AlcherisArtifact.complete(` or `.submit(` |
| `submission.enabled` | boolean; if false, `mode` is `none` |
| enabled submission | `storage: "alcheris_managed"` and code calls `.submit(` |
| `on_submit` | code calls `.submit(` |
| `analytics.events` | includes `block_viewed`, `block_interacted`, `block_completed` |
| `security.sandbox` | `true` |
| `security.allowNetwork` | `false` (network is disabled during beta) |
| `security.allowStorage` | `false` |
| `security.allowClipboard` | boolean; `true` only if the activity needs it |

## Bridge

```js
window.AlcherisArtifact?.track('step_viewed', { step: 2 });   // analytics, aggregate only
window.AlcherisArtifact?.complete({ transformed: ['table'] }); // marks the block done
window.AlcherisArtifact?.submit({ answer }, { files });        // teacher review inbox
window.AlcherisArtifact?.onThemeChange((theme) => { /* tokens already applied to :root */ });
```

The host writes theme tokens onto `document.documentElement` and sets `data-alcheris-theme="light|dark"` and `color-scheme`. Allowed tokens: `--color-background`, `--color-foreground`, `--color-muted`, `--color-muted-foreground`, `--color-border`, `--color-input`, `--color-card`, `--color-card-foreground`, `--color-surface`, `--color-surface-foreground`, `--color-primary`, `--color-primary-foreground`, `--color-accent`, `--color-accent-foreground`, `--color-ring`, `--color-success`, `--color-warning`, `--color-error`, `--radius`.

## Security

No secrets in any file. Media must come from Alcheris-managed URLs (teacher assets or `media.alcheris.com`), because the CSP blocks other origins when the network is off. Data URIs are fine for small images. Never use `eval` or `new Function`, never handle credentials, and never fetch anything.
