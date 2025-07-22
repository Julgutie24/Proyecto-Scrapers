# Proyecto-Scrapers


Este proyecto utiliza **[Playwright](https://playwright.dev/python/)** para automatizar la navegación en páginas web con el objetivo de extraer información útil de manera estructurada. Está dividido en dos partes complementarias:

- **Parte 1 – Scraper Retail (sincrónico)**: Automatiza la extracción de productos desde tiendas online como **MercadoLibre** y **Éxito**.
- **Parte 2 – Scraper Wiki (asincrónico)**: Extrae información estructurada desde artículos de una Wiki.

Esto permite comparar dos enfoques distintos de programación (sincrónico y asincrónico), ambos usando Playwright con Python.

---

## 🤖 ¿Qué es Playwright?

Playwright es una herramienta poderosa que permite controlar navegadores como **Chromium, Firefox y WebKit** desde código. Sirve para:

- Automatizar pruebas web (como Selenium)
- Hacer scraping de sitios dinámicos (que cargan con JavaScript)
- Interactuar con elementos como botones, formularios, scrolls, etc.

Es compatible con múltiples lenguajes como **Python**, **JavaScript** y **C#**.  
En este proyecto usamos **Playwright para Python**.

---

## ¿Qué es programación Sincrónica y Asincrónica?

Playwright puede ejecutarse de dos maneras diferentes en Python:

| Tipo        | Descripción                                                                 |
|-------------|------------------------------------------------------------------------------|
|  **Sincrónica** | Ejecuta cada instrucción **una tras otra**, esperando a que termine para pasar a la siguiente. Más fácil de entender y depurar. Ideal para proyectos simples. |
|  **Asincrónica** | Permite realizar múltiples tareas al mismo tiempo usando `async/await`. Ideal para scraping en paralelo o cuando se necesitan muchas esperas. |

---

### Ejemplo de uso Sincrónico (como en el scraper retail):

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
```
### Ejemplo de uso Asincrónico (como en el scraper wiki):

```python
from playwright.async_api import async_playwright
import asyncio

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        print(await page.title())
        await browser.close()

asyncio.run(run())
```
