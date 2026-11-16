# Explainer Media: Diagrams, Clips, and When to Use an Artifact

Use this reference when an explanation should be shown rather than written: a structure, a decision, a sequence, a before/after. It covers choosing the medium, making original media, uploading it, and placing it in a block.

## 1. Choose the medium

Start from the cheapest thing that shows the idea, and from the most active thing that teaches it.

| The idea... | Use |
|---|---|
| Has a shape but does not move (parts, layout, categories, a rule with examples) | Still diagram in an `image` block |
| Changes over time and the learner should predict, choose, or try first | `artifact` (step-through or game) |
| Branches ("if X, do this; if not, ask...") | `artifact`: the learner answers each question and sees where it leads |
| Needs the learner to set the pace (step back, replay one step) | `artifact` |
| Must stay sharp, follow dark mode or the teacher's palette, or be edited later | `artifact` or still diagram (a video bakes text in) |
| Is carried by a voice: pronunciation, tone, a teacher talking through a worked example | `video` |
| Is a short watch-once demo with nothing to decide | `video` (or a still diagram if the motion adds little) |
| Data that moves over time | Native `interaction` graph first (see `alcheris-interactive-blocks.md`) |

Default: **artifact over video**. A video is passive, cannot check understanding, and must be re-rendered to fix one word. Choose it only when the voice is the content.

Examples from a shipped IELTS lesson pair:

- "Linear or cyclical?" (one idea, a short watch) worked as a voiced clip.
- "Read the time first" (three tense cases, no decision) worked as a voiced clip.
- "Read the layout" is a two-question decision tree. It should be an artifact where the learner answers the questions.
- "One stage, one full sentence" is better as an artifact where the learner taps material, tool, and manual or machine before the sentence assembles.

## 2. Rules for any explainer visual

- **Original only.** Invent the data, places, products, and wording. Never trace or copy an exam chart, map, diagram, or model essay.
- **One idea per visual.** If it needs a legend paragraph, split it.
- **Readable on a phone.** Design at 16:9 or 4:3, text at least about 28 px on a 1280 px wide canvas, high contrast, no text in the outer 5%.
- **Words on screen.** Key terms appear as labels or captions, so the visual teaches with the sound off.
- **Alt text that teaches.** The `altText` describes what the visual shows and concludes, not "diagram".
- **Pair it with practice.** A visual is followed by a block where the learner uses it.

## 3. Making original media

### Still diagrams

Draw in SVG (or HTML/CSS) and export a PNG at 2x, or upload the SVG. Use a calm palette with one accent colour, and keep labels short.

### Narrated clips

A pipeline that works without paid services:

1. **Script the voice first.** Three to five short lines, about 15 to 30 seconds in total. Spoken language, one idea per line.
2. **Generate the voice offline** with a local TTS model (for example Kokoro ONNX). Write one WAV per line and record each line's start time and duration in a `lines.json` (a short lead-in, then a fixed gap of about 0.5 s between lines).
3. **Animate from the timings.** Build the clip in Remotion (or another code-to-video tool) at 1280×720, 30 fps. Time every scene from `lines.json`, so a re-voiced line moves its animation automatically, and never hard-code frame numbers.
4. **Render silent, then mix.** Delay each WAV to its start time, mix them, pad to the clip length, and normalise loudness to about -16 LUFS (ffmpeg `adelay`, `amix`, `loudnorm`).
5. **Mux for the web.** H.264 video, **stereo** AAC audio at about 160 kbps, `+faststart`. Mono audio plays from one speaker on some setups and reads as "no sound".
   For iPhone Safari, encode H.264 **Constrained Baseline** (level 3.1), `yuv420p`, limited range, 48 kHz audio: `ffmpeg -i in.mp4 -c:v libx264 -profile:v baseline -level 3.1 -pix_fmt yuv420p -color_range tv -c:a aac -ac 2 -ar 48000 -b:a 160k -movflags +faststart out.mp4`. A High-profile full-range file played on desktop but not on an iPhone.
6. **Check before uploading.** Watch it at phone size, confirm no label overlaps or overflows, and measure the loudness again.

Keep the voice, timing, and render scripts in the project so a clip can be fixed and re-rendered later.

## 4. Upload

Use the connector's `upload_asset`, which returns a public URL from the teacher's asset library:

- Local (stdio) MCP: `upload_asset(file_path="clip.mp4")`. Kind is guessed from the file type.
- Hosted connector: `upload_asset(content_base64=..., filename="diagram.png")`, up to about 2.5 MB.
- Anything larger through the hosted connector: ask the user to upload it at `/teacher/assets`, then find it with `list_assets(kind="video", query="clip")`.

Upload once and reuse the URL. Artifacts run with network off, so any media an artifact shows must be an Alcheris asset URL or drawn in the artifact itself.

## 5. Place it in a block

Image block:

```json
{"url": "<asset url>", "altText": "What the diagram shows and concludes", "caption": "",
 "width": "100%", "align": "center", "sourceType": "url", "isGif": false, "hotspots": []}
```

Video block:

```json
{"url": "<asset url>", "sourceType": "local", "role": "walkthrough",
 "autoplay": false, "muted": false, "loop": false, "controls": true,
 "credit": "", "caption": "One line saying what to watch for"}
```

- Never autoplay with sound, and never ship a narrated clip with `muted: true`.
- To turn an existing image into a video, use `update_block(..., new_type="video", content={...})`. The block keeps its id and place.
- Explainer visuals usually sit on the left panel of a split page, next to the practice on the right.

## 6. Verify in the player

- Open the lesson as a learner (or `?preview=1`). In guided flow, reveal blocks one at a time with `>` to reach the media.
- Image: it loads and is readable at phone width.
- Video: it plays, is not muted, the sound plays (in the browser, `webkitAudioDecodedByteCount` rises while it plays), and the frame fits the phone width with no sideways scroll.
- If the user hears nothing, check the file has an audio stream and that it is stereo before re-rendering anything.
