import json
from pathlib import Path
from transformers import pipeline  # type: ignore


def process_text(url: str, seccion: str, texto: str):
    """
    Procesa el texto extraído de un scrap:
    - Permite al usuario elegir entre ver el texto completo o un resumen generado por IA.
    - Guarda el resultado en archivos .txt y .json.
    """
    if not texto:
        print("⚠️ No hay texto para procesar.")
        return

    print("¿Qué prefiere?")
    print("1. Texto normal")
    print("2. Resumen hecho por IA")
    option = input("👉 Seleccione una opción (1-2): ")

    if option == "1":
        print("\n📄 Texto completo:\n")
        print(texto)
        save_as(url, seccion, "texto", texto)

    elif option == "2":
        resumen = ia_summary(texto)
        if resumen:
            save_as(url, seccion, "resumen_IA", resumen)
    else:
        print("❌ Opción inválida.")


def ia_summary(text: str) -> str:
    """
    Usa un modelo preentrenado de Hugging Face para generar un resumen del texto.
    """
    if not text:
        print("⚠️ No hay texto para resumir.")
        return ""

    print("\n⏳ Resumiendo texto con IA...\n")

    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6"
    )

    summary = summarizer(text[:1024], max_length=130, min_length=30, do_sample=False)
    final_summary = summary[0]['summary_text']

    print(f"📄 Resumen:\n\n{final_summary}\n")
    return final_summary


def save_as(url: str, seccion: str, modo: str, texto: str):
    """
    Guarda el contenido en archivos:
    - .txt plano
    - .json estructurado
    """
    carpeta = Path(__file__).resolve().parent / "reportes"
    carpeta.mkdir(exist_ok=True)

    # Guardar .txt
    with open(carpeta / "salida.txt", "w", encoding="utf-8") as f_txt:
        f_txt.write(f"URL: {url}\n")
        f_txt.write(f"Sección: {seccion}\n")
        f_txt.write(f"Modo: {modo}\n\n")
        f_txt.write(texto)

    # Guardar .json
    data = {
        "url": url,
        "seccion": seccion,
        "modo": modo,
        "contenido": texto
    }
    with open(carpeta / "salida.json", "w", encoding="utf-8") as f_json:
        json.dump(data, f_json, ensure_ascii=False, indent=2)

    print("📁 Contenido exportado a 'resultados/salida.txt' y 'resultados/salida.json'")