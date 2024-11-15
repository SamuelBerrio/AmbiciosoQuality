import logging
import random
import os
from typing import Optional, Tuple, List
from llamaapi import LlamaAPI
from requests.exceptions import RequestException
from dotenv import load_dotenv  # Importar la función para cargar .env

# Cargar las variables de entorno desde .env
load_dotenv()

# Configurar el registro con un formato más detallado y niveles apropiados
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Obtener el token de la API de variables de entorno para mayor seguridad
LLAMA_API_TOKEN = os.getenv('LLAMA_API_TOKEN')
if not LLAMA_API_TOKEN:
    logging.error("Token de API de Llama no encontrado en las variables de entorno.")
    raise EnvironmentError("LLAMA_API_TOKEN no está configurado.")

# Inicializar el SDK de Llama con el token de API de manera segura
llama = LlamaAPI(LLAMA_API_TOKEN)

# Constante para el nombre del modelo
MODEL_NAME = "llama3.1-405b"

def call_llama_api(prompt: str, max_tokens: int = 1000) -> Optional[str]:
    """
    Realiza una solicitud a la API de Llama y devuelve la respuesta.

    Args:
        prompt (str): El texto del prompt para enviar a la API.
        max_tokens (int, opcional): El número máximo de tokens para la respuesta.

    Returns:
        Optional[str]: La respuesta de la API si tiene éxito, None en caso contrario.
    """
    logging.info(f"Enviando solicitud a la API de Llama con max_tokens={max_tokens}.")
    api_request_json = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "stream": False,
    }
    try:
        response = llama.run(api_request_json)
        response.raise_for_status()  # Asegura que las respuestas HTTP de error se manejen
        response_data = response.json()
        content = response_data['choices'][0]['message']['content']
        logging.info("Respuesta recibida de la API de Llama.")
        return content.strip()
    except RequestException as req_err:
        logging.error(f"Error de solicitud al conectar con la API: {req_err}")
    except (KeyError, IndexError) as parse_err:
        logging.error(f"Error al parsear la respuesta de la API: {parse_err}")
    except Exception as e:
        logging.error(f"Error inesperado al llamar a la API de Llama: {e}")
    return None

def parse_api_response(content: str, required_keys: List[str]) -> Optional[dict]:
    """
    Parsea la respuesta de la API para extraer claves y valores específicos.

    Args:
        content (str): El contenido de la respuesta de la API.
        required_keys (List[str]): Las claves requeridas para una respuesta válida.

    Returns:
        Optional[dict]: Un diccionario con las claves y valores extraídos si son válidos, None en caso contrario.
    """
    try:
        lines = content.strip().split('\n')
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
            elif ')' in line:
                key, value = line.split(')', 1)
                data[key.strip()] = value.strip()
        if all(key in data for key in required_keys):
            return data
        else:
            missing_keys = [key for key in required_keys if key not in data]
            logging.error(f"Faltan claves en la respuesta de la API: {missing_keys}")
    except Exception as e:
        logging.error(f"Error al parsear la respuesta: {e}")
    return None

def generate_multiple_choice_question(topic: str) -> Tuple[Optional[str], Optional[List[Tuple[str, str]]], Optional[str]]:
    """
    Genera una pregunta de opción múltiple sobre un tema específico.

    Args:
        topic (str): El tema sobre el cual se generará la pregunta.

    Returns:
        Tuple[Optional[str], Optional[List[Tuple[str, str]]], Optional[str]]:
            Una tupla que contiene la pregunta, las opciones y la opción correcta.
    """
    prompt = (
        f"Actúa como un experto en diseño educativo especializado en preguntas de opción múltiple. "
        f"Crea una pregunta sobre el tema '{topic}' siguiendo el formato EXACTO siguiente, utilizando dos puntos ':' sin variaciones:\n"
        f"Pregunta: [texto de la pregunta]\n"
        f"A: [opción A]\n"
        f"B: [opción B]\n"
        f"C: [opción C]\n"
        f"D: [opción D]\n"
        f"Respuesta Correcta: [letra de la opción correcta]\n"
        f"La pregunta debe ser clara, adecuada para estudiantes de nivel medio, y enfocada en un concepto clave del tema. "
        f"Asegúrate de que solo se incluya la pregunta y las opciones en el formato indicado, sin explicaciones adicionales ni texto extra."
    )

    content = call_llama_api(prompt)
    if not content:
        logging.error("No se pudo generar la pregunta de opción múltiple.")
        return None, None, None

    required_keys = ['Pregunta', 'A', 'B', 'C', 'D', 'Respuesta Correcta']
    data = parse_api_response(content, required_keys)
    if not data:
        logging.error("Formato de respuesta inválido al generar pregunta de opción múltiple.")
        return None, None, None

    question = data['Pregunta']
    options = [('A', data['A']), ('B', data['B']), ('C', data['C']), ('D', data['D'])]
    correct_option = data['Respuesta Correcta']

    logging.info(f"Pregunta generada: {question}")
    logging.info(f"Opciones: {options}")
    logging.info(f"Opción correcta: {correct_option}")

    return question, options, correct_option

