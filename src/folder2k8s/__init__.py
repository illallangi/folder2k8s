import base64
import os
import secrets
import sys
from warnings import filterwarnings

from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import HttpRequest, JsonResponse
from django.urls import include, re_path
from django.views.decorators.http import require_GET
from dotenv import load_dotenv

from folder2k8s.folder.folderadapter import FolderAdapter
from folder2k8s.kubernetes.kubernetesadapter import KubernetesAdapter

load_dotenv(
    override=True,
)

filterwarnings(
    action="ignore",
    message=r".*has conflict with protected namespace.*",
    category=UserWarning,
)

settings.configure(
    DEBUG=True,
    SECRET_KEY=base64.b64encode(
        secrets.token_bytes(32),
    ).decode(),
    ROOT_URLCONF=__name__,
    INSTALLED_APPS=[
        "health_check",
    ],
    MIDDLEWARE=(
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
    ),
    ALLOWED_HOSTS=["*"],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
        },
    ],
    FOLDER2K8S={
        "path": os.environ.get("FOLDER2K8S_PATH", "/folder2k8s"),
        "source": os.environ.get("FOLDER2K8S_SOURCE", "folder2k8s"),
    },
)


@require_GET
def receive_hook(
    _: HttpRequest,
) -> JsonResponse:
    src = FolderAdapter(
        settings.FOLDER2K8S["path"],
    )
    dst = KubernetesAdapter(
        settings.FOLDER2K8S["source"],
    )

    src.load()
    dst.load()

    diff = src.sync_to(dst)

    return JsonResponse(
        diff.dict(),
    )


urlpatterns = [
    re_path(
        r"^.well-known/receive-webhook/$",
        receive_hook,
        name="receive-webhook",
    ),
    re_path(
        r"^.well-known/health-check/",
        include("health_check.urls"),
    ),
]


def main() -> None:
    from django.core.management.commands.runserver import Command

    Command.default_port = "8000"
    Command.default_addr = "0.0.0.0"  # noqa: S104

    execute_from_command_line(
        [
            sys.argv[0],
            "runserver",
        ],
    )


if __name__ == "__main__":
    main()
