from playwright.sync_api import sync_playwright
import csv
import time
import random
from datetime import datetime
import os
import json
from abc import ABC, abstractmethod

class BaseRetailScraper(ABC):
    """Clase base abstracta para scrapers de retail con funcionalidades comunes"""
    
    def __init__(self, site_name, base_url=None):
        self.site_name = site_name
        self.base_url = base_url
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
        self.viewport = {"width": 1366, "height": 768}
        self.report_dir = "reportes_retail"
        self.default_wait_time = 3000  # 3 segundos
        self.tiempo_espera_post_busqueda = 3  # Valor por defecto para todos los sitios
        
        # Selectores (deben definirse en cada clase hija)
        self.search_input_selector = None
        self.search_button_selector = None
        self.product_container_selector = None
        self.product_name_selector = None
        self.product_price_selector = None
        self.product_original_price_selector = None
        self.product_link_selector = None
        self.product_discount_selector = None
        self.next_page_selector = None
        self.cookie_accept_selector = None
        
        os.makedirs(self.report_dir, exist_ok=True)

    @abstractmethod
    def scrape(self, producto: str, paginas: int = 1):
        """Método principal de scraping a implementar por cada sitio"""
        pass

    def _setup_browser(self):
        """Configura el navegador Playwright con opciones anti-detección"""
        browser = sync_playwright().start().chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--start-maximized'
            ]
        )
        context = browser.new_context(
            user_agent=self.user_agent,
            viewport=self.viewport,
            locale="es-CO",
            timezone_id="America/Bogota",
            extra_http_headers={
                "Accept-Language": "es-CO,es;q=0.9",
                "Referer": self.base_url
            }
        )
        return browser, context.new_page()

    def _guardar_resultados(self, productos: list, producto: str):
        """Guarda los resultados en CSV y JSON"""
        if not productos:
            print("No hay productos para guardar")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{self.site_name}_{producto}_{timestamp}"

        # CSV
        csv_path = os.path.join(self.report_dir, f"{nombre_archivo}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=productos[0].keys())
            writer.writeheader()
            writer.writerows(productos)

        # JSON
        json_path = os.path.join(self.report_dir, f"{nombre_archivo}.json")
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(productos, file, ensure_ascii=False, indent=2)

        print(f"\n✅ Resultados guardados en:\n- {csv_path}\n- {json_path}")

    def _manejar_cookies(self, page):
        """Maneja el popup de cookies si aparece"""
        try:
            if self.cookie_accept_selector:
                page.click(self.cookie_accept_selector, timeout=self.default_wait_time)
                print("Cookies aceptadas")
        except:
            print("No se encontró popup de cookies")

    def _esperar_carga(self, min=2, max=4):
        """Espera aleatoria entre acciones para parecer humano"""
        delay = random.uniform(min, max)
        print(f"⏱️ Esperando {delay:.1f} segundos...")
        time.sleep(delay)

    def _limpiar_precio(self, texto_precio):
        """Normaliza formato de precios"""
        if not texto_precio:
            return "0"
        return texto_precio.replace("$", "").replace(".", "").replace(",", "").strip()

    def _calcular_descuento(self, precio_original, precio_actual):
        """Calcula porcentaje de descuento entre dos precios"""
        try:
            if precio_original == precio_actual:
                return ""
            original = float(precio_original)
            actual = float(precio_actual)
            descuento = round(((original - actual) / original) * 100)
            return f"{descuento}%"
        except:
            return ""

    def _realizar_busqueda(self, page, producto):
        """Método unificado para realizar búsquedas con espera configurable"""
        search_input = page.wait_for_selector(self.search_input_selector, timeout=15000)
        search_input.fill(producto)
        
        if self.search_button_selector:
            search_button = page.wait_for_selector(self.search_button_selector, timeout=5000)
            search_button.click()
        else:
            search_input.press("Enter")
        
        # Espera configurable después de la búsqueda
        print(f"⏳ Esperando {self.tiempo_espera_post_busqueda} segundos para carga...")
        time.sleep(self.tiempo_espera_post_busqueda)
        
        page.wait_for_selector(self.product_container_selector, timeout=20000)
        self._esperar_carga()

    def _extraer_datos_producto(self, item):
        """Método unificado para extraer datos de un producto"""
        try:
            # Nombre del producto
            nombre_element = item.query_selector(self.product_name_selector)
            nombre = nombre_element.inner_text().strip() if nombre_element else "Producto sin nombre"
            
            # Precio actual
            precio_element = item.query_selector(self.product_price_selector)
            precio = self._limpiar_precio(precio_element.inner_text().strip() if precio_element else "0")
            
            # Precio original
            precio_original_element = item.query_selector(self.product_original_price_selector) if self.product_original_price_selector else None
            precio_original = self._limpiar_precio(precio_original_element.inner_text().strip() if precio_original_element else precio)
            
            # Enlace del producto
            enlace_element = item.query_selector(self.product_link_selector)
            enlace = enlace_element.get_attribute("href") if enlace_element else "#"
            if enlace and not enlace.startswith("http"):
                enlace = f"{self.base_url}{enlace}"
            
            # Descuento
            descuento_element = item.query_selector(self.product_discount_selector) if self.product_discount_selector else None
            descuento = descuento_element.inner_text().strip() if descuento_element else self._calcular_descuento(precio_original, precio)
            
            return {
                "producto": nombre,
                "precio_actual": f"${precio} COP",
                "precio_original": f"${precio_original} COP" if precio_original != precio else "",
                "descuento": descuento,
                "enlace": enlace,
                "sitio": self.site_name,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        except Exception as e:
            print(f"Error extrayendo producto: {str(e)}")
            return None

    def _ir_a_siguiente_pagina(self, page):
        """Método unificado de paginación con comportamiento robusto"""
        if not self.next_page_selector:
            print("⚠️ Selector de paginación no definido para este sitio")
            return False

        try:
            # 1. Localizar el botón usando el selector específico del sitio
            next_btn = page.locator(self.next_page_selector)
            
            if not next_btn.count():
                print(f"✅ Fin de páginas en {self.site_name} (no hay botón 'Siguiente')")
                return False

            # 2. Simulación de comportamiento humano
            next_btn.hover()
            page.wait_for_timeout(random.uniform(800, 1200))  # Espera aleatoria
            
            # 3. Click forzado para mayor robustez
            next_btn.click(force=True, timeout=3000)
            print(f"✔ Avanzando a siguiente página en {self.site_name}")
            
            # 4. Esperar carga de nueva página
            page.wait_for_timeout(random.uniform(2000, 3500))
            page.wait_for_selector(self.product_container_selector, timeout=10000)
            return True

        except Exception as e:
            print(f"❌ Error en paginación en {self.site_name}: {str(e)}")
            return False

class MercadoLibreScraper(BaseRetailScraper):
    """Scraper especializado para Mercado Libre Colombia"""
    
    def __init__(self):
        super().__init__("MercadoLibre", "https://www.mercadolibre.com.co")
        
        # Definición de selectores específicos
        self.search_input_selector = "input.nav-search-input"
        self.search_button_selector = None  # Se usa Enter
        self.product_container_selector = "div.poly-card__content"
        self.product_name_selector = "a.poly-component__title"
        self.product_price_selector = ".poly-price__current .andes-money-amount__fraction"
        self.product_original_price_selector = "s .andes-money-amount__fraction"
        self.product_link_selector = "a.poly-component__title"
        self.product_discount_selector = ".andes-money-amount__discount"
        self.next_page_selector = "li.andes-pagination__button--next a"
        self.cookie_accept_selector = "button:has-text('Aceptar cookies')"

    def scrape(self, producto: str, paginas: int = 1):
        """Implementación principal del scraper para Mercado Libre"""
        productos = []
        browser, page = self._setup_browser()

        try:
            print(f"\n🔍 Buscando '{producto}' en {self.site_name}...")
            page.goto(self.base_url, timeout=60000)
            self._manejar_cookies(page)
            self._esperar_carga(3, 5)
            
            self._realizar_busqueda(page, producto)

            # Bucle de paginación
            for pagina_actual in range(1, paginas + 1):
                print(f"📄 Procesando página {pagina_actual}...")
                items = page.query_selector_all(self.product_container_selector)
                
                for item in items:
                    producto_data = self._extraer_datos_producto(item)
                    if producto_data:
                        productos.append(producto_data)
                        print(f"✔ {producto_data['producto'][:30]}... - {producto_data['precio_actual']} {'('+producto_data['descuento']+')' if producto_data['descuento'] else ''}")

                if pagina_actual < paginas and not self._ir_a_siguiente_pagina(page):
                    print("No hay más páginas disponibles.")
                    break

            self._guardar_resultados(productos, producto)
            return productos

        except Exception as e:
            print(f"\n❌ Error durante scraping: {str(e)}")
            page.screenshot(path=os.path.join(self.report_dir, f"error_{self.site_name.lower()}.png"))
            return []
        finally:
            page.context.close()
            browser.close()

class ExitoScraper(BaseRetailScraper):
    """Scraper especializado para Éxito Colombia"""
    
    def __init__(self):
        super().__init__("Exito", "https://www.exito.com")
        # Configurar tiempo de espera más largo para Éxito
        self.tiempo_espera_post_busqueda = 10  # 10 segundos después de buscar
        
        # Definición de selectores específicos
        self.search_input_selector = 'input[data-fs-search-input="true"]'
        self.search_button_selector = 'button[type="submit"][aria-label="Submit Search"]'
        self.product_container_selector = 'article[class*="productCard_productCard"]'
        self.product_name_selector = 'h3[class*="styles_name__"]'
        self.product_price_selector = 'p[class*="ProductPrice_container__price__"]'
        self.product_original_price_selector = 'p[class*="price-dashed"]'
        self.product_link_selector = 'a[data-testid="product-link"]'
        self.product_discount_selector = '[class*="priceSection_container-promotion_discount__"] span[data-percentage="true"]'
        self.next_page_selector = 'button:has-text("Siguiente"), button[aria-label="Próxima Pagina"]'
        self.cookie_accept_selector = 'button:has-text("Aceptar cookies"), button#cookie-banner-lgpd-accept'

    def scrape(self, producto: str, paginas: int = 1):
        """Implementación principal del scraper para Éxito"""
        productos = []
        browser, page = self._setup_browser()

        try:
            print(f"\n🔍 Buscando '{producto}' en {self.site_name}...")
            page.goto(self.base_url, timeout=60000)
            self._manejar_cookies(page)
            self._esperar_carga(3, 5)
            
            self._realizar_busqueda(page, producto)

            # Bucle de paginación
            for pagina_actual in range(1, paginas + 1):
                print(f"📄 Procesando página {pagina_actual}...")
                items = page.query_selector_all(self.product_container_selector)
                
                for item in items:
                    producto_data = self._extraer_datos_producto(item)
                    if producto_data:
                        # Añadir marca específica para Éxito
                        marca_element = item.query_selector('h3[class*="styles_brand__"]')
                        if marca_element:
                            producto_data['producto'] = f"{marca_element.inner_text().strip()} {producto_data['producto']}"
                        
                        # Añadir vendedor específico para Éxito
                        vendedor_element = item.query_selector('span[data-fs-product-details-seller__name="true"]')
                        producto_data['vendedor'] = vendedor_element.inner_text().replace("Vendido por:", "").strip() if vendedor_element else "Éxito"
                        
                        productos.append(producto_data)
                        print(f"✔ {producto_data['producto'][:50]}... - {producto_data['precio_actual']}")

                if pagina_actual < paginas and not self._ir_a_siguiente_pagina(page):
                    print("No hay más páginas disponibles.")
                    break

            self._guardar_resultados(productos, producto)
            return productos

        except Exception as e:
            print(f"\n❌ Error durante scraping: {str(e)}")
            page.screenshot(path=os.path.join(self.report_dir, f"error_{self.site_name.lower()}.png"))
            return []
        finally:
            page.context.close()
            browser.close()

class RetailScraper:
    """Orquestador principal de los scrapers"""
    
    def __init__(self):
        self.scrapers = {
            "mercadolibre": MercadoLibreScraper(),
            "exito": ExitoScraper()
        }

    def scrape(self, producto: str, sitio: str, paginas: int = 1):
        """Ejecuta el scraping en el sitio especificado"""
        sitio = sitio.lower()
        if sitio in self.scrapers:
            return self.scrapers[sitio].scrape(producto, paginas)
        else:
            sitios_disponibles = ", ".join(self.scrapers.keys())
            print(f"Error: Sitio {sitio} no soportado. Opciones: {sitios_disponibles}")
            return []