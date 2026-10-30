"""Shared helpers: connect to Looker and write CSV files."""
import csv
import os

import looker_sdk


def connect(config_file=None):
    """Return a Looker API 4.0 client.

    The credentials file is taken from `config_file`, then the LOOKER_INI
    environment variable, then ./looker.ini (see looker.ini.example).
    """
    config_file = config_file or os.environ.get("LOOKER_INI", "looker.ini")
    return looker_sdk.init40(config_file)


def write_csv(rows, path):
    """Write a list of dicts to `path`. List values are joined with '; '."""
    if not rows:
        print(f"[INFO] No rows to write to {path}")
        return
    columns = list(rows[0].keys())
    with open(path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {k: "; ".join(map(str, v)) if isinstance(v, list) else v for k, v in row.items()}
            )
    print(f"[DONE] Wrote {len(rows)} rows to {path}")
