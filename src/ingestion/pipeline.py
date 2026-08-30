"""
pipeline.py

End-to-end ingestion pipeline orchestrator.
Discovers raw files, parses all formats, cleans text, splits into chunks,
assigns unique chunk IDs, and saves output artifacts to data/processed/.
"""

import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any

from tqdm import tqdm

from src.logger import get_logger
from src.ingestion.loader import discover_files
from src.ingestion.parser import parse_file
from src.ingestion.cleaner import clean_document
from src.ingestion.chunker import chunk_document, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR

logger = get_logger(__name__)


def generate_chunk_id(chunk: Dict[str, Any]) -> str:
    """
    Generates a deterministic unique ID for each chunk based on:
    source_file + chunk_index + content hash (SHA-256).
    
    Format: <source_file_name>#chunk_<idx>#<short_hash>
    Example: kyc_policy.pdf#chunk_0#a3f89b1c
    """
    source_file = chunk.get("source_file", "unknown")
    chunk_index = chunk.get("chunk_index", 0)
    text = chunk.get("text", "")

    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
    return f"{source_file}#chunk_{chunk_index}#{content_hash}"


def run_ingestion_pipeline(
    raw_dir: Path = RAW_DATA_DIR,
    output_dir: Path = PROCESSED_DATA_DIR,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Runs the complete document ingestion pipeline:
    1. Discovers all files in raw_dir
    2. Parses each file based on its extension
    3. Cleans and normalizes text
    4. Splits documents into overlapping chunks
    5. Assigns unique chunk IDs
    6. Saves all chunks into data/processed/chunks.json

    Returns:
        List of all processed chunk dictionaries.
    """
    logger.info("=" * 60)
    logger.info("STARTING DOCUMENT INGESTION PIPELINE")
    logger.info("=" * 60)

    # 1. Discover files
    files = discover_files(raw_dir)
    if not files:
        logger.warning(f"No files found to ingest in {raw_dir}")
        return []

    all_chunks: List[Dict[str, Any]] = []
    failed_files: List[str] = []
    processed_count = 0

    # Ensure output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process files with progress bar
    for file_info in tqdm(files, desc="Ingesting Documents"):
        file_name = file_info["file_name"]
        try:
            # 2. Parse file
            raw_doc = parse_file(file_info)
            if not raw_doc or not raw_doc.get("text"):
                logger.warning(f"Skipping empty or unparseable file: {file_name}")
                failed_files.append(file_name)
                continue

            # 3. Clean document
            cleaned_doc = clean_document(raw_doc)

            # 4. Chunk document
            doc_chunks = chunk_document(
                cleaned_doc,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

            # 5. Assign unique IDs to each chunk
            for chunk in doc_chunks:
                chunk["chunk_id"] = generate_chunk_id(chunk)
                all_chunks.append(chunk)

            processed_count += 1

        except Exception as e:
            logger.error(f"Error processing {file_name}: {e}", exc_info=True)
            failed_files.append(file_name)

    # 6. Save chunks to disk as JSON
    output_file = output_dir / "chunks.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    logger.info("=" * 60)
    logger.info("INGESTION PIPELINE COMPLETED")
    logger.info(f"Total files discovered : {len(files)}")
    logger.info(f"Successfully processed  : {processed_count}")
    logger.info(f"Failed / Skipped        : {len(failed_files)}")
    logger.info(f"Total chunks generated  : {len(all_chunks)}")
    logger.info(f"Artifact saved to       : {output_file}")
    logger.info("=" * 60)

    return all_chunks


if __name__ == "__main__":
    run_ingestion_pipeline()
