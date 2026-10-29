# ==============================================================================
# Master Makefile for Semantic Data Lake-House (SDLH) Core
# ==============================================================================

CXX      := g++
CXXFLAGS := -std=c++17 -Wall -Wextra -O2 -pthread -Iinclude
LDFLAGS  := -pthread

BIN_DIR  := bin
LIB_DIR  := lib

MODULES  := src/dedup_packer.cpp src/mmap_extractor.cpp src/updater.cpp
MASTER_BIN := $(BIN_DIR)/sdlh
SHARED_LIB := $(LIB_DIR)/libsdlh.so

.PHONY: all clean directories

all: directories $(MASTER_BIN) $(SHARED_LIB)
	@echo ""
	@echo "===================================================="
	@echo " [SUCCESS] SDLH UNIFIED SYSTEM BUILT SUCCESSFULLY!"
	@echo " Master CLI Tool : ./$(MASTER_BIN)"
	@echo " Shared Library  : ./$(SHARED_LIB)"
	@echo "===================================================="

directories:
	@mkdir -p $(BIN_DIR) $(LIB_DIR)

$(MASTER_BIN): src/main.cpp $(MODULES)
	@echo "[LINK] Compiling Unified CLI Executable: $@..."
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LDFLAGS)

$(SHARED_LIB): $(MODULES)
	@echo "[BUILD] Compiling Shared Library: $@..."
	$(CXX) $(CXXFLAGS) -fPIC -shared $^ -o $@ $(LDFLAGS)

clean:
	@echo "[CLEAN] Removing binaries and test data..."
	rm -rf $(BIN_DIR) $(LIB_DIR) *.blob *.csv *.txt
	@echo "[CLEAN] Done!"
