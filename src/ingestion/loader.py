"""
loader.py

Responsible for discovering files in the raw data directory.
Does NOT extract text — that is the parser's job.
Returns a list of FileInfo dictionaries describing each discovered file.
"""

from pathlib import Path
from typing import List, Dict, Any

from src.logger import get_logger
from config import RAW_DATA_DIR

logger = get_logger(__name__)

# The file extensions we know how to handle.
# Any file NOT in this set will be skipped with a warning.
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".md", ".txt",
    ".csv", ".json", ".ndjson", ".yaml", ".yml", ".html"
}


def discover_files(directory: Path = RAW_DATA_DIR) -> List[Dict[str, Any]]:
    """
    Walks the given directory and returns metadata for every supported file.

    Each item in the returned list is a dictionary with:
        - file_path : full absolute Path object
        - file_name : just the filename e.g. 'upi_integration_guide.pdf'
        - extension : lowercase extension e.g. '.pdf'
        - size_bytes : file size in bytes

    Args:
        directory: Path to scan. Defaults to RAW_DATA_DIR from config.

    Returns:
        List of file metadata dictionaries, sorted by filename.
    """
    directory = Path(directory)

    if not directory.exists():
        logger.error(f"Directory does not exist: {directory}")
        return []

    if not directory.is_dir():
        logger.error(f"Path is not a directory: {directory}")
        return []

    logger.info(f"Scanning directory: {directory}")

    discovered = []
    skipped = []

    # Path.rglob("*") walks ALL files in the directory and subdirectories.
    # We use rglob so future subdirectories inside data/raw/ are also handled.
    for file_path in sorted(directory.rglob("*")):

        # Skip subdirectories — we only want files
        if not file_path.is_file():
            continue

        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            skipped.append(file_path.name)
            continue

        file_info: Dict[str, Any] = {
            "file_path": file_path,
            "file_name": file_path.name,
            "extension": extension,
            "size_bytes": file_path.stat().st_size,
        }

        discovered.append(file_info)

    # Summary logging
    logger.info(f"Discovered {len(discovered)} supported file(s)")

    if skipped:
        logger.warning(f"Skipped {len(skipped)} unsupported file(s): {skipped}")

    return discovered
