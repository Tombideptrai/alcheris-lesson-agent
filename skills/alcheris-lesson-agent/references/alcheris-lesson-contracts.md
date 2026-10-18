# Alcheris Lesson Contracts

## MCP And API Notes

The Alcheris MCP server (`mcp-server/` in the app repo, package `alcheris-mcp`) is also served as the claude.ai Alcheris connector. Its tools, by job:

| Job | Tools |
|---|---|
| Identity | `whoami` |
| Read | `list_lessons`, `get_lesson`, `get_block_content`, `get_lesson_quality`, `get_lesson_analytics` |
| Lesson | `create_lesson(title, description)`, `update_lesson(lesson_id, title?, description?, is_published?)`, `delete_lesson` |
| Page | `add_page(lesson_id, title, layout="split", position?)`, `update_page(lesson_id, page_index, title?, layout?, right_panel_mode?)`, `delete_page(lesson_id, page_id)` |
| Block | `add_block(lesson_id, page_index, panel, block_type, content?, position?, raw=False)`, `update_block(lesson_id, page_index, block_id, content, new_type?, raw=False)`, `delete_block(lesson_id, block_id)` |
| Restructure | `move_block`, `reorder_blocks`, `save_lesson_structure` (below) |
| Artifacts | `list_artifacts(scope)`, `save_artifact(name, definition, ...)`, `duplicate_artifact`, `add_artifact_block(lesson_id, page_index, artifact_id, panel="right", position?)` |
| Media search | `image_search`, `video_search`, `youtube_search` |

`page_index` is 0-based. `panel` is `"left"` or `"right"`. There is no duplicate-lesson tool; duplication is in the teacher UI (`POST /api/lessons/{id}/duplicate/`).

### Restructure tools

Every write reads the lesson, then sends the full lesson to `POST /api/lessons/{id}/autosave/` with explicit block orders and `base_revision` = the lesson's `content_revision`. Blocks keep their ids, content, learner answers, and analytics when moved.

- `move_block(lesson_id, block_id, page_index?, panel?, position?)`: move within a page, to the other panel, or to another page. Omitted arguments keep the current page/panel; omitted `position` appends. `position` is counted without the moved block.
- `reorder_blocks(lesson_id, page_index, left_ids?, right_ids?)`: the complete top-to-bottom order of a panel. An id from the other panel of the same page moves across. An omitted panel keeps its order. Every block of the page must still be placed.
- `save_lesson_structure(lesson_id, pages, deleted_block_ids?, deleted_page_ids?)`: one atomic write of the whole lesson.
  - `pages` lists every page to keep, in order: `{"id"?, "title"?, "layout"?: "single|split", "rightPanelMode"?: "standard|essay|exam|code-practice|data-lab|ui-project|artifact|illustration", "left": [...], "right": [...]}`. Omit `id` for a new page. Omitted title/layout/mode keep stored values.
  - A block entry is one of: `"<block uuid>"` or `{"id": "<uuid>"}` (keep content, only place it); `{"id": "<uuid>", "content": {...}}` (replace content, `type` optional); `{"type": "quiz", "content": {...}, "id"?: "my-client-id"}` (new block; a non-uuid id is echoed in `id_map`). Add `"raw": true` to any entry to store content exactly as given.
  - Every existing page and block must be placed or listed for deletion. Blocks on a deleted page that you place elsewhere are recreated with new ids (see `id_map`).
  - Returns the page/block summary, the new `content_revision`, `id_map`, and `warnings` (for example right-panel blocks on a single page).

### `raw` and content building

Without `raw`, `add_block`, `update_block`, and new entries in `save_lesson_structure` build content: plain/markdown text becomes Lexical rich text, quiz questions are normalized, and `update_block` merges into the existing content. With `raw: true`, content is stored exactly as given (`update_block` replaces the whole content). Use `raw` for anything copied from `get_block_content`, another lesson, or a stored callout (callout `text` is a Lexical JSON string; re-sending it without `raw` would treat that JSON as plain text).

Never "move" a block by deleting it and adding it again. That rebuilds rich text and loses formatting, gives the block a new id, and detaches learner answers and analytics.

### Errors

