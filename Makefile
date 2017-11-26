# -----------------------
# Targets
# -----------------------
help:
	@echo "Simkev2 HaliteS2 Makefile Targets:"
	@echo "  clean      to clear submission zips and build directories"
	@echo "  deps       to install the required files for development"
	@echo "  package    to create a submission zip"
	@echo "  release    to submit the current submission zip"
	@echo "  test       to run all tests"
	@echo ""


.PHONY: clean
clean:
	rm -f submission.zip


.PHONY: deps
deps:
	pip install -q -r requirements_dev.txt


.PHONY: package
package:
	zip -r submission.zip MyBot.py hlt/


.PHONY: release
release:
	python ./HaliteClient/hlt_client/client.py bot -b ./submission.zip


.PHONY: test
test: deps
	flake8
	coverage erase
	nosetests
	coverage report --fail-under=100
