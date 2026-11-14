# Test plan
1. Run unit tests: `python -m unittest discover -s tests -v`.
2. Start app: `python main.py`.
3. Scan a small folder with a few .txt/.pdf/image files.
4. Search a unique word present in a text file.
5. Re-scan the folder and verify stable asset count and duplicate flag behavior.
6. Modify/delete a scanned file and run Integrity.
7. Run Benchmark and record machine specs, indexed count, average latency.
