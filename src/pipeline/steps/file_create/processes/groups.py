from __future__ import annotations

from typing import Any, Dict, List, Optional

from .registry import process
from ..utils.tokens import ctx_tokens, resolve_template, TokenError


def create_group(name: str, parent: Optional[str] = None) -> str:
    import maya.cmds as cmds  # type: ignore
    if not cmds.objExists(str(name)):
        if parent:
            return cmds.group(empty=True, name=str(name), parent=parent)
        return cmds.group(empty=True, name=str(name))
    return str(name)


@process(
    "makeEmptyGroup",
    requires_keys=("group_templates", "entity_type"),
    requires_tokens=(),  # template-driven; strict resolution enforces needed ones
)
def makeEmptyGroup(ctx: Any) -> None:
    """
    FINAL CONTRACT:
      - ctx["group_templates"] : dict (groups/templates JSON)
      - ctx["entity_type"]
      - Prefer ctx["tokens"] for token resolution (backend source of truth)
    """
    import maya.cmds as cmds  # type: ignore
    import pprint
    pprint.pprint(ctx)
    templates: Dict[str, Any] = ctx.get("group_templates") or {}
    if not templates:
        cmds.warning("[makeEmptyGroup] ERROR: payload missing 'group_templates'")
        return

    entity_type = str(ctx.get("entity_type") or "").strip()
    entity_template = (templates.get("templates") or {}).get(entity_type)
    if not entity_template:
        cmds.warning("[makeEmptyGroup] ERROR: no template for entity_type='%s'" % entity_type)
        return

    toks, warns = ctx_tokens(ctx)
    print(toks , '>>>>>')
    if warns:
        # warn once (avoid spam)
        try:
            cmds.warning(warns[0])
        except Exception:
            pass

    root_tpl = str(entity_template.get("root") or "")
    try:
        print(root_tpl, toks)
        root_name = resolve_template(root_tpl, toks, strict=True)
    except TokenError as e:
        cmds.warning("[makeEmptyGroup] Token error in root template '%s': %s %s" % (root_tpl, e.token, e.reason))
        raise

    root_grp = create_group(root_name)

    group_key = ctx.get("group_template_key") or entity_template.get("groups")
    group_chains: List[List[str]] = (templates.get("groups") or {}).get(group_key, []) or []

    parent = root_grp
    for chain in group_chains:
        for grp in chain:
            try:
                grp_name = resolve_template(str(grp), toks, strict=True)
                print(grp, grp_name ,'>>>!24')
            except TokenError as e:
                cmds.warning(
                    "[makeEmptyGroup] Token error in group template '%s': %s %s" % (str(group_key), e.token, e.reason)
                )
                raise
            create_group(grp_name, parent)

    print("[makeEmptyGroup] Root: %s" % root_grp)