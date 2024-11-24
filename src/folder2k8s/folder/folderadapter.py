from pathlib import Path
from typing import ClassVar

import diffsync
from yaml import safe_load

from folder2k8s.folder.helmchart import HelmChart


class FolderAdapter(diffsync.Adapter):
    HelmChart = HelmChart

    top_level: ClassVar = [
        "HelmChart",
    ]

    type = "folder"

    def __init__(
        self,
        path: Path,
        *args: list,
        **kwargs: dict,
    ) -> None:
        if type(path) is not Path:
            path = Path(path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        if not path.is_dir():
            msg = "Path must be a directory"
            raise ValueError(msg)
        self.path = path
        super().__init__(*args, **kwargs)

    def load(
        self,
    ) -> None:
        for file in self.path.rglob("*.yaml"):
            with file.open("r") as f:
                data = safe_load(f)
                if (
                    data["kind"] == "HelmChart"
                    and data["apiVersion"] == "helm.cattle.io/v1"
                ):
                    self.add(
                        HelmChart(
                            namespace=data["metadata"]["namespace"],
                            name=data["metadata"]["name"],
                            spec=data["spec"],
                        ),
                    )
