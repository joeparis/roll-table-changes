import argparse
import re
from pathlib import Path
from typing import Optional

from titlecase import titlecase

ITEM_CATEGORIES = r"(Ammunition|Apex|Armor|Bomb|Companion|Elixir|Held|Mutagen|Oil|Other|Poison|Potion|Rune|Scroll|Shield|Snare|Staff|Structure|Talisman|Tool|Wand|Weapon|Worn)"
ITEM_GRADES = r"(major|lesser|moderate|minor|greater|true)"
ITEM_TYPES = r"(campfire|ladder|chest|horse|boat|agate ellipsoid|amber sphere|amplifying|azure briolette|black disc|black pearl|clear quartz octagon|consumed|cymophane cabochon|delaying|dusty rose prism|envisioning|gold nodule|lavender and green ellipsoid|mottled ellipsoid|nourishing|olivine pendeloque|pale lavender ellipsoid|pale orange rhomboid|pearlescent pyramid|pearly white spindle|peering|pink rhomboid|polished pebble|preserving|rainbow prism|smoothing|sprouting|western star)"
GRADES = r"(low-grade|medium-grade|high-grade)"

TYPES_AND_GRADES = ITEM_TYPES[1:-1].split("|") + ITEM_GRADES[1:-1].split("|")


def sanitize_line(line: str) -> Optional[str]:

    line = re.sub(rf"(?<!^)\b(?:{ITEM_CATEGORIES})\b.*\n", "", line)

    line = re.sub(r"’", "'", line)

    line = re.sub(r"\s[UR]", "", line)

    line = re.sub(
        rf",\s*{ITEM_GRADES}\s*$", lambda match: f" ({match.group(1)})", line, flags=re.IGNORECASE
    )

    line = re.sub(
        rf",\s*{ITEM_TYPES}\s*", lambda match: f" ({match.group(1)})", line, flags=re.IGNORECASE
    )

    line = re.sub(
        rf"(,\s*){GRADES}", lambda match: f" ({match.group(2)})", line, flags=re.IGNORECASE
    )

    if line.endswith(", \n"):
        line = line[:-3] + "\n"

    if line.startswith("+"):
        line = re.sub(
            r"^(\+\d*)(\s*)(.*)",
            lambda match: f"{match.group(3)}({match.group(1)})",
            line,
            flags=re.IGNORECASE,
        )

    line = line.replace(",", "")

    return titlecase(line.strip() + "\n") if line else None


def process_file(input_file: Path, output_file: Path) -> None:
    with input_file.open("r", encoding="utf-8") as infile, output_file.open(
        "w", encoding="utf-8"
    ) as outfile:

        sanitized_lines = [
            sanitized_line for line in infile.readlines() if (sanitized_line := sanitize_line(line))
        ]

        processed_lines = []
        for line in sanitized_lines:
            if (stripped_line := line.strip()).lower() in TYPES_AND_GRADES:
                if processed_lines:
                    processed_lines[-1] = processed_lines[-1].strip() + f" ({stripped_line})\n"
            else:
                processed_lines.append(line)

        seen = set()
        unique_lines = [line for line in processed_lines if not (line in seen or seen.add(line))]

        # unique_lines will never have a None value because of the filter above
        # but mypy doesn't seem to know that
        outfile.writelines(unique_lines)  # type: ignore


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
