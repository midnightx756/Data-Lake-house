#ifndef ASSET_HEAER_H
#define ASSET_HEAER_H

#include <cstdint>
#include <cstring>

#pragma pack(push, 1)// To keep 0 padding trash
struct AssetHeader{
    char magic[4]; //SDLH
    uint64_t asset_id; // FIle ID(e.g., 1,2, 3)
    uint64_t payload_size; //
    uint64_t timestamp;
    uint8_t sha256[32];
    uint8_t flags;
    char reserved[3];

    void set_magic(){
        std::memcpy(magic, "SDLH", 4);
    }

    bool is_valid() const {
        return std::memcmp(magic, "SDLH", 4) == 0;
    }
};
#pragma pack(pop)

static_assert(sizeof(AssetHeader) == 64, "Header must be exactly 64 bytes!");

#endif
