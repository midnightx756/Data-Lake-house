#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <cstring>
#include <chrono>

// POSIX System Calls for Resizing and Memory-Mapping
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include "asset_header.h"

// Simple 64-bit FNV-1a Hash
uint64_t compute_hash(const std::string& data) {
    uint64_t hash = 14695981039346656037ULL;
    for (char c : data) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 1099511628211ULL;
    }
    return hash;
}

// ============================================================================
// Core Module: In-Place Shift Updater (Your Algorithm!)
// ============================================================================
bool update_asset_payload(const std::string& blob_path, 
                          uint64_t target_offset, 
                          const std::string& new_payload) {

    std::cout << "\n[UPDATER] Initiating update at Offset " << target_offset << "..." << std::endl;

    // 1. Open blob in READ & WRITE mode (O_RDWR)
    int fd = open(blob_path.c_str(), O_RDWR);
    if (fd < 0) {
        std::cerr << "Error: Could not open blob for update!" << std::endl;
        return false;
    }

    // 2. Get current file size
    struct stat sb;
    if (fstat(fd, &sb) == -1) {
        close(fd);
        return false;
    }
    size_t old_file_size = sb.st_size;

    // 3. Map the file temporarily to read the old header
    char* initial_map = static_cast<char*>(mmap(NULL, old_file_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));
    if (initial_map == MAP_FAILED) {
        close(fd);
        return false;
    }

    AssetHeader* old_header = reinterpret_cast<AssetHeader*>(initial_map + target_offset);
    if (!old_header->is_valid()) {
        std::cerr << "Error: Invalid header at target offset!" << std::endl;
        munmap(initial_map, old_file_size);
        close(fd);
        return false;
    }

    uint64_t old_payload_size = old_header->payload_size;
    uint64_t new_payload_size = new_payload.size();
    int64_t delta = static_cast<int64_t>(new_payload_size) - static_cast<int64_t>(old_payload_size);

    std::cout << "[UPDATER] Old Size: " << old_payload_size << " B | New Size: " << new_payload_size << " B" << std::endl;
    std::cout << "[UPDATER] Calculated Delta (Shift Distance): " << delta << " Bytes" << std::endl;

    // Unmap before resizing the physical file
    munmap(initial_map, old_file_size);

    // ========================================================================
    // CASE 1: File size is IDENTICAL (delta == 0)
    // ========================================================================
    if (delta == 0) {
        std::cout << "[UPDATER] Delta is 0. Performing exact in-place overwrite..." << std::endl;
        char* map = static_cast<char*>(mmap(NULL, old_file_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));
        
        // Overwrite payload bytes
        std::memcpy(map + target_offset + sizeof(AssetHeader), new_payload.data(), new_payload_size);
        
        // Update header
        AssetHeader* hdr = reinterpret_cast<AssetHeader*>(map + target_offset);
        hdr->timestamp = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count();
        
        msync(map, old_file_size, MS_SYNC);
        munmap(map, old_file_size);
        close(fd);
        return true;
    }

    // ========================================================================
    // CASE 2: File GREW (delta > 0) -> Your Backward Shift Algorithm!
    // ========================================================================
    if (delta > 0) {
        size_t new_file_size = old_file_size + delta;

        // TODO 1: Resize the physical file on disk using ftruncate()
        ftruncate(fd, new_file_size);
        // HINT: ftruncate(fd, new_file_size);

        // TODO 2: Map the EXPANDED file into virtual memory
        char* pp = static_cast<char*>(mmap(nullptr, new_file_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));
        if(pp == MAP_FAILED){
            close(fd);
            return false;
        }
        // HINT: Call mmap() with new_file_size and PROT_READ | PROT_WRITE

        // Calculate boundaries:
        // 'shift_start' is where the subsequent assets begin (right after old payload)
        uint64_t shift_src_start = target_offset + sizeof(AssetHeader) + old_payload_size;
        uint64_t bytes_to_shift = old_file_size - shift_src_start;
        uint64_t shift_dst_start = shift_src_start + delta;

        // TODO 3: Perform the Backward Shift using std::memmove!
        std::memmove(pp + shift_dst_start, pp + shift_src_start, bytes_to_shift);

        // HINT: std::memmove(mapped_ptr + shift_dst_start, mapped_ptr + shift_src_start, bytes_to_shift);
        // Notice: memmove safely handles overlapping memory!

        // TODO 4: Write the new payload into the carved space!
        std::memcpy(pp + target_offset + sizeof(AssetHeader), new_payload.data(), new_payload_size);
        // HINT: std::memcpy(mapped_ptr + target_offset + sizeof(AssetHeader), new_payload.data(), new_payload_size);

        // TODO 5: Update target AssetHeader fields:
        // - payload_size = new_payload_size
        // - timestamp = current time
        // - sha256 = new computed hash
        AssetHeader* hdr = reinterpret_cast<AssetHeader*>(pp + target_offset);
        hdr -> payload_size = new_payload_size;
        hdr -> timestamp = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count();
        uint64_t rockstar = compute_hash(new_payload);
        std::memset(  hdr -> sha256, 0, 32);
        std::memcpy(hdr -> sha256, &rockstar, sizeof(uint64_t));

        // TODO 6: Flush changes to disk using msync() and clean up (munmap, close)!
        msync(pp, new_file_size, MS_SYNC);
        munmap(pp, new_file_size);
        close(fd);
        return true;
    }

    return true;
}

