#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <chrono>
#include <iomanip>

#include "asset_header.h"

// A fast, lightweight 64-bit FNV-1a Hash function (No external libraries needed!)
uint64_t compute_fnv1a_hash(const std::vector<char>& data) {
    uint64_t hash = 14695981039346656037ULL; // FNV offset basis
    for (char byte : data) {
        hash ^= static_cast<uint8_t>(byte);
        hash *= 1099511628211ULL;            // FNV prime
    }
    return hash;
}

struct ManifestEntry {
    uint64_t asset_id;
    std::string original_name;
    uint64_t content_hash;
    uint64_t byte_offset;
    uint64_t payload_size;
    bool is_duplicate;
};

// ============================================================================
// Task: Pack files with Content-Addressable Deduplication & Export Manifest
// ============================================================================
void pack_with_deduplication(const std::vector<std::string>& file_paths,
    const std::string& blob_output_path,
    const std::string& manifest_output_path) {

    std::ofstream blob(blob_output_path, std::ios::binary);
    if (!blob) {
        std::cerr << "Failed to open output blob!" << std::endl;
        return;
    }

    std::vector<ManifestEntry> manifest;

    // Hash-Table to track existing content: Map<ContentHash, ExistingByteOffset>
    std::unordered_map<uint64_t, uint64_t> hash_to_offset_table;
    // Map<ContentHash, PayloadSize> to track payload sizes of existing assets
    std::unordered_map<uint64_t, uint64_t> hash_to_size_table;

    uint64_t current_blob_offset = 0;
    uint64_t current_asset_id = 1;
    uint64_t bytes_saved = 0;

    for (const auto& path : file_paths) {
        // 1. Read input file
        std::ifstream file(path, std::ios::binary | std::ios::ate);
        if (!file) {
            std::cerr << "Skipping missing file: " << path << std::endl;
            continue;
        }
        std::streamsize size = file.tellg();
        file.seekg(0, std::ios::beg);
        std::vector<char> buffer(size);
        file.read(buffer.data(), size);

        // 2. Compute cryptographic fingerprint
        uint64_t file_hash = compute_fnv1a_hash(buffer);

        bool duplicate_found = false; // Change this based on your check!
        // TODO 1: Check if 'file_hash' already exists in 'hash_to_offset_table'
        if(hash_to_offset_table.find(file_hash) != hash_to_offset_table.end()){
            duplicate_found = true;
        }
        else{
            duplicate_found = false;
        }
        // HINT: Use hash_to_offset_table.find(file_hash) != hash_to_offset_table.end()

        if (duplicate_found) {
            // --- DEDUPLICATION BRANCH (ZERO BYTES WRITTEN TO DISK!) ---

            // TODO 2: Retrieve the existing offset and payload size from your hash tables
            uint64_t existing_offset = 0; // Retrieve from hash_to_offset_table
            uint64_t existing_size = 0;   // Retrieve from hash_to_size_table
            existing_offset = hash_to_offset_table.at(file_hash);
            existing_size = hash_to_size_table.at(file_hash);

            // TODO 3: Create a ManifestEntry marked as 'is_duplicate = true'
            // and pointing to 'existing_offset'. Push it to 'manifest'.
            ManifestEntry entry;
            entry.is_duplicate = true;
            entry.byte_offset = existing_offset;
            entry.payload_size = existing_size;
            entry.content_hash = file_hash;
            entry.asset_id = current_asset_id++;
            entry.original_name = path;
            manifest.push_back(entry);

            bytes_saved += (sizeof(AssetHeader) + buffer.size());
            std::cout << "[DEDUP] " << path << " is identical to an existing asset! "
            << "Reusing Offset " << existing_offset << " (Saved " << buffer.size() << " B)" << std::endl;

        } else {
            // --- NEW UNIQUE ASSET BRANCH (WRITE TO BLOB) ---

            // Build Header
            AssetHeader header{};
            header.set_magic();
            header.asset_id = current_asset_id;
            header.payload_size = buffer.size();
            header.timestamp = std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();

                // Write 64-byte Header and raw payload to .blob
                blob.write(reinterpret_cast<const char*>(&header), sizeof(AssetHeader));
                blob.write(buffer.data(), buffer.size());

                // TODO 4: Record this new asset in both hash tables so future duplicates can find it!
                hash_to_size_table[file_hash] = header.payload_size; //buffer.size();
                hash_to_offset_table[file_hash] = current_blob_offset;
                // hash_to_offset_table[file_hash] = current_blob_offset;
                // hash_to_size_table[file_hash] = buffer.size();

                // TODO 5: Create a ManifestEntry marked as 'is_duplicate = false'
                // with byte_offset = current_blob_offset. Push it to 'manifest'.
                ManifestEntry entry;
                entry.asset_id = current_asset_id;
                entry.original_name = path;
                entry.byte_offset = current_blob_offset;
                entry.content_hash = file_hash;
                entry.payload_size = buffer.size();
                entry.is_duplicate = false;
                manifest.push_back(entry);

                // TODO 6: Advance 'current_blob_offset' by (sizeof(AssetHeader) + buffer.size())
                current_blob_offset += buffer.size() + sizeof(AssetHeader);

                std::cout << "[WRITE] " << path << " -> Stored at Offset " << manifest.back().byte_offset
                << " (ID: " << current_asset_id << ")" << std::endl;
        }

        current_asset_id++;
    }

    blob.close();

    // ========================================================================
    // Task 2: Export Manifest to CSV for Python / SQLite Team
    // ========================================================================
    std::ofstream csv(manifest_output_path);
    csv << "asset_id,original_name,content_hash,byte_offset,payload_size,is_duplicate\n";

    // TODO 7: Loop through 'manifest' vector and write each record as a CSV row!
    // Example format: 1,sample1.txt,14695981039346656037,0,1024,0
    for(auto mani : manifest){
        csv << mani.asset_id <<","<< mani.original_name << "," <<  mani.content_hash << "," << mani.byte_offset << ","<< mani.payload_size << "," <<mani.is_duplicate<< "\n";
    }
    csv.close();

    std::cout << "\n==========================================" << std::endl;
    std::cout << "[SUCCESS] Packing Complete!" << std::endl;
    std::cout << "Total Disk Bytes Saved via Dedup: " << bytes_saved << " bytes" << std::endl;
    std::cout << "Manifest exported to: " << manifest_output_path << std::endl;
    std::cout << "==========================================\n" << std::endl;
}

// ============================================================================
// Main Execution
// ============================================================================
int main() {
    // 1. Create 4 test files (Notice doc1 and doc3 have IDENTICAL contents!)
    {
        std::ofstream("doc1.txt") << "Identical Content: Neural Network Weights Layer 1";
        std::ofstream("doc2.txt") << "Unique Content: Hyperparameter configuration parameters.";
        std::ofstream("doc3.txt") << "Identical Content: Neural Network Weights Layer 1"; // DUPLICATE OF DOC1
        std::ofstream("doc4.txt") << "Unique Content: Loss function gradients.";
    }

    std::vector<std::string> dataset = {"doc1.txt", "doc2.txt", "doc3.txt", "doc4.txt"};

    pack_with_deduplication(dataset, "data.blob", "manifest.csv");

    return 0;
}
