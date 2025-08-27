import streamlit as st
import re
import requests
import json
import time

# Define the API endpoint and key based on environment
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
API_KEY = "" # The platform will provide this

def find_words_with_substring(text, substring):
    """
    Finds all unique words in a text that contain a substring.
    The process is case-insensitive and handles various languages.
    """
    if not text or not substring:
        return []

    substring_lower = substring.lower()

    # Simple regex to split text into words by punctuation and spaces
    words = re.split(r'[\s,.!?;:()\'"“”‘’«»]+', text)

    found_words = set()
    for word in words:
        cleaned_word = word.strip().strip("'").strip('"')
        if cleaned_word and substring_lower in cleaned_word.lower():
            found_words.add(cleaned_word)

    return sorted(list(found_words))

def get_gemini_analysis(words_list, language):
    """
    Performs morphological analysis on a list of words using the Gemini API.
    The prompt is adapted to the specified language.
    Returns a dictionary with the word and its analysis.
    """
    if not words_list:
        return {}

    prompt_text = f"""
    Eres un experto en lingüística. Para la siguiente lista de palabras en {language},
    proporciona un análisis morfológico detallado en un formato JSON.
    Para cada palabra, devuelve su 'lemma' (forma base), 'parte_oracion' (sustantivo, verbo, adjetivo, etc.)
    y 'caracteristicas_morfo' como un diccionario con propiedades como 'numero', 'genero', 'tiempo', etc.

    Palabras: {', '.join(words_list)}

    El resultado debe ser un array de objetos JSON. Cada objeto debe tener la siguiente estructura:
    {{
        "palabra": "palabra_original",
        "lemma": "forma_base",
        "parte_oracion": "categoria_gramatical",
        "caracteristicas_morfo": {{
            "genero": "masculino|femenino|neutro",
            "numero": "singular|plural",
            "tiempo": "presente|pasado|futuro",
            "persona": "1|2|3",
            "modo": "indicativo|subjuntivo|imperativo"
        }}
    }}

    Devuelve solo el JSON, sin texto adicional.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "palabra": {"type": "STRING"},
                        "lemma": {"type": "STRING"},
                        "parte_oracion": {"type": "STRING"},
                        "caracteristicas_morfo": {
                            "type": "OBJECT",
                            "properties": {
                                "genero": {"type": "STRING", "enum": ["masculino", "femenino", "neutro", "indeterminado"]},
                                "numero": {"type": "STRING", "enum": ["singular", "plural", "indeterminado"]},
                                "tiempo": {"type": "STRING", "enum": ["presente", "pasado", "futuro", "indeterminado"]},
                                "persona": {"type": "STRING", "enum": ["1", "2", "3", "indeterminado"]},
                                "modo": {"type": "STRING", "enum": ["indicativo", "subjuntivo", "imperativo", "indeterminado"]}
                            }
                        }
                    },
                    "propertyOrdering": ["palabra", "lemma", "parte_oracion", "caracteristicas_morfo"]
                }
            }
        }
    }

    retries = 3
    delay = 1

    for i in range(retries):
        try:
            response = requests.post(f"{API_URL}?key={API_KEY}", json=payload)
            response.raise_for_status() # Raise an exception for bad status codes

            gemini_response = response.json()

            # Extract the JSON string and parse it
            json_string = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(json_string)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                st.error("Error 403: Acceso prohibido. Esto generalmente significa que su clave de API es inválida o no está configurada correctamente.")
                st.info("Por favor, asegúrese de que su clave de API está configurada en la sección de 'Secrets' de Streamlit Cloud.")
                return {}
            elif e.response.status_code == 429 or e.response.status_code >= 500:
                st.warning(f"Error {e.response.status_code}: Reintentando en {delay} segundos...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                st.error(f"Error al conectar con la API de Gemini: {e}")
                return {}
        except (KeyError, json.JSONDecodeError) as e:
            st.error(f"Error al procesar la respuesta de Gemini: {e}")
            st.json(gemini_response) # Show the raw response for debugging
            return {}

    return {}


def detect_language(text):
    """
    Simple function to detect language based on common characters.
    """
    if re.search(r'[\u0370-\u03FF]', text):
        return "griego"
    return "español"


def main():
    """
    Main Streamlit application function.
    Sets up the interface and handles application logic.
    """
    st.title("Buscador de palabras con análisis morfológico de Gemini")
    st.markdown("---")

    st.write("Esta aplicación encuentra palabras que contienen una serie de letras y usa la API de Gemini para proporcionar un análisis morfológico detallado.")

    user_text = st.text_area(
        "1. Pega tu texto aquí (ejemplo en español y griego):",
        height=250,
        placeholder="Ejemplo: Las casas eran blancas. La palabra 'tecnología' en griego es τεχνολογία, que se traduce a 'technologia'."
    )

    search_term = st.text_input(
        "2. Ingresa la serie de letras (subcadena) a buscar:",
        placeholder="Ejemplo: logia"
    )

    st.markdown("---")

    if st.button("3. Buscar y analizar"):
        if not user_text:
            st.warning("Por favor, ingresa un texto para analizar.")
        elif not search_term:
            st.warning("Por favor, ingresa una serie de letras a buscar.")
        else:
            with st.spinner('Analizando palabras con Gemini...'):
                result_words = find_words_with_substring(user_text, search_term)

                if result_words:
                    detected_language = detect_language(user_text)
                    st.subheader("Resultados:")
                    st.write(f"Se encontraron {len(result_words)} palabra(s) única(s) que contienen '{search_term}':")

                    morphology_data = get_gemini_analysis(result_words, detected_language)
                    
                    if morphology_data:
                        for word_data in morphology_data:
                            # Find the original word from the Gemini response for display
                            original_word = word_data.get("palabra", "Palabra no encontrada")
                            with st.expander(f"**{original_word}**"):
                                st.json(word_data)
                else:
                    st.warning(f"No se encontraron palabras que contengan '{search_term}' en el texto proporcionado.")

# Run the main function
if __name__ == "__main__":
    main()
