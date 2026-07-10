---
name: alcheris-lesson-agent
description: Build, edit, audit, and repair interactive self-study lessons in Alcheris through the Alcheris MCP or backend API for any subject area. Use when Codex is asked to create or improve Alcheris lessons, use the lesson-maker app, work with the alcheris-mcp server, convert source material into learner-facing Alcheris pages/blocks, choose block/layout/full-panel modes, add media/practice/workspaces/custom_activity/artifact blocks, add interactive/animated blocks (interaction graph/distribution/equation widgets, artifact HTML/CSS/JS sandboxes, illustration, comparison, canvas, mindmap) instead of static equivalents, design lessons for the guided-flow (mobile + desktop) path, verify lesson quality, fix empty or weak blocks, generate safe custom activity or artifact definitions, reuse teacher assets, respect sequential-order courses, or prepare an installable workflow for Alcheris lesson generation.
---

# Alcheris Lesson Agent

## Core Rule

Create Alcheris lessons as real self-study learning experiences for the target subject, not teacher lesson plans and not content dumps. Every lesson must have visible learner-facing explanation, purposeful media or examples when the content needs them, active practice, and a verified student/player route before delivery.

## Voice, Format, and the Spine

### Persona (voice) - decide before writing a word
Every lesson has a teaching **persona**, and every learner-facing line - hook, explanation, feedback, callouts, jokes - is written in it, consistently. A voiceless lesson reads like a textbook no matter how interactive it is. Read `references/alcheris-teacher-personas.md`. Teachers pick a preset or define their own; if the user names a character or vibe (e.g. "like Dante from Devil May Cry"), build a custom persona from it. Voice never changes the pedagogy - only how it sounds - and it NEVER shortens the teaching: keep full explanatory depth, at least one worked example, and the *why*, not just the *what*. Punchy personas (Dante/high-energy) are the biggest trap here - be cool AND thorough, never reduce an explanation to one-liners. Keep it classroom-appropriate; a wrong answer gets a warm or witty nudge, never a put-down.

### Interactive article vs pinned workspace - the format decision
Alcheris single-column pages are NOT static reading. They are **interactive articles**: a flowing narrative with interactions woven INLINE - a drag-to-reveal `interaction` graph mid-paragraph, an `illustration` the learner scrolls to, an inline quick-check quiz or cloze, a "try changing this" widget. This explorable-explanation format is the product's edge; make it the DEFAULT for teaching.
Use a SPLIT page (pinned workspace) only when the learner has a **sustained task that needs the guidance kept visible beside it**: writing an essay, coding, a data-lab, a formal exam. Test: "Is there a sustained workspace the guidance must sit beside?" No -> interactive article (single layout). Yes -> split. Do NOT split-ify ordinary teaching or push quick checks into a side panel - inline them in the article instead.

### The spine: Hook -> Realize -> Understand -> Apply -> Reflect
1. **Hook** (engagement) - the "why should I care?" opener: a relatable scene, stakes, a curiosity gap, or a "by the end you'll..." promise, in persona. Distinct from Realize - it earns attention before any content. Usually an article opener with one inline interactive pull.
2. **Realize** - the learner notices the phenomenon via an interactive element before any rule is stated (drag a slider, watch an animation, a "what do you notice?" prompt). Never explain a rule the learner has not yet felt a need for.
3. **Understand** - give the rule, model, and worked example; scannable (bold key terms, callouts for the core rule/trap, bullets or an accordion for multi-point), with inline widgets.
4. **Apply** - guided practice (varied types) + real production. Light checks stay INLINE in the article; a sustained production task (essay/coding/exam) becomes a split pinned workspace.
5. **Reflect** - a short article closer in persona: what you can now do, the one big idea, a next step.

### Progressive disclosure (extra reading)
Keep the main path clean and reward the curious: put depth (the why, the proof, an edge case, a bit of history, a harder challenge for fast finishers) in **"go deeper" accordions** and **side callouts**, not in the main flow. The confident reader flows through; the curious one taps to dig.

## User-Saved Rules

