import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "typologies.json"


def load_typologies():
    """Load allowed typologies and subtypologies from the config file."""

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)
