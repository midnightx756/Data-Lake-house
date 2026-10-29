#include <iostream>
#include <string>
#include <vector>
#include "asset_header.h"

// Forward declarations matching functions in our modules
void pack_with_deduplication(const std::vector<std::string>& file_paths,
                             const std::string& blob_output_path,
                             const std::string& manifest_output_path);

void extract_asset_mmap(const std::string& blob_path, uint64_t byte_offset);

bool update_asset_payload(const std::string& blob_path,
                          uint64_t target_offset,
                          const std::string& new_payload);

void inspect_blob(const std::string& blob_path);

void print_usage() {
    std::cout << "====================================================\n";
    std::cout << "   Semantic Data Lake-House (SDLH) Systems Core    \n";
    std::cout << "====================================================\n";
    std::cout << "Usage:\n";
    std::cout << "  ./bin/sdlh pack    <output.blob> <manifest.csv> <file1> [file2...]\n";
    std::cout << "  ./bin/sdlh extract <blob_path> <byte_offset>\n";
    std::cout << "  ./bin/sdlh update  <blob_path> <byte_offset> <new_text>\n";
    std::cout << "  ./bin/sdlh inspect <blob_path>\n";
    std::cout << "====================================================\n";
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_usage();
        return 1;
    }

    std::string command = argv[1];

    if (command == "pack") {
        if (argc < 5) {
            std::cerr << "[ERROR] pack requires: <output.blob> <manifest.csv> <file1> [file2...]\n";
            return 1;
        }
        std::string blob_path = argv[2];
        std::string manifest_path = argv[3];
        std::vector<std::string> files;
        for (int i = 4; i < argc; ++i) {
            files.push_back(argv[i]);
        }
        pack_with_deduplication(files, blob_path, manifest_path);

    } else if (command == "extract") {
        if (argc < 4) {
            std::cerr << "[ERROR] extract requires: <blob_path> <byte_offset>\n";
            return 1;
        }
        std::string blob_path = argv[2];
        uint64_t offset = std::stoull(argv[3]);
        extract_asset_mmap(blob_path, offset);

    } else if (command == "update") {
        if (argc < 5) {
            std::cerr << "[ERROR] update requires: <blob_path> <byte_offset> <new_text>\n";
            return 1;
        }
        std::string blob_path = argv[2];
        uint64_t offset = std::stoull(argv[3]);
        std::string new_text = argv[4];
        update_asset_payload(blob_path, offset, new_text);

    } else if (command == "inspect") {
        if (argc < 3) {
            std::cerr << "[ERROR] inspect requires: <blob_path>\n";
            return 1;
        }
        inspect_blob(argv[2]);

    } else {
        std::cerr << "[ERROR] Unknown command: " << command << "\n";
        print_usage();
        return 1;
    }

    return 0;
}
