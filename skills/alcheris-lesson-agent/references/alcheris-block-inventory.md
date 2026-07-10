# Alcheris Block Inventory

This inventory comes from the current frontend block renderer, command menu, and right-panel mode code. Treat it as the block-selection map for agents creating Alcheris lessons through MCP/API.

## Lesson Architecture Framework

Use a domain-neutral learning spine before choosing blocks:

1. Orient: show the goal, task, artifact, problem, case, dataset, or scenario.
2. Recognize or notice: help learners identify what matters.
3. Explore deeper: let learners inspect patterns, parts, constraints, or examples.
4. Explain or model: give learner-facing rules, reasoning, examples, and worked steps.
5. Guided practice: ask small questions with feedback.
6. Independent application: ask learners to write, build, solve, analyze, draw, code, or decide.
7. Check and reflect: reveal answers, compare with a model, or submit work.

Do not use every stage mechanically. Preserve the stages that the source material actually teaches.

## Layout And Panel Decision Guide

Choose layout before choosing blocks:

- Single or blog-style page: use when the page has no practice task. Good uses include an introduction, reflection, pure reference, or one continuous explorable explanation where the learner is not being checked or asked to produce.
- Split page with `standard` right panel: use when the left side teaches/explores and the right side contains practice from several ordinary block families, such as quiz + cloze, sequence + quiz, or flashcards + quick check.
- Split page with a full-panel mode: use when the right side is one unified practice/workspace desk and the left side supports that work.

Do not classify every interactive object as practice. Use two categories:

- Exploratory interactions help learners encounter, inspect, manipulate, or understand an idea: `interaction` graph/distribution/equation, hotspot image, illustration, comparison, canvas replay, mindmap, source chart/table/image. These usually belong on the left with teaching.
- Practice interactions make learners answer, arrange, fill, write, code, submit, or produce: quiz, cloze, sequence, flashcard, essay, coding, data-lab, custom_activity, artifact, checkpoint. These belong on the right/floating panel on split pages.
- `artifact` is flexible: it can be exploratory, practice, or production depending on the custom interface. Use it when the native block inventory cannot express the learning experience well enough.

Do not put the main exploratory stimulus above the right-panel practice. Keep the source, guidance, and exploratory visuals where students can look them up while practising. If a quiz or flashcard item needs a visual, add that image inside the question/card in addition to the page source.

Left panel jobs:

- Teach: explanation, rules, worked examples, models, vocabulary, formulas, criteria.
- Supply source material: chart, text, case, dataset, prompt, diagram, screenshot, code context.
- Host exploratory interactions: slider graph, distribution/equation explorer, hotspot image, staged visual, before/after comparison, replayable diagram.
- Support action: checklist, hint, rubric, self-check, answer reveal, common mistake.

Right panel jobs:

- Make the learner do something: choose, arrange, fill, write, code, draw, inspect, compare, submit, or reflect.
- Check theoretical understanding with focused practice: quiz, cloze, sequence, flashcards, or checkpoint.
- Keep the task focused. If the right panel has one large task, use the matching full-panel mode.
- Keep mixed micro-practice in `standard` mode. Use `exam` mode for one focused quiz block, even when that quiz is configured as practice.

## High-Detail Source Sections

When the source material gives detailed guidance for one component, treat that component as a mini-lesson. Do not summarize it as a shallow rule.

For each high-detail component, include:

1. Purpose: what this component does.
2. Ingredients: what information belongs inside it.
3. Exclusions: what does not belong there.
4. Model: a complete example.
5. Decision logic: how the learner chooses the content.
6. Reason: why this rule or decision protects the learner from a common mistake.
7. Examples: at least one good example, plus a non-example or contrast case when the rule could be misapplied.
8. Guided practice: quiz, sequence, cloze, table completion, canvas, or short answer.
9. Production: the learner makes the component independently.
10. Feedback: answer reveal, rubric, checklist, or model comparison.

Use `table` for ingredient lists, `callout` for rules and traps, exploratory interactions for ideas that move/change/can be inspected, `sequence` for ordered procedures, `quiz` for choices, `cloze` for precise wording, and `essay` or short-answer quiz for production.

## Block Families

### Structure And Explanation

- `text`, `paragraph`, `h1`-`h6`, `quote`: explanations, page headings, instructions, definitions, source excerpts. Use bullets when a text block has many ideas.
- `callout`: key rule, warning, tip, misconception, or important takeaway.
- `accordion`: hidden answer key, optional explanation, self-check, spoiler, model answer reveal. Do not hide the only essential explanation here.
- `table`: structured comparisons, rubrics, ingredients, taxonomies, timelines, language banks, formulas, data tables. Prefer this over screenshotting a table.

### Media And Source Material

- `image`: charts, diagrams, screenshots, worked visuals, annotated source material. Include `altText` and a useful caption.
- `video`: hosted or uploaded video.
- `recording`: audio/video recording task or media capture.
- `gallery`: multiple images, visual examples, before/after variants, artwork or product comparisons.
- `pdf`: document handout, source article, technical spec, paper, worksheet, or long reading.
- `embed`: external interactive/site/resource in an iframe-like block.

### Practice And Assessment

- `quiz`: recognition, diagnosis, decision-making, conceptual checks, interpretation, multiple choice/select, short answer. Each question supports an `image` (URL) shown above it - use it for chart/diagram/map/picture questions instead of asking a visual question with no visual.
- `cloze`: constrained recall or language/formula/code completion. Use bracketed answers and alternatives when appropriate.
- `sequence`: ordering steps, workflows, process logic, chronology, body structure, algorithm order. Teach the order first.
- `flashcard`: memory checks only: vocabulary, definitions, commands, formulas, key distinctions, symbols. Do not use for complex explanation. Each card supports an `image` (URL) and `imagePosition` (0-100) - add images for vocabulary, objects, and places rather than text-only cards.
- `essay`: long-form writing or open response.
- `custom_activity`: structured teacher-defined activity built from safe JSON primitives such as instructions, short/long text, choice, checklist, file upload reference, and submit. Use when one activity needs multiple fields, review rules, mobile behavior, completion rules, analytics events, or checkpoint signals. Do not include executable code.
- `artifact`: sandboxed HTML/CSS/JS learning object, like a Notion-style artifact inside the lesson editor/player. Use when the learning object needs a custom interface, simulation, manipulative, drag/drop activity, structured production desk, or visual tool that native blocks cannot express well enough. It can serve exploratory, practice, or production purposes, but still must obey Alcheris render targets, mobile behavior, completion, submission, analytics, and security rules. `allowNetwork` is off by default; artifacts reach Alcheris-managed asset URLs (teacher assets) only. Students cannot edit artifact source code - authoring is teacher/admin only. Do not use it for auth, arbitrary storage access, hidden tracking, unsandboxed scripts, or bypassing native block contracts.
- `checkpoint`: reveal solution, sync/compare state, staged answer reveal, recovery point. In guided flow, use `checkpoint` explicitly when a page should PAUSE and force the learner to reveal/confirm before continuing - it is the designed "gate" block for staged reveal. (The runtime is still adding per-block trigger rules for code/data-lab/artifact; author with the gate intent even where the enforcement isn't fully wired yet.)

### Interactive And Visual Thinking

These are the "alive" blocks. Prefer them over a static equivalent when the source has
movement, parameters, a before/after state, or a process. Full content schemas, minimal
examples, and the interactive-first decision rule are in
`references/alcheris-interactive-blocks.md`. Author their `content` from that file, not
from memory. Mobile note: `interaction` is mobile-native; the others become viewers on
phones (see `references/alcheris-learning-beats.md`).

- `interaction`: exploratory widgets with four modes. `graph` = animated line graph with
  a slider that progressively reveals data points (prefer over a static chart image when
  data changes over time). `distribution` = live bell curve with mean/std sliders.
  `equation` = function grapher with variable sliders and an optional match-the-curve
  puzzle (`gameMode`). `embed` = external web resource. Highest-leverage block for turning
  a static data lesson into an explorable one. This is usually teaching/exploration, not a
  right-panel exercise.
- `canvas`: replayable drawing. Plays back `paths` like a hand drawing live, or a student
  sketch surface. Use when the build order teaches something.
- `mindmap`: node/relationship map for concept maps, brainstorms, relationship structures.
- `comparison`: before/after via `compareType` = image (draggable slider), text (word
  diff), or code (line diff). Use when the change itself is the lesson.
- `illustration`: keyframed multi-scene animation that auto-plays and auto-advances. Use
  when a process or transformation is best shown in motion; keep text minimal and verify
  no overlap. Prioritize full-panel `illustration` mode. Use a normal inline illustration
  only when it is small/simple and there is a clear reason.

### Data Visualization

- `chart`: responsive data chart - `line`, `bar`, `area`, or `pie`, with multiple series and optionally multiple charts per block. Use to PRESENT data figures cleanly. Content: `{ chartType, title, xKey, series:[{key,label,color}], data:[rows] }` (pie uses `data:[{name,value}]`). Prefer `interaction` mode `graph` instead when you want the learner to drag-to-reveal and explore; use `chart` when you just need to show the data richly (especially multi-series). Mobile: full.

### Coding And Data

- `code`: static formatted code display.
- `snippet`: inline runnable snippet.
- `coding`: runnable code block. With immersive content it becomes a workspace.
- `data-lab`: notebook-style data exploration.

## Right-Panel Modes

Use `rightPanelMode` intentionally:

- `standard`: use for mixed ordinary practice. Right panel can contain sequence + quiz, quiz + standalone cloze, flashcards, quick checks, short canvas tasks, or several small activities from different block families. Do not use it for a single focused quiz/writing/code/data workspace if a full-panel mode exists.
- `essay`: use when the learner writes or revises one substantial response. Right panel should be one `essay` block. Left panel should contain the prompt, source material, structure checklist, model criteria, vocabulary, or rubric.
- `exam`: use for one focused question desk. This includes diagnostics, checkpoints, mastery checks, structured practice, mock tests, and formal exams. Use it when the right side is a unified set of questions and does not need mixed right-panel text/reminder blocks. Right panel should be one `quiz` block. The quiz can be `content.mode: "practice"` for per-question checks and explanations or `content.mode: "exam"` for whole-quiz submission. Left panel should contain the rules, source material, timing, scoring criteria, hints, or pre-test reminder.
- `code-practice`: use when the learner edits or writes one focused code solution. Right panel should be one immersive `coding` block. Left panel should contain the goal, constraints, API/syntax notes, examples, test cases, and hints.
- `ui-project`: use when the learner builds a small interface or frontend project with preview. Right panel should be one immersive `coding` block. Left panel should contain design brief, acceptance criteria, assets, states, and interaction requirements.
- `data-lab`: use when the learner explores data through notebook-like steps. Right panel should be one `data-lab` block. Left panel should contain the question, dataset description, variable guide, analysis checklist, and expected outputs.
- `illustration`: use when motion, staged reveal, or visual transformation is the main teaching object. Prioritize this full-panel mode. Right panel should be one `illustration` block. Left panel should contain the purpose, observation prompts, legend/key, and follow-up question. Keep text inside the illustration minimal.
- `artifact`: use when the right side is one custom HTML/CSS/JS learning object. Right panel should be one `artifact` block. Left panel should contain the learning purpose, instructions, success criteria, mobile note if needed, and any model/checklist the artifact depends on.

If a page has many ordinary right-panel activities, keep `standard`. If the right side is the main workspace, use the matching full-panel mode.

Use this quick test:

- Many small tasks on the right: `standard`.
- One final written answer: `essay`.
- One focused quiz workspace, whether practice or formal test: `exam`.
- One coding workspace: `code-practice` or `ui-project`.
- One notebook/data exploration workspace: `data-lab`.
- One animated or staged visual workspace: `illustration`.
- One custom sandboxed HTML/CSS/JS learning object: `artifact`.
- Reading or reference only: single/blog-style page, not split.

## Selection Heuristics

- Need learners to identify a type, classify a case, choose a response, or diagnose a misconception: use `quiz`.
- Need learners to remember names, terms, symbols, commands, formulas, definitions, or small distinctions: use `flashcard`.
- Need learners to arrange a process, paragraph order, algorithm, timeline, workflow, or decision sequence: explain first, then use `sequence`.
- Need learners to complete constrained wording, formulas, commands, labels, code fragments, or terminology: use `cloze`.
- Need learners to inspect a visual, product, chart, diagram, screenshot, or before/after state: use `image`, `gallery`, `comparison`, `canvas`, or `illustration`.
- Need learners to annotate, connect, sketch, or map visual reasoning: use `canvas` or `mindmap`.
- Need learners to explore a live concept or parameter before/during explanation: use `interaction` on the teaching side.
- Need learners to practise with a live workspace: use `data-lab`, `coding`, `artifact`, or `custom_activity` on the practice side.
- Need a reusable custom interface, simulation, drag/drop micro-tool, exploratory manipulative, custom practice flow, production desk, or generated HTML/JS object that native blocks cannot express well enough: use `artifact`.
- Need learners to produce final written work: use `essay`.
- Need learners to complete a structured multi-field submission, such as choose a stance + write an argument + attach evidence + submit for review: use `custom_activity`.
- Need learners to produce final code or UI work: use `coding` in the matching full-panel mode.
- Need learners to reveal answers after effort: use `accordion` or `checkpoint`.
- Need learners to compare a learner answer with a model: use `accordion`, `checkpoint`, `table`, or left-panel model plus right-panel production.

## Exercise Variety And Underused Blocks

Do not default to multiple-choice quizzes. A good lesson feels varied. Reach for the blocks agents most often forget:

- `comparison` (text mode): weak vs strong sentence, draft vs revision, before vs after. Ideal for writing lessons.
- `sequence`: order the steps of a process, the parts of a report, a paragraph's sentences, a workflow - after the order has been taught.
- `cloze`: fill-the-gap for precise wording, collocations, formulas, or code fragments; use `[rose/increased/climbed]` for accepted alternatives.
- `flashcard`: vocabulary, definitions, symbols, commands - grouped decks, not one flat table.
- `mindmap`: brainstorm ideas or map relationships before writing.
- `canvas`: annotate a chart, sketch a diagram, connect points.
- `gallery`: multiple worked examples or before/after variants.
- `checkpoint`: staged answer reveal after the learner attempts.
- Quiz question types beyond `multiple_choice`: `short_answer` (one-line production), `multiple_select` (choose all that apply), `cloze` (inline fill-gap).

For every skill the lesson teaches, include a practice ladder: guided check -> constrained practice -> varied practice -> production. The exact count depends on content, but it should be dense enough for learners to remember the pattern; one quiz is not enough. Every skill also needs at least one PRODUCTION task (write / build / use it), not only recognition. A `short_answer` question can count as production only when it asks the learner to generate a real sentence, analysis, decision, or answer; otherwise treat it as a knowledge check.

Vocabulary presentation: never a single long flat table - it is exhausting to scan. Group by meaning into `flashcard` decks or `accordion` sections, and pair with a usage exercise (fill-gap or sentence writing).

## Anti-Patterns

- Do not use flashcards as a substitute for teaching or analysis.
- Do not ask an exercise before explaining the rule, workflow, or anchor knowledge it needs.
- Do not turn a detailed source section into a single vague sentence such as "write the introduction" or "find the overview."
- Do not put answer labels directly into a chart or visual that appears before the quiz.
- Do not flatten tables into paragraphs or screenshots when `table` can represent them.
- Do not put several normal practice blocks inside a full-panel workspace mode.
- Do not leave blocks with default labels, empty content, placeholder options, or generic titles.
- Do not use full-panel illustration for text-heavy teaching. It is for staged visuals.
- Do not use `custom_activity` for arbitrary plugin code, custom render functions, scripts, or storing student work inside the block definition.
- Do not use `artifact` to bypass Alcheris rules. It must be sandboxed, mobile-aware, teacher/admin-authored, teacher-reusable, network-off by default, and communicate only through the Alcheris artifact bridge.
