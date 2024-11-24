from functools import cached_property
from typing import ClassVar

import diffsync
import kubernetes
from kubernetes.client.api.custom_objects_api import CustomObjectsApi

from folder2k8s.kubernetes.helmchart import HelmChart

GROUP = "helm.cattle.io"
VERSION = "v1"
PLURAL = "helmcharts"


class KubernetesAdapter(diffsync.Adapter):
    HelmChart = HelmChart

    top_level: ClassVar = [
        "HelmChart",
    ]

    type = "kubernetes"

    @cached_property
    def client(
        self,
    ) -> CustomObjectsApi:
        api_client = kubernetes.config.load_config()
        return kubernetes.client.CustomObjectsApi(api_client)

    def __init__(
        self,
        source: str,
        *args: list,
        **kwargs: dict,
    ) -> None:
        self.source = source
        super().__init__(
            *args,
            **kwargs,
        )

    def load(
        self,
    ) -> None:
        for chart in self.client.list_cluster_custom_object(
            GROUP,
            VERSION,
            PLURAL,
            label_selector=f"folder2k8s.illallangi.enterprises/source={self.source}",
        )["items"]:
            self.add(
                HelmChart(
                    uid=chart["metadata"]["uid"],
                    namespace=chart["metadata"]["namespace"],
                    name=chart["metadata"]["name"],
                    spec=chart["spec"],
                    client=self.client,
                    source=self.source,
                ),
            )
