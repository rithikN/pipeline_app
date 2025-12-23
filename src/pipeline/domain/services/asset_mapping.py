ASSET_MAPPING = {
    "Location": {
        "group": "Locations",
        "dir": "03_Master Backgrounds"
    },
    "Character": {
        "group": "Characters",
        "dir": lambda asset: f"04_Characters/{asset['asset_type_name']}"
    },
    "Prop": {
        "group": "Props",
        "dir": lambda asset: f"05_Props/{asset['asset_type_name']}"
    }
}


def resolve_asset_info(asset: dict) -> tuple[str, str]:
    """
    Resolve asset grouping and directory based on asset type.

    Args:
        asset (dict): Asset dictionary containing at least 'asset_type_name'.

    Returns:
        tuple[str, str]: (asset_group, asset_directory)
    """
    for key, config in ASSET_MAPPING.items():
        if key in asset["asset_type_name"]:
            asset_group = config["group"]
            asset_type_dir = config["dir"](asset) if callable(config["dir"]) else config["dir"]
            return asset_group, asset_type_dir

    # Fallback
    return "Misc", f"99_Misc/{asset['asset_type_name']}"
