import asyncio
from playwright.async_api import async_playwright
from herramientas import process_text


class NewScraper:
    """
    Scraper de noticias para El Tiempo, Semana y El Espectador.

    Permite buscar noticias por palabra clave o extraer el contenido completo desde un link.
    Usa Playwright para la navegación y requiere una función 'process_text' para procesar los textos.
    """
    
    TIMEOUT = 30000
    MAX_RESULTS = 3
    HEADLESS = False

    # 🔍 Scraper para El Tiempo
    async def eltiempo_scraper(self, page, keyword):
        search_url = f"https://www.eltiempo.com/buscar?q={self.normalize_keyword(keyword, 'eltiempo')}"
        await page.goto(search_url, timeout=self.TIMEOUT)

        try:
            await page.wait_for_selector("h3.c-article__title a", timeout=self.TIMEOUT)
        except:
            print("\n🕵️ No se encontraron resultados en El Tiempo.")
            return

        items = await page.locator("h3.c-article__title a").all()
        print("=" * 197)
        print(f"\n📰 Resultados de El Tiempo para: {keyword}")
        count = 0

        for item in items:
            href = await item.get_attribute("href")
            title = await item.inner_text()

            if href and title:
                full_url = href if href.startswith("http") else f"https://www.eltiempo.com{href}"
                print(f"\n🔗 {title}")
                print(f"🌐 {full_url}")
                count += 1
                if count >= self.MAX_RESULTS:
                    print("\n" + "=" * 197)
                    break

    # 🔍 Scraper para Semana
    async def semana_scraper(self, page, keyword):
        search_url = f"https://www.semana.com/buscador/?query={self.normalize_keyword(keyword, 'semana')}"
        await page.goto(search_url, timeout=self.TIMEOUT)

        try:
            await page.wait_for_selector("a:has(div.queryly_item_title)", timeout=self.TIMEOUT)
        except:
            print("\n🕵️ No se encontraron resultados en Semana.")
            return

        items = await page.locator("a:has(div.queryly_item_title)").all()
        print(f"\n📰 Resultados de Semana para: {keyword}")
        count = 0

        for item in items:
            title_el = item.locator("div.queryly_item_title")
            title = await title_el.inner_text() if await title_el.count() else None
            href = await item.get_attribute("href")

            if href and title:
                full_url = href if href.startswith("http") else f"https://www.semana.com{href}"
                print(f"\n🔗 {title}")
                print(f"🌐 {full_url}")
                count += 1
                if count >= self.MAX_RESULTS:
                    print("\n" + "=" * 197)
                    break

    # 🔍 Scraper para El Espectador
    async def elespectador_scraper(self, page, keyword):
        search_url = f"https://www.elespectador.com/buscador/{self.normalize_keyword(keyword, 'elespectador')}"
        await page.goto(search_url, timeout=self.TIMEOUT)

        try:
            await page.wait_for_selector("h2.Card-Title > a", timeout=self.TIMEOUT)
        except:
            print("\n🕵️ No se encontraron resultados en El Espectador.")
            return

        items = await page.locator("h2.Card-Title > a").all()
        print(f"\n📰 Resultados de El Espectador para: {keyword}")
        count = 0

        for item in items:
            href = await item.get_attribute("href")
            title = await item.inner_text()

            if href and title:
                full_url = href if href.startswith("http") else f"https://www.elespectador.com{href}"
                print(f"\n🔗 {title}")
                print(f"🌐 {full_url}")
                count += 1
                if count >= self.MAX_RESULTS:
                    print("\n" + "=" * 197)
                    break

    # 🧩 Ejecuta todos los scrapers para una palabra clave
    async def scraper(self, keyword):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.HEADLESS)
            page = await browser.new_page()

            await self.eltiempo_scraper(page, keyword)
            await self.semana_scraper(page, keyword)
            await self.elespectador_scraper(page, keyword)

            await browser.close()

    # 📄 Extrae contenido de un artículo de El Tiempo
    async def scrape_eltiempo_article(self, page):
        try:
            await page.wait_for_selector("h1", timeout=self.TIMEOUT)
            title = await page.locator("h1").first.inner_text()

            paragraph_elements = page.locator("div.paragraph")
            count = await paragraph_elements.count()
            paragraphs = [
                await paragraph_elements.nth(i).inner_text()
                for i in range(count)
                if await paragraph_elements.nth(i).inner_text()
            ]

            full_text = "\n\n".join(paragraphs)
            print(f"\n📰 {title}\n")
            process_text(page.url, "Noticia", full_text)

        except Exception as e:
            print(f"❌ No se pudo extraer la noticia de El Tiempo. Error: {e}")

    # 📄 Extrae contenido de un artículo de Semana
    async def scrape_semana_article(self, page):
        try:
            await page.wait_for_selector("h1.text-smoke-700", timeout=self.TIMEOUT)
            title = await page.locator("h1.text-smoke-700").first.inner_text()

            paragraph_elements = page.locator("p[data-type='text']")
            count = await paragraph_elements.count()
            paragraphs = [
                await paragraph_elements.nth(i).inner_text()
                for i in range(count)
                if await paragraph_elements.nth(i).inner_text()
            ]

            full_text = "\n\n".join(paragraphs)
            print(f"\n📰 {title}\n")
            process_text(page.url, "Noticia", full_text)

        except Exception as e:
            print(f"❌ No se pudo extraer la noticia de Semana. Error: {e}")

    # 📄 Extrae contenido de un artículo de El Espectador
    async def scrape_elespectador_article(self, page):
        try:
            await page.wait_for_selector("h1.Title", timeout=self.TIMEOUT)
            title = await page.locator("h1.Title").inner_text()

            paragraph_elements = page.locator("div.Article-Content p")
            count = await paragraph_elements.count()
            paragraphs = [
                await paragraph_elements.nth(i).inner_text()
                for i in range(count)
                if await paragraph_elements.nth(i).inner_text()
            ]

            full_text = "\n\n".join(paragraphs)
            print(f"\n📰 {title}\n")
            process_text(page.url, "Noticia", full_text)

        except Exception as e:
            print(f"❌ No se pudo extraer la noticia de El Espectador. Error: {e}")

    # 🔀 Escoge scraper según el dominio del URL
    async def scrape_article(self, page, url):
        await page.goto(url, timeout=self.TIMEOUT)

        if "eltiempo.com" in url:
            await self.scrape_eltiempo_article(page)
        elif "semana.com" in url:
            await self.scrape_semana_article(page)
        elif "elespectador.com" in url:
            await self.scrape_elespectador_article(page)
        else:
            print("❌ Sitio no reconocido.")

    # 🔧 Normaliza palabras clave para cada sitio
    @staticmethod
    def normalize_keyword(keyword: str, site: str) -> str:
        keyword = keyword.lower()
        if site == "eltiempo":
            return keyword.replace(" ", "+")
        elif site == "semana":
            return keyword.replace(" ", "%20")
        elif site == "elespectador":
            return keyword.replace(" ", "-")
        return keyword

    # 🧪 Punto de entrada desde consola
    @staticmethod
    def launch_scraper():
        modo = input("\n📌 ¿Deseas buscar una palabra (1) o buscar una noticia por link (2)? ")

        async def run_scraper():
            scrap = NewScraper()
            try:
                if modo == "1":
                    word = input("🔍 ¿Qué término deseas buscar en noticias? ")
                    await scrap.scraper(word)
                elif modo == "2":
                    url = input("🔗 Pega el link de la noticia: ")
                    async with async_playwright() as p:
                        browser = await p.chromium.launch(headless=scrap.HEADLESS)
                        page = await browser.new_page()
                        await scrap.scrape_article(page, url)
                        await browser.close()
                else:
                    print("❌ Opción inválida.")
            except Exception as e:
                print(f"\n❌ Error: {e}")

        try:
            asyncio.run(run_scraper())
        except Exception as e:
            print(f"\n❌ Error al ejecutar el scraper: {e}")
