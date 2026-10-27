#include <iostream>
#include <string>
#include <vector>
#include "asset_header.h"

//Declarations
void pack_files(const std:;vector<std::string>& filepaths, const std::string&blob_path, const std::string& manifest_path);
void extracat_asset_mmap(const std::string& blob)path, uint64_t offset);
bool update asset_payload(const std::string& blob_path, uint64_t offset, const std:: string& new_payload);


