"""Condition B runner for open-weight models: bare review, no guidelines.

Sends the manuscript with a generic "review this" prompt to an
OpenAI-compatible endpoint (Ollama, vLLM, Blablador) and stores the raw
findings JSON. Stdlib only.

Usage:
    python3 evals/run_bare_openweight.py <model> <manuscript.tex> <out.json> \
        [base_url]            # default http://localhost:11434/v1
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

PROMPT = """You are an experienced reviewer of computational mechanics \
manuscripts. Review the manuscript below and identify ALL problems you can \
find — scientific writing quality, structure, storyline, language, grammar, \
mathematics/notation, figures, claims, consistency, anything a meticulous \
reviewer would flag. Be thorough and specific.

Respond with ONLY a JSON array (no prose, no markdown fences), one object per \
finding:
[{"location": "<section/line>", "excerpt": "<short verbatim quote>", \
"problem": "<what is wrong and why>"}]

MANUSCRIPT:

"""


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    model, manuscript, out = sys.argv[1], sys.argv[2], sys.argv[3]
    base = sys.argv[4] if len(sys.argv) > 4 else "http://localhost:11434/v1"

    import os

    text = Path(manuscript).read_text(encoding="utf-8")
    text += os.environ.get("SWA_PROMPT_SUFFIX", "")
    api_key = os.environ.get("SWA_API_KEY", "ollama")
    if "11434" in base:
        # Ollama: use the native API so we can force think=false — on CPU the
        # thinking budget of reasoning models otherwise eats the completion.
        body = {
            "model": model,
            "messages": [{"role": "user", "content": PROMPT + text}],
            "think": False,
            "stream": False,
            "options": {"temperature": 0, "num_predict": 8000},
        }
        url = base.removesuffix("/v1") + "/api/chat"
    else:
        body = {
            "model": model,
            "messages": [{"role": "user", "content": PROMPT + text}],
            "temperature": 0,
            "max_tokens": 8000,
        }
        url = f"{base}/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(req, timeout=7200) as r:
        resp = json.load(r)

    if "message" in resp:  # ollama native
        print(f"done_reason: {resp.get('done_reason')}, "
              f"eval_count: {resp.get('eval_count')}")
        content = resp["message"]["content"]
        usage = {"prompt_tokens": resp.get("prompt_eval_count"),
                 "completion_tokens": resp.get("eval_count")}
    else:
        choice = resp["choices"][0]
        print(f"finish_reason: {choice.get('finish_reason')}")
        content = choice["message"]["content"]
        usage = resp.get("usage", {})
    # strip <think> blocks (reasoning models) and markdown fences
    if "</think>" in content:
        content = content.split("</think>", 1)[1]
    content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    Path(out).write_text(content + "\n", encoding="utf-8")
    try:
        findings = json.loads(content)
        print(f"OK: {len(findings)} findings -> {out}")
    except json.JSONDecodeError as e:
        print(f"WARNING: output is not valid JSON ({e}); raw text saved to {out}")
        return 1
    print(f"tokens: prompt={usage.get('prompt_tokens')}, "
          f"completion={usage.get('completion_tokens')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
