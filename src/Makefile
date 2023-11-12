PROJECT = setupimagebbs

all:

clean:
	-rm *~
	$(MAKE) -C setupimagebbs clean
#	$(MAKE) -C bin clean

push:
	git push

version:
	@echo '__version__ = "'`git log -1 --format='%H' | cut -c 1-16`'"' > $(PROJECT)/_version.py
	@echo '__datestamp__ = "'`date +%Y%m%d-%H%M`-`whoami`'"' >> $(PROJECT)/_version.py
	@echo "_version updated"

install: version build
	sudo ./setup.py install

build: version
	./setup.py build

sdist: version
	./setup.py sdist
