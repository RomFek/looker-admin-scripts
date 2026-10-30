"""Export every explore in the instance (with its joins and tags) to a CSV.

Useful as an inventory of the semantic layer: what is exposed, what is hidden,
and which views each explore joins.

    python export_explores.py --out explores.csv
"""
import argparse

from common import connect, write_csv


def get_explores(sdk):
    explores = []
    for model in sdk.all_lookml_models():
        if not model.has_content or not model.explores:
            continue
        for explore in model.explores:
            details = sdk.lookml_model_explore(model.name, explore.name)
            explores.append(
                {
                    "model_label": model.label,
                    "model": model.name,
                    "explore_name": explore.name,
                    "explore_label": explore.label,
                    "description": explore.description,
                    "hidden": explore.hidden,
                    "group_label": explore.group_label,
                    "joins": [join.name for join in details.joins or []],
                    "tags": details.tags or [],
                }
            )
    return explores


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="explores.csv")
    parser.add_argument("--config", help="Path to looker.ini (default: $LOOKER_INI or ./looker.ini)")
    args = parser.parse_args()

    sdk = connect(args.config)
    write_csv(get_explores(sdk), args.out)


if __name__ == "__main__":
    main()
