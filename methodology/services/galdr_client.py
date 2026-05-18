"""Anthropic Claude client for Galdr PIP assessments."""

from __future__ import annotations

import json
import logging
import re
from typing import Tuple

from django.conf import settings

from methodology.services.galdr_prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GaldrLLMError(Exception):
    """API failure or malformed model output."""


class GaldrClient:
    """
    Thin wrapper around Anthropic Claude for per-change verdicts.

    Example:
        rec, why = GaldrClient().evaluate_change("...")
    """

    def evaluate_change(self, user_prompt: str) -> Tuple[str, str]:
        """
        Ask the model for a JSON verdict.

        :param user_prompt: User message describing playbook + one change.
        :return: ``(recommendation, reasoning)`` where recommendation is ACCEPT|REJECT|NEEDS_CLARIFICATION.
        :raises GaldrLLMError: on transport or parsing errors.
        """
        raw = self._call_llm_raw(user_prompt)
        return self._parse_response(raw)

    def _call_llm_raw(self, user_prompt: str) -> str:
        model = getattr(settings, "GALDR_MODEL", "claude-sonnet-4-20250514")
        try:
            import anthropic
        except ImportError as exc:
            raise GaldrLLMError("anthropic package is not installed") from exc

        logger.info(
            "GaldrClient anthropic model=%s user_chars=%s", model, len(user_prompt)
        )
        client = anthropic.Anthropic()
        message = client.messages.create(
            model=model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        pieces: list[str] = []
        for block in getattr(message, "content", []) or []:
            txt = getattr(block, "text", None)
            if txt:
                pieces.append(txt)
        text = "".join(pieces).strip()
        if not text:
            first = getattr(message, "content", [None])[0]
            text = getattr(first, "text", "") or str(message.content)
        logger.info(
            "GaldrClient anthropic response_chars=%s stop=%s",
            len(text),
            getattr(message.stop_reason, "value", message.stop_reason),
        )
        return text

    @staticmethod
    def _strip_code_fences(raw: str) -> str:
        s = raw.strip()
        fence = re.match(r"^```(?:json)?\s*(.*?)```", s, re.DOTALL | re.IGNORECASE)
        return fence.group(1).strip() if fence else s

    def _parse_response(self, raw: str) -> Tuple[str, str]:
        blob = self._strip_code_fences(raw)
        try:
            payload = json.loads(blob)
        except json.JSONDecodeError as exc:
            logger.warning("Galdr parse JSON failure raw=%s", blob[:400])
            raise GaldrLLMError("Invalid JSON from model") from exc
        rec = str(payload.get("recommendation", "")).strip().upper()
        why = str(payload.get("reasoning", "")).strip()
        ok = {"ACCEPT", "REJECT", "NEEDS_CLARIFICATION"}
        if rec not in ok or not why:
            raise GaldrLLMError("Missing recommendation or reasoning in JSON payload")
        return rec, why


class StubGaldrClient(GaldrClient):
    """Deterministic client for CI / tests."""

    STUB_SENTENCE = "Galdr stub — automated ACCEPT for integration tests."

    def _call_llm_raw(self, user_prompt: str) -> str:  # noqa: ARG002
        logger.info("StubGaldrClient returning canned ACCEPT")
        return json.dumps(
            {"recommendation": "ACCEPT", "reasoning": self.STUB_SENTENCE},
        )


def get_galdr_client() -> GaldrClient:
    """
    Prefer Anthropic when enabled; otherwise deterministic stub.

    :return: Concrete client instance.
    """
    if getattr(settings, "GALDR_USE_ANTHROPIC", False):
        logger.info("Galdr using Anthropic client")
        return GaldrClient()
    logger.info("Galdr using stub client (no live LLM)")
    return StubGaldrClient()
