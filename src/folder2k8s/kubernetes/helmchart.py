import diffsync
import kubernetes


class HelmChart(
    diffsync.DiffSyncModel,
):
    _modelname = "HelmChart"
    _identifiers = (
        "namespace",
        "name",
    )
    _attributes = ("spec",)

    client: kubernetes.client
    source: str

    namespace: str
    name: str

    spec: dict

    @classmethod
    def create(
        cls,
        adapter: diffsync.Adapter,
        ids: dict,
        attrs: dict,
    ) -> "HelmChart":
        adapter.client.create_namespaced_custom_object(
            group="helm.cattle.io",
            version="v1",
            namespace=ids["namespace"],
            plural="helmcharts",
            body={
                "apiVersion": "helm.cattle.io/v1",
                "kind": "HelmChart",
                "metadata": {
                    "name": ids["name"],
                    "namespace": ids["namespace"],
                    "labels": {
                        "app.kubernetes.io/managed-by": "folder2k8s",
                        "folder2k8s.illallangi.enterprises/source": adapter.source,
                    },
                },
                "spec": attrs["spec"],
            },
        )

        return super().create(
            adapter,
            {
                **ids,
                "client": adapter.client,
                "source": adapter.source,
            },
            attrs,
        )

    def update(
        self,
        attrs: dict,
    ) -> "HelmChart":
        # Update the Helm Chart object in Kubernetes

        current = self.client.get_namespaced_custom_object(
            group="helm.cattle.io",
            version="v1",
            namespace=self.namespace,
            plural="helmcharts",
            name=self.name,
        )

        self.client.patch_namespaced_custom_object(
            group="helm.cattle.io",
            version="v1",
            namespace=self.namespace,
            plural="helmcharts",
            name=self.name,
            body={
                **current,
                "metadata": {
                    **current["metadata"],
                    "labels": {
                        **current["metadata"]["labels"],
                        "app.kubernetes.io/managed-by": "folder2k8s",
                        "folder2k8s.illallangi.enterprises/source": self.source,
                    },
                },
                "spec": attrs["spec"],
            },
            field_validation="Strict",
        )

        return super().update(attrs)

    def delete(
        self,
    ) -> "HelmChart":
        # Delete the Helm Chart object in Kubernetes
        self.client.delete_namespaced_custom_object(
            group="helm.cattle.io",
            version="v1",
            namespace=self.namespace,
            plural="helmcharts",
            name=self.name,
            body=kubernetes.client.V1DeleteOptions(
                propagation_policy="Foreground",
            ),
        )

        return super().delete()