- `{"code": "edit_conflict"}` (HTTP 409): someone saved the lesson after you read it. Re-read, re-apply, save again.
- `{"code": "block_contract_invalid", "block_contract_errors": [{page_index, panel, block_index, block_id, block_type, errors}]}` (HTTP 400): a `custom_activity` or `artifact` failed backend validation. Nothing was saved.
- `{"error": "..."}`: a structure problem caught before saving (unknown block id, block not placed, bad page index).

### Connector caching

claude.ai caches the connector's tool list. If a tool or parameter documented here is missing, ask the user to disconnect and reconnect the Alcheris connector in claude.ai settings; a new chat alone may not refresh it.

Local backend defaults:

- Base URL: `http://localhost:8000`
- Frontend URL: `http://localhost:5173`
- Auth endpoint: `/api/token/`
- Lesson detail: `/api/lessons/{lesson_id}/`
- Autosave: `/api/lessons/{lesson_id}/autosave/`
- Quality: `/api/lessons/{lesson_id}/quality/`

Do not include credentials in final responses or artifacts.

## Readback Shape

The write path may accept pages shaped like:

```json
{
  "leftPanel": [{"type": "text", "content": {}}],
  "rightPanel": [{"type": "quiz", "content": {}}]
}
```

The read path commonly returns flat blocks:

```json
{
  "blocks": [
    {"type": "text", "panel": "leftPanel", "order": 0, "content": {}},
    {"type": "quiz", "panel": "rightPanel", "order": 0, "content": {}}
  ]
}
```

On verification, split blocks by `panel`; do not assume `leftPanel` and `rightPanel` are present in readback.

## Panel Semantics

Alcheris lessons are student-facing self-study lessons by default. Do not build a lesson plan inside the lesson player unless the user explicitly asks for a teacher edition.

Choose the page layout from the learning action:

- Use single or blog-style layout only when the page has no practice/check/application/production task. Good uses include an introduction, reflection, pure reference, or one continuous explorable explanation.
- Use split layout when the page has practice/check/application/production. The left side teaches or supplies source/exploration; the right side is the learner's practice/floating panel.
- Use split layout with a full-panel right mode when the right side is one focused practice/workspace desk.

Alcheris has two interaction categories:

- Exploratory interactions: graph/distribution/equation explorers, hotspot images, staged illustrations, comparisons, canvas replays, mindmaps, and visual/source inspection. These help the learner encounter or understand an idea and usually belong on the left.
- Practice interactions: quiz, cloze, sequence, flashcard, essay, branching_scenario, coding, data-lab, custom_activity, artifact, checkpoint, or any task where the learner answers, arranges, writes, codes, submits, or produces. These belong on the right/floating panel.
- `artifact` can be exploratory, practice, or production depending on the custom interface. If the native block inventory cannot express the intended learning experience well enough, create a sandboxed artifact instead of forcing a weak native-block fit.

Do not put the main exploratory stimulus above the right-panel practice. The two-panel design lets learners look up the source, guidance, criteria, and explanatory visuals while practising. If a right-panel question/card needs a visual, include an `image` inside that quiz question or flashcard card too.

Left panel is for learner-facing guidance and input:

- lesson objective
- instructions to the learner
- concept explanation
- models and worked examples
- images/charts/source texts
- exploratory interactions such as `interaction` graph/distribution/equation blocks
- hints, self-checks, and answer reveal accordions
- optional Vietnamese support notes for the learner

Important models, worked examples, and explanations should be directly visible as `text` or `callout` blocks. Use `accordion` for optional answer reveals, extra details, or self-checks, not as the only place where the model answer exists.

For the exact task the learner is about to attempt, reveal the model answer after the learner tries. Put the task's model answer behind a checkpoint, accordion, answer reveal, or follow-up beat/page. Before the attempt, provide criteria, language bank, checklist, worked example, or a different model that teaches the pattern without giving away the learner's answer.

Right panel is for student practice/action:

- quiz
- cloze
- sequence
- flashcard
- essay
- branching_scenario
- coding
- data-lab
- illustration
- checkpoint
- canvas, mindmap, comparison, embed, gallery, or other active/source blocks only when they create learner action rather than merely explaining

If a page is `layout: "split"`, both panels should have visible content unless the user explicitly asks otherwise.

Panel anti-patterns:

