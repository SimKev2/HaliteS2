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
	rm -f *.log
	rm -f *.hlt


.PHONY: deps
deps:
	pip install -q -r requirements_dev.txt


.PHONY: package
package:
	zip -r submission.zip MyBot.py __init__.py hlt/


.PHONY: release
release:
	hlt bot -b ./submission.zip


.PHONY: gym
gym: package
	hlt gym -r "python3 MyBot.py" -r "python3 MyBot.py" -b "./halite" -i 100 -H 240 -W 320


.PHONY: test
test: deps
	flake8
	coverage erase
	nosetests
	coverage report --fail-under=100
