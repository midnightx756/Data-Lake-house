#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include "asset_header.h"

// ============================================================================
// Helper 1: Read an entire real file from disk into a byte vector
// ============================================================================
std::vector<char> read_file_bytes(const std::string& filepath) {
    // 1. Open file in binary mode at the END (std::ios::ate) to find its size
    std::ifstream file(filepath, std::ios::binary | std::ios::ate);
    if (!file) {
        std::cerr << "Could not open input file: " << filepath << std::endl;
        return {};
    }

    std::streamsize size = file.tellg(); // Get file size in bytes
    file.seekg(0, std::ios::beg);        // Rewind to the beginning

    std::vector<char> buffer(size);

    // TODO: Read the entire file into 'buffer' using file.read()
    // HINT: file.read(buffer.data(), size);
    file.read(buffer.data(), size);

    return buffer;
}

// ============================================================================
// Task 1: Pack multiple files into a single .blob
// ============================================================================
void pack_files(const std::vector<std::string>& file_paths, const std::string& blob_output_path) {
    std::ofstream blob(blob_output_path, std::ios::binary);
    if (!blob) {
        std::cerr << "Failed to open output blob: " << blob_output_path << std::endl;
        return;
    }

    uint64_t current_asset_id = 1;

    for (const auto& path : file_paths) {
        // Step A: Read raw bytes of the current file
        std::vector<char> file_data = read_file_bytes(path);
        if (file_data.empty()) continue;

        // Step B: Build the 64-byte Header for this file
        AssetHeader header{};
        header.set_magic();
        header.asset_id = current_asset_id++;
        header.payload_size = file_data.size();

        // Get current timestamp (UNIX epoch in seconds)
        auto now = std::chrono::system_clock::now();
        header.timestamp = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();

        // TODO: 1. Write the 64-byte header into 'blob'
        // HINT: Use blob.write(reinterpret_cast<const char*>(&header), sizeof(AssetHeader));
        blob.write(reinterpret_cast<const char*>(&header), sizeof(AssetHeader));

        // TODO: 2. Write the actual file payload bytes immediately after the header
        // HINT: Use blob.write(file_data.data(), file_data.size());
        blob.write(file_data.data(), file_data.size());

        std::cout << "[PACKED] " << path << " -> ID: " << header.asset_id
        << " (" << header.payload_size << " bytes)" << std::endl;
    }

    blob.close();
    std::cout << "[SUCCESS] Packed all files into " << blob_output_path << "\n" << std::endl;
}

// ============================================================================
// Task 2: Read through the .blob and unpack every asset
// ============================================================================
void unpack_blob(const std::string& blob_path) {
    std::ifstream blob(blob_path, std::ios::binary);
    if (!blob) {
        std::cerr << "Failed to open blob for reading: " << blob_path << std::endl;
        return;
    }

    std::cout << "--- READING ASSETS FROM BLOB ---" << std::endl;

    while (true) {
        AssetHeader header{};

        // TODO: 1. Read the next 64 bytes into 'header'
        // HINT: blob.read(reinterpret_cast<char*>(&header), sizeof(AssetHeader));
        blob.read(reinterpret_cast<char*>(&header), sizeof(AssetHeader));
        // Check if we hit End-Of-File (EOF)
        if (!blob) break;

        // Verify magic bytes
        if (!header.is_valid()) {
            std::cerr << "[ERROR] Invalid or corrupted header found!" << std::endl;
            break;
        }

        // Prepare a vector to hold the file's payload
        std::vector<char> payload(header.payload_size);
        blob.read(payload.data(), header.payload_size);
        // TODO: 2. Read the file's raw payload bytes into 'payload'


        // Convert the bytes to a string and print (works for text files!)
        std::string content(payload.begin(), payload.end());

        std::cout << "Asset ID: " << header.asset_id << " | Size: " << header.payload_size << " bytes" << std::endl;
        std::cout << "Content: \"" << content << "\"\n" << std::endl;
    }

    blob.close();
}

// ============================================================================
// Main Execution
// ============================================================================
int main() {
    // 1. Create 2 sample text files for testing
    {
        std::ofstream f1("sample1.txt");
        f1 << "Hello, this is asset #1 stored inside our Semantic Data Lake!";
        std::ofstream f2("sample2.txt");
        f2 << "And this is asset #2, proving sequential binary blob encapsulation works!";
    }

    std::vector<std::string> my_files = {"sample1.txt", "sample2.txt"};

    // 2. Pack them
    pack_files(my_files, "data.blob");

    // 3. Unpack & Verify them
    unpack_blob("data.blob");

    return 0;
}


// HINT: blob.read(payload.data(), header.payload_size);
