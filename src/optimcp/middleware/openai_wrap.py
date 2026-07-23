"""OpenAI-compatible client wrapper that verifies structured JSON emissions."""

from __future__ import annotations

import json
from typing import Any, Callable, Optional

from optimcp.middleware.policy import (
    VerificationRefused,
    result_as_tool_error,
    verify_then_policy,
)


def extract_json_object(text: str) -> Optional[dict]:
    if not text:
        return None
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        obj = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


class VerifyingOpenAI:
    """Thin wrapper: after each completion, optionally verify extracted JSON."""

    def __init__(
        self,
        client: Any,
        *,
        ruleset_id: str,
        raise_on_refuse: bool = True,
        extractor: Optional[Callable[[str], Optional[dict]]] = None,
        prefer_remote: bool = True,
    ) -> None:
        self._client = client
        self.ruleset_id = ruleset_id
        self.raise_on_refuse = raise_on_refuse
        self.extractor = extractor or extract_json_object
        self.prefer_remote = prefer_remote
        self.chat = _ChatNamespace(self)

    def verify_document(self, document: dict, *, correlation_id: Optional[str] = None):
        return verify_then_policy(
            self.ruleset_id,
            document,
            correlation_id=correlation_id,
            prefer_remote=self.prefer_remote,
            source="agent",
            raise_on_refuse=self.raise_on_refuse,
        )


class _ChatNamespace:
    def __init__(self, parent: VerifyingOpenAI) -> None:
        self._parent = parent
        self.completions = _Completions(parent)


class _Completions:
    def __init__(self, parent: VerifyingOpenAI) -> None:
        self._parent = parent

    def create(self, *args: Any, **kwargs: Any) -> Any:
        resp = self._parent._client.chat.completions.create(*args, **kwargs)
        try:
            content = resp.choices[0].message.content
        except Exception:
            return resp
        doc = self._parent.extractor(content or "")
        if doc is None:
            return resp
        try:
            self._parent.verify_document(doc)
        except VerificationRefused as exc:
            exc.result_payload = result_as_tool_error(exc.result)
            raise
        return resp