- Do not put only explanation in the right panel and only a decorative heading in the left panel.
- Do not place the only important model answer in a collapsed accordion.
- Do not make the right panel a random pile of activities. Each right-panel block should practice the current left-panel teaching point.
- Do not use split layout for a long uninterrupted reading page unless the right side has meaningful practice/action.

## Full-Panel Modes

Use `rightPanelMode: "standard"` for normal split pages with multiple ordinary right-panel blocks, especially when the right panel mixes different block families such as sequence plus quiz, quiz plus a standalone word-bank cloze, flashcards plus a quick check, or several short task types.

Use non-standard modes only for immersive right-side work. The right panel should usually contain exactly one compatible workspace block. The left panel must prepare or support that workspace.

- `essay`: use when the learner writes, rewrites, plans, or revises one substantial response. Right panel should contain one `essay` block. Left panel should contain source material, prompt, structure, vocabulary, model, checklist, rubric, or common mistakes.
- `exam`: use when the learner works through one focused question desk. This includes diagnostics, checkpoints, mastery checks, structured practice, mock tests, and formal exams. Use it when the right side is just the unified question set and does not need mixed right-panel text/reminder blocks. Right panel should contain exactly one `quiz` block. The quiz block may use `content.mode: "practice"` for per-question checks and explanations, or `content.mode: "exam"` for whole-quiz submission. Left panel should contain source material, instructions, timing, scoring criteria, hints, or final reminders.
- `code-practice`: use when the learner solves one focused coding task. Right panel should contain one non-inline `coding` block. Left panel should contain task goal, starter context, constraints, API/syntax reference, examples, tests, and hints.
- `ui-project`: use when the learner builds or edits an interface with preview. Right panel should contain one non-inline `coding` block. Left panel should contain design brief, required states, assets, acceptance criteria, and interaction notes.
- `data-lab`: use when the learner works through notebook-like data exploration. Right panel should contain one `data-lab` block. Left panel should contain dataset context, variable guide, analysis question, expected output, and interpretation checklist.
- `illustration`: use when the main learning object is animated or staged visual explanation. Prioritize full-panel illustration mode. Right panel should contain one `illustration` block. Left panel should contain purpose, observation prompts, legend/key, and after-view question. A normal inline illustration is acceptable only when it is small/simple and there is a clear reason.
- `artifact`: use when the learner works with one sandboxed custom HTML/CSS/JS learning object. Right panel should contain one `artifact` block. Left panel should contain purpose, instructions, success criteria, mobile note when relevant, and any supporting model/checklist.

Keep `standard` mode when the right side contains several normal activity blocks such as quiz plus sequence, quiz plus standalone cloze, flashcard plus quick check, short canvas task plus quiz, or other mixed task families. Do not put quiz plus flashcards plus text into `essay`, `data-lab`, or another non-quiz immersive mode. Those modes make the entire right panel behave like a workspace.

## Block Content Contracts

Minimum visible content by block type:

- `text`, `paragraph`, `h1`-`h6`, `quote`: provide visible content through Lexical `content.json`, sanitized `content.html`, or plain `content.text`. App-authored rich text usually stores Lexical JSON.
- `callout`: `content.text` must be non-empty. In this app it may be serialized Lexical JSON.
- `accordion`: `content.title` and `content.body` should be non-empty.
- `image`: `content.url` must be non-empty. Add `caption` and `altText` for teaching clarity.
- `table`: `content.headers` and `content.rows` should be non-empty arrays. Use for structured comparisons, sentence patterns, ingredient lists, and data tables instead of flattening columns into a text block or generating a table screenshot.
- `video`: `content.url` must be non-empty.
- `gallery`: `content.slides` should contain visible slides (`[{"url", "caption"?}]`). `content.layout` is `"threads"` (the default, also used when `layout` is omitted: a sideways-swipeable row of rounded cards at natural aspect ratio with peek and scroll-snap; tap opens a full-size lightbox) or `"carousel"` (opt-in: one large slide with a thumbnail strip). Use `threads` for 3+ charts or examples learners should compare; set `carousel` only to step through one image at a time in a set order. There is no `grid` layout.
- `pdf`: include a non-empty URL or file reference.
- `embed`: include a non-empty `embedUrl`.
- `recording`: include a media URL for playback, or use only when the learner is meant to record.
- `quiz`: `content.questions` must be non-empty. Each question needs a visible `question`, a supported `type`, the correct answer field for that type, and feedback/explanation when used for practice.
  - `multiple_choice`: at least 2 options and valid `correctAnswerIndex`.
  - `multiple_select`: at least 2 options and valid `correctAnswerIndices`.
  - `short_answer`: non-empty `correctShortAnswer`.
  - `cloze`: bracketed answers inside the question text, e.g. `The value [increased/rose] sharply`.
  - Media: any question may include `image` (a URL), rendered above the question. Add it when the question refers to a chart, diagram, map, or picture, so learners are not answering a visual question with no visual. Reuse an existing lesson image URL or an uploaded asset.
