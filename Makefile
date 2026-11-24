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

clean:
	$(MAKE) -C src clean
	-rm *~
