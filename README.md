#HandBrake Automation Script

A Python-based automation tool that batch processes video files using HandBrakeCLI.  
It scans a directory, compresses videos one-by-one (or in parallel), outputs them to a separate folder, and safely removes originals after successful encoding.

---

##Features

- 📂 Automatically scans an input directory for video files
- ⚙️ Uses HandBrakeCLI for high-quality compression
- ⚡ Optional parallel processing for faster encoding
- 🧹 Automatically moves processed files to a separate folder
- 🗑️ Safely deletes originals only after successful compression
- 📜 Logs all operations for tracking and debugging
- 🚫 Skips already processed files to avoid duplication