- If the user asks to save a rule, save the rule in project or skill instructions. Do not interpret that as permission to create, rewrite, merge, publish, or upload a lesson.
- Before editing a live lesson, identify the exact requested scope: refine existing page, add missing material, split a lesson, upload a new lesson, or only save an instruction.
- Preserve existing good work. Add missing material unless the user explicitly asks to replace or rebuild.
- Hard rule: do not skip anything from the relevant source material.
- Do not mix separate lesson scopes unless the user explicitly asks for a combined lesson.
- Trend graph and static graph are separate lesson scopes unless the user explicitly asks to combine them. If the user asks to differentiate them, add a focused contrast section without turning the lesson into a full combined trend/static module.
- Write as the teacher speaking directly to students. Do not write meta phrases such as "your notes say", "the source says", "the Google Doc says", or "this page maps the source". Do not talk to the user inside the student lesson.
- Use clear, natural classroom language. Use flowing paragraphs when narrating one continuous line of thinking, but when an explanation covers multiple distinct points, rules, items, or steps, break it into a bullet list or an accordion instead of a dense paragraph. Text blocks support bullet lists - use them. Do not present three or more parallel ideas as one long paragraph.
- Emphasize meaning: put key terms in **bold** and put the core rule, trap, or warning in a callout. Do not bold whole sentences, over-highlight, or rely on ALL CAPS - emphasis loses force when overused.
- Prefer split pages for teaching: the realize hook and explanation go on the LEFT, the practice/production goes in the RIGHT (floating) panel. Use single/blog-style pages only for pure reading with no practice, such as a lesson introduction or a standalone reference. Do not stack practice underneath explanation in one column when a split (explanation left, practice right) is possible.
- Do not put questions on the lesson introduction page unless the user explicitly asks for a diagnostic opener.
- Teach the rule before asking students to answer questions about it.
- Transformation must be taught mechanically when source material requires it: x-axis = time, y-axis = value/unit, each repeated category = one line, each bar/cell/slice value = one plotted point, connect points, then read movement.

## Workflow

1. Ground the target.
   - If editing, read the existing lesson first with `get_lesson` or `/api/lessons/{id}/`.
   - Preserve existing content unless the user asks to replace it.
   - Never publish, delete, or overwrite a full lesson without explicit user intent.
   - Check the course's Sequential Order setting (`course.linear_progression`) and the lesson's `unlock_requirements`. In a sequential-order course, EVERY lesson must be completable start-to-finish and every answer-gated block must be resolvable, because a broken quiz or artifact blocks the student from unlocking the next lesson. Flag any lesson you cannot make completable rather than silently shipping a dead-end.
   - Reuse teacher assets when applicable. The teacher's `/teacher/assets` library (`/api/assets/`) already contains uploaded images/video/PDFs/DOCX/SVG - prefer those Alcheris-managed URLs over one-off external URLs when the same media recurs in a course or is referenced from an `artifact` (whose sandbox has network off by default).

2. Plan the learning path before writing blocks.
   - Define the learner outcome.
   - Extract all teachable ideas from the source before compressing it into pages.
   - Mark any source section that explains a sub-skill in detail as a high-detail teaching target. Do not collapse it into a single sentence, quiz, or heading.
   - Structure the path on the Realize -> Understand -> Apply spine (see the top of this skill). The finer stages `orient -> recognize/notice -> explore deeper -> explain/model -> guided practice -> independent application -> check/reflect` all fold under those three: realize (orient/recognize/explore), understand (explain/model), apply (practice/application/check).
   - Each teaching page should ideally complete a mini realize -> understand -> apply cycle, or the lesson should move through them across pages. Do not open a page with a wall of text; open with the realize hook.
   - Adapt the spine to the subject: charts, coding, math, design, language, science, product training, exam prep, or professional skills may emphasize different stages.
   - Make the structure visible to the learner. Page titles should read like steps in a lesson, not miscellaneous notes.

3. Use panels deliberately (realize + understand LEFT, apply RIGHT).
   - Left panel = realize + understand: the interactive hook, explanation, models, worked examples, reference visuals/charts, the interactive `graph` (drag-to-reveal is explanation), hints, self-check notes. Interactive exploration and stimulus are explanation and belong on the left.
   - Right (floating) panel = apply: the practice or production workspace - quiz, cloze, sequence, flashcards, essay, coding, data-lab, canvas, checkpoint, artifact, or a custom_activity. The floating panel should be mainly practice.
   - Exception: `illustration` always goes in the RIGHT panel using `illustration` mode - it needs the space (see step 4), even though it is explanatory.
   - Decide the panel role before adding blocks. A teaching-and-practice page is split. A pure reading/introduction/reference page with no practice is single.
   - Do not leave either panel empty on split pages. Do not put the main practice on the left.
   - Do not write teacher-facing lesson-plan language into the student lesson unless the user explicitly asks for a teacher edition.

