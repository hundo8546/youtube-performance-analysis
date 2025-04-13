.PHONY: help build clean notebook

# I based this on the self-documenting Makefile https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
# Add ## with a message after a target, and it will be displayed when `make help` is run.
help: ## Display this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


build: ## build requirements and virtual environment
	python3 -m venv .venv
	.venv/bin/pip3 install -r requirements.txt

clean: ## Remove all installed dependences to start fresh
	rm -rf .venv
	rm .test

notebook: ## Start Jupyter notebook
	.venv/bin/jupyter notebook
