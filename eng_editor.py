

#!/usr/bin/env python3
# eng_editor.py

import os


def get_folder():
    return os.path.dirname(os.path.abspath(__file__))


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()

    # 1. Replace availability text
    txt = txt.replace("В наличии", "In Stock")

    # 2. Replace Contact button block (donate.stream -> telegram)
    old_block = '''<p class="u-align-center u-text u-text-availability"><a  class="u-btn u-button-style u-custom-font u-heading-font u-hover-palette-1-light-1 u-palette-1-base u-radius-50 u-btn-1" href="https://donate.stream/anahart" style="border-radius: 100px;" title="Укажите нужную сумму и наименование товара в комментарии к донату">Contact</a></p>'''

    new_block = '''<p class="u-align-center u-text u-text-availability"><a  class="u-btn u-button-style u-custom-font u-heading-font u-hover-palette-1-light-1 u-palette-1-base u-radius-50 u-btn-1" href="https://t.me/anahart" style="border-radius: 100px;" title="Telegram">Contact</a></p>'''

    txt = txt.replace(old_block, new_block)

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
        print("No eng_*.html files found")
        return

    for f in files:
        process_file(os.path.join(folder, f))


if __name__ == "__main__":
    main()