4. Use full-panel modes only when they improve the experience.
   - Treat the right-panel mode as a page-level learning decision, not a cosmetic setting.
   - `standard`: mixed ordinary right-panel blocks, especially when the right side combines different block families such as sequence plus quiz, quiz plus standalone cloze, or flashcard plus quick check.
   - `essay`: one focused writing block on the right, with source material/checklist/model support on the left.
   - `exam`: one focused quiz workspace. Use it for diagnostics, checkpoints, mastery checks, structured practice, mock tests, and formal exams. The quiz block itself may still be in `practice` mode for per-question feedback.
   - `code-practice`: single-file programming practice.
   - `ui-project`: full frontend project sandbox with preview.
   - `data-lab`: notebook-style data exploration.
   - `illustration`: animated or visual presentation workspace. Always place an illustration in the RIGHT panel using `illustration` mode as the single right-panel block - it demands space and breaks or looks cramped in a shared column. The left panel then holds the purpose, observation prompt, and follow-up.
   - `artifact`: one sandboxed HTML/CSS/JS learning object, like a Notion-style artifact block, with Alcheris-managed analytics/submission/completion events.
   - Avoid putting many ordinary blocks into a non-standard workspace mode.
   - For each non-standard mode, the left panel must support the workspace with source material, instructions, criteria, model, checklist, or hints. The right panel should usually contain one main workspace block.

