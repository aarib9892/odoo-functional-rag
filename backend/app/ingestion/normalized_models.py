"""Initial normalized-record contract, independent of Sphinx node classes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from typing import Literal


type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]


@dataclass(frozen=True)
class SourceIdentity:
    repository_url: str
    odoo_version: str
    language: str
    commit: str
    source_path: str
    sha256: str
    application: str


@dataclass(frozen=True)
class SourceLocation:
    source_path: str
    line: int | None
    line_origin: Literal["node", "ancestor", "unknown"]


@dataclass(frozen=True)
class Diagnostic:
    severity: Literal["warning", "error"]
    code: str
    message: str
    source: SourceLocation


@dataclass(frozen=True)
class Inline:
    kind: str
    text: str
    source: SourceLocation
    attributes: dict[str, JsonValue] = field(default_factory=dict)
    children: tuple[Inline, ...] = ()


@dataclass(frozen=True)
class Block:
    block_id: str
    kind: str
    source: SourceLocation
    heading_path: tuple[str, ...]
    text: str = ""
    attributes: dict[str, JsonValue] = field(default_factory=dict)
    inlines: tuple[Inline, ...] = ()
    children: tuple[Block, ...] = ()


@dataclass(frozen=True)
class Section:
    section_id: str
    title: str
    source: SourceLocation
    heading_path: tuple[str, ...]
    anchors: tuple[str, ...]
    labels: tuple[str, ...]
    items: tuple[Section | Block, ...]


@dataclass(frozen=True)
class NormalizedDocument:
    schema_version: str
    normalizer_version: str
    parser_id: str
    document_id: str
    revision_id: str
    source: SourceIdentity
    title: str
    status: Literal["ok", "partial"]
    metadata: tuple[dict[str, JsonValue], ...]
    items: tuple[Section | Block, ...]
    diagnostics: tuple[Diagnostic, ...]
    parser_diagnostics: str
    parser_messages: tuple[Diagnostic, ...] = ()

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
