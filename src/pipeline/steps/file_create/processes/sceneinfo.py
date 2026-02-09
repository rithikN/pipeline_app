from __future__ import annotations

from pathlib import Path
from typing import Any

from .registry import process


def _maya_path(p: str) -> str:
    return (p or "").replace("\\", "/")


@process("setTechSpecDefaults")
def setTechSpecDefaults(ctx: Any) -> None:
    """
    Legacy behavior (final keys):
      - res_w, res_h, fps
    """
    import maya.cmds as cmds  # type: ignore

    w = int(ctx.get("res_w", 1920) or 1920)
    h = int(ctx.get("res_h", 1080) or 1080)
    fps = float(ctx.get("fps", 23.976) or 23.976)

    try:
        cmds.setAttr("defaultResolution.width", w)
        cmds.setAttr("defaultResolution.height", h)
    except Exception:
        pass

    # time unit (legacy best-effort)
    try:
        cmds.currentUnit(time=f"{fps}fps", updateAnimation=False)
    except Exception:
        try:
            cmds.currentUnit(time="film", updateAnimation=False)
        except Exception:
            pass

    try:
        cmds.playbackOptions(playbackSpeed=1)
        cmds.playbackOptions(maxPlaybackSpeed=1)
    except Exception:
        pass


@process("setTimeline")
def setTimeline(ctx: Any) -> None:
    """
    Legacy behavior (final keys):
      - start, end, handle
      - sets min/max and ast/aet with handles
    """
    import maya.cmds as cmds  # type: ignore

    start = int(ctx.get("start", 1001) or 1001)
    end = int(ctx.get("end", 1100) or 1100)
    handle = int(ctx.get("handle", 8) or 8)

    cmds.playbackOptions(min=start)
    cmds.playbackOptions(ast=start - handle)
    cmds.playbackOptions(max=end)
    cmds.playbackOptions(aet=end + handle)


@process("importAudio")
def importAudio(ctx: Any) -> None:
    """
    Legacy behavior (final keys):
      - no_audio
      - audio_root, episode, sequence, entity_name
      - attaches to playback slider via scriptNode
    """
    import maya.cmds as cmds  # type: ignore

    if bool(ctx.get("no_audio", False)):
        return

    audio_root = ctx.get("audio_root")
    ep = ctx.get("episode")
    sq = ctx.get("sequence")
    sh = ctx.get("entity_name")

    if not (audio_root and ep and sq and sh):
        return

    wav = Path(str(audio_root)) / f"{ep}_{sq}_{sh}.wav"
    if not wav.exists():
        cmds.warning(f"[AUDIO] Not found: {wav}")
        return

    snd = cmds.sound(file=_maya_path(str(wav)))
    snd = cmds.rename(snd, f"{ep}_{sq}_{sh}_AUD")
    try:
        cmds.setAttr(snd + ".offset", int(ctx.get("start", 1001) or 1001))
    except Exception:
        pass

    code = f'''
import maya.mel as mel
import maya.cmds as cmds
snd="{snd}"
if cmds.objExists(snd):
    try:
        mel.eval('global string $gPlayBackSlider; timeControl -e -sound "%s" $gPlayBackSlider;' % snd)
    except Exception:
        pass
'''
    name = "HLD_AudioAttach_OnOpen"
    if cmds.objExists(name):
        try:
            cmds.delete(name)
        except Exception:
            pass
    try:
        cmds.scriptNode(name=name, scriptType=2, sourceType="python", beforeScript=code)
    except Exception:
        pass


@process("createSceneInfo")
def createSceneInfo(ctx: Any) -> None:
    """
    Legacy behavior:
      - creates Maya 'shot' node named sceneInfo
      - sets start/end + shotName
      - adds Asset_Info / Check_Info
      - connects render camera (if referenceCameraRig stored it)
    """
    import maya.cmds as cmds  # type: ignore
    import json

    cam = getattr(ctx, "render_camera_transform", None)
    start = int((getattr(ctx, "get", None) and ctx.get("start")) or getattr(ctx, "start", 101) or 101)
    end   = int((getattr(ctx, "get", None) and ctx.get("end"))   or getattr(ctx, "end", 110)   or 110)
    shot_name = (getattr(ctx, "get", None) and (ctx.get("shot") or ctx.get("entity_name"))) or (getattr(ctx, "shot", None) or getattr(ctx, "entity_name", "")) or ""

    node = "sceneInfo"
    if cmds.objExists(node):
        try: cmds.delete(node)
        except Exception: pass

    node = cmds.createNode("shot", name=node)

    try:
        cmds.setAttr(node + ".startFrame", start, lock=True)
        cmds.setAttr(node + ".endFrame", end, lock=True)
        cmds.setAttr(node + ".shotName", str(shot_name), type="string")
    except Exception:
        pass

    # ensure attrs exist
    try:
        if not cmds.attributeQuery("Asset_Info", node=node, exists=True):
            cmds.addAttr(node, ln="Asset_Info", dt="string")
        if not cmds.attributeQuery("Check_Info", node=node, exists=True):
            cmds.addAttr(node, ln="Check_Info", dt="string")
    except Exception:
        pass

    #  write expected namespaces (what validator reads)
    try:
        raw = (getattr(ctx, "dependency_inputs", None) or (ctx.get("dependency_inputs") if hasattr(ctx, "get") else None) or [])  # type: ignore
        asset_info = []
        for it in raw:
            if not isinstance(it, dict):
                continue
            meta = it.get("meta") or {}
            ns = (meta.get("namespace") or it.get("namespace") or "").strip()
            if not ns:
                continue
            asset_info.append({
                "namespace": ns,
                "path": it.get("path", ""),
                "occurrence_index": meta.get("occurrence_index"),
                "occurrence_total": meta.get("occurrence_total"),
                "asset_type": meta.get("asset_type"),
                "requested_by": meta.get("requested_by"),
            })

        cmds.setAttr(node + ".Asset_Info", json.dumps(asset_info), type="string")
    except Exception as e:
        cmds.warning(f"[createSceneInfo] Failed to write Asset_Info: {e}")

    if cam and cmds.objExists(cam):
        try:
            cmds.connectAttr(cam + ".message", node + ".currentCamera", force=True)
        except Exception:
            pass