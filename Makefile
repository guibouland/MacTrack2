# Paths
SPHINX_SOURCE = docs/source
SPHINX_BUILD = docs/build
MODULE_DIRS = Set_up mactrack
QUICKSTART_SCRIPT = quickstart.py
QUICKSTART_RST = $(SPHINX_SOURCE)/quickstart.rst

# Default target
all: quickstart apidoc html

# Generate quickstart.rst from the Python script
quickstart:
	@echo "Generating quickstart.rst from $(QUICKSTART_SCRIPT)..."
	@echo "Quickstart for MacTrack2" > $(QUICKSTART_RST)
	@echo "=========================" >> $(QUICKSTART_RST)
	@echo "" >> $(QUICKSTART_RST)
	@echo ".. literalinclude:: ../../$(QUICKSTART_SCRIPT)" >> $(QUICKSTART_RST)
	@echo "   :language: python" >> $(QUICKSTART_RST)
	@echo "   :linenos:" >> $(QUICKSTART_RST)

# Generate .rst files from modules using sphinx-apidoc
apidoc:
	sphinx-apidoc -o $(SPHINX_SOURCE) $(MODULE_DIRS) --force --no-toc

# Build the HTML documentation
html:
	sphinx-build -b html $(SPHINX_SOURCE) $(SPHINX_BUILD)/html

# Clean all generated files
clean:
	rm -rf $(SPHINX_BUILD)/*
	rm -f $(SPHINX_SOURCE)/Set_up*.rst
	rm -f $(SPHINX_SOURCE)/mactrack*.rst
	rm -f $(SPHINX_SOURCE)/modules.rst
	rm -f $(QUICKSTART_RST)

# Clean and rebuild everything
rebuild: clean all

.PHONY: all apidoc html clean rebuild quickstart
