/*#include <iostream>
#include <string>
#include <vector>
#include "asset_header.h"

//Declarations
void pack_files(const std:;vector<std::string>& filepaths, const std::string&blob_path, const std::string& manifest_path);
void extracat_asset_mmap(const std::string& blob)path, uint64_t offset);
bool update asset_payload(const std::string& blob_path, uint64_t offset, const std:: string& new_payload);
*/
#include <iostream>
#include <string>
#include <vector>
#include "asset_header.h"

// Forward declarations of your functions
void pack_files(const std::vector<std::string>& file_paths, const std::string& blob_path, const std::string& manifest_path);
void extract_asset_mmap(const std::string& blob_path, uint64_t offset);
bool update_asset_payload(const std::string& blob_path, uint64_t offset, const std::string& new_payload);

void print_usage() {
    std::cout << "====================================================\n";
    std::cout << "   Semantic Data Lake-House (SDLH) Systems Core    \n";
    std::cout << "====================================================\n";
    std::cout << "Usage:\n";
    std::cout << "  ./sdlh pack <output.blob> <manifest.csv> <file1> [file2...]\n";
    std::cout << "  ./sdlh extract <blob_path> <byte_offset>\n";
    std::cout << "  ./sdlh update <blob_path> <byte_offset> <new_text>\n";
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
            std::cerr << "Error: pack requires <output.blob> <manifest.csv> and at least one file!\n";
            return 1;
        }
        std::string blob_path = argv[2];
        std::string manifest_path = argv[3];
        std::vector<std::string> files;
        for (int i = 4; i < argc; ++i) {
            files.push_back(argv[i]);
        }
        pack_files(files, blob_path, manifest_path);

    } else if (command == "extract") {
        if (argc < 4) {
            std::cerr << "Error: extract requires <blob_path> and <byte_offset>!\n";
            return 1;
        }
        std::string blob_path = argv[2];
        uint64_t offset = std::stoull(argv[3]);
        extract_asset_mmap(blob_path, offset);

    } else if (command == "update") {
        if (argc < 5) {
            std::cerr << "Error: update requires <blob_path>, <byte_offset>, and <new_text>!\n";
            return 1;
        }
        std::string blob_path = argv[2];
        uint64_t offset = std::stoull(argv[3]);
        std::string new_text = argv[4];
        update_asset_payload(blob_path, offset, new_text);

    } else {
        std::cerr << "Unknown command: " << command << "\n";
        print_usage();
        return 1;
    }

    return 0;
}