// ============================================================================
// Verification Helper: Reads all assets from blob and prints them
// ============================================================================
void inspect_blob(const std::string& blob_path) {
    int fd = open(blob_path.c_str(), O_RDONLY);
    if (fd < 0) return;
    struct stat sb;
    fstat(fd, &sb);
    char* map = static_cast<char*>(mmap(NULL, sb.st_size, PROT_READ, MAP_SHARED, fd, 0));

    std::cout << "\n--- CURRENT BLOB CONTENTS (Total Size: " << sb.st_size << " B) ---" << std::endl;
    uint64_t offset = 0;
    while (offset < static_cast<uint64_t>(sb.st_size)){
        const AssetHeader* hdr = reinterpret_cast<const AssetHeader*>(map + offset);
        if (!hdr->is_valid()) {
            std::cerr << "[CORRUPTION] Invalid header at offset " << offset << "!" << std::endl;
            break;
        }
        std::string payload(map + offset + sizeof(AssetHeader), hdr->payload_size);
        std::cout << "Offset " << offset << " | Asset ID: " << hdr->asset_id 
                  << " | Size: " << hdr->payload_size << " B | Content: \"" << payload << "\"" << std::endl;
        
        offset += sizeof(AssetHeader) + hdr->payload_size;
    }
    munmap(map, sb.st_size);
    close(fd);
}

/*
// ============================================================================
// Main
// ============================================================================
int main() {
    std::string blob_path = "update_test.blob";

    // 1. Create a fresh test blob with 3 assets
    {
        std::ofstream blob(blob_path, std::ios::binary);
        
        // Asset 1 (Will be updated!)
        AssetHeader h1{}; h1.set_magic(); h1.asset_id = 1; 
        std::string p1 = "Short string 1."; h1.payload_size = p1.size();
        blob.write(reinterpret_cast<char*>(&h1), 64);
        blob.write(p1.data(), p1.size());

        // Asset 2 (Neighbor)
        AssetHeader h2{}; h2.set_magic(); h2.asset_id = 2; 
        std::string p2 = "Neighboring Asset #2."; h2.payload_size = p2.size();
        blob.write(reinterpret_cast<char*>(&h2), 64);
        blob.write(p2.data(), p2.size());

        // Asset 3 (Tail)
        AssetHeader h3{}; h3.set_magic(); h3.asset_id = 3; 
        std::string p3 = "Tail Asset #3 standing at the end."; h3.payload_size = p3.size();
        blob.write(reinterpret_cast<char*>(&h3), 64);
        blob.write(p3.data(), p3.size());
    }

    // Inspect initial state
    inspect_blob(blob_path);

    // 2. Perform the Update! Asset 1 grows significantly!
    std::string larger_payload = "This is a MUCH LARGER updated payload for Asset 1 that triggers our backward shift algorithm!";
    
    // Target offset 0 (Asset 1)
    update_asset_payload(blob_path, 0, larger_payload);

    // 3. Inspect final state to prove Asset 2 and Asset 3 survived uncorrupted!
    inspect_blob(blob_path);

    return 0;
}
*/
