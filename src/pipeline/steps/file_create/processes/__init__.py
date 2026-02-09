from __future__ import annotations

# Import modules to register processes via decorators.
# NOTE: must be imported only after maya.standalone.initialize() in mayapy flows.

from .registry import REGISTRY
REGISTRY.clear()

# order doesn't matter; imported for side-effects (registration)
from .folders import makeFolders  # noqa: F401
from .files import (  # noqa: F401
    saveEmptyFile,
    saveFile,
    cloneUpstreamShotPublishFile,
    cloneLayoutPublishToAnm,
    importMasterTemplate,
)
from .groups import makeEmptyGroup  # noqa: F401
from .refs import (  # noqa: F401
    assetReference,
    shotReference,
    referenceCameraRig,
    referenceDependencyInputs,
)
from .caches import connectCachesFromDependencyInputs  # noqa: F401
from .sceneinfo import (  # noqa: F401
    setTechSpecDefaults as _setTechSpecDefaults_sceneinfo,
    setTimeline as _setTimeline_sceneinfo,
    importAudio as _importAudio_sceneinfo,
    createSceneInfo as _createSceneInfo_sceneinfo,
)

# Export registry in legacy shape
PROCESS_REGISTRY = REGISTRY.as_dict()