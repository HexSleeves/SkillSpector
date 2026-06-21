# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for the meta_analyzer node — LLM-call telemetry and fail-closed
construction (drives the report's degradation signal)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from skillspector.models import Finding
from skillspector.nodes.meta_analyzer import meta_analyzer
from skillspector.state import SkillspectorState


def _finding(rule_id: str = "P1", severity: str = "HIGH") -> Finding:
    return Finding(
        rule_id=rule_id,
        message="test",
        severity=severity,
        confidence=0.8,
        file="SKILL.md",
        start_line=1,
    )


def _state(**overrides: object) -> SkillspectorState:
    state: SkillspectorState = {
        "findings": [_finding()],
        "use_llm": True,
        "file_cache": {"SKILL.md": "# Skill"},
        "manifest": {},
        "model_config": {},
    }
    state.update(overrides)  # type: ignore[typeddict-item]
    return state


def test_records_ok_true_on_success() -> None:
    with (
        patch("skillspector.llm_analyzer_base.get_chat_model", return_value=MagicMock()),
        patch(
            "skillspector.nodes.meta_analyzer.LLMMetaAnalyzer.arun_batches",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        result = meta_analyzer(_state())
    assert result["llm_call_log"] == [{"node": "meta_analyzer", "ok": True, "error": None}]


def test_construction_failure_is_caught_not_raised() -> None:
    """Regression: the chat model is constructed INSIDE the try, so a construction
    failure degrades (records ok=False, preserves findings) instead of crashing
    the whole graph."""
    with patch(
        "skillspector.llm_analyzer_base.get_chat_model",
        side_effect=RuntimeError("provider construction failed"),
    ):
        result = meta_analyzer(_state())  # must not raise
    # Findings are preserved via the fallback path...
    assert len(result["filtered_findings"]) == 1
    # ...and the failure is recorded so the report can flag degradation.
    log = result["llm_call_log"]
    assert log[0]["node"] == "meta_analyzer"
    assert log[0]["ok"] is False
    assert "provider construction failed" in log[0]["error"]


def test_use_llm_false_records_nothing() -> None:
    result = meta_analyzer(_state(use_llm=False))
    assert "llm_call_log" not in result


def test_no_findings_records_nothing() -> None:
    result = meta_analyzer(_state(findings=[]))
    assert "llm_call_log" not in result
