## To get help on this makefile, run `make help`.
# https://www.gnu.org/software/make/manual/make.html

# Adapt these variables for this project:
py_code_locs = coverage_simple_excludes tests
# Hint: $(filter-out whatever,$(py_code_locs))
# Remember to keep in sync with GitHub Actions workflows:
requirement_txts = requirements.txt dev/requirements.txt
perm_checks = ./* .gitignore .vscode .github

# The user can change the following on the command line, but note that some tools below may not use this variable!
PYTHON3BIN = python

.PHONY: help tasklist installdeps test
.PHONY: smoke-checks nix-checks shellcheck ver-checks other-checks coverage unittest
test:   smoke-checks nix-checks shellcheck ver-checks other-checks coverage  ## Run all tests
# Reminder: If the `test` target changes, make the appropriate changes to .github/workflows/tests.yml

SHELL = /bin/bash
.ONESHELL:  # each recipe is executed as a single script

tasklist:	## List open tasks.
	@grep --color=auto \
		--exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.ipynb_checkpoints --exclude-dir='.venv*' \
		--exclude-dir='.*cache' --exclude-dir=node_modules --exclude='LICENSE*' --exclude='.*.swp' \
		-Eri 'to.?do'
	true  # ignore nonzero exit code from grep

installdeps:  ## Install project dependencies
	@set -euxo pipefail
	$(PYTHON3BIN) -m pip install --upgrade --upgrade-strategy=eager --no-warn-script-location pip wheel
	$(PYTHON3BIN) -m pip install --upgrade --upgrade-strategy=eager --no-warn-script-location $(foreach x,$(requirement_txts),-r $(x))
	# for modules/packages:
	# $(PYTHON3BIN) -m pip install --editable .
	# other examples: git lfs install / npm ci

smoke-checks:  ## Basic smoke tests
	@set -euxo pipefail
	# example: [[ "$$OSTYPE" =~ linux.* ]]  # this project only runs on Linux
	[[ "$$($(PYTHON3BIN) --version)" =~ ^Python\ 3\. ]]  # make sure we're on Python 3

nix-checks:  ## Checks that depend on a *NIX OS/FS
	@set -euo pipefail
	UNRELIABLE_PERMS="yes"
	if [ "$$OSTYPE" == "msys" ]; then  # e.g. Git bash on Windows
		echo "- Assuming unreliable permission bits because Windows"
		set -x
	else
		FSTYPE="$$( findmnt --all --first --noheadings --list --output FSTYPE --notruncate --target . )"
		if [[ "$$FSTYPE" =~ ^(vfat|vboxsf)$$ ]]; then
			echo "- Assuming unreliable permission bits because FSTYPE=$$FSTYPE"
			set -x
		else  # we can probably depend on permission bits being correct
			UNRELIABLE_PERMS=""
			set -x
			$(PYTHON3BIN) -m simple_perms -r $(perm_checks)  # if this errors, run `simple-perms -m ...` for auto fix
			test -z "$$( find . \( -type d -name '.venv*' -prune \) -o \( -iname '*.sh' ! -executable -print \) )"
		fi
	fi
	py-check-script-vs-lib $${UNRELIABLE_PERMS:+"--exec-git"} --notice $(py_code_locs)
	# exclusions to the above can be done via:
	# find $(py_code_locs) -path '*/exclude/me.py' -o -type f -iname '*.py' -exec py-check-script-vs-lib --notice '{}' +

shellcheck:  ## Run shellcheck
	@set -euxo pipefail
	# https://www.gnu.org/software/findutils/manual/html_mono/find.html
	find . \( -type d -name '.venv*' -prune \) -o \( -iname '*.sh' -exec shellcheck '{}' + \)

ver-checks:  ## Checks that depend on the Python version
	@set -euxo pipefail
	# https://microsoft.github.io/pyright/#/command-line
	npx pyright --project pyproject.toml --pythonpath "$$( $(PYTHON3BIN) -c 'import sys; print(sys.executable)' )" $(py_code_locs)
	$(PYTHON3BIN) -m mypy --config-file pyproject.toml $(py_code_locs)
	# Note I'm not sure if the following are actually version-dependent, but because they parse the Python code, I'll leave them here.
	$(PYTHON3BIN) -m flake8 --toml-config=pyproject.toml $(py_code_locs)
	$(PYTHON3BIN) -m pylint --rcfile=pyproject.toml --recursive=y $(py_code_locs)

other-checks:  ## Checks not depending on the Python version
	@set -euxo pipefail
	# note the following is on one line b/c GitHub macOS Action Runners are running bash 3.2 and the multiline version didn't work there...
	for REQ in $(requirement_txts); do $(PYTHON3BIN) -m pur --skip-gt --dry-run-changed --nonzero-exit-code -r "$$REQ"; done

unittest:  ## Run unit tests
	@PYTHONDEVMODE=1 PYTHONWARNINGS=error PYTHONWARNDEFAULTENCODING=1 $(PYTHON3BIN) -m unittest -v

coverage:  ## Run unit tests with coverage
	@set -euxo pipefail
	# Note: Don't add command-line arguments here, put them in the rcfile
	# We also don't use --fail_under=100 because then the report won't be written.
	PYTHONDEVMODE=1 PYTHONWARNINGS=error PYTHONWARNDEFAULTENCODING=1 $(PYTHON3BIN) -m coverage run --rcfile=pyproject.toml
	$(PYTHON3BIN) -m coverage report --rcfile=pyproject.toml
	# $(PYTHON3BIN) -m coverage html --rcfile=pyproject.toml
	$(PYTHON3BIN) -m coverage xml --rcfile=pyproject.toml
	$(PYTHON3BIN) -m coverage json --rcfile=pyproject.toml -o- \
		| perl -wM5.014 -MJSON::PP=decode_json -MTerm::ANSIColor=colored -0777 -ne \
		'$$_=decode_json($$_)->{totals}{percent_covered};print"=> ",colored([$$_==100?"green":"red"],"$$_% Coverage")," <=\n";exit($$_==100?0:1)'

# https://stackoverflow.com/q/8889035
help:   ## Show this help
	@sed -ne 's/^\([^[:space:]]*\):.*##/\1:\t/p' $(MAKEFILE_LIST) | column -t -s $$'\t'