- `flashcard`: `content.title`, `content.instructions`, and `content.cards` must be non-empty. Each card needs meaningful `front` and `back`; avoid vague fronts such as `Question 1`. Cards may include `image` (a URL) and `imagePosition` (0-100 vertical focal point, default 50); add images for vocabulary, objects, places, and visual recall rather than leaving vocabulary cards text-only.
- `sequence`: `content.title`, `content.instructions`, and at least 2 ordered `items` are required. Each item needs text. Items must be the real sentences/steps/lines the learner reorders into a coherent whole, not abstract labels (use the actual model sentences for paragraph-order practice).
- `cloze`: `content.title`, `content.instructions`, and `content.text` are required. Text must include bracketed answers, e.g. `The trend [increased] sharply`. For writing language practice, include alternatives such as `[rose/increased/climbed]`. Always include `content.wordBank` (an array of words the learner drags onto the blanks, with a few plausible distractors); never leave a fill-the-gap with no word list.
- `essay`: `content.prompt` must be non-empty. Include `minWords` and `maxWords`.
- `branching_scenario`: `content.title`, `content.prompt`, `content.startNodeId`, and `content.nodes` are required. Each node is `{id, title, body, choices: [{id, label, feedback, nextNodeId}]}`; a node with `choices: []` is an ending. `completionMode` defaults to `"on_terminal"` (completed when the learner reaches an ending). `startNodeId` must name an existing node; each `nextNodeId` must name an existing node or be left blank, which ends the scenario. Every path must reach an ending. Write real, specific feedback for each choice, not "Correct"/"Wrong". It is answer-gated in guided flow and counts toward lesson completion.
- `chart`: `content.chartType` (`line`, `bar`, `area`, `pie`), `title`, `xKey`, `series: [{key, label, color}]`, and `data` rows (pie: `data: [{name, value}]`). Use to present data; use `interaction` mode `graph` when the learner should reveal data over time.
- `custom_activity`: `content` is the complete safe custom activity definition. It must be JSON-compatible data only, with no executable functions, imports, closures, or arbitrary runtime code. See "Custom Activity Contract" below.
- `artifact`: `content` is the complete sandboxed artifact definition. Build it with the `alcheris-artifact-builder` skill; see "Artifact Contract" below for placement rules.
- `coding` or `snippet`: include `language`, `files` or `code`, and avoid immersive coding unless the right panel mode supports it.
- `data-lab`: include non-empty `cells`.
- `interaction`: set `content.mode` to `graph`, `distribution`, `equation`, or `embed`, plus the fields that mode requires. `graph` needs `graphData` (array of `{ id, label, value, annotation? }`) with `graphTitle`/axis labels; `distribution` needs `statMean`/`statStdDev` with `statTitle`/`statInstruction`; `equation` needs `mathExpression` with range fields and optional `gameMode`/`targets`. Full schemas and examples: `references/alcheris-interactive-blocks.md` and `data/block-contracts.json`.
- `illustration`: `content.scenes` must be a non-empty array; each scene needs `durationMs`, a `layers` array (shape/text/image/svg), and `keyframes` keyed by layer id. Keep on-screen text short and verify no overlap in the player.
- `comparison`: set `content.compareType` (`image`, `code`, or `text`) and the matching before/after pair (`beforeImage`/`afterImage`, `beforeCode`/`afterCode`, or `beforeText`/`afterText`).
- `canvas`: include `paths` (and optionally `images`) plus playback flags (`autoplay`, `showReplayButton`). `mindmap`: include a `nodes` array with at least a root node. Verify visually in the player.
- For all interactive blocks, choose them over a static equivalent when the source has movement, parameters, before/after, or a process; see the interactive-first decision rule in `references/alcheris-interactive-blocks.md`.

