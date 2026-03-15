from dataclasses import dataclass
from pathlib import Path


@dataclass
class SharedArgs:
    config_file: Path | None
    session: str | None
