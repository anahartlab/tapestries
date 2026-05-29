#!/usr/bin/env python3
# eng_editor.py

import os
import re


def get_folder():
    return os.path.dirname(os.path.abspath(__file__))


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()

    # 1. replace UI text
    txt = txt.replace(
        "Посмотреть полотно в AR",
        "View in AR on phone"
    )

    # 2. fix AR links: ar/name.html -> ar/eng_name.html
    def repl(match):
        name = match.group(1)
        return f"href=\"ar/eng_{name}.html\""

    txt = re.sub(r"href=\"ar/([^\"]+)\.html\"", repl, txt)

    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)

    print(f"OK: {os.path.basename(path)}")


def main():
    folder = get_folder()

    files = [
        f for f in os.listdir(folder)
        if f.startswith("eng_")
        and f.endswith(".html")
        and os.path.isfile(os.path.join(folder, f))
    ]

    if not files:
        print("No files found")
        return

    for f in files:
        process_file(os.path.join(folder, f))


if __name__ == "__main__":
    main()