def generate_open_ended_question(topic: str) -> Optional[str]:
    """
    Genera una pregunta abierta sencilla sobre un tema específico.
    Puede generar una pregunta directa o un caso de estudio con una pregunta asociada.

    Args:
        topic (str): El tema sobre el cual se generará la pregunta.

    Returns:
        Optional[str]: La pregunta generada si tiene éxito, None en caso contrario.
    """
    prompts = {
        'direct': (
            f"Actúa como un educador experto en diseñar preguntas educativas para estudiantes de nivel medio. "
            f"Genera una pregunta breve, clara y sencilla sobre '{topic}', enfocada en un concepto clave del tema. "
            f"La pregunta debe ser fácil de responder y adecuada para su nivel. "
            f"Proporciona solo la pregunta, sin explicaciones adicionales ni caracteres especiales."
        ),
        'case_study': (
            f"Actúa como un educador experto en diseñar casos de estudio educativos para estudiantes de nivel medio. "
            f"Genera un caso de estudio muy corto de no mas de 2 renglones y muy claro relacionado con '{topic}', que describa un contexto o situación realista "
            f"para que el estudiante pueda analizar. El caso debe estar seguido de una pregunta clara y sencilla relacionada "
            f"con el contexto descrito, y que permita proponer una solución directa. "
            f"Proporciona solo el caso y la pregunta en un único párrafo, sin caracteres especiales, saltos de línea ni explicaciones adicionales."
        )
    }

    # Elegir aleatoriamente el tipo de prompt para diversificar las preguntas generadas
    prompt_type = random.choice(['direct', 'case_study'])
    prompt = prompts[prompt_type]
    logging.debug(f"Tipo de prompt seleccionado para pregunta abierta: {prompt_type}")

    # Definir max_tokens de manera eficiente para evitar respuestas excesivamente largas
    max_tokens = 500 if prompt_type == 'case_study' else 300

    content = call_llama_api(prompt, max_tokens=max_tokens)
    if content:
        # Limpiar el contenido para asegurar que esté en un solo párrafo
        cleaned_content = ' '.join(content.replace('\r', '').split())
        logging.info(f"Pregunta abierta generada: {cleaned_content}")
        return cleaned_content
    else:
        logging.error("No se pudo generar la pregunta abierta.")
        return None

def evaluate_response(user_response: str, topic: str, original_question: str) -> Tuple[bool, str]:
    """
    Evalúa la respuesta del usuario comparándola con el concepto del tema.

    Args:
        user_response (str): La respuesta proporcionada por el usuario.
        topic (str): El tema relacionado con la pregunta.
        original_question (str): La pregunta original que se le hizo al usuario.

    Returns:
        Tuple[bool, str]:
            Una tupla que contiene un booleano indicando si es correcta y una explicación.
    """
    prompt = (
        f"Actúa como un evaluador experto en análisis de respuestas educativas. "
        f"Evalúa la siguiente respuesta: '{user_response}' en relación con la pregunta: '{original_question}', "
        f"comparándola con el concepto de '{topic}'. "
        f"Proporciona la evaluación en el siguiente formato EXACTO, utilizando las etiquetas indicadas sin variaciones:\n"
        f"Evaluación: [Correcta/Incorrecta]\n"
        f"Explicación: [Explicación clara y detallada sobre por qué la respuesta es correcta o incorrecta, "
        f"incluyendo recomendaciones o correcciones si aplica]\n"
        f"Asegúrate de que la evaluación sea precisa, directa y útil, centrándote únicamente en la comparación indicada."
    )

    content = call_llama_api(prompt)
    if not content:
        logging.error("No se pudo evaluar la respuesta.")
        return False, "Error al evaluar la respuesta."

    required_keys = ['Evaluación', 'Explicación']
    data = parse_api_response(content, required_keys)
    if not data:
        logging.error("Formato de evaluación inválido.")
        return False, "No se pudo evaluar la respuesta."

    evaluation = data['Evaluación']
    explanation = data.get('Explicación', '')

    is_correct = evaluation.lower() == 'correcta'

    logging.info(f"Evaluación: {evaluation}")
    logging.info(f"Explicación: {explanation}")

    return is_correct, explanation
