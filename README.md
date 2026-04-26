# Repo to Text (Python CLI)

A command-line utility designed to scan a local directory and aggregate all source code and text files into a single, structured document. This is ideal for generating context for LLMs (like ChatGPT or Claude) or performing a full project audit.

## Features

- **Recursive Scanning:** Automatically traverses subdirectories to find files.
- **Interactive Extension Selection:** Scans your directory first and lets you choose which file types (e.g., `.py`, `.js`, `.md`) to include.
- **Smart Encoding Detection:** Uses the `chardet` library to handle various file encodings automatically.
- **Binary & Size Filters:** 
  - Automatically skips binary files (images, executables, etc.).
  - Filters out files larger than a specified limit (default 10MB).
- **Default Exclusions:** Pre-configured to ignore common folders like `.git`, `node_modules`, `__pycache__`, and `venv`.
- **Progress Feedback:** Uses `tqdm` to show a progress bar during processing.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/theilyakost/repo-to-text-python.git
   cd repo-to-text-python
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script from your terminal:

```bash
python main.py
```

1. **Path:** Enter the directory path you want to scan.
2. **Extensions:** Select specific file extensions from the generated list or type `all`.
3. **Output:** The script will generate a file named `all_texts.txt` containing the combined content with clear headers for each file path.

## Requirements

- `chardet`: For character encoding detection.
- `tqdm`: For the progress bar UI.

## Note on Rust Version
This is the Python CLI implementation. A separate repository featuring a **Rust GUI version** is currently planned to provide better performance and a graphical user interface.

## License

This project is licensed under the MIT License.
