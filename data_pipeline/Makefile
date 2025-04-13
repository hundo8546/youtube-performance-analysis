.PHONY: help build clean test

# I based this on the self-documenting Makefile https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
# Add ## with a message after a target, and it will be displayed when `make help` is run.
help: ## Display this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Directory where source files are located
CODE_DIR = y8m-processor/src
# Directory where test files are located
TESTS_DIR = y8m-processor/tests
# All source files in the directory
SRC_FILES = $(wildcard $(CODE_DIR)/*)

build: ## build requirements and virtual environment
	python3 -m venv .venv
	.venv/bin/pip3 install -r requirements.txt

clean: ## Remove all installed dependences to start fresh
	rm -rf .venv
	rm .test

.test: $(SRC_FILES) .venv
	.venv/bin/pytest $(TESTS_DIR)
	touch .test

test: .test ## Run tests
	

process: .test ## Process a TFRecord file. Usage: make process TF_FILE=path/name.tfrecord
	@if [ -z "$(TF_FILE)" ]; then \
        echo "Error: Argument 'TF_FILE' is required."; \
        exit 1; \
    fi
	.venv/bin/python3 y8m-processor/src/main.py $(TF_FILE)

join: .test ## Join Data
	.venv/bin/python3 join_data.py