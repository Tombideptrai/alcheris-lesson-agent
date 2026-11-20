#!/usr/bin/env python3
"""Turn a finished Python program with step markers into a stepped code-practice exercise.

Write the solution once, marking where each step starts:

    import hashlib                      <- above the first step = the learner's starter

    # step: Count the bytes             <- step title
    # say: Make `data = b"hello\\n"` and print `len(data)`.   <- the instruction
    # hint: `len()` counts bytes.       <- optional hint
    data = b"hello\\n"
    print(len(data))

    # step: Build the header
    ...

For each step this runs the program from the top through that step (`python -I`,
fresh temp dir, 10 s timeout), records the output the step ADDS, and uses it as
the step's check. Expected outputs therefore come from real runs, never by hand.
It fails if a step errors or prints nothing new (a step that prints nothing
cannot be checked).

Output JSON (stdout):
    {"starterFiles": {"/main.py": {"type": "text/x-python", "content": ...}},
     "steps": [{"id", "title", "instructions", "hint",
                "check": {"expected", "matchMode": "contains"},
                "solutionFiles": {"/main.py": {"content": <program through this step>}}}]}

Put `steps` on the coding block's content and `starterFiles` in `curriculum[0].files`.
The Alcheris editor has the same tool ("Build steps" in the coding block's Steps
section), which also handles JavaScript and SQL.

Usage:
    python stepify.py solution.py > steps.json
    python stepify.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile

MARKER = re.compile(r"^\s*#\s*(step|say|hint)\s*:\s*(.*)$", re.IGNORECASE)

SELF_TEST = '''import hashlib

# step: Count the bytes
# say: Make `data = b"hello\\n"` and print `len(data)`.
# hint: `len()` counts bytes.
data = b"hello\\n"
print(len(data))

# step: Build the header
# say: Make `header` from the type and the length, then print it.
header = f"blob {len(data)}".encode()
print(header)

# step: Fingerprint it
# say: Glue header, a zero byte and data, then print the SHA-1.
full = header + b"\\x00" + data
print(hashlib.sha1(full).hexdigest())
'''


class StepError(ValueError):
    pass


def _trim(lines: list[str]) -> list[str]:
    out = list(lines)
    while out and not out[-1].strip():
        out.pop()
    return out


def parse(code: str) -> tuple[str, list[dict]]:
    starter: list[str] = []
    steps: list[dict] = []
    for line in code.replace("\r\n", "\n").split("\n"):
        match = MARKER.match(line)
        if match:
            kind, value = match.group(1).lower(), match.group(2).strip()
            if kind == "step":
                steps.append({"title": value, "instructions": "", "hint": "", "lines": []})
            elif steps:
                key = "instructions" if kind == "say" else "hint"
                steps[-1][key] = f"{steps[-1][key]} {value}".strip()
            continue
        (steps[-1]["lines"] if steps else starter).append(line)

    starter_code = "\n".join(_trim(starter))
    running = starter_code
    for step in steps:
        body = "\n".join(_trim(step.pop("lines")))
        running = "\n\n".join(part for part in (running, body) if part.strip())
        step["code"] = running + "\n"
    return (starter_code + "\n") if starter_code else "", steps


def run(code: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, "-I", "-c", code],
            cwd=tmp, capture_output=True, text=True, timeout=10, encoding="utf-8",
        )
    if result.returncode != 0 or result.stderr.strip():
        raise StepError(result.stderr.strip()[-400:] or f"exit code {result.returncode}")
    return result.stdout.replace("\r\n", "\n")


def new_output(previous: str, current: str) -> str:
    prev, curr = previous.rstrip(), current.rstrip()
    if prev and curr.startswith(prev):
        return curr[len(prev):].lstrip("\n")
    return curr


def stepify(code: str, file: str = "/main.py") -> dict:
    starter, steps = parse(code)
    if not steps:
        raise StepError('Add at least one "# step: Title" line.')
    previous = ""
    built = []
    for index, step in enumerate(steps, 1):
        try:
            stdout = run(step["code"])
        except StepError as err:
            raise StepError(f"Step {index} ({step['title']}) failed: {err}") from None
        expected = new_output(previous, stdout)
        if not expected.strip():
            raise StepError(f"Step {index} ({step['title']}) prints nothing new, so it can't be checked.")
        if previous and expected.strip() in previous:
            raise StepError(
                f"Step {index} ({step['title']}) prints {expected.strip()[:60]!r}, which an earlier step already "
                "printed, so it would pass before the learner writes it. Print something only this step produces."
            )
        previous = stdout
        built.append({
            "id": f"step-{index}",
            "title": step["title"],
            "instructions": step["instructions"],
            "hint": step["hint"],
            "check": {"expected": expected, "matchMode": "contains"},
            "solutionFiles": {file: {"content": step["code"]}},
        })
    return {
        "starterFiles": {file: {"type": "text/x-python", "content": starter}},
        "steps": built,
    }


def self_test() -> int:
    result = stepify(SELF_TEST)
    expected = ["6", "b'blob 6'", "ce013625030ba8dba906f756967f9e9ca394464a"]
    got = [s["check"]["expected"] for s in result["steps"]]
    assert got == expected, got
    assert result["starterFiles"]["/main.py"]["content"] == "import hashlib\n"
    assert result["steps"][0]["hint"] == "`len()` counts bytes."
    try:
        stepify("x = 1\n# step: silent\ny = 2\n")
    except StepError:
        pass
    else:
        raise AssertionError("a silent step must fail")
    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("solution", nargs="?", help="Python file with # step: markers")
    parser.add_argument("--file", default="/main.py", help="workspace file name (default /main.py)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.solution:
        parser.error("give a solution file or --self-test")
    with open(args.solution, encoding="utf-8") as fh:
        code = fh.read()
    try:
        result = stepify(code, args.file)
    except StepError as err:
        print(f"stepify: {err}", file=sys.stderr)
        return 1
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
