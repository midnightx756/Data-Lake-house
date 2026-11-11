# ==============================================================================
# Makefile for Semantic Data Lake-House (SDLH) Core
# Source Path : core_cpp/src/
# Header Path : core_cpp/include/
# Outputs     : bin/sdlh, lib/libsdlh.so
# ==============================================================================

CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -O2 -pthread -Icore_cpp/include
LDFLAGS  := -pthread

BIN_DIR  := bin
LIB_DIR  := lib

# Core engine source files linked into both CLI and Shared Library
CORE_SRCS := core_cpp/src/dedup_packer.cpp \
             core_cpp/src/mmap_extractor.cpp \
             core_cpp/src/updater.cpp

# Main CLI entry point
MAIN_SRC  := core_cpp/src/main.cpp

# Targets
MASTER_BIN := $(BIN_DIR)/sdlh
SHARED_LIB := $(LIB_DIR)/libsdlh.so

.PHONY: all clean directories help

# Default target: builds both executable and shared library
all: directories $(MASTER_BIN) $(SHARED_LIB)
	@echo ""
	@echo "===================================================="
	@echo " [SUCCESS] SDLH BUILD COMPLETE"
	@echo " CLI Executable : ./$(MASTER_BIN)"
	@echo " Shared Library : ./$(SHARED_LIB)"
	@echo "===================================================="

directories:
	@mkdir -p $(BIN_DIR) $(LIB_DIR)

# 1. Compile the master CLI tool (links main.cpp with the core modules)
$(MASTER_BIN): $(MAIN_SRC) $(CORE_SRCS)
	@echo "[LINK] Compiling CLI executable: $@..."
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LDFLAGS)

# 2. Compile the Shared Dynamic Library (.so) for Python / ctypes integration
$(SHARED_LIB): $(CORE_SRCS)
	@echo "[BUILD] Compiling Shared Library: $@..."
	$(CXX) $(CXXFLAGS) -fPIC -shared $^ -o $@ $(LDFLAGS)

# Remove build artifacts and temporary files
clean:
	@echo "[CLEAN] Removing build artifacts and test outputs..."
	rm -rf $(BIN_DIR) $(LIB_DIR) *.blob *.csv *.txt
	@echo "[CLEAN] Complete!"

help:
	@echo "Available commands:"
	@echo "  make        - Build bin/sdlh and lib/libsdlh.so"
	@echo "  make clean  - Wipe bin/, lib/, and generated test files"
