# Uploading and verifying through the Alcheris connector

Tool names are those of the Alcheris MCP server (`alcheris-mcp`, also served as the claude.ai Alcheris connector). Run `whoami` first to confirm the account and server.

## Rules

- **Send artifacts raw.** Without `raw: true`, `add_block` and `update_block` run content through `build_block_content`, and `update_block` *merges* the result into the stored content. The artifact builder fills defaults (for example `mobileBehavior` without `minWidth`) and keeps only the fields it knows. Raw sends your built `definition.json` exactly as it is.
- **Always send the whole definition.** A raw update replaces the content; a partial object is rejected by the validator. That's safe, since nothing is saved, but it wastes a call.
- **Write to a copy** of a teacher's lesson unless told to edit the original. Duplicate it first (`POST /api/lessons/{id}/duplicate/` from the app, or ask the teacher), and remember that block IDs change in the copy.
- **Never hand-type a minified or base64 blob.** Read the built file and pass its JSON. The content is plain text (HTML, CSS, JS), so copying it is safe; a single wrong character in base64 is not.

## Replace an existing artifact

```
update_block(lesson_id, page_index, block_id, raw=true, content=<definition.json>)
```

`page_index` must be the page that block is on, or the call errors.

## Add a new artifact

```
add_block(lesson_id, page_index, panel="left"|"right", block_type="artifact", position=<n>, raw=true, content=<definition.json>)
```

Or, as part of a page restructure, use `save_lesson_structure`. Every existing block is listed by ID, and the new one is `{"type": "artifact", "content": {...}, "raw": true}` at its position. Exploratory or teaching artifacts usually go on the left; practice or production artifacts go on the right (the floating panel). A saved library artifact can be inserted with `add_artifact_block(artifact_id)`, and `save_artifact(name, definition)` saves one to the teacher's library for reuse.

## Verify

1. `get_lesson(lesson_id)`. The result is often large and gets saved to a file.
2. Find the block by ID and compare `content` with your `definition.json`, using sorted-key JSON so that key order doesn't matter:
   ```python
   json.dumps(stored, sort_keys=True) == json.dumps(built, sort_keys=True)
   ```
3. Report the result: identical, or what differs.

## Failure modes seen

- **The tool is missing from the list.** claude.ai caches a connector's tool list; the user has to disconnect and reconnect the connector in Settings → Connectors, then start a new chat. A local stdio MCP needs the app restarted.
- **`block_contract_invalid`.** Read `block_contract_errors[].errors[].path`, fix the definition, and run `validate_artifact.py` before trying again.
- **`edit_conflict` (409)** from `save_lesson_structure`. Someone edited the lesson in the browser meanwhile. Re-read the lesson and rebuild the call.
