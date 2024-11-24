import diffsync


class HelmChart(
    diffsync.DiffSyncModel,
):
    _modelname = "HelmChart"
    _identifiers = (
        "namespace",
        "name",
    )
    _attributes = ("spec",)

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
        msg = "HelmChart.create() is not implemented"
        raise NotImplementedError(msg)

    def update(
        self,
        attrs: dict,
    ) -> "HelmChart":
        msg = "HelmChart.update() is not implemented"
        raise NotImplementedError(msg)

    def delete(
        self,
    ) -> "HelmChart":
        msg = "HelmChart.delete() is not implemented"
        raise NotImplementedError(msg)