## Custom Activity Contract

Use `custom_activity` when the learner needs a teacher-defined activity made from safe primitives that Alcheris owns and renders. Do not use it as a plugin host. The block content is saved as JSON-compatible data and interpreted by the editor/player.

Allowed field primitives:

- `instructions`
- `short_text`
- `long_text`
- `choice`
- `checklist`
- `file_upload`

Required top-level shape:

```json
{
  "type": "custom_activity",
  "title": "Argument Builder",
  "version": "1.0.0",
  "fields": [],
  "renderTargets": {
    "editorBlock": true,
    "fullPanel": true,
    "playerDesktop": true,
    "playerMobile": true
  },
  "mobilePlayer": {
    "mode": "native",
    "layout": "single_column",
    "behavior": "submit_activity"
  },
  "inspector": {
    "properties": []
  },
  "submission": {
    "enabled": true,
    "mode": "draft_and_submit",
    "storage": "alcheris_managed",
    "allowFiles": false,
    "requiresTeacherReview": false
  },
  "completion": {
    "type": "on_submit"
  },
  "analytics": {
    "events": ["block_viewed", "block_interacted", "block_completed"]
  },
  "interactions": {
    "emits": ["submitted", "completed"],
    "canUnlock": ["checkpoint_block"],
    "canBeRequiredBy": ["checkpoint_block"],
    "providesSignals": ["submission_status", "completion_status"]
  }
}
```

Mobile player support is required. `renderTargets.playerMobile` must be `true`; mobile mode may be `native`, `simplified`, `viewer`, `desktop_recommended`, or `desktop_required`, but use `native` plus `single_column` for MVP activities students should complete on phones.

Submission modes:

- `none`
- `draft_only`
- `submit_required`
- `draft_and_submit`
- `teacher_review_required`
- `score_required`

Completion types:

- `manual`
- `on_interaction`
- `on_submit`
- `score_threshold`
- `teacher_reviewed`
- `all_required_fields_valid`
- `checkpoint_passed`

Baseline analytics events are required:

- `block_viewed`
- `block_interacted`
- `block_completed`

Optional analytics events:

- `draft_saved`
- `attempt_started`
- `attempt_submitted`
- `answer_changed`
- `feedback_viewed`
- `hint_used`
- `score_changed`
- `desktop_required_seen`

Inspector properties may use `text`, `textarea`, `number`, `boolean`, or `choice`. Property ids should map to fields in the definition or to per-lesson overrides.

Example MVP custom activity:

```json
{
  "type": "custom_activity",
  "title": "Argument Builder",
  "version": "1.0.0",
  "prompt": "Choose a side, then write a short argument with supporting evidence.",
  "minWords": 40,
  "requiresReview": true,
  "fields": [
    {
      "id": "instructions",
      "type": "instructions",
      "label": "Instructions",
      "text": "Choose a side, then write a short argument with supporting evidence."
    },
    {
      "id": "position",
      "type": "choice",
      "label": "Choose a side",
      "required": true,
      "options": ["Agree", "Disagree"]
    },
    {
      "id": "argument",
      "type": "long_text",
      "label": "Write your argument",
      "required": true,
      "minWords": 40
    },
    {
      "id": "evidence",
      "type": "file_upload",
      "label": "Evidence file",
      "required": false
    }
  ],
  "renderTargets": {
    "editorBlock": true,
    "fullPanel": true,
    "playerDesktop": true,
    "playerMobile": true
  },
  "mobilePlayer": {
    "mode": "native",
    "layout": "single_column",
    "behavior": "submit_activity"
  },
  "inspector": {
    "properties": [
      { "id": "title", "type": "text", "label": "Title" },
      { "id": "prompt", "type": "textarea", "label": "Prompt" },
      { "id": "minWords", "type": "number", "label": "Minimum words" },
      { "id": "requiresReview", "type": "boolean", "label": "Teacher review required" }
    ]
  },
  "submission": {
    "enabled": true,
    "mode": "draft_and_submit",
    "storage": "alcheris_managed",
    "allowFiles": true,
    "requiresTeacherReview": true
  },
  "completion": { "type": "on_submit" },
  "analytics": {
    "events": ["block_viewed", "block_interacted", "block_completed", "draft_saved", "attempt_submitted", "answer_changed"]
  },
  "interactions": {
    "emits": ["submitted", "completed"],
    "canUnlock": ["checkpoint_block"],
    "canBeRequiredBy": ["checkpoint_block"],
    "providesSignals": ["submission_status", "completion_status"]
  }
}
```

