"""Build a verified chunk snapshot with recorded retrieval eligibility."""

import argparse
from pathlib import Path

from app.chunking.snapshot import save_chunk_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("../data/chunks/corpus"))
    parser.add_argument("--max-tokens", type=int, default=512)
    args = parser.parse_args()

    try:
        destination, summary, reused = save_chunk_snapshot(
            args.snapshot.resolve(),
            args.output.resolve(),
            max_tokens=args.max_tokens,
        )
    except (OSError, ValueError) as error:
        parser.exit(1, f"Chunking failed: {error}\n")

    print("Normalized documents:", summary["normalized_documents"])
    print("Chunk records:", summary["chunk_records"])
    print("Eligible:", summary["eligible_chunk_records"])
    print("Metadata-only:", summary["metadata_only_chunk_records"])
    print("Largest chunk tokens:", summary["largest_chunk_tokens"])
    print("Snapshot reused:", reused)
    print("Snapshot ID:", destination.name)
    print("Saved:", destination)


if __name__ == "__main__":
    main()
