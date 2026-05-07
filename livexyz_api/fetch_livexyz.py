import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to sys.path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from livexyz_api.graphql_fetcher import LiveXYZFetcher
from livexyz_api.graphql_fetcher import _looks_like_jwt
from livexyz_api.graphql_fetcher import _normalize_token


LOGGER = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Fetch LiveXYZ GraphQL API data and write output as "
            "JSONL pages or flattened CSV rows"
        )
    )
    parser.add_argument(
        "--page_count"
        ,type=int
        ,default=1000
        ,help="Items per page to request (pageSize)")
    parser.add_argument(
        "--max_pages"
        ,type=int
        ,default=None
        ,help="Max pages to write; omit to fetch all pages")
    parser.add_argument(
        "--output_format"
        ,type=str
        ,choices=["jsonl", "csv"]
        ,default="jsonl"
        ,help="Output format to write")
    parser.add_argument(
        "--output_path"
        ,type=str
        ,default=None
        ,help="File path for output; defaults by format")
    parser.add_argument(
        "--log_path"
        ,type=str
        ,default=None
        ,help=(
            "Directory or file path for log output. A file named "
            "fetch_livexyz_<timestamp>.log will be created there."
        ))
    return parser.parse_args()


def _timestamped_log_path(log_path):
    parent = Path(log_path)

    # If a file-like path is passed, use its parent directory.
    if parent.suffix:
        parent = parent.parent

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return parent / f"fetch_livexyz_{timestamp}.log"


def _configure_logging(log_path):
    handlers = []
    resolved_log_path = None

    if log_path:
        resolved_log_path = _timestamped_log_path(log_path)
        resolved_log_path.parent.mkdir(parents=True
                                     ,exist_ok=True)
        handlers.append(
            logging.FileHandler(resolved_log_path
                               ,encoding="utf-8")
        )
    else:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO
        ,format=(
            "%(asctime)s %(levelname)s %(name)s - %(message)s"
        )
        ,handlers=handlers
        ,force=True
    )

    return resolved_log_path


def _default_output_path(output_format):
    if output_format == "csv":
        return Path("scratch/livexyz_rows.csv")
    return Path("scratch/livexyz_pages.jsonl")


def _to_csv_value(value):
    if value is None:
        return ""
    if isinstance(value, list) and len(value) == 0:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _flatten_record(record
                   ,parent_key=""
                   ,flat=None):
    if flat is None:
        flat = {}

    if isinstance(record, dict):
        for key, value in record.items():
            next_key = f"{parent_key}.{key}" if parent_key else key
            _flatten_record(value
                           ,next_key
                           ,flat)
        return flat

    if isinstance(record, list):
        flat[parent_key] = _to_csv_value(record)
        return flat

    flat[parent_key] = record
    return flat


KNOWN_CSV_FIELDNAMES = [
    "placeId"
    ,"name"
    ,"resolvedName"
    ,"address"
    ,"postcode"
    ,"lat"
    ,"lon"
    ,"spaceStatus"
    ,"placeStatus"
    ,"hours"
    ,"tel"
    ,"categories"
    ,"categoriesPrimary"
    ,"categoriesPrimary.id"
    ,"categoriesPrimary.name"
    ,"chain"
    ,"chain.chainId"
    ,"chain.name"
    ,"chain.urls.website"
    ,"description"
    ,"emails"
    ,"entrances.main.entranceMethod"
    ,"entrances.main.floor"
    ,"entrances.main.lat"
    ,"entrances.main.lon"
    ,"genericName"
    ,"genericName.id"
    ,"genericName.name"
    ,"isInterior"
    ,"isMobile"
    ,"isStorefront"
    ,"offerings.positive"
    ,"parent"
    ,"parent.name"
    ,"parent.placeId"
    ,"parent.subcategoriesPrimary"
    ,"parent.subcategoriesPrimary.id"
    ,"parent.subcategoriesPrimary.name"
    ,"placeCreationDate"
    ,"slug"
    ,"spaceCreationDate"
    ,"spaceId"
    ,"stateId"
    ,"subcategories"
    ,"subcategoriesPrimary"
    ,"subcategoriesPrimary.id"
    ,"subcategoriesPrimary.name"
    ,"tags"
    ,"tagsPrimary"
    ,"tagsPrimary.id"
    ,"tagsPrimary.name"
    ,"urls.contact"
    ,"urls.facebook"
    ,"urls.instagram"
    ,"urls.liveWeb"
    ,"urls.menu"
    ,"urls.website"
    ,"validityTime.end"
    ,"validityTime.start"
    ,"verifiedTimes"
    ,"verifiedTimesLast"
]


def _pages_label(max_pages):
    if max_pages is None:
        return "all pages"
    return f"up to {max_pages} pages"


