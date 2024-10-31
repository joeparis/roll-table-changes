#!/usr/bin/env python3

import os
import json
import re
from bs4 import BeautifulSoup


def read_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_key_value_pairs(json_data):
    key_value_dict = {}
    if "pages" in json_data:
        for page in json_data["pages"]:
            if "text" in page and "content" in page["text"]:
                content = page["text"]["content"]
                soup = BeautifulSoup(content, "html.parser")

                for table in soup.find_all("table"):
                    header_row = table.find("tr")
                    headers = [
                        header.get_text(strip=True) for header in header_row.find_all(["th", "td"])
                    ]

                    new_name_index = headers.index("New Name") if "New Name" in headers else None

                    for row in table.find_all("tr")[1:]:
                        cells = row.find_all(["td", "th"])
                        if cells:
                            first_cell = cells[0].get_text(strip=True)
                            new_name_cell = (
                                cells[new_name_index].get_text(strip=True)
                                if new_name_index is not None
                                else ""
                            )

                            if new_name_cell == "—":
                                new_name_cell = "removed"
                            else:
                                new_name_cell = re.sub(
                                    r"@UUID\[.*?]{(.*?)}", r"\1", new_name_cell
                                ).strip()

                            if first_cell:
                                key_value_dict[first_cell] = new_name_cell

    return key_value_dict


def extract_name_and_parenthesis(name):
    match = re.match(r"^(.*?)\s*(\((.*?)\))?$", name.strip())
    if match:
        base_name = match.group(1).strip()
        parenthetical = match.group(2) or ""
        return base_name, parenthetical
    return name, ""


def replace_level_with_rank(text):
    return re.sub(r"(\d+)(?:st|nd|rd|th)-level Spell", r"\1-rank Spell", text)


def find_changes(dictionary, json_data):
    changes = []
    for item in json_data.get("results", []):
        original_name = item.get("text", "")
        base_name, parenthetical = extract_name_and_parenthesis(original_name)

        if base_name in dictionary:
            new_name = dictionary[base_name]
            if parenthetical:
                new_name = f"{new_name} {parenthetical}"

            new_name = replace_level_with_rank(new_name)

            changes.append((original_name, new_name))
    return changes


def append_to_markdown(markdown_lines, file_name, changes):
    markdown_lines.append(f"### {os.path.splitext(file_name)[0]}\n")
    markdown_lines.append("| Original Name                 | New Name                 |\n")
    markdown_lines.append("|-------------------------------|--------------------------|\n")
    for original, new in changes:
        markdown_lines.append(f"| {original} | {new} |\n")
    markdown_lines.append("\n")


def main():
    src_folder = "src"
    first_json_file = "remaster-changes.json"

    dictionary = extract_key_value_pairs(read_json_file(first_json_file))
    markdown_lines = []

    for second_file in sorted(os.listdir(src_folder)):
        if second_file.endswith(".json"):
            second_json_data = read_json_file(os.path.join(src_folder, second_file))
            changes = find_changes(dictionary, second_json_data)
            append_to_markdown(markdown_lines, second_file, changes)

    with open("combined_results.md", "w", encoding="utf-8") as md_file:
        md_file.writelines(markdown_lines)


if __name__ == "__main__":
    main()
