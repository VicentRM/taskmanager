import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_simple_tasks(description):
    if not client.api_key:
        return ["Error: La API key de OpenAI no está configurada."]
    try:
        prompt = f"""Desglosa la siguiente tarea compleja en una lista de 3 a 5 subtareas simples y accionables.
        Tarea: {description}
        Formato de respuesta
        - Subtarea 1
        - Subtarea 2
        - Subtarea 3
        etc.
        Responde solo con la lista de subtareas, una por línea empezando cada líena con un guión.
        """
        params = {
            "model": "gpt-5",
            "messages": [
                {"role": "system", "content": "Eres un asistente experto en gestión de tareas que ayuda a dividir tareas complejas en subtareas simples y accionables."},
                {"role": "user", "content": prompt}],
                "max_completion_tokens": 300,
                "verbosity": "medium",
                "reasoning_effort": "minimal",
        }
        response = client.chat.completions.create(**params)
        content = response.choices[0].message.content.strip()
        subtasks = []
        for line in content.split("\n"):
            line = line.strip()
            if line and line.startswith("-"):
                subtask = line[1:].strip()
                subtasks.append(subtask)
        if not subtasks:
            return ["Error: No se pudo crear la tarea. La respuesta del modelo está vacía."]
        return subtasks
    except Exception as e:
        return ["Error: No se pudo crear la tarea.", str(e)]