def _resolve_auth_inputs():
    token = _normalize_token(os.getenv("LIVEXYZTOKEN"))
    service_name = _normalize_token(
        os.getenv("LIVEXYZ_SERVICE_ACCOUNT_NAME")
    )
    service_key = _normalize_token(
        os.getenv("LIVEXYZ_SERVICE_ACCOUNT_KEY")
    )

    if service_key and not service_name:
        raise SystemExit(
            "LIVEXYZ_SERVICE_ACCOUNT_NAME is required when "
            "LIVEXYZ_SERVICE_ACCOUNT_KEY is set"
        )

    if token and not _looks_like_jwt(token):
        if not service_name:
            raise SystemExit(
                "LIVEXYZTOKEN is not a JWT. If using service-account auth, "
                "set LIVEXYZ_SERVICE_ACCOUNT_NAME and "
                "LIVEXYZ_SERVICE_ACCOUNT_KEY"
            )
        service_key = token
        token = None

    if not token and not service_key:
        raise SystemExit(
            "Set LIVEXYZTOKEN (JWT) or set both "
            "LIVEXYZ_SERVICE_ACCOUNT_NAME and "
            "LIVEXYZ_SERVICE_ACCOUNT_KEY"
        )

    return token, service_name, service_key


def _write_jsonl(fetcher
                ,base_payload
                ,page_count
                ,max_pages
                ,output_path):
    LOGGER.info(
        "Writing JSONL output to %s (%s)"
        ,output_path
        ,_pages_label(max_pages)
    )

    pages_written = 0
    with open(output_path
             ,"w"
             ,encoding="utf-8") as out_f:
        for page in fetcher.iter_pages(base_payload
                                      ,page_count
                                      ,max_pages):
            out_f.write(json.dumps(page, ensure_ascii=False))
            out_f.write("\n")
            pages_written += 1

            if pages_written % 10 == 0:
                LOGGER.info("Written %d pages so far", pages_written)

    LOGGER.info("Written %d pages to %s", pages_written, output_path)


def _write_csv(fetcher
              ,base_payload
              ,page_count
              ,max_pages
              ,output_path):
    LOGGER.info(
        "Writing CSV output to %s (%s)"
        ,output_path
        ,_pages_label(max_pages)
    )

    nodes_written = 0
    unknown_fields_warned = set()

    with open(output_path
             ,"w"
             ,encoding="utf-8"
             ,newline="") as out_f:
        writer = csv.DictWriter(out_f
                               ,KNOWN_CSV_FIELDNAMES
                               ,extrasaction="ignore")
        writer.writeheader()

        for node in fetcher.iter_nodes(base_payload
                                      ,page_count
                                      ,max_pages):
            row = _flatten_record(node)

            main_entrance = (
                node.get("entrances", {})
                    .get("main", {})
            )
            row["lat"] = main_entrance.get("lat")
            row["lon"] = main_entrance.get("lon")

            unknown = (
                row.keys() - set(KNOWN_CSV_FIELDNAMES)
            )
            for field in unknown - unknown_fields_warned:
                LOGGER.warning(
                    "Unknown field dropped from CSV: %s"
                    ,field
                )
            unknown_fields_warned.update(unknown)

            writer.writerow(
                {
                    key: _to_csv_value(row.get(key))
                    for key in KNOWN_CSV_FIELDNAMES
                }
            )
            nodes_written += 1

            if nodes_written % 5000 == 0:
                LOGGER.info(
                    "Written %d rows to CSV"
                    ,nodes_written
                )

    LOGGER.info(
        "Written %d rows from %s to %s"
        ,nodes_written
        ,_pages_label(max_pages)
        ,output_path
    )


def main():
    args = parse_args()
    resolved_log_path = _configure_logging(args.log_path)

    if resolved_log_path:
        LOGGER.info("File logging enabled: %s", resolved_log_path)

    output_path = (
        Path(args.output_path)
        if args.output_path
        else _default_output_path(args.output_format)
    )

    LOGGER.info(
        "Starting fetch with format=%s page_size=%d max_pages=%s"
        ,args.output_format
        ,args.page_count
        ,"ALL" if args.max_pages is None else args.max_pages
    )

    if output_path.exists():
        LOGGER.info("Removing existing output file: %s", output_path)
        output_path.unlink()

    output_path.parent.mkdir(parents=True
                            ,exist_ok=True)

    token, service_name, service_key = _resolve_auth_inputs()

    if service_key:
        LOGGER.info(
            "Authenticating with service account name %s"
            ,service_name
        )
    else:
        LOGGER.info("Authenticating with JWT token")

    fetcher = LiveXYZFetcher(token
                            ,None
                            ,service_name
                            ,service_key)

    base_payload = {}

    if args.output_format == "csv":
        _write_csv(fetcher
                  ,base_payload
                  ,args.page_count
                  ,args.max_pages
                  ,output_path)
    else:
        _write_jsonl(fetcher
                    ,base_payload
                    ,args.page_count
                    ,args.max_pages
                    ,output_path)

    LOGGER.info("Fetch complete")


if __name__ == "__main__":
    main()