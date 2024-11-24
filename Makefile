.PHONY: usage
usage:
	@echo "Usage: make [target]"
	@echo
	@echo "Targets:"
	@echo "  clean       Remove all generated files"
	@echo "  lint        Run ruff format, check and uv sync"
	@echo "  commit      Run cz commit"
	@echo "  build       Build the project"
	@echo "  image       Build an image"
	@echo

.PHONY: clean
clean:
	@git clean -Xdf
	@mkdir -p .git/hooks
	@rm -f .git/hooks/*.sample
	@find .git/hooks/ -type f  | while read i; do chmod +x $$i; done

.PHONY: lint
lint:
	@uv run --quiet deptry src --experimental-namespace-package
	@uv run --quiet ruff format src
	@uv run --quiet djlint --reformat src --quiet || true
	@uv run --quiet ruff check src --quiet
	@uv run --quiet djlint --lint src --quiet
	@uv sync --quiet

.PHONY: commit
commit: lint
	@uv run --quiet cz commit

.PHONY: build
build: lint
	@uv build

.PHONY: image
image: build
	@podman build --format=docker --tag illallangi/folder2k8s:latest .

.PHONY: runimage
runimage: image
	@fuser --kill 8000/tcp || true
	@podman run \
		-it \
		--rm \
		--env-file $$(uv run python -c "from dotenv import find_dotenv; print(find_dotenv())") \
		-p 8000:8000 \
		illallangi/folder2k8s:latest

.PHONY: pushimage
pushimage: image
	@podman push \
	  illallangi/folder2k8s:latest \
	  registry.great-tuna.ts.net/folder2k8s:latest