5. Build with the right blocks.
   - Read `references/alcheris-block-inventory.md` before selecting blocks for a new lesson or major revision.
   - Every lesson needs at least one active learning block: quiz, cloze, sequence, flashcard, essay, custom_activity, artifact, coding, data-lab, interaction, checkpoint, etc.
   - Interactive-first: when the source has movement, parameters, a before/after state, or a process, reach for an interactive block instead of a static equivalent. Read `references/alcheris-interactive-blocks.md`. In particular: data over time -> `interaction` mode `graph` (slider reveal), not a static chart image; spread/parameter concept -> `interaction` mode `distribution` or `equation`; a process/transformation -> `illustration` staged scenes, not a bullet list; a before/after change -> `comparison`, not two stacked blocks; a step-by-step diagram -> `canvas` replay. Apply reveal-before-explain and manipulate-before-tell. Use one interactive block per teaching point; do not decorate.
   - Data or chart lessons need an image/chart/table stimulus, not only text. A live `interaction` graph counts as the stimulus and is preferred over a static image when the data moves over time.
   - Domain-specific source stages must be preserved. Do not skip recognition, transformation, worked analysis, setup vocabulary, rules, safety notes, or examples when the source material teaches them.
   - Learner explanations and model answers should be visible as text or callout blocks; use accordion only for optional reveal/check content.
   - Practice blocks must contain enough content to render visibly.
   - Flashcards must teach real vocabulary, concepts, or recall prompts. Do not use labels like "Overview question 1" as the card front unless the back makes the learning value obvious.
   - Add images to quiz questions and flashcards when a visual aids recognition or recall: chart/diagram/map questions, and vocabulary/object/place flashcards. Quiz question `image` and flashcard card `image` (plus `imagePosition`, 0-100) take a URL - reuse an existing lesson image URL or an uploaded asset. If a helpful image would need a picture you do not have a URL for, flag it in a brief callout rather than silently leaving the visual out. (Autonomous image search/generation is a planned feature; until it ships, only reuse or flag.)
   - Vary the practice; do not make every exercise multiple choice. Within a quiz use `short_answer`, `multiple_select`, and `cloze` (fill-the-gap) question types, and reach for standalone `sequence` (ordering), `cloze` (precise wording), `flashcard` (recall), and `comparison` (weak-vs-strong) blocks. Match the type to the skill, not to habit.
   - Vary the correct-answer position in multiple choice. NEVER leave the correct option in position A (`correctAnswerIndex: 0`) by default. Order options naturally (not answer-first) and distribute the correct answer across A/B/C/D roughly evenly across the lesson. A lesson where every correct answer is A is broken - shuffle each question's options and set `correctAnswerIndex` to wherever the correct option actually lands.
   - Do not duplicate practice across pages. Each page's exercises must be distinct in content AND type. Do not repeat the same question, reuse the same block type with the same material, or give two pages an identical practice structure (e.g. both pages = cloze + essay + quiz). Give each page a different mix.
   - Include production, not only recognition. Every skill the lesson teaches needs at least one task where the learner PRODUCES it: write a sentence, build the paragraph, use the vocabulary. Use `short_answer` for one-sentence production, `essay` for longer writing, `custom_activity` for structured multi-field tasks, and `artifact` for a custom interactive learning object that needs HTML/CSS/JS. For language/writing lessons, add exercises that test USING the target language (e.g. "write one sentence describing this trend using a strong verb"), not only choosing the right definition.
   - Do not dump vocabulary or long reference lists into one flat table - it is exhausting to scan. Present vocabulary as `flashcard` decks grouped by meaning, grouped `accordion` sections, or short compact grouped lists, and always pair a vocabulary bank with at least one usage exercise (fill-the-gap or sentence writing), not just a lookup table.
   - Sequence and cloze blocks must have a visible title and instructions.
   - Sequence items must be the REAL sentences, steps, or lines the learner reorders into a coherent whole - not abstract labels like "Starting point:" or "Trend movement:". To practise paragraph order, use the actual model sentences that form the paragraph.
   - Cloze: use bracket syntax `[rose/increased/climbed]` to accept multiple answers, AND always include a `wordBank` (an array of words the learner drags onto the blanks, with a few plausible distractors). Never ship a fill-the-gap with empty blanks and no word list to choose from.
   - If the learner must produce language, code, diagrams, analysis, calculations, or decisions, include the needed vocabulary, syntax, rules, examples, or criteria before asking for production.
   - If the source teaches how to write or build a component, include the component's purpose, ingredients, allowed content, forbidden content, model, non-example or distractor, guided practice, and independent production task.
   - When stating a rule, explain why the rule exists and give at least one concrete example. For decision rules, also include a non-example or contrast case when it helps prevent random or shallow application.
   - Use `custom_activity` only for safe JSON-compatible teacher-created activity definitions interpreted by Alcheris renderers. Do not put JavaScript functions, imports, arbitrary code, binary files, or oversized media into `content`; use file references/metadata for uploads.
   - Use `artifact` only for sandboxed HTML/CSS/JS learning objects with the Alcheris artifact contract: `runtime: "html_sandbox"`, `files`, `entry`, render targets, mobile behavior, completion, submission, analytics, and security flags. `allowNetwork` is off by default; artifacts reach Alcheris-managed asset URLs only. Do not use artifacts for auth, teacher credentials, arbitrary storage access, eval-style code, or hidden data exfiltration. Student communication must go through the Alcheris artifact bridge, and students never edit artifact source (teacher/admin authoring only).

