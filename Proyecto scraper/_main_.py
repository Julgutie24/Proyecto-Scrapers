"""
main.py

Módulo principal para ejecutar un sistema de scraping integrado.
Incluye funciones para buscar productos, información en Wikipedia y noticias en sitios colombianos.
"""

import time
from Scrapers.wikiscraper import WikiScraper
from Scrapers.newscraper import NewScraper
from Scrapers.retail_scraper import RetailScraper

def mostrar_menu():
    """Muestra un menú interactivo al usuario con mejor formato."""
    print("\n" + "=" * 50)
    print("🛒 SISTEMA DE SCRAPING INTEGRADO".center(50))
    print("=" * 50)
    print("\n1. Buscar producto en Mercado Libre")
    print("2. Buscar producto en Éxito")
    print("3. Buscar información en Wikipedia")
    print("4. Buscar noticias")
    print("5. Salir")
    return input("\n👉 Seleccione una opción (1-5): ")


def obtener_numero_paginas():
    """Solicita y valida el número de páginas a scrapear."""
    while True:
        try:
            paginas = input("\n📄 ¿Cuántas páginas deseas scrapear? (1-5, default 1): ") or "1"
            paginas = int(paginas)
            if 1 <= paginas <= 5:
                return paginas
            print("⚠️ Por favor ingrese un número entre 1 y 5")
        except ValueError:
            print("⚠️ Debe ingresar un número válido")


def main():
    """Función principal para ejecutar el menú interactivo."""
    wiki = WikiScraper()
    retail = RetailScraper()

    while True:
        opcion = mostrar_menu()
        if opcion in ("1", "2"):
            # Opciones de retail (MercadoLibre o Éxito)
            producto = input(f"\n🔍 ¿Qué producto deseas buscar en {'Mercado Libre' if opcion == '1' else 'Éxito'}? ")
            paginas = obtener_numero_paginas()
            
            print("\n⏳ Buscando productos...")
            start_time = time.time()
            retail.scrape(
                producto=producto,
                sitio="mercadolibre" if opcion == "1" else "exito",
                paginas=paginas
            )
            print(f"⌛ Tiempo de búsqueda: {time.time() - start_time:.2f} segundos")

        elif opcion == "3":
            # Buscar en Wikipedia
            termino = input("\n🔍 ¿Qué término deseas buscar en Wikipedia? ")
            print("\n⏳ Buscando información...")
            start_time = time.time()
            print("🚀 Llamando a scraper...")
            wiki.scraper([f"https://es.wikipedia.org/wiki/{termino.replace(' ', '_')}"])
            print(f"⌛ Tiempo de búsqueda: {time.time() - start_time:.2f} segundos")

        elif opcion == "4":
            # Buscar en sitios de noticias
            NewScraper.launch_scraper()

        elif opcion == "5":
            # Salir del programa
            print("\n✅ ¡Gracias por usar el sistema de scraping! ¡Hasta luego!")
            break

        else:
            # Entrada inválida
            print("\n❌ Opción no válida. Por favor ingrese un número del 1 al 5.")

        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    main()
