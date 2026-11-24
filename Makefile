# VERSION_PREFIX is this package's own version line. Build versions are <prefix><YYYYMMDDHHMMSS>.
VERSION_PREFIX ?= 0.1.0.dev
PROJECT = setupimagebbs
WHEELS_DIR ?= /tmp/$(PROJECT)-$(shell id -un)
VERSION = $(shell mkdir -p $(WHEELS_DIR) && ../scripts/next_version.sh $(VERSION_PREFIX) $(WHEELS_DIR))

all: version

# Writes src/setupimagebbs/_version.py (generated, git-ignored). The build reads __version__ from it.
version:
	@mkdir -p $(WHEELS_DIR)
	@echo '__version__ = "$(VERSION)"' > src/$(PROJECT)/_version.py
	@echo '__datestamp__ = "$(VERSION)"' >> src/$(PROJECT)/_version.py
	@echo '__githash__ = "'`git log -1 --format='%H' 2>/dev/null | cut -c 1-16`'"' >> src/$(PROJECT)/_version.py
	@cat src/$(PROJECT)/_version.py

# Installs setupimagebbs into the user's venv: the active one ($VIRTUAL_ENV), or the python on PATH. Not zoid6's venv.
PYTHON ?= $(if $(VIRTUAL_ENV),$(VIRTUAL_ENV)/bin/python,python3)
DEPLOY_DRY_RUN ?= 0

venv: version
ifeq ($(DEPLOY_DRY_RUN),1)
	@echo "dry-run: would build setupimagebbs and install it into $(dir $(PYTHON))..; skipped"
else
	@work="$$(mktemp -d)" && \
	trap 'rm -rf "$$work"' EXIT && \
	tar -C . --exclude=./.git --exclude=./sandbox --exclude=./dist-wheels --exclude=./build --exclude='*.egg-info' --exclude=__pycache__ \
		--exclude='*.img' --exclude='*.dumpconfig' --exclude='*.png' -cf - . | tar -C "$$work" -xf - && \
	cp src/$(PROJECT)/_version.py "$$work/src/$(PROJECT)/_version.py" && \
	mkdir -p "$(WHEELS_DIR)" && \
	$(PYTHON) -m pip install --upgrade build && \
	$(PYTHON) -m build --wheel --outdir "$(WHEELS_DIR)" "$$work" && \
	$(PYTHON) -m pip install --upgrade "$(WHEELS_DIR)"/setupimagebbs-*.whl
endif

clean:
	$(MAKE) -C src clean
	-rm *~
