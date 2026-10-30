"""Find dashboard tiles that use a given view or field.

Answers "what breaks if I rename or remove this field?" before a LookML change.
Regular tiles, Look-based tiles and merged-query tiles are all covered.

    python search_dashboards_by_field.py --keyword fact_consumption --keyword churn
    python search_dashboards_by_field.py --keyword hours --dashboard "My Dashboard" \\
        --folder-parent-id 12 --folder-parent-id 34 --out-dir results
"""
import argparse
import os

from common import connect, write_csv

RED, BLUE, GREEN, YELLOW, RESET = "\033[91m", "\033[94m", "\033[92m", "\033[93m", "\033[0m"
ERROR, RUN, INFO, DONE = (f"{c}[{t}]{RESET}" for c, t in
                          ((RED, "ERROR"), (BLUE, "RUN"), (YELLOW, "INFO"), (GREEN, "DONE")))


def get_dashboards(sdk, title=None, folder_parent_ids=None):
    """Dashboards, optionally filtered by exact title and by parent folder ids."""
    print(f"{RUN} Getting dashboards...")
    dashboards = []
    for d in sdk.all_dashboards():
        if title is not None and d.title != title:
            continue
        parent_id = d.folder.parent_id if d.folder else None
        if folder_parent_ids and (parent_id is None or int(parent_id) not in folder_parent_ids):
            continue
        dashboards.append(
            {
                "Dashboard ID": d.id,
                "Dashboard Title": d.title,
                "Folder": d.folder.name if d.folder else None,
                "Folder Parent ID": parent_id,
            }
        )
    print(f"{DONE} Found {len(dashboards)} dashboards")
    return dashboards


def tile_fields(sdk, element):
    """All fields used by a dashboard element, or None if it has no query."""
    if element.merge_result_id is not None:
        fields = []
        for source in sdk.merge_query(element.merge_result_id).source_queries:
            fields += sdk.query(source.query_id).fields
        return sorted(set(fields))
    if element.query is not None:
        return element.query.fields
    if element.look is not None:
        return element.look.query.fields
    return None


def get_tiles(sdk, dashboards):
    print(f"{RUN} Getting tiles...")
    tiles = []
    for d in dashboards:
        try:
            elements = sdk.dashboard_dashboard_elements(d["Dashboard ID"])
        except Exception as exc:  # keep going if one dashboard is not readable
            print(f"{ERROR} Could not read elements of {d['Dashboard Title']}: {exc}")
            continue
        for e in elements:
            if e.type == "text":
                continue
            fields = tile_fields(sdk, e)
            if fields is None:
                continue
            tiles.append({**d, "Tile ID": e.id, "Tile Title": e.title, "Fields": fields})
    print(f"{DONE} Found {len(tiles)} tiles")
    return tiles


def search_tiles(tiles, keyword):
    """Tiles with at least one field containing `keyword`, keeping only matching fields."""
    matches = []
    for tile in tiles:
        matching_fields = [f for f in tile["Fields"] if keyword in f]
        if matching_fields:
            matches.append({**tile, "Fields": matching_fields})
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--keyword", action="append", required=True,
                        help="View or field substring to look for (repeatable)")
    parser.add_argument("--dashboard", help="Only this dashboard title (exact match)")
    parser.add_argument("--folder-parent-id", type=int, action="append",
                        help="Only dashboards under these parent folder ids (repeatable)")
    parser.add_argument("--out-dir", default=".")
    parser.add_argument("--config", help="Path to looker.ini (default: $LOOKER_INI or ./looker.ini)")
    args = parser.parse_args()

    sdk = connect(args.config)
    tiles = get_tiles(sdk, get_dashboards(sdk, args.dashboard, args.folder_parent_id))

    os.makedirs(args.out_dir, exist_ok=True)
    for keyword in args.keyword:
        print(f"{RUN} Searching for '{keyword}'")
        matches = search_tiles(tiles, keyword)
        if not matches:
            print(f"{INFO} No tiles use '{keyword}'")
            continue
        write_csv(matches, os.path.join(args.out_dir, f"search_results_for_{keyword}.csv"))


if __name__ == "__main__":
    main()
