from bs4 import BeautifulSoup
import sys

# Путь к файлу HTML
html_file = "/Users/anahart/GitHub/tapestries/tapestries/instock.html"

# Читаем HTML
with open(html_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# 1️⃣ Удаляем проданные товары
sections = soup.find_all("section", class_="u-clearfix u-section-16")
if not sections:
    print("⚠️ Внимание: не найдено секций с классом 'u-clearfix u-section-16'.")
for section in sections:
    availability = section.find("p", class_="u-text-availability")
    if availability:
        text = availability.get_text(strip=True)
        if "0" in text or "нет" in text.lower():
            section.decompose()

## Удаляем старые меню, кнопку "В меню" и контейнеры, если есть
for old_nav in soup.find_all("nav", class_="u-nav"):
    old_nav.decompose()
old_menu_btn = soup.find(id="scroll-to-menu")
if old_menu_btn:
    old_menu_btn.decompose()
old_toggle = soup.find(id="menu-toggle")
if old_toggle:
    old_toggle.decompose()
old_back = soup.find(id="back-to-menu")
if old_back:
    old_back.decompose()
old_container = soup.find(id="menu-container")
if old_container:
    old_container.decompose()

# 2️⃣ Создаем новую красивую навигацию по оставшимся товарам
nav = soup.new_tag("nav", **{"class": "u-nav u-unstyled u-center"})
nav["style"] = "margin:20px 0; display:grid; justify-content:center;"
ul = soup.new_tag("ul", **{"class": "u-unstyled"})
ul["style"] = (
    "list-style:none; padding:0; margin:0 auto; "
    "display:grid; grid-template-columns: 350px 350px; gap:20px 40px; "
    "justify-content:center; width:100%; max-width:800px;"
)
for section in soup.find_all("section", class_="u-clearfix u-section-16"):
    sec_id = section.get("id")
    if not sec_id:
        continue
    # ищем заголовок внутри секции
    h3 = section.find(["h3", "h2", "h1"])
    if not h3:
        continue
    title = h3.get_text(strip=True)
    li = soup.new_tag("li")
    li["style"] = (
        "display:flex; align-items:center; gap:8px; padding:10px 15px; "
        "box-sizing:border-box; justify-content:flex-start; width:100%; text-align:left;"
    )
    a = soup.new_tag("a", href=f"#{sec_id}")
    a["style"] = (
        "display:flex; align-items:center; text-decoration:none; color:#333; width:100%; text-align:left;"
    )
    a.string = title
    li.append(a)
    ul.append(li)
nav.append(ul)

body = soup.find("body")
if body:
    # Вставляем навигацию в начало body
    body.insert(0, nav)

    # Добавляем hover-эффекты и фон для мини-каталога
    style_tag = soup.new_tag("style")
    style_tag.string = """
    nav.u-nav ul li {
        background-color:#f9f9f9;
        border-radius:8px;
        transition: background-color 0.3s, color 0.3s;
        padding:10px 15px;
        display:flex;
        align-items:center;
        gap:8px;
    }
    nav.u-nav ul li:hover {
        background-color:#e0e0e0;
    }
    nav.u-nav ul li:hover a {
        color:#222;
    }
    nav.u-nav ul a {
        text-decoration:none;
        color:#333;
        display:flex;
        align-items:center;
        width:100%;
        text-align:left;
    }
    @media (max-width: 600px) {
        nav.u-nav ul { grid-template-columns: 1fr !important; max-width: 100% !important; }
    }
    """
    soup.head.append(style_tag) if soup.head else soup.insert(0, style_tag)

    # Добавляем фиксированную кнопку "В меню"
    menu_btn = soup.new_tag("button", id="scroll-to-menu")
    menu_btn.string = "В меню"
    menu_btn["style"] = (
        "position:fixed; bottom:20px; right:20px; padding:10px 15px; "
        "background:#007BFF; color:#fff; border:none; border-radius:5px; cursor:pointer; "
        "box-shadow:0 4px 6px rgba(0,0,0,0.3); z-index:999;"
    )
    body.append(menu_btn)

    # Плавный скролл к навигации
    script_scroll = soup.new_tag("script")
    script_scroll.string = """
    document.getElementById("scroll-to-menu").addEventListener("click", function() {
        const nav = document.querySelector("nav.u-nav");
        if(nav){ nav.scrollIntoView({behavior:'smooth'}); }
    });
    """
    body.append(script_scroll)

# Сохраняем HTML
with open(html_file, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("✅ Проданные товары удалены, навигация создана.")
