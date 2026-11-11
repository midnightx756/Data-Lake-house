#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>

// Linux / POSIX Headers for Memory-Mapping
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include "asset_header.h"

// A simple structure to store our offset manifest
struct IndexRecord {
    uint64_t asset_id;
    std::string original_name;
    uint64_t byte_offset; // Where this asset starts inside data.blob
    uint64_t total_size;  // 64 bytes header + payload bytes
};

// ============================================================================
// Step 1: Pack files AND record their starting byte-offsets
// ============================================================================
std::vector<IndexRecord> pack_files_with_index(const std::vector<std::string>& file_paths, 
                                               const std::string& blob_output_path) {
    std::ofstream blob(blob_output_path, std::ios::binary);
    std::vector<IndexRecord> manifest;

    uint64_t current_offset = 0;
    uint64_t current_id = 1;

    for (const auto& path : file_paths) {
        // Read input file
        std::ifstream file(path, std::ios::binary | std::ios::ate);
        if (!file) continue;
        std::streamsize size = file.tellg();
        file.seekg(0, std::ios::beg);
        std::vector<char> buffer(size);
        file.read(buffer.data(), size);

        // Build 64-byte Header
        AssetHeader header{};
        header.set_magic();
        header.asset_id = current_id++;
        header.payload_size = buffer.size();
        
        auto now = std::chrono::system_clock::now();
        header.timestamp = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();

        // Write header and payload
        blob.write(reinterpret_cast<const char*>(&header), sizeof(AssetHeader));
        blob.write(buffer.data(), buffer.size());

        // TODO 1: Create an IndexRecord for this file and record:
        //         - asset_id
        //         - original_name
        //         - byte_offset (which is current_offset)
        //         - total_size (sizeof(AssetHeader) + payload size)
        // Then push it into the 'manifest' vector.
        IndexRecord indexRecord;
        indexRecord.asset_id = header.asset_id;
        indexRecord.original_name = path;
        indexRecord.byte_offset = current_offset;
        indexRecord.total_size = sizeof(AssetHeader) + header.payload_size;//buffer.size();

        manifest.push_back(indexRecord);

        // TODO 2: Update 'current_offset' so the NEXT file knows where it starts.
        current_offset += indexRecord.total_size;
        // HINT: The next offset is current_offset + sizeof(AssetHeader) + payload size.

    }

    blob.close();
    return manifest;
}

// ============================================================================
// Step 2: Instant Random-Access Extraction using mmap()
// ============================================================================
void extract_asset_mmap(const std::string& blob_path, uint64_t byte_offset) {
    std::cout << "\n[MMAP] Attempting direct jump to byte offset: " << byte_offset << "..." << std::endl;

    // TODO 3: Open the blob file using low-level POSIX open()
    // Open in Read-Only mode (O_RDONLY). Store the file descriptor in an int 'fd'.
    // Check if fd < 0 (failed to open).
    int fd = open(blob_path.c_str(), O_RDONLY, 0000);
    if(fd < 0){
        std::cerr << "Blob failed  to open" << "\n";
        return;
    }

    // TODO 4: Find the total size of the blob file on disk.
    // Use the POSIX function: fstat(fd, &sb) where 'struct stat sb' holds file metadata.
    // Store the size in a variable: size_t file_size = sb.st_size;
    struct stat sb;
    if(fstat(fd, &sb) == -1){
        std::cerr << "Failed to get file stats\n";
        close(fd);
        return;
    }
    size_t file_size = sb.st_size;

    // TODO 5: Call mmap() to map the file into virtual address space!
    // Parameters needed for mmap:
    // - Address hint: NULL (let OS choose)
    // - Length: file_size
    // - Memory protection: PROT_READ (read-only)
    // - Flags: MAP_SHARED (or MAP_PRIVATE)
    // - File descriptor: fd
    // - Offset: 0 (map from the beginning)
    // Cast the returned pointer to: char* mapped_data
    char* mapped_data = static_cast<char*>(mmap(nullptr, file_size, PROT_READ, MAP_SHARED, fd, 0));

    // TODO 6: Check if mmap failed.
    // If (mapped_data == MAP_FAILED), print error and close(fd).
    if(mapped_data == MAP_FAILED){
        std::cout << "Error using MMAP\n";
        close(fd);
        return;
    }
    // --- ZERO-COPY EXTRACTION LOGIC ---
    // TODO 7: Create a pointer that points DIRECTLY to the target offset.
    // const char* target_ptr = mapped_data + byte_offset;
    const char* target_ptr = mapped_data + byte_offset;

    // TODO 8: Cast target_ptr to an (const AssetHeader*) to read the 64-byte header.
    // Verify that header->is_valid() is true!
   const AssetHeader* header = reinterpret_cast<const AssetHeader*>(target_ptr);
    if(!header -> is_valid()){
        std::cout << "invalid header\n";
        close(fd);
        munmap(mapped_data, file_size);
        return;
    }

    // TODO 9: Point directly to the payload bytes (which start right after the 64-byte header).
    // Read the string content and print it to the screen!
    const char* payload = target_ptr + sizeof(AssetHeader);
    std::string s(payload, header -> payload_size);
    std::cout << "ID: "  << header -> asset_id << "\n"<<"File Data: " << s << "\n";

    // TODO 10: Clean up resources.
    // - Unmap the memory using munmap(mapped_data, file_size);
    // - Close the file descriptor using close(fd);
    munmap(mapped_data, file_size);
    close(fd);
}

// ============================================================================
// Main
// ============================================================================
int main() {
    // 1. Create 3 test files
    {
        std::ofstream("doc1.txt") << "Document #1: Alpha version dataset specifications.";
        std::ofstream("doc2.txt") << "Document #2: Beta version kernel page table mappings.";
        std::ofstream("doc3.txt") << "Document #3: Gamma version zero-copy latency benchmark.";
    }

    std::vector<std::string> files = {"doc1.txt", "doc2.txt", "doc3.txt"};

    // 2. Pack files and get back our index manifest
    std::vector<IndexRecord> manifest = pack_files_with_index(files, "data.blob");

    // Print our index table
    std::cout << "--- ASSET INDEX MANIFEST ---" << std::endl;
    for (const auto& entry : manifest) {
        std::cout << "ID: " << entry.asset_id 
                  << " | Name: " << entry.original_name 
                  << " | Offset: " << entry.byte_offset 
                  << " | Total Size: " << entry.total_size << " bytes" << std::endl;
    }

    // 3. TEST: Jump directly to Document #3 without touching Document #1 or #2!
    std::cout << "\n>>> EXTRACTING ONLY DOCUMENT #3 DIRECTLY <<<";
    uint64_t doc3_offset = manifest[2].byte_offset;
    extract_asset_mmap("data.blob", doc3_offset);

    return 0;
}
