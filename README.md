# Looker admin scripts

Small, read-only Python scripts for administering a Looker instance through the
[Looker SDK](https://github.com/looker-open-source/sdk-codegen).

## Why

As a LookML project grows, two questions come up constantly:

1. **What does the semantic layer actually expose?** Which explores exist, what
   do they join, and which are hidden?
2. **What breaks if I rename or remove this field?** Which dashboards and tiles
   depend on it?

Looker's UI answers these one dashboard at a time. These scripts answer them
for the whole instance in one run and write the result to CSV, so the output
can be filtered in a spreadsheet or loaded into a warehouse.

## Scripts

| Script | What it does | Output |
|---|---|---|
| `export_explores.py` | Inventory of every explore: model, label, description, hidden flag, group label, joins and tags | `explores.csv` |
| `export_lookml_files.py` | Lists the model and view files of a LookML project | `lookml_files.csv` |
| `search_dashboards_by_field.py` | Finds dashboard tiles that use a given view or field. Covers query tiles, Look-based tiles and merged-query tiles | `search_results_for_<keyword>.csv` |

`common.py` holds the shared connection and CSV helpers.

## Setup

Requires Python 3.9+ and a Looker API3 key (Admin → Users → Edit keys). The
key's user needs permission to view models, dashboards and project files.

```bash
pip install -r requirements.txt
cp looker.ini.example looker.ini   # add your own base_url and API credentials
```

Credentials are read from `looker.ini` in the current directory, from the path
in the `LOOKER_INI` environment variable, or from `--config`.

> `looker.ini` and generated CSV files are in `.gitignore`. Never commit them.
> The CSVs describe your instance's models and dashboards.

## Usage

```bash
# Inventory of all explores
python export_explores.py --out explores.csv

# All view files of one LookML project
python export_lookml_files.py --project my_project --type view --out views.csv

# Which tiles use these views or fields?
python search_dashboards_by_field.py --keyword fact_orders --keyword churn

# Restrict to one dashboard, or to dashboards under specific parent folders
python search_dashboards_by_field.py --keyword revenue \
    --dashboard "Revenue Overview" --folder-parent-id 12 --folder-parent-id 34
```

Example output of `search_dashboards_by_field.py`:

| Dashboard Title | Folder | Tile Title | Fields |
|---|---|---|---|
| Revenue Overview | Finance | Monthly revenue | fact_orders.revenue; fact_orders.order_month |

## How it works

`search_dashboards_by_field.py` lists dashboards, fetches each dashboard's
elements, and collects the fields from every tile's query. For merged-query
tiles it follows each source query and combines their fields. It then keeps the
tiles where any field contains the keyword. Dashboards that can't be read are
reported and skipped instead of stopping the run.

## Limitations

- Keyword matching is a substring match on the full field name
  (`view.field`), so `orders` also matches `fact_orders.revenue`. Use a more
  specific keyword if you need an exact view or field.
- Only dashboard tiles are searched. Standalone Looks and scheduled plans are
  not included.
- Large instances make one API call per dashboard and per explore, so the first
  run can take a few minutes.

All scripts only read from the API. They don't change anything in Looker.
