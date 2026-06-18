# NVIDIA Convention Compliance Audit

Audits all 8 Python source files against SkillSpector upstream conventions.

| | |
|---|---|
| Date | 2026-06-19 |
| Scope | `contrib/multilingual/*.py` (8 files) |
| Reference | `src/skillspector/cli.py`, `llm_analyzer_base.py`, `providers/chat_models.py` |

---

## Summary

| Category | Issues |
|----------|--------|
| SPDX headers | 8 missing |
| `from __future__ import annotations` | 1 missing |
| Dead code / unused | 3 items |
| Docstring stale | 1 item |
| Minor style | 3 items |
| **Total** | **16** |

---

## Block / Must Fix

### B1 — Missing SPDX headers (all 8 files)

Upstream pattern:
```python
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 ...
```

**Affected:** `__init__.py`, `annotation.py`, `api_pool.py`, `batch_scan.py`, `detection.py`, `discovery.py`, `gap_fill.py`, `reports.py`, `runner.py`

**Recommendation:** Add SPDX header to all 8 `.py` files. If contributing to NVIDIA upstream, use NVIDIA copyright. If keeping as independent contrib, use `Copyright (c) 2026 The SkillSpector Contributors`.

---

### B2 — `__init__.py` missing `from __future__ import annotations`

All other 7 files have it. `__init__.py` must match.

---

### B3 — `batch_scan.py` docstring outdated

Line 13-14: "A 300-second timeout and event-loop-crash retry" — code now uses **90s timeout, no retry**.

---

### B4 — `batch_scan.py` dead code block (lines 136-139)

```python
if lang != "en" and not use_llm and require_llm:
    # Warning is printed by the caller after collecting the result
    pass
```

The `if` body is `pass`. The warning is printed 230 lines later. Remove this block.

---

### B5 — `batch_scan.py` unused import `TYPE_CHECKING`

Line 50: `from typing import TYPE_CHECKING` — never used anywhere in the file.

---

## Should Fix

### S1 — `batch_scan.py` shebang line

Line 1: `#!/usr/bin/env python3` — this module is invoked via `python -m`, not executed directly. Upstream `cli.py` has **no shebang**.

---

### S2 — `batch_scan.py` import order: dotenv before stdlib

Lines 38-43: `import dotenv` with `# noqa: I001` sits before stdlib imports. The comment explains why, but upstream never does this. Consider moving the dotenv import to `__init__.py` only and removing the duplicate from `batch_scan.py`. (Already loaded in `__init__.py` line 23-28.)

---

### S3 — `reports.py` unused import `defaultdict`

Line 11: `from collections import defaultdict` — actually used on line 166 (`_print_source_breakdown`). OK, this one is used.

Let me recheck: `defaultdict` — used in `_print_source_breakdown` and `_print_language_breakdown`. OK, this is fine.

Actually, let me double-check all reports.py imports...

OK reports.py looks clean.

---

### S4 — `api_pool.py` `record_retry_success` misleading name

The method counts retry **attempts**, not retry **successes**. Rename to `record_retry_attempt` or move the increment to after a successful retry. (Flagged in HEALTH_REPORT.md M2 but kept for telemetry purposes.)

---

## Informational / Accepted

### I1 — Patch functions lack type annotations

`_patched_base_init(self, base_prompt, model)` — `model` has no type. Same for `_patched_base_parse(self, response, batch)`. These are intentionally loose to match the original method signatures they replace. Upstream uses `object` for similar passthrough types.

### I2 — `gap_fill.py` line 281 `except ValueError: raise`

Bare re-raise of ValueError before generic exception handler. Acceptable pattern — gap-fill is optional enhancement, failure should not block the scan.

### I3 — `CONSOLE_WIDTH = 80` hardcoded in reports.py

Rich terminal width hardcoded. Upstream uses `Console()` without width constraint. Minor cosmetic difference.

---

## File-by-File Checklist

| Convention | `__init__` | `annotation` | `api_pool` | `batch_scan` | `detection` | `discovery` | `gap_fill` | `reports` | `runner` |
|---|---|---|---|---|---|---|---|---|---|
| SPDX header | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `from __future__` | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Import order | ✓ | ✓ | ✓ | △ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Type annotations | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Naming conventions | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Docstrings | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Logging | △ | ✓ | ✓ | △ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dead code | — | — | — | ✗ | — | — | — | — | — |

(✓ = matches, ✗ = issue, △ = borderline, — = not applicable)

---

## Recommended Fix Priority

| Order | Item | Files | Effort |
|-------|------|-------|--------|
| 1 | Add SPDX headers | 8 files | 3 lines each |
| 2 | Add `from __future__` to `__init__.py` | 1 file | 1 line |
| 3 | Fix outdated docstring (300s→90s) | batch_scan.py | 1 line |
| 4 | Remove dead `if/pass` block | batch_scan.py | -3 lines |
| 5 | Remove unused `TYPE_CHECKING` import | batch_scan.py | -1 line |
| 6 | Remove shebang line | batch_scan.py | -1 line |
| 7 | Move dotenv to `__init__.py` only | batch_scan.py + __init__.py | ~5 lines |
| 8 | Rename `record_retry_success` | api_pool.py | 1 line |
