"""List the model and view files of a LookML project to CSV.

    python export_lookml_files.py --project my_project
    python export_lookml_files.py --project my_project --type view --out views.csv
"""
import argparse

from common import connect, write_csv


def get_project_files(sdk, project, file_type):
    return [
        {"name": f.title, "type": f.type, "path": f.path}
        for f in sdk.all_project_files(project)
        if file_type == "all" or f.type == file_type
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", required=True, help="LookML project id")
    parser.add_argument("--type", choices=["model", "view", "all"], default="all")
    parser.add_argument("--out", default="lookml_files.csv")
    parser.add_argument("--config", help="Path to looker.ini (default: $LOOKER_INI or ./looker.ini)")
    args = parser.parse_args()

    sdk = connect(args.config)
    write_csv(get_project_files(sdk, args.project, args.type), args.out)


if __name__ == "__main__":
    main()