6. Design for guided flow (mobile always, desktop opt-in).
   - Alcheris is self-study; many learners are on phones AND desktop learners can toggle a **guided flow** that reveals blocks one at a time. Both paths use the same learning-beats engine, so beat quality drives both experiences. Read `references/alcheris-learning-beats.md`.
   - Signpost with one heading per teaching point; keep each right-panel activity next to the explanation it practices; for a split page with N activities provide about N left heading sections (rough 1:1).
   - Be mobile-behavior aware: `interaction` widgets are mobile-native (`full`); `canvas`, `mindmap`, `comparison`, and `illustration` become viewers on phones. For interactivity that must work on mobile, prefer `interaction`. Mark a genuinely desktop-only block `desktop_required` on purpose rather than shipping a cramped version.
   - Only set `mobileBeatsOverride` when clean auto-grouping is not achievable; prefer fixing block order and headings first.
   - **Answer-gate contract.** In guided flow, `quiz`, `cloze`, `sequence`, `essay`, `custom_activity`, `artifact`, and `interaction` blocks HARD-BLOCK progression until the learner completes them (the block dispatches an "answered" event). Every gated block MUST be completable end-to-end: a quiz needs at least one question with a valid answer; a cloze needs bracketed answers and a `wordBank`; a sequence needs >=2 real items; an essay needs a prompt (learners submit their draft); a `custom_activity` must include a working submit step; an `artifact` must call `window.AlcherisArtifact.submit` (or `.complete`) somewhere in its code; an `interaction` must be resolvable (e.g. the graph slider can reach the end, the equation puzzle has a valid target). A gated block that cannot be completed silently traps the learner mid-lesson. Prefer non-gated equivalents (`text`, `callout`, `image`, `illustration`, `chart`) if a block is decorative and not meant to be completed.
   - **Empty text blocks are silently filtered out of the player** (`text | paragraph | h1-h6 | quote | code` with no content). An empty block leaves no visible hole to catch during editor preview, so do not ship placeholder-only text/heading blocks and assume they will be visible - they will not.
   - **Fork-friendly authoring.** Students can save any block into their personal notebook - the notebook stores a frozen snapshot of the block at fork time (source_snapshot), so a student's saved copy stays valid even after the teacher edits the lesson. Author every block to be MEANINGFUL WHEN DETACHED from the surrounding page: a callout should carry its own rule, a worked example should include the problem AND the solution, a flashcard should teach without needing the lesson context, an interaction should have a title and observation prompt inside the widget. Blocks that only make sense next to their neighbours become unusable notebook items.
   - **Checkpoint block is the designed gate.** Beyond the answer-gated types above, use `checkpoint` explicitly when you want a page to stop and force the learner to reveal/confirm before continuing (staged answer reveal, sync/compare, recovery point). The player's future guided-flow spec extends per-block trigger rules to checkpoint and desktop-heavy blocks (code/data-lab/artifact) with teacher-configurable pass-check/manual-continue/desktop-required notices - author for that intent even where it isn't fully wired yet.

7. Verify through readback and the browser.
   - Read the saved lesson after writes.
   - Treat API `pages[].blocks` as canonical on readback; split into panels by `block.panel`.
   - Check that each block has non-empty renderer-required content.
   - Open `/learn/{lesson_id}` or editor preview and verify visible content, media, and no empty-panel messages.
   - Mentally run beat generation: does each right-panel activity land with the explanation it practices? Would the mobile path read cleanly?
   - Run `scripts/validate_alcheris_lesson.py` when backend credentials are available.

## Required Checks Before Final Response

