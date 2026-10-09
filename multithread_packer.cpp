#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>

#include "asset_header.h"

// 64-bit FNV-1a Hash function
uint64_t compute_fnv1a_hash(const std::vector<char>& data) {
    uint64_t hash = 14695981039346656037ULL;
    for (char byte : data) {
        hash ^= static_cast<uint8_t>(byte);
        hash *= 1099511628211ULL;
    }
    return hash;
}

// Struct holding the processed result from a worker thread
struct ProcessedFile {
    std::string path;
    uint64_t content_hash;
    std::vector<char> buffer;
};

// ============================================================================
// Thread-Safe Task Queue for Producer-Consumer Pattern
// ============================================================================
class SafeQueue {
private:
    std::queue<std::string> queue_;
    std::mutex mutex_;
    std::condition_variable cv_;
    bool finished_ = false;

public:
    // Producer pushes files
    void push(const std::string& item) {
        // TODO 1: Lock the mutex using std::lock_guard<std::mutex>
        // Push the item into queue_
        // Notify one waiting worker using cv_.notify_one()
        std::lock_guard<std::mutex>lock(mutex_);
        queue_.push(item);
        cv_.notify_one();
    }

    // Signals workers that no more files will be added
    void set_finished() {
        std::lock_guard<std::mutex> lock(mutex_);
        finished_ = true;
        cv_.notify_all(); // Wake up ALL sleeping workers so they can exit cleanly
    }

    // Consumer worker pops a file
    bool pop(std::string& item) {
        // TODO 2: Acquire a unique_lock on the mutex: std::unique_lock<std::mutex> lock(mutex_);
        std::unique_lock<std::mutex> lock(mutex_);
        // Wait until queue is NOT empty OR finished_ is true using cv_.wait(lock, ...)
        cv_.wait(lock, [&]{return !queue_.empty() || finished_;});
        // If queue is empty and finished_ is true, return false (work is done!)
        if(queue_.empty() && finished_)
            return false;
        // Otherwise, pop the front item into 'item' and return true
        else{
            item = queue_.front();
            queue_.pop();
            return true; // Replace this with your logic
        }
    }
};

// ============================================================================
// Worker Thread Function (Executed concurrently across CPU cores)
// ============================================================================
void worker_task(int thread_id, SafeQueue& task_queue, 
                 std::vector<ProcessedFile>& results, std::mutex& results_mutex) {
    
    std::string file_path;

    // Keep pulling files from the queue until it is finished
    while (task_queue.pop(file_path)) {
        // 1. Read file bytes
        std::ifstream file(file_path, std::ios::binary | std::ios::ate);
        if (!file){
            std::cout << file_path << " Not found\n";
            continue;
        }
        std::streamsize size = file.tellg();
        file.seekg(0, std::ios::beg);
        std::vector<char> buffer(size);
        file.read(buffer.data(), size);

        // 2. Compute hash in parallel (Heavy CPU work!)
        uint64_t hash = compute_fnv1a_hash(buffer);

        ProcessedFile result{file_path, hash, std::move(buffer)};

        // TODO 3: Safely push 'result' into the shared 'results' vector.
        std::lock_guard<std::mutex> lock(results_mutex);
        results.push_back(result);
        // HINT: Protect 'results.push_back()' with 'results_mutex' using std::lock_guard!

        std::cout << "[Thread " << thread_id << "] Processed: " << file_path 
                  << " (Hash: " << hash << ")" << std::endl;
    }
}

// ============================================================================
// Main Execution: Spawns Thread Pool
// ============================================================================
int main() {
    // 1. Create 6 dummy test files
    for (int i = 1; i <= 6; ++i) {
        std::ofstream("batch_file_" + std::to_string(i) + ".txt") 
            << "Data payload for parallel processing test item #" << i;
    }

    SafeQueue task_queue;
    std::vector<ProcessedFile> shared_results;
    std::mutex results_mutex;

    // 2. Spawn 3 Worker Threads
    const int NUM_THREADS = 3;
    std::vector<std::thread> thread_pool;
    
    std::cout << "--- SPAWNING THREAD POOL (" << NUM_THREADS << " THREADS) ---" << std::endl;
    for (int i = 0; i < NUM_THREADS; ++i) {
        // TODO 4: Spawn a thread running worker_task and push it into thread_pool
        thread_pool.emplace_back(worker_task, i+1 , std::ref(task_queue) , std::ref(shared_results), std::ref(results_mutex));
        // HINT: thread_pool.emplace_back(worker_task, i + 1, std::ref(task_queue), 
        //                                std::ref(shared_results), std::ref(results_mutex));
    }

    // 3. Producer (Main thread) pushes 6 files into the queue
    std::cout << "\n[Producer] Adding files to task queue..." << std::endl;
    for (int i = 1; i <= 6; ++i) {
        task_queue.push("batch_file_" + std::to_string(i) + ".txt");
    }

    // Signal workers that all files have been queued
    task_queue.set_finished();

    // TODO 5: Wait for all worker threads to finish using t.join() in a loop!
    for(auto &t : thread_pool)
            t.join();

    std::cout << "\n==========================================" << std::endl;
    std::cout << "[SUCCESS] Parallel Ingestion Complete!" << std::endl;
    std::cout << "Total Files Processed by Thread Pool: " << shared_results.size() << std::endl;
    std::cout << "==========================================" << std::endl;

    return 0;
}
