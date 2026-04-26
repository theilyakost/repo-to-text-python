import os
from pathlib import Path
from typing import List, Optional, Set
import chardet
from tqdm import tqdm

def detect_encoding(file_path: Path) -> str:
    """
    Automatically detects the file encoding using chardet.
    Returns 'utf-8' by default if detection fails.
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(1024 * 10)  # Read first 10KB for detection
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
            confidence = result['confidence']
            if confidence < 0.7:
                encoding = 'utf-8'
            return encoding
    except Exception:
        return 'utf-8'

def is_text_file(file_path: Path, max_size_mb: int = 10, allowed_extensions: Optional[List[str]] = None) -> bool:
    """
    Checks if a file is a text file and matches the allowed extensions.
    - Checks the file size.
    - Checks the extension if a list is provided.
    - Tries to read the file as text.
    """
    if file_path.stat().st_size > max_size_mb * 1024 * 1024:
        return False

    if allowed_extensions and file_path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
        return False
    
    # Exclude known binary extensions
    binary_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf', '.zip', '.exe', '.dll', '.bin', '.img', '.iso', '.webp', '.ttf'}
    if file_path.suffix.lower() in binary_extensions:
        return False

    try:
        with file_path.open('rb') as f:
            sample = f.read(1024)
            if b'\x00' in sample:
                return False
            sample.decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        return False
    return True

def get_all_extensions(directory: str) -> List[str]:
    """
    Collects all unique file extensions in a directory (including subdirectories),
    excluding empty ones (files without an extension) and duplicates.
    Returns a sorted list with '*' at the beginning.
    """
    target_path = Path(directory)
    if not target_path.is_dir():
        return []
    
    extensions_set: Set[str] = set()
    for file_path in target_path.rglob('*'):
        if file_path.is_file() and file_path.suffix:
            extensions_set.add(file_path.suffix.lower())

    all_exts = sorted(list(extensions_set))
    all_exts.insert(0, '*')
    return all_exts

def select_extensions(available_extensions: List[str]) -> List[str]:
    """
    Interactively prompts the user to select file extensions from a list.
    Displays a numbered list and asks for comma-separated numbers.
    """
    if not available_extensions or available_extensions == ['*']:
        return ['*']
    
    print("\nAvailable file extensions in the directory:")
    for i, ext in enumerate(available_extensions, 1):
        print(f"{i}. {ext}")
    
    while True:
        try:
            selection = input("\nSelect extension numbers separated by a comma (e.g., 1,3,5) or 'all' for all: ").strip()
            if selection.lower() == 'all':
                return ['*']
            indices = [int(x.strip()) - 1 for x in selection.split(',') if x.strip().isdigit()]
            if not indices:
                print("Invalid input. Please try again.")
                continue
            selected = [available_extensions[i] for i in indices if 0 <= i < len(available_extensions)]
            if selected:
                return selected
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter numbers.")

def copy_all_text_from_directory(
    directory: str,
    allowed_extensions: List[str],
    exclude_dirs: Optional[List[str]] = None,
    max_file_size_mb: int = 10,
    use_progress_bar: bool = True,
    output_file: str = "all_texts.txt"
):
    """
    Scans all text files in a specified directory (including subdirectories),
    reads their content with automatic encoding detection, and saves everything
    into a single output file.
    
    Args:
    - directory: The path to the directory to scan.
    - allowed_extensions: A list of allowed extensions (e.g., ['.txt', '.py']) or ['*'] for all.
    - exclude_dirs: A list of directory names to exclude from the scan.
    - max_file_size_mb: The maximum size of a file to process in megabytes.
    - use_progress_bar: Whether to display a progress bar.
    - output_file: The name of the file to save the combined text to.
    """
    target_path = Path(directory)
    if not target_path.is_dir():
        print(f"Error: Directory '{directory}' not found.")
        return

    print(f"Starting to scan directory: {target_path.resolve()}")

    if exclude_dirs is None:
        exclude_dirs = []

    all_texts = []
    processed_files_count = 0
    skipped_files_count = 0

    all_files = [f for f in target_path.rglob('*') if f.is_file()]
    if use_progress_bar:
        file_iterator = tqdm(all_files, desc="Processing files", unit="file")
    else:
        file_iterator = all_files

    for file_path in file_iterator:
        rel_path_parts = file_path.relative_to(target_path).parts
        if any(part in exclude_dirs for part in rel_path_parts):
            skipped_files_count += 1
            continue

        if not is_text_file(file_path, max_file_size_mb, None if '*' in allowed_extensions else allowed_extensions):
            skipped_files_count += 1
            continue

        print(f"  -> Processing: {file_path.relative_to(target_path)}")
        try:
            encoding = detect_encoding(file_path)
            with file_path.open('r', encoding=encoding, errors='replace') as f:
                content = f.read()
                
                size_mb = file_path.stat().st_size / (1024 * 1024)
                header = f"--- FILE CONTENT: {file_path.relative_to(target_path)} (encoding: {encoding}, size: {size_mb:.2f} MB) ---\n"
                all_texts.append(header + content)
                processed_files_count += 1

        except Exception as e:
            print(f"     ! Could not read file {file_path.name}. Error: {e}")
            skipped_files_count += 1

    if not all_texts:
        print("\nNo text files found in the directory to copy.")
        return

    final_text = "\n\n".join(all_texts)

    output_path = Path(output_file)
    with output_path.open('w', encoding='utf-8') as f:
        f.write(final_text)

    print("-" * 50)
    print(f"Done! Processed files: {processed_files_count}.")
    print(f"Skipped files: {skipped_files_count} (binary, oversized, wrong extension, or in excluded dirs).")
    print(f"All text saved to file: {output_path.absolute()}")
    total_size_mb = len(final_text.encode('utf-8')) / (1024 * 1024)
    print(f"Total text size: {total_size_mb:.2f} MB")
    print("You can open it in a text editor (like Notepad) to view the contents.")

if __name__ == "__main__":
    while True:
        directory = input("Enter the path to the directory to scan (or press Enter for current): ").strip()
        if not directory:
            directory = "."
        target_path = Path(directory)
        if target_path.is_dir():
            break
        print(f"Error: Directory '{directory}' not found. Please try again.")

    available_extensions = get_all_extensions(directory)
    if not available_extensions or available_extensions == ['*']:
        print("No files with extensions found in the directory. Processing all files.")
        allowed_extensions = ['*']
    else:
        allowed_extensions = select_extensions(available_extensions)

    # Common directories to exclude
    exclude_dirs = [".git", "node_modules", "__pycache__", ".vscode", "venv"]
    max_file_size_mb = 10

    copy_all_text_from_directory(
        directory=directory,
        allowed_extensions=allowed_extensions,
        exclude_dirs=exclude_dirs,
        max_file_size_mb=max_file_size_mb,
        use_progress_bar=True,
        output_file="all_texts.txt"
    )
