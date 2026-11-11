#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <chrono>

#pragma pack(push, 1)
struct AssetHeader {
    char magic[4];
    uint64_t asset_id;
    uint64_t payload_size;
    uint64_t timestamp;
    uint8_t sha256[32];
    uint8_t flags;
    char reserved[3];
};
#pragma pack(pop)
static_assert(sizeof(AssetHeader) == 64, "SDLH header must be 64 bytes");

static bool read_file(const std::string& path, std::vector<char>& bytes) {
    std::ifstream in(path, std::ios::binary | std::ios::ate);
    if (!in) return false;
    auto n = in.tellg();
    if (n < 0) return false;
    bytes.resize(static_cast<size_t>(n));
    in.seekg(0);
    if (!bytes.empty()) in.read(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    return static_cast<bool>(in) || bytes.empty();
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: sdlh_blob pack <blob> <manifest.csv> <file...> | inspect <blob> | extract <blob> <offset> <output>\n";
        return 2;
    }
    const std::string cmd=argv[1];
    if (cmd=="pack") {
        if (argc < 5) { std::cerr << "pack requires blob, manifest, and at least one file\n"; return 2; }
        const std::string blob_path=argv[2], manifest_path=argv[3];
        std::ofstream blob(blob_path,std::ios::binary|std::ios::trunc);
        std::ofstream manifest(manifest_path,std::ios::trunc);
        if(!blob || !manifest){std::cerr<<"Cannot create output files\n";return 3;}
        manifest<<"asset_id,original_name,byte_offset,payload_size,is_duplicate\n";
        uint64_t id=1, offset=0, unique_bytes=0, saved_bytes=0;
        struct Seen { uint64_t offset; uint64_t size; std::vector<char> data; };
        std::vector<Seen> seen;
        for(int i=4;i<argc;i++){
            std::vector<char> data;
            if(!read_file(argv[i],data)){std::cerr<<"Skipping unreadable file: "<<argv[i]<<"\n";continue;}
            uint64_t duplicate_offset=0; bool duplicate=false;
            for(const auto& item:seen) if(item.size==data.size() && item.data==data){duplicate=true;duplicate_offset=item.offset;break;}
            uint64_t item_offset=offset;
            if(!duplicate){
                AssetHeader h{}; std::memcpy(h.magic,"SDLH",4); h.asset_id=id;
                h.payload_size=data.size();
                h.timestamp=static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::seconds>(
                    std::chrono::system_clock::now().time_since_epoch()).count());
                h.flags=0;
                blob.write(reinterpret_cast<const char*>(&h),sizeof(h));
                if(!data.empty()) blob.write(data.data(),static_cast<std::streamsize>(data.size()));
                if(!blob){std::cerr<<"Blob write failed\n";return 4;}
                seen.push_back({item_offset,static_cast<uint64_t>(data.size()),data});
                offset += sizeof(h)+data.size(); unique_bytes+=sizeof(h)+data.size();
            } else { item_offset=duplicate_offset; saved_bytes+=sizeof(AssetHeader)+data.size(); }
            manifest<<id<<",\"";
            for(char c:std::string(argv[i])) { if(c=='"') manifest<<"\"\""; else manifest<<c; }
            manifest<<"\","<<item_offset<<","<<data.size()<<","<<(duplicate?1:0)<<"\n";
            std::cout<<(duplicate?"DEDUP ":"PACKED ")<<argv[i]<<" offset="<<item_offset<<" size="<<data.size()<<"\n";
            id++;
        }
        manifest.close(); blob.close();
        std::cout<<"OK unique_bytes="<<unique_bytes<<" saved_bytes="<<saved_bytes<<"\n";
        return 0;
    }
    if(cmd=="inspect"){
        if(argc<3){std::cerr<<"inspect requires blob\n";return 2;}
        std::ifstream in(argv[2],std::ios::binary|std::ios::ate);
        if(!in){std::cerr<<"Cannot open blob\n";return 3;}
        std::cout<<"blob_bytes="<<in.tellg()<<"\n";
        return 0;
    }
    if(cmd=="extract"){
        if(argc<5){std::cerr<<"extract requires blob offset output\n";return 2;}
        uint64_t off=0;
        try{off=std::stoull(argv[3]);}catch(...){std::cerr<<"Invalid offset\n";return 2;}
        std::ifstream in(argv[2],std::ios::binary|std::ios::ate);
        if(!in){std::cerr<<"Cannot open blob\n";return 3;}
        auto end=in.tellg();
        if(off+sizeof(AssetHeader)>static_cast<uint64_t>(end)){std::cerr<<"Offset outside blob\n";return 4;}
        in.seekg(static_cast<std::streamoff>(off));
        AssetHeader h{}; in.read(reinterpret_cast<char*>(&h),sizeof(h));
        if(!in || std::memcmp(h.magic,"SDLH",4)!=0){std::cerr<<"Invalid SDLH header at offset\n";return 4;}
        if(off+sizeof(h)+h.payload_size>static_cast<uint64_t>(end)){std::cerr<<"Payload extends beyond blob\n";return 4;}
        std::vector<char> data(static_cast<size_t>(h.payload_size));
        if(!data.empty()) in.read(data.data(),static_cast<std::streamsize>(data.size()));
        if(!in && !data.empty()){std::cerr<<"Payload read failed\n";return 4;}
        std::ofstream out(argv[4],std::ios::binary|std::ios::trunc);
        if(!out){std::cerr<<"Cannot create output file\n";return 3;}
        if(!data.empty()) out.write(data.data(),static_cast<std::streamsize>(data.size()));
        std::cout<<"EXTRACTED bytes="<<data.size()<<"\n"; return 0;
    }
    std::cerr<<"Unknown command\n"; return 2;
}