Custom activity anti-patterns:

- Do not include `render()`, function bodies, scripts, imports, JSX, HTML event handlers, or eval-like strings.
- Do not save student answers or drafts inside the definition.
- Do not store uploaded binary data in JSON. Store file metadata/reference ids only.
- Do not omit `playerMobile`; students may complete lessons on phones.

## Artifact Contract

The full artifact definition contract (fields, `viewport` presets, sizing, bridge, validator rules, upload and verify steps) lives in the sibling skill `skills/alcheris-artifact-builder` (`references/contract.md`, `references/frame-and-sizing.md`, `references/upload-and-verify.md`). Build every artifact with that skill: start from its `assets/starter/`, run `scripts/validate_artifact.py`, and check the frames with `scripts/frame_check.html`. Do not hand-write a definition from memory: the host frame is a fixed `viewport` preset (`square` 1:1 or `portrait` 9:16, `scrolling: "none"`), the backend rejects arbitrary heights (`embedHeight`) and internal scroll regions, and files must stay under 200 KB. Long content is split into steps, tabs, or scenes instead of scrolling.

What this skill decides:

- **Whether to use one.** Use an `artifact` when the learner must see something transform or do something the native blocks cannot express: a simulation, a step-through transformation (table -> line graph), a drag/drop or build-it activity, a custom production desk. Prefer native blocks (quiz, cloze, sequence, `interaction` graph, `chart`, `illustration`, `branching_scenario`) when they fit; they are cheaper to build and maintain.
- **Where it goes.** An exploratory artifact sits on the LEFT with the teaching, or as the single right-panel block in `artifact` mode with left-side guidance. A practice/production artifact goes on the RIGHT. In `artifact` mode the right panel holds exactly one artifact and the left panel holds purpose, instructions, success criteria, and any model/checklist.
- **How it completes.** In guided flow it must call `window.AlcherisArtifact.submit(answer)` or `.complete({...})` during the learner's interaction, or the answer gate traps the learner. An artifact with `submission.enabled: true` and `completion.type: "on_submit"` is also required for lesson completion.
- **Mobile.** Mark `mobileBehavior.mode: "full"` only if it really works at phone width; otherwise `viewer`, `desktop_recommended`, or (rarely) `desktop_required`.
- **Theme.** Prefer `appearance: {mode: "inherit", tokenVersion: "1"}` so the artifact follows the learner's light, dark, or custom palette through Alcheris CSS tokens; use `fixed` only when the artifact's own visual system is part of the content.
- **Import and reuse.** Artifact packages (`.alcheris-artifact.json`, raw definition or a `format: "alcheris_artifact"` envelope) are imported into the Artifact Library or an editable artifact workspace and validated by the same server contract. Artifact JSON belongs in the Artifact Library, not Teacher Assets; Teacher Assets hold the images/video/audio/documents an artifact references.
- **Safety.** Sandbox on, network/storage/clipboard off, no credentials or hidden tracking, media from Alcheris-managed teacher assets only. Students run artifacts but never edit their source. Save reusable artifacts to the library (`save_artifact`) and insert them with `add_artifact_block`.

## Lesson Design Patterns

Use these as examples, not as the whole skill. Alcheris is subject-neutral.

### High-Detail Teaching Targets

When the source material explains a component in detail, make that component a visible teaching sequence. This applies to writing sections, code modules, formulas, design choices, analysis steps, safety procedures, and any other sub-skill.

Required shape:

1. State the component's job in learner-facing language.
2. Break the component into ingredients or decision criteria.
3. Show what belongs and what must be excluded.
4. Give a model and, when useful, a weak non-example.
5. Add a guided recognition task before asking the learner to produce it.
6. Add constrained practice with enough items to build fluency; the count depends on the skill, but one shallow exercise is not enough.
7. Add a production task with a checklist, rubric, or model reveal.

Good block choices:

