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
    substring_lower = substring.lower()

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

    st.write("Esta aplicación encuentra todas las palabras únicas que contienen una serie de letras que especifiques.")

    # Widget para el área de texto donde el usuario ingresa el texto
    user_text = st.text_area(
        "1. Pega tu texto aquí:",
        height=250,
        placeholder="Ejemplo: Las casas eran blancas. Las niñas jugaban con pelotas en el jardín."
    )

    # Widget para la entrada de la subcadena a buscar
    search_term = st.text_input(
        "2. Ingresa la serie de letras (subcadena) a buscar:",
        placeholder="Ejemplo: casa"
    )

    st.markdown("---")

    # Botón para iniciar la búsqueda
    if st.button("3. Buscar palabras"):
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
                st.write(", ".join(result_words))
            else:
                st.warning(f"No se encontraron palabras que contengan '{search_term}' en el texto proporcionado.")

# Se ejecuta la función principal si el script se ejecuta directamente
if __name__ == "__main__":
    main()
