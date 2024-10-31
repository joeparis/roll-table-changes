import argparse
import re
from pathlib import Path
from typing import Optional

from titlecase import titlecase


def sanitize_line(line: str) -> Optional[str]:
    line = re.sub(
        r"(?<!^)\b(?:Ammunition|Apex|Armor|Bomb|Companion|Elixir|Held|Mutagen|Oil|Other|Poison|Potion|Rune|Scroll|Shield|Snare|Staff|Structure|Talisman|Tool|Wand|Weapon|Worn)\b.*",
        "",
        line,
    )
    line = re.sub(r"’", "'", line)
    line = re.sub(r"\s[UR]", "", line)
    line = re.sub(
        r",\s*(major|lesser|moderate|minor|greater|true)\s*$",
        lambda match: f" ({match.group(1)})",
        line,
        flags=re.IGNORECASE,
    )

    return titlecase(line.strip() + "\n") if line else None


def process_file(input_file: Path, output_file: Path) -> None:
    with input_file.open("r", encoding="utf-8") as infile, output_file.open(
        "w", encoding="utf-8"
    ) as outfile:

        sanitized_lines = [
            sanitize_line(line) for line in infile.readlines() if sanitize_line(line) is not None
        ]


def process_all_files(input_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for input_file in input_dir.glob("*"):
        if input_file.is_file():
            output_file = output_dir / input_file.name

            process_file(input_file, output_file)
            print(f"Processed {input_file} -> {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files in a directory.")
    parser.add_argument(
        "-i",
        "--input_dir",
        default="input_files",
        help="Directory containing input files (default: input_files)",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        default="output_files",
        help="Directory to save processed files (default: output_files)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    process_all_files(input_dir, output_dir)
