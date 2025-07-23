from playwright.sync_api import sync_playwright
from herramientas import process_text


class WikiScraper:
    def scraper(self, urls):
        """
        Permite al usuario seleccionar una sección de Wikipedia y extraer su contenido.
        Usa Playwright para navegar y scrapear dinámicamente.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            for url in urls:
                page.goto(url, timeout=60000)

                # Obtener secciones <h2>, ignorando algunas que no tienen texto relevante
                sections = page.locator("h2").all_inner_texts()
                banned = {
                    "Contenidos", "Véase también", "Referencias",
                    "Enlaces externos", "Bibliografía"
                }
                filtered = [s for s in sections if s not in banned]
                filtered_ = ["Introducción"] + filtered

                if not sections:
                    print("❌ No se encontraron secciones.")
                    continue

                # Mostrar secciones al usuario
                print("\n📌 Secciones disponibles:")
                for i, sec in enumerate(filtered_):
                    print(f"{i + 1}. {sec}")

                try:
                    select = int(input("👉 Elija la sección escribiendo el número: "))
                    selected_section = filtered_[select - 1]

                    print(f"\n✅ Sección seleccionada: {selected_section}")
                    print("\n📄 Procesando contenido...\n")

                    full_text = ""
                    count = 0

                    # Caso especial: Introducción (antes del primer <h2>)
                    if selected_section == "Introducción":
                        paragraphs = page.locator("p")
                        for i in range(paragraphs.count()):
                            nodo = paragraphs.nth(i)

                            # Parar si se detecta un encabezado (h2) antes del párrafo
                            prev = nodo.locator("xpath=preceding-sibling::h2")
                            if prev.count() > 0:
                                break

                            text = nodo.inner_text()
                            if not text:
                                continue

                            full_text += text + "\n\n"
                            count += 1
                            if count >= 3:
                                break

                    # Para otras secciones
                    else:
                        secciones_divs = page.locator("div.mw-heading.mw-heading2")
                        matched_div = None

                        # Buscar el div <h2> que coincide con la sección seleccionada
                        for i in range(secciones_divs.count()):
                            div = secciones_divs.nth(i)
                            h2 = div.locator("h2")

                            if h2.count() > 0 and h2.inner_text() == selected_section:
                                matched_div = div
                                break

                        if matched_div:
                            siblings = matched_div.locator("xpath=following-sibling::*")

                            for i in range(siblings.count()):
                                node = siblings.nth(i)

                                # Parar si se llega a otro título de sección
                                class_name = node.get_attribute("class") or ""
                                if "mw-heading2" in class_name:
                                    break

                                # Agregar párrafos
                                if node.evaluate("el => el.tagName") == "P":
                                    text = node.inner_text()
                                    if not text:
                                        continue

                                    full_text += text + "\n\n"
                                    count += 1
                                    if count >= 3:
                                        break
                        else:
                            print("❌ No se encontró la sección en el DOM.")
                            continue

                    # Resultado
                    if not full_text:
                        print("⚠️ No se encontró texto en esta sección.")
                    else:
                        process_text(url, selected_section, full_text)

                except (ValueError, IndexError):
                    print("❌ Selección inválida. Intente de nuevo.")

            browser.close()