- `table`: ingredients, decision criteria, sentence patterns, checklists.
- `callout`: key rule, trap, exclusion, or warning.
- `quiz`: recognize correct/incorrect choices.
- `sequence`: order the procedure after the procedure has been explained.
- `cloze`: practice constrained wording with accepted alternatives.
- `essay`, `custom_activity`, coding/data-lab, or a genuine production-style short-answer task: final production.

For rich source material, use many small pages rather than compressing the source. Prefer one micro-skill per page with left-side teaching/support and right-side practice. IELTS Writing Task 1, coding, and data lessons often need long lessons.

### Generic Self-Study Lesson

Page 1: Encounter

- Left: outcome, task/context/source material, visible lesson path.
- Right: quick diagnostic or simple recognition task if the page checks understanding; otherwise keep the page single.

Page 2: Explore

- Left: example, visual, dataset, scenario, code, text, case, or exploratory interaction that makes the learner inspect the material.
- Right: guided check such as quiz, sequence, cloze, or checkpoint.

Page 3: Explain or model

- Left: rule, model, worked example, table, callout, and optional accordion.
- Right: guided practice with feedback.

Page 4: Apply

- Left: checklist, criteria, source material, hints, or reference table.
- Right: essay, coding, data-lab, canvas, illustration, branching_scenario, quiz set, or other production block.

Page 5: Check and reflect

- Left: answer key, model, rubric, or next-step advice.
- Right: checkpoint, self-assessment, revision task, or final submission.

### Chart Or Data Interpretation Lesson

Page 1: Lesson map and input

- Left: learning outcome, visible page path, source visual/data, rule of thumb, vocabulary/formula/reference accordion when needed.
- Right: quick recognition quiz or diagnostic.

Page 2: Recognize the display and logic

- Left: h2, learner instruction text, image/table/chart, callout with recognition rules.
- Right: quiz or sequence identifying form, variables, units, time/structure, and what kind of reasoning is needed.

Page 3: Analyze or transform

- Left: h2, worked analysis, transformation rule, annotated image/table, optional answer reveal accordion.
- Left also hosts exploratory interaction or canvas replay when the learner needs to track patterns visually.
- Right: quiz, sequence, cloze, checkpoint, or short-answer task that makes the learner justify choices.

Page 4: Apply and check

- Left: h2, checklist, source visual/data, feedback/self-check prompts.
- Right: essay, short-answer, data-lab, quiz set, or other production block.
- Page mode: `rightPanelMode: "essay"`.

### Trend-Report Introduction Contract

Use this when the lesson teaches a written introduction for a trend chart, table, bar chart, pie set, or mixed data task.

The introduction has one job: paraphrase the task and add basic chart information. It should not analyze trends.

Teach these required ingredients before practice:

- Chart form: line graph, bar chart, table, pie chart, mixed chart, diagram, or other display.
- Topic and unit: what is measured and how it is measured.
- Categories: the groups, items, places, people, products, or variables being compared.
- Place or scope: country, city, organization, population, or dataset scope when given.
- Time period: years, months, days, `from...to...`, `between...and...`, or `over the period`.

Teach exclusions:

- Do not mention rises, falls, peaks, dramatic changes, highest/lowest categories, or final comparisons in the introduction.
- Do not list exact figures in the introduction unless the task itself is only asking for basic chart information.
- Do not copy the task sentence word for word.

Recommended Alcheris page shape:

- Left: chart/task image, ingredient table, paraphrase rule, model introduction.
- Right: quiz to choose introduction vs overview sentences, cloze for paraphrasing, sequence for ingredient order, then a short-answer or essay production task.

Example model:

`The line graph compares the amount of time spent on three types of telephone calls in the UK between 1995 and 2002, measured in billions of minutes.`

### Trend-Report Overview Contract

Use this when the lesson teaches an overview, overall statement, executive summary, or main-pattern summary for a trend/data report.

The overview gives the biggest ideas. It should summarize what matters before the body paragraphs give exact figures.

Teach these required overview questions before practice:

- Which categories increase?
- Which categories decrease, stay stable, fluctuate, or return to the starting level?
- Which category has the strongest growth or biggest change?
- Which category stays highest or lowest overall?
- Which categories can be grouped together because they share a trend?
- Is there a turning point, peak, trough, or reversal that changes the story?

Teach exclusions:

- Do not describe points randomly.
- Do not use the overview for exact supporting figures unless the writing genre explicitly requires them.
- Do not write one sentence per year.
- Do not repeat the introduction.

