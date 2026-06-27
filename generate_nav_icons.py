from bs4 import BeautifulSoup
import os
import csv

# Путь к файлу HTML
theway = "fantasy"
html_file = f"/Users/anahart/GitHub/tapestries/tapestries/{theway}.html"
# Путь к папке с изображениями товаров
images_root = f"/Users/anahart/GitHub/tapestries/tapestries/images/"

csv_file = f"/Users/anahart/GitHub/tapestries/tapestries/{theway}.csv"
csv_map = {}
with open(csv_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("Name", "").strip()
        seo = row.get("SEO_url", "").strip()
        if name and seo:
            csv_map[name.lower()] = seo

# Читаем HTML
with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

## Удаляем старые nav и все иконки внутри
for old_nav in soup.find_all("nav", class_="u-nav"):
    old_nav.decompose()

# Создаем nav с иконками
nav = soup.new_tag("nav", **{"class": "u-nav u-unstyled u-center"})
nav["style"] = "margin:20px 0; display:grid; justify-content:center;"

ul = soup.new_tag("ul", **{"class": "u-unstyled"})
ul["style"] = (
    "list-style:none; padding:0; margin:0 auto; "
    "display:grid; grid-template-columns:350px 350px; "
    "gap:20px 40px; max-width:800px; justify-content:center; justify-items:flex-start;"
)
nav.append(ul)

li_style = "display:flex; align-items:center; gap:12px; padding:10px 15px; box-sizing:border-box; justify-content:flex-start; width:100%; text-align:left;"

with open(csv_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        folder_name = row.get("Name", "").strip()
        sec_id = row.get("SEO_url", "").strip()
        title = row.get("Title", "").strip()

        folder_path = os.path.join(images_root, folder_name)
        icon_src = None
        if os.path.exists(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    icon_src = os.path.join("images", folder_name, file_name).replace(
                        "\\", "/"
                    )
                    break

        li = soup.new_tag("li")
        li["style"] = li_style
        a = soup.new_tag("a", href=f"#{sec_id}")
        a["style"] = (
            "display:flex; align-items:center; text-decoration:none; color:#333; width:100%; "
            "text-align:left; margin-left:8px; transition:0.3s;"
        )
        if icon_src:
            img = soup.new_tag("img", src=icon_src)
            img["style"] = (
                "width:50px; height:50px; object-fit:cover; border-radius:5px; margin-right:8px;"
            )
            a.append(img)
        span = soup.new_tag("span")
        span.string = title
        a.append(span)
        li.append(a)
        ul.append(li)

header = soup.find("header")
if header:
    header.insert_after(nav)

    # Добавляем фиксированную кнопку "В меню" в правом нижнем углу
    button = soup.new_tag("button", id="scroll-to-menu")
    button.string = "В меню"
    button["style"] = (
        "position: fixed; bottom: 20px; right: 20px; z-index: 1000; "
        "padding: 10px 15px; background-color: #007BFF; color: white; border: none; "
        "border-radius: 5px; cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.3);"
    )
    nav.insert_after(button)

    # Добавляем скрипт для плавного скролла к навигации при нажатии на кнопку
    script = soup.new_tag("script")
    script.string = (
        "document.getElementById('scroll-to-menu').addEventListener('click', function() {"
        "  document.querySelector('nav.u-nav').scrollIntoView({ behavior: 'smooth' });"
        "});"
    )
    button.insert_after(script)

style_tag = soup.new_tag("style")
style_tag.string = (
    "nav.u-nav ul li { transition: background-color 0.3s, color 0.3s; }"
    "nav.u-nav ul li:hover { background-color: #e0e0e0; }"
    "nav.u-nav ul li:hover a { color: #222; }"
    "@media (max-width: 600px) {"
    "  nav.u-nav ul { grid-template-columns: 1fr !important; max-width: 100% !important; }"
    "}"
)
soup.head.append(style_tag) if soup.head else soup.insert(0, style_tag)

# Сохраняем HTML
with open(html_file, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("✅ Навигация с иконками создана.")
