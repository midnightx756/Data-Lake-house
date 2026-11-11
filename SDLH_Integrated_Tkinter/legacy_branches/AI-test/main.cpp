#include <iostream>
#include <fstream>
#include "asset_header.h"

int main() {
    std::cout << "--- SDLH BINARY HEADER TEST ---" << std::endl;

    // 1. Create a dummy header in RAM
    AssetHeader original_header{};
    original_header.set_magic();
    original_header.asset_id = 101;
    original_header.payload_size = 2048; // Pretend we have a 2KB file
    original_header.timestamp = 1710000000;
    original_header.flags = 0;

    // 2. Write it to a binary file
    std::ofstream out_file("test.blob", std::ios::binary);
    if (!out_file) {
        std::cerr << "Error: Could not create test.blob!" << std::endl;
        return 1;
    }
    out_file.write(reinterpret_cast<const char*>(&original_header), sizeof(AssetHeader));
    out_file.close();
    std::cout << "[SUCCESS] Wrote 64-byte header to 'test.blob'!" << std::endl;

    // 3. Read it back from the binary file
    std::ifstream in_file("test.blob", std::ios::binary);
    AssetHeader read_header{};
    in_file.read(reinterpret_cast<char*>(&read_header), sizeof(AssetHeader));
    in_file.close();

    // 4. Verify the data
    if (read_header.is_valid()) {
        std::cout << "[SUCCESS] Valid SDLH Magic Bytes found!" << std::endl;
        std::cout << "  - Asset ID: " << read_header.asset_id << std::endl;
        std::cout << "  - Payload Size: " << read_header.payload_size << " bytes" << std::endl;
        std::cout << "  - Header Size: " << sizeof(AssetHeader) << " bytes" << std::endl;
    } else {
        std::cerr << "[FAIL] Corrupted header!" << std::endl;
    }

    return 0;
}
