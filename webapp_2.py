import streamlit as st
import re

def find_words_with_substring(text, substring):
    """
    Encuentra todas las palabras únicas en un texto que contienen una subcadena.
    El proceso es insensible a mayúsculas y minúsculas y maneja varios idiomas.
    """
    if not text or not substring:
        return []

    # Se convierte el texto y la subcadena a minúsculas para una búsqueda insensible
    text_lower = text.lower()
    substring_lower = substring.lower()

    # Se usa una expresión regular para encontrar todas las palabras.
    # El patrón r'\b\w+\b' busca palabras completas.
    # El patrón r'\b[\w\u0370-\u03FF\u0600-\u06FF\u0400-\u04FF]+\b' busca palabras con caracteres de idiomas específicos
    # (Griego, Árabe, Cirílico, etc.). Esto mejora la compatibilidad.
    # Para simplificar y cubrir los idiomas solicitados (español y griego),
    # usamos un patrón más general que incluye caracteres latinos y griegos.
    # El re.UNICODE es útil para asegurar que se manejen correctamente los caracteres Unicode.
    # Sin embargo, re.findall ya tiene en cuenta Unicode por defecto en Python 3.
    # El patrón más seguro para este caso sería r'\b[\w\u0386\u0388-\u038A\u038C\u038E-\u03A1\u03A3-\u03CE\u03D0-\u03F5]+\b'
    # para griego, pero r'\b\w+\b' con re.UNICODE a menudo es suficiente para muchos casos.
    # Optamos por una solución más simple pero robusta: usar un regex que capture grupos de caracteres
    # y luego filtrar en Python.

    # Una mejor aproximación para varios idiomas es dividir por espacios y signos de puntuación
    # y luego verificar la subcadena.
    # Se utiliza una expresión regular para reemplazar los caracteres de puntuación por espacios
    # y luego se divide el texto en palabras.
    words = re.split(r'[\s,.!?;:()\'"“”‘’«»]+', text)

    found_words = set()
    for word in words:
        cleaned_word = word.strip().strip("'").strip('"')
        if cleaned_word and substring_lower in cleaned_word.lower():
            found_words.add(cleaned_word)

    return sorted(list(found_words))

def main():
    """
    Función principal de la aplicación Streamlit.
    Configura la interfaz y maneja la lógica de la aplicación.
    """
    st.title("Buscador de palabras")
    st.markdown("---")

    st.write("Esta aplicación encuentra todas las palabras que contienen una serie de letras específica en un texto. Funciona con idiomas como el español y el griego.")

    # Widget para el área de texto donde el usuario ingresa el texto
    user_text = st.text_area(
        "1. Pega tu texto aquí (funciona con español y griego):",
        height=250,
        placeholder="Ejemplo: La palabra 'tecnología' en griego es τεχνολογία, que se traduce a 'technologia'."
    )

    # Widget para la entrada de la subcadena a buscar
    search_term = st.text_input(
        "2. Ingresa la serie de letras (subcadena) a buscar:",
        placeholder="Ejemplo: logia"
    )

    st.markdown("---")

    # Botón para iniciar la búsqueda
    if st.button("3. Buscar palabras"):
        # Se muestra un mensaje de advertencia si no se ingresó el texto o la subcadena
        if not user_text:
            st.warning("Por favor, ingresa un texto para analizar.")
        elif not search_term:
            st.warning("Por favor, ingresa una serie de letras a buscar.")
        else:
            # Se llama a la función para encontrar las palabras
            result_words = find_words_with_substring(user_text, search_term)

            # Se muestran los resultados
            if result_words:
                st.subheader("Resultados:")
                st.write(f"Se encontraron {len(result_words)} palabra(s) única(s) que contienen '{search_term}':")
                st.info(", ".join(result_words))
            else:
                st.warning(f"No se encontraron palabras que contengan '{search_term}' en el texto proporcionado.")

# Se ejecuta la función principal si el script se ejecuta directamente
if __name__ == "__main__":
    main()
