# ==============================================================================
# Master Makefile for Semantic Data Lake-House (SDLH) Core
# ==============================================================================

CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -O2 -pthread -Iinclude
LDFLAGS  := -pthread

# Output directories
BIN_DIR  := bin
LIB_DIR  := lib

# Individual Module Binaries
TARGET_DEDUP     := $(BIN_DIR)/sdlh_dedup
TARGET_EXTRACTOR := $(BIN_DIR)/sdlh_extractor
TARGET_THREADS   := $(BIN_DIR)/sdlh_threads
TARGET_UPDATER   := $(BIN_DIR)/sdlh_updater
TARGET_BASIC     := $(BIN_DIR)/sdlh_basic

# Shared Dynamic Library for Python / DBMS
TARGET_LIB       := $(LIB_DIR)/libsdlh.so

# List of all targets
ALL_TARGETS      := $(TARGET_DEDUP) $(TARGET_EXTRACTOR) $(TARGET_THREADS) $(TARGET_UPDATER) $(TARGET_BASIC) $(TARGET_LIB)

.PHONY: all clean help directories

# Default: compile all modules and libraries
all: directories $(ALL_TARGETS)
	@echo ""
	@echo "===================================================="
	@echo " [SUCCESS] ALL SDLH MODULES COMPILED CLEANLY!"
	@echo " Binaries located in: ./$(BIN_DIR)/"
	@echo " Shared library in  : ./$(LIB_DIR)/"
	@echo "===================================================="

directories:
	@mkdir -p $(BIN_DIR) $(LIB_DIR)

# 1. Deduplication & Manifest Packer Module
$(TARGET_DEDUP): src/dedup_packer.cpp
	@echo "[BUILD] Compiling CAS Dedup Engine: $@..."
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

# 2. mmap Zero-Copy Extractor Module
$(TARGET_EXTRACTOR): src/mmap_extractor.cpp
	@echo "[BUILD] Compiling Zero-Copy mmap Extractor: $@..."
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

# 3. Multithreaded Ingestion Pool Module
$(TARGET_THREADS): src/multithread_packer.cpp
	@echo "[BUILD] Compiling Multithreaded Ingest Engine: $@..."
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

# 4. In-Place Backward Shift Updater Module
$(TARGET_UPDATER): src/updater.cpp
	@echo "[BUILD] Compiling Backward Shift Updater: $@..."
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

# 5. Baseline Sequential Packer Module
$(TARGET_BASIC): src/packer.cpp
	@echo "[BUILD] Compiling Baseline Packer: $@..."
	$(CXX) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

# 6. Shared Dynamic Library for Python Integration (-fPIC)
$(TARGET_LIB): src/mmap_extractor.cpp src/updater.cpp src/dedup_packer.cpp
	@echo "[BUILD] Compiling Shared Library: $@..."
	$(CXX) $(CXXFLAGS) -fPIC -shared -DSDLH_LIB $^ -o $@ $(LDFLAGS)

# Clean rule
clean:
	@echo "[CLEAN] Removing all compiled binaries and test data..."
	rm -rf $(BIN_DIR) $(LIB_DIR) src/*.o *.blob *.csv *.txt
	@echo "[CLEAN] Complete!"

help:
	@echo "Available targets:"
	@echo "  make        - Compiles all 5 systems modules + Shared Library"
	@echo "  make clean  - Removes all binaries and generated test files"