- No split page has an empty left or right panel.
- No text-like block has empty `text` or Lexical JSON.
- No image block has an empty `url`.
- No quiz has empty questions/options/answer.
- No flashcard has an empty front or back.
- No sequence has fewer than 2 items.
- No sequence, cloze, or flashcard block lacks a learner-facing task title/instructions.
- No cloze lacks bracketed answers such as `[answer]`; for language practice, prefer alternatives like `[rose/increased/climbed]`.
- No essay lacks a prompt and word target.
- No custom_activity or artifact violates the contract in `references/alcheris-lesson-contracts.md`; every custom block must support the mobile player appropriately and include baseline analytics events.
- Chart/data lessons include at least one visual stimulus. If the data moves over time, a live `interaction` graph is used rather than a static chart image, unless the user asked for a static image.
- Quiz questions that refer to a chart, diagram, map, or picture include an `image`, and vocabulary/visual flashcards include card `image`s, instead of being text-only when a visual would help.
- Interactive blocks are authored with valid `content` per `references/alcheris-interactive-blocks.md`: `interaction` has a valid `mode` and its mode data; `illustration` has scenes with layers and keyframes; `comparison` has a `compareType` and its before/after pair; `canvas`/`mindmap` have their required arrays.
- Source material with movement, parameters, before/after, or a process was not flattened into static text/image when an interactive block fits.
- The guided-flow path is sound (mobile always, desktop opt-in): each right-panel activity pairs with its explanation, headings roughly match activity count on split pages, and `viewer`/`desktop_recommended` blocks are acceptable on a phone or replaced with a mobile-native alternative.
- Every answer-gated block (`quiz`, `cloze`, `sequence`, `essay`, `custom_activity`, `artifact`, `interaction`) is completable: no empty quizzes, no cloze without bracketed answers + `wordBank`, no single-item sequence, no essay without a prompt, no `custom_activity` without a submit step, no `artifact` that never calls `AlcherisArtifact.submit`/`complete`, no `interaction` in an unresolvable state. A gated block that cannot be completed traps the learner in guided flow.
- No text/heading/quote/code block is empty. The player filters empties silently, so they will not show up as visible gaps during preview.
- If the target course has Sequential Order on (`linear_progression`) or the lesson has `unlock_requirements`, the whole lesson is verified completable end-to-end - no dead-end block leaves a student unable to unlock the next lesson.
- Media that recurs across the course reuses teacher-asset library URLs (from `/api/assets/`) rather than one-off external URLs, and any `artifact` that needs media references Alcheris-managed asset URLs (its sandbox has `allowNetwork` off by default).
- Every block is meaningful when detached: a student who forks it into their notebook can still learn from it without the surrounding page. Callouts carry the rule, worked examples include problem + solution, flashcards teach standalone, interactions have their own title/prompt inside the widget.
- The lesson does not skip major source stages such as recognition, transformation, analysis, worked examples, setup knowledge, or production criteria.
- Detailed source sections are preserved as teachable steps: purpose, ingredients, rules, model, practice, and final production.
- Production tasks include the needed language bank, API/syntax reference, formula list, rubric, checklist, or example first.
- Model answers/examples are visible to the learner and not only hidden behind a collapsed accordion.
- Full-panel pages use a compatible right-panel block.
- Standard-mode pages are not hiding a major workspace that should be `essay`, `exam`, `code-practice`, `ui-project`, `data-lab`, or `illustration`.
- The lesson opens with an engagement hook (why-care, in persona), and is written in ONE consistent persona from hook to reflection.
- Teaching flows as interactive articles (single column, interactions and quick checks woven inline); split/pinned-workspace layout is used ONLY for sustained tasks (essay, coding, data-lab, exam), not ordinary teaching.
- A short reflection closes the lesson; depth and extra reading live in "go deeper" accordions and side callouts, not dumped in the main flow.
- Every page follows the spine (hook -> realize -> understand -> apply -> reflect): no page tests a rule before it is taught, and no page opens with a wall of text instead of a hook.
- Practice and production live on the RIGHT (floating) panel; explanation and interactive hooks live on the LEFT; illustrations use `illustration` mode as the single right-panel block.
- Key terms are bolded and core rules/traps sit in callouts; explanations with three or more parallel points use bullets or an accordion, not one dense paragraph.
- Exercises are not all multiple choice: the lesson mixes question types (`short_answer`, `multiple_select`, `cloze`) and practice blocks (`sequence`, `cloze`, `flashcard`, `comparison`) matched to the skill.
- Multiple-choice correct answers are distributed across positions (NOT all at index 0 / A); options are not ordered answer-first.
- No two pages duplicate the same exercise content or an identical practice structure; each page has a distinct mix.
- Every taught skill has at least one production task (write / build / use it), not only recognition. Language/writing lessons include tasks to write separate sentences and to reorder real sentences into a paragraph, not only multiple-choice recognition.
- Every cloze includes a `wordBank` of draggable words (with a few distractors); no fill-the-gap ships with blanks and no word list. Sequence items are the real sentences/steps to reorder, not abstract labels.
- Vocabulary and long reference lists are presented as flashcards, grouped accordions, or compact grouped lists (not one long flat table) and paired with at least one usage exercise.
- The student/player route has been checked or the inability to check is reported.

## References

- Read `references/alcheris-lesson-contracts.md` before creating or substantially editing a lesson.
- Read `references/alcheris-block-inventory.md` when choosing blocks, layouts, and full-panel modes.
- Read `references/alcheris-interactive-blocks.md` when the source has movement, parameters, a before/after state, or a process, and to author interaction/illustration/comparison/canvas/mindmap content correctly.
- Read `references/alcheris-learning-beats.md` when structuring a lesson so it collapses into a clean mobile path.
- Read `references/alcheris-teacher-personas.md` before writing any learner-facing text; write the whole lesson in the declared persona.
- `data/block-contracts.json` is the machine-readable source of truth for interactive-block schemas, mobile behavior, and beats. The human references above and the native in-app agent prompt both derive from it; keep them in sync with it.
- Use `scripts/validate_alcheris_lesson.py` to audit a saved lesson from the backend.
