from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Tuple

ProcessFn = Callable[[Any], None]


@dataclass
class ProcessSpec:
    name: str
    fn: ProcessFn
    requires_keys: Tuple[str, ...] = field(default_factory=tuple)
    requires_tokens: Tuple[str, ...] = field(default_factory=tuple)


class ProcessRegistry:
    def __init__(self) -> None:
        self._specs: Dict[str, ProcessSpec] = {}

    def register(
        self,
        name: str,
        fn: ProcessFn,
        *,
        requires_keys: Iterable[str] = (),
        requires_tokens: Iterable[str] = (),
    ) -> ProcessFn:
        if name in self._specs:
            raise RuntimeError(f"Duplicate process name registered: {name}")
        self._specs[name] = ProcessSpec(
            name=name,
            fn=fn,
            requires_keys=tuple(requires_keys),
            requires_tokens=tuple(requires_tokens),
        )
        return fn

    def as_dict(self) -> Dict[str, ProcessFn]:
        return {k: v.fn for k, v in self._specs.items()}

    def run(self, name: str, ctx: Any) -> None:
        if name not in self._specs:
            raise KeyError(f"Unknown process: {name}")

        spec = self._specs[name]

        # 1) payload key validation (None is missing; falsey values allowed)
        missing_keys = [k for k in spec.requires_keys if ctx.get(k, None) is None]
        if missing_keys:
            raise RuntimeError(
                f"[file_create] {name} missing required payload keys: {missing_keys} "
                f"(project={ctx.get('project')}, entity={ctx.get('entity_type')}:{ctx.get('entity_name')}, dept={ctx.get('department')})"
            )

        # 2) token name validation (if process declares token deps)
        toks = ctx.get("tokens", None) or {}
        missing_tokens = [t for t in spec.requires_tokens if toks.get(t, None) in (None, "")]
        if missing_tokens:
            raise RuntimeError(
                f"[file_create] {name} missing required token names: {missing_tokens} "
                f"(project={ctx.get('project')}, entity={ctx.get('entity_type')}:{ctx.get('entity_name')}, dept={ctx.get('department')})"
            )

        spec.fn(ctx)

    def clear(self) -> None:
        self._specs.clear()


REGISTRY = ProcessRegistry()


def process(
    name: str,
    *,
    requires_keys: Iterable[str] = (),
    requires_tokens: Iterable[str] = (),
):
    def _decorator(fn: ProcessFn) -> ProcessFn:
        return REGISTRY.register(
            name,
            fn,
            requires_keys=requires_keys,
            requires_tokens=requires_tokens,
        )
    return _decorator