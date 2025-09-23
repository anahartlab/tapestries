# -*- coding: utf-8 -*-
import os
import csv
import random
import sys

# === Устанавливаем рабочую директорию — скрипт всегда будет работать из папки с файлом ===
repo_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo_root)

# === Параметры ===
csv_path = "tapestriesCatalog.csv"
html_path = "instock.html"
images_dir = "images"
valid_exts = {".jpg", ".jpeg", ".png"}

# === Проверки существования файлов ===
if not os.path.exists(csv_path):
    print(f"❌ CSV-файл '{csv_path}' не найден в {repo_root}")
    sys.exit(1)
if not os.path.exists(html_path):
    print(f"❌ HTML-файл '{html_path}' не найден в {repo_root}")
    sys.exit(1)

# === Читаем текущий HTML ===
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

lower = html_content.lower()
header_start = lower.find("<header")
header_end = -1
if header_start != -1:
    header_end = lower.find("</header>", header_start)
    if header_end != -1:
        header_end += len("</header>")

footer_start = lower.find("<footer")
if footer_start == -1:
    footer_start = lower.find("</body>")

# Определим точку вставки и: если найдены и header и footer — удалим содержимое между ними (оставим header и footer)
insert_index = None
if header_end != -1 and footer_start != -1 and header_end < footer_start:
    # удаляем только содержимое между концом header и началом footer (оставляем header и footer)
    html_content = html_content[:header_end] + html_content[footer_start:]
    insert_index = header_end
else:
    # fallback: вставляем перед <footer> если он есть, иначе перед </body>, иначе в конец файла
    lower = html_content.lower()
    fpos = lower.find("<footer")
    if fpos != -1:
        insert_index = fpos
    else:
        bpos = lower.find("</body>")
        insert_index = bpos if bpos != -1 else len(html_content)

# === Читаем CSV и генерируем секции ===
with open(csv_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    # Проверяем нужные столбцы
    required = ["Name", "Title", "Description", "Stock"]
    for col in required:
        if col not in reader.fieldnames:
            print(f"❌ В CSV нет столбца '{col}'. Найдены столбцы: {reader.fieldnames}")
            sys.exit(1)

    for row in reader:
        name = row["Name"].strip()
        title = row["Title"].strip()
        description = row["Description"].strip()
        stock = row["Stock"].strip()
        folder_path = os.path.join(images_dir, name)

        if not os.path.isdir(folder_path):
            print(f"⚠️  Пропущен '{name}' — папка '{folder_path}' не найдена.")
            continue

        images = [
            f
            for f in sorted(os.listdir(folder_path))
            if os.path.isfile(os.path.join(folder_path, f))
            and os.path.splitext(f)[1].lower() in valid_exts
        ]

        if images:
            images = random.sample(images, min(5, len(images)))
        else:
            print(f"⚠️  Пропущен '{name}' — нет изображений.")
            continue

        # Удаление существующего блока (если есть)
        start_tag = f'<section class="u-clearfix u-section-16" id="{name}">'
        start_pos = html_content.find(start_tag)
        if start_pos != -1:
            end_pos = html_content.find("</section>", start_pos)
            if end_pos != -1:
                html_content = (
                    html_content[:start_pos]
                    + html_content[end_pos + len("</section>") :]
                )
                # после удаления пересчитываем точку вставки
                lower = html_content.lower()
                fpos = lower.find("<footer")
                if fpos != -1:
                    insert_index = fpos
                else:
                    bpos = lower.find("</body>")
                    insert_index = bpos if bpos != -1 else len(html_content)

        # Формируем карусель
        safe_id = name.replace(" ", "_")[:32]
        carousel_id = f"carousel-{safe_id}"
        carousel_indicators = ""
        carousel_items = ""

        for i, img_name in enumerate(images):
            # индикаторы
            active_class = "u-active" if i == 0 else ""
            carousel_indicators += (
                f'                          <li data-u-target="#{carousel_id}" data-u-slide-to="{i}" '
                f'class="{active_class} u-grey-70 u-shape-circle" style="width: 10px; height: 10px;"></li>\n'
            )

            # слайды
            slide_class = f"u-carousel-item u-gallery-item u-carousel-item-{i+1}"
            if i == 0:
                slide_class = "u-active " + slide_class

            item_div = f"""                          <div class="{slide_class}" data-image-width="960" data-image-height="1280">
                            <div class="u-back-slide">
                              <img class="u-back-image u-expanded" src="images/{name}/{img_name}">
                            </div>
                            <div class="u-align-center u-over-slide u-shading u-valign-bottom u-over-slide-{i+1}"></div>
                            <style data-mode="XL"></style>
                            <style data-mode="LG"></style>
                            <style data-mode="MD"></style>
                            <style data-mode="SM"></style>
                            <style data-mode="XS"></style>
                          </div>"""
            carousel_items += item_div + "\n"

        stock_html = stock.replace("☀️", "<br>☀️")
        description_html = f"{title}<br><br>{description}<br><br>В наличии {stock_html}<br><br>Доставка 450р за весь заказ"

        block = f"""
    <section class="u-clearfix u-section-16" id="{name}">
      <div class="u-clearfix u-sheet u-valign-middle-md u-valign-top-lg u-valign-top-xl u-sheet-1">
        <div class="data-layout-selected u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-size-30">
                <div class="u-layout-col">
                  <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-1">
                    <div class="u-container-layout u-valign-middle-lg u-valign-middle-sm u-valign-middle-xs u-container-layout-1">
                      <div class="custom-expanded u-carousel u-gallery u-gallery-slider u-layout-carousel u-lightbox u-no-transition u-show-text-none u-gallery-1" data-interval="5000" data-u-ride="carousel" id="{carousel_id}">
                        <ol class="u-absolute-hcenter u-carousel-indicators u-carousel-indicators-1">
{carousel_indicators}                        </ol>
                        <div class="u-carousel-inner u-gallery-inner u-gallery-inner-1" role="listbox">
{carousel_items}                        </div>
                        <a class="u-absolute-vcenter u-carousel-control u-carousel-control-prev u-grey-70 u-icon-circle u-opacity u-opacity-70 u-spacing-10 u-text-white u-carousel-control-1" href="#{carousel_id}" role="button" data-u-slide="prev">
                          <span aria-hidden="true">
                            <svg viewBox="0 0 451.847 451.847"><path d="..."/></svg></span><span class="sr-only">Previous</span>
                        </a>
                        <a class="u-absolute-vcenter u-carousel-control u-carousel-control-next u-grey-70 u-icon-circle u-opacity u-opacity-70 u-spacing-10 u-text-white u-carousel-control-2" href="#{carousel_id}" role="button" data-u-slide="next">
                          <span aria-hidden="true">
                            <svg viewBox="0 0 451.846 451.847"><path d="..."/></svg></span><span class="sr-only">Next</span>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="u-size-30">
                <div class="u-layout-col">
                  <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-2">
                    <div class="u-container-layout u-container-layout-2">
                      <p class="u-align-left u-text u-text-2">{description_html}</p>
                      <div class="u-align-center">
                        <a href="https://donate.stream/anahart" class="u-btn u-button-style u-custom-font u-heading-font u-hover-palette-1-light-1 u-palette-1-base u-radius-50 u-btn-1" style="border-radius: 100px;" title="Укажите нужную сумму и наименование товара в комментарии к донату">Оплатить</a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>"""

        # === Вставка перед точкой вставки ===
        html_content = (
            html_content[:insert_index] + block + "\n" + html_content[insert_index:]
        )
        insert_index += len(block) + 1  # с учётом добавленного перевода строки

# === Сохраняем результат ===
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Все товары из CSV добавлены в instock.html")
