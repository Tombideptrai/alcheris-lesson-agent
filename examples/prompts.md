# Example Prompts

## Create From Notes

```text
Use $alcheris-lesson-agent and the Alcheris MCP to create a self-study lesson from these notes.

Requirements:
- Preserve every important concept from the source.
- Use a clear learner-facing structure.
- Use split layout on pages with practice: left = encounter/explore/understand, right = quiz/cloze/sequence/essay/code/data-lab/production.
- Put exploratory interactions such as graphs, sliders, hotspot images, staged visuals, and comparisons with the explanation/source material, not in the practice panel unless they are explicitly the task.
- Keep any chart/image/source needed for practice visible on the page while students practise; add per-question/card images when a practice item refers to that visual.
- Use many small pages for rich source material, one micro-skill per page where possible.
- Build dense practice: guided checks, constrained practice, varied practice, then production. Do not stop at one quiz.
- Reveal the exact model answer after the learner attempts, not before.
- Choose blocks from the Alcheris block inventory.
- Use full-panel modes when the right side is the main workspace.
- Validate the saved lesson and check the learner route before you finish.
```

## Improve An Existing Lesson

```text
Use $alcheris-lesson-agent to audit lesson <lesson-id>.

Find:
- empty blocks,
- weak block choices,
- missing explanation before exercises,
- overuse of flashcards,
- skipped source stages,
- right-panel mode mistakes,
- missing media or source material.
- exploratory interactions placed in the practice panel,
- practice that is too shallow or only multiple choice,
- missing production tasks.

Then repair the lesson and validate it.
```

## Build A Data Lesson

```text
Use $alcheris-lesson-agent to create an Alcheris lesson about this dataset.

The lesson should:
- orient the learner to the data,
- help them notice variables and patterns,
- explain the analysis method,
- include a data-lab or interaction block,
- include guided checks,
- end with an independent interpretation task.
```

## Build A Coding Lesson

```text
Use $alcheris-lesson-agent to create a coding lesson from this topic.

Use:
- explanation and worked examples on the left,
- code-practice or ui-project full-panel mode when learners need to write code,
- checkpoints or quizzes for self-checks,
- a final task that requires real production.
```

## Build A Visual/Design Lesson

```text
Use $alcheris-lesson-agent to create a visual self-study lesson from these design notes.

Use images, comparison, canvas, gallery, or illustration blocks where useful.
Do not put dense explanation text inside an illustration workspace.
Validate that all visuals render and that no answer is spoiled before the learner attempts the task.
```

## Make A Lesson Interactive (not boring)

```text
Use $alcheris-lesson-agent to make lesson <lesson-id> more interactive.

Where the content has movement, parameters, a before/after state, or a process, replace
static blocks with interactive ones:
- data over time -> interaction graph with slider reveal, not a static chart image,
- a parameter or spread concept -> interaction distribution or equation,
- a process or transformation -> illustration staged scenes,
- a before/after change -> comparison,
- a step-by-step diagram -> canvas replay.

Apply reveal-before-explain and manipulate-before-tell. Keep one interactive block per
teaching point. Validate the saved lesson before you finish.
```

## Check The Mobile Path

```text
Use $alcheris-lesson-agent to review lesson <lesson-id> for the mobile learning-beat path.

Confirm each right-panel activity pairs with the explanation it practices, split pages
have roughly one left heading per right activity, and viewer/desktop_recommended blocks
are acceptable on a phone or replaced with a mobile-native alternative. Fix block order
and headings first; set mobileBeatsOverride only if clean auto-grouping is not possible.
```

## Final QA Prompt

```text
Use $alcheris-lesson-agent to perform final QA on lesson <lesson-id>.

Run the validator, inspect the learner route, and report:
- page structure,
- block types,
- panel modes,
- empty or weak blocks,
- source stages that were skipped,
- source coverage,
- practice ladder depth,
- production vs knowledge-check mistakes,
- model-answer timing,
- persona consistency,
- changes still recommended before publishing.
```