Recommended Alcheris page shape:

- Left: chart image, overview question checklist, grouping rule, model overview, optional answer reveal.
- Right: quiz to identify major patterns, sequence to order overview decisions, cloze for overview wording, then a production task.

Example model:

`Overall, local fixed-line calls remained the highest category and rose to a peak before returning to their initial level, while the other two categories increased, with mobiles growing most sharply despite staying comparatively low.`

### Writing Or Idea Development Lesson

Page 1: Understand the question

- Left: prompt, task type, stance/criteria choices, learner-facing explanation.
- Right: quiz or poll for task response.

Page 2: Build a paragraph

- Left: model paragraph and explanation of idea -> reason -> example -> result.
- Right: sequence or cloze practice.

Page 3: Write and upgrade

- Left: checklist and common Vietnamese learner traps.
- Right: essay block or short answer quiz.

## Visuals

Use visuals when the source is visual, spatial, data-heavy, product-like, or process-based.

For chart lessons:

- Add a real `image` block for the chart/table/graph.
- Add alt text.
- Put the visual where students can inspect it while practising.
- Repeat the visual on a writing page if the right panel is an essay workspace.
- Any practice that depends on a chart/image/source keeps that visual visible on the page while students practise; add per-question images too when the question itself references the visual.

For trend-graph lessons:

- Include a chart-recognition stage before writing: chart form (`line`, `bar`, `table`, `pie`) is separate from chart logic (`trend` vs `static`).
- Include a transformation stage when the source teaches it: bar charts, tables, and multi-pie sets with time should be mentally transformed into line-graph logic by tracking each category across time.
- Include an analysis stage before introduction/overview writing: identify categories, unit, time period, direction, strongest growth, highest/lowest category, turning points, useful anchor figures, and body grouping.
- If the lesson teaches introduction writing, include the Trend-Report Introduction Contract.
- If the lesson teaches overview or overall writing, include the Trend-Report Overview Contract.
- Do not jump directly from the chart image to introduction/overview practice when the source notes include recognition, transformation, or analysis steps.

## Verification Checklist

After writes:

1. Fetch `/api/lessons/{lesson_id}/` (or `get_lesson`). If you revised a copy, confirm you are reading the copy's id, not the original's.
2. Confirm page count and titles.
3. Split blocks by `panel`.
4. Validate block contracts.
5. Fetch `/api/lessons/{lesson_id}/quality/`.
6. Open `/learn/{lesson_id}` in the browser.
7. Confirm no visible messages:
   - `This page has no content yet.`
   - `No interaction added yet.`
   - `No content added yet.`
8. Confirm images render, not only the image block payload.
9. Confirm full-panel pages show the intended workspace.
10. Search learner-facing text for author notes, TODOs, placeholders, or questions to the teacher, and remove them.
11. Check the mobile path: mentally run beat generation (see `references/alcheris-learning-beats.md`). Each right-panel activity should pair with the explanation it practices; split pages should have roughly one left heading section per right activity; `viewer`/`desktop_recommended` blocks should be acceptable on a phone or replaced with a mobile-native alternative. Set `mobileBeatsOverride` only if clean auto-grouping is not achievable.

## Builder Self-Audit

Before final delivery, audit the lesson and fix issues found:

1. Source coverage: every important source idea, example, rule, sub-skill, exception, and stage appears somewhere in the lesson.
2. Practice ladder: every taught micro-skill has enough guided checks, constrained practice, varied practice, and production for learners to remember the pattern.
3. Panel placement: practice pages are split; left teaches/explores, right practises/produces; exploratory interactions are not used as the main right-panel stimulus.
4. Visual support: any image/chart/source needed for practice remains visible while students practise, and per-question/card images are added when useful.
5. Block fit: movement/parameters/process/before-after use exploratory interactions; when native blocks cannot express the experience, use an artifact.
6. Production: production asks learners to generate something, not merely choose an answer. Short-answer counts only when it genuinely asks for a sentence, analysis, decision, solution, or similar output.
7. Model timing: exact model answers appear after the learner attempts the task.
8. Persona: one declared persona is used consistently and does not reduce explanatory depth.
9. Player route: inspect the student/player route when available for empty panels, cramped workspaces, rendering failures, guided-flow/mobile order, and answer-gate dead ends.
