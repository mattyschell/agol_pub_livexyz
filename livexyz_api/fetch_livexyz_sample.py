import argparse
import json
import os
import sys
from pathlib import Path

# Add parent directory to sys.path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from livexyz_api.graphql_fetcher import LiveXYZFetcher

def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch pages from LiveXYZ GraphQL API")
    parser.add_argument(
        "--page_count"
        ,type=int
        ,default=1000
        ,help="Items per page to request (pageSize)")
    parser.add_argument(
        "--max_pages"
        ,type=int
        ,default=5
        ,help="Max pages to write before stopping")
    parser.add_argument(
        "--output_path"
        ,type=str
        ,default="scratch/response_pages.jsonl"
        ,help="File path for JSONL output")
    return parser.parse_args()

def main():
    args = parse_args()
    output_path = Path(args.output_path)

    if output_path.exists():
        output_path.unlink()

    output_path.parent.mkdir(parents=True
                           ,exist_ok=True)

    token = os.getenv("LIVEXYZTOKEN")
    if token:
        token = token.strip()
        if token.startswith('"') and token.endswith('"'):
            token = token[1:-1].strip()
        if token.lower().startswith("bearer "):
            token = token[7:].strip()

    if not token:
        raise SystemExit(
            "LIVEXYZTOKEN environment variable is required")

    fetcher = LiveXYZFetcher(token)

    base_payload = {
        "validityTime": {
            "lte": "2016-03-03T00:00:00Z"
        }
    }

    written = 0
    with open(output_path, "a", encoding="utf-8") as out_f:
        for page in fetcher.fetch_paginated(base_payload
                                           ,args.page_count):
            out_f.write(json.dumps(page, ensure_ascii=False))
            out_f.write("\n")
            written += 1
            if written >= args.max_pages:
                break

    print(f"Written {written} pages to {output_path}")

if __name__ == "__main__":
    main()