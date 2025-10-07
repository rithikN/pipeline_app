from pathlib import Path
from pipeline.config.settings import SYSTEM


def get_local_asset_base(project_name: str = "Heirloom") -> Path:
    if SYSTEM == "Windows":
        return Path(f"D:/{project_name}/{project_name}_Project/Assets")
    elif SYSTEM == "Darwin":
        return Path.home() / "Documents" / project_name / f"{project_name}_Project" / "Assets"
    raise OSError(f"Unsupported OS: {SYSTEM}")
