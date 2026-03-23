# Gestor de Tareas Inteligente

Aplicación de línea de comandos para gestionar tareas personales, con integración de IA (OpenAI) para descomponer tareas complejas en subtareas simples y accionables.

## Características

- Añadir tareas simples con descripción libre
- Descomponer tareas complejas en 3–5 subtareas usando GPT
- Listar todas las tareas con su estado (pendiente / completada)
- Marcar tareas como completadas
- Eliminar tareas
- Persistencia automática en archivo JSON (`tasks.json`)

## Estructura del proyecto

```
taskmanager/
├── main.py                # Punto de entrada y menú interactivo
├── task_manager.py        # Lógica de negocio: Task y TaskManager
├── ai_service.py          # Integración con la API de OpenAI
├── tasks.json             # Almacenamiento persistente de tareas
├── test_task_manager.py   # Suite de tests unitarios
├── requirements.txt       # Dependencias del proyecto
└── .env                   # Variables de entorno (no se versiona)
```

## Requisitos

- Python 3.10 o superior (se usa `match/case`)
- Cuenta y API key de OpenAI (solo necesaria para tareas complejas)

## Instalación

```bash
# Clonar o descargar el repositorio
cd taskmanager

# Crear entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto con tu API key de OpenAI:

```
OPENAI_API_KEY=sk-...
```

> Sin esta clave, el resto de funcionalidades (añadir tareas simples, listar, completar, eliminar) funcionan con normalidad. Solo la opción de tareas complejas requiere conexión a la API.

## Uso

```bash
python main.py
```

Al ejecutar la aplicación aparece el menú interactivo:

```
---Gestor de Tareas Inteligente---
1. Añadir Tarea
2. Añadir tarea compleja
3. Listar Tareas
4. Marcar Tarea como Completada
5. Eliminar Tarea
6. Salir
```

### Opciones del menú

| Opción | Descripción |
|--------|-------------|
| 1 | Añade una tarea simple introduciendo su descripción |
| 2 | Usa GPT para dividir una tarea compleja en subtareas y las añade automáticamente |
| 3 | Muestra todas las tareas con su ID y estado (`[ ]` pendiente, `[✓]` completada) |
| 4 | Marca una tarea como completada indicando su ID |
| 5 | Elimina una tarea indicando su ID |
| 6 | Sale de la aplicación |

## Arquitectura

### `Task`
Modelo de datos con tres atributos: `id`, `description` y `completed`. Su método `__str__` devuelve una representación visual del tipo `[✓] #1: Descripción`.

### `TaskManager`
Gestiona la lista de tareas en memoria y la sincroniza con `tasks.json`. Expone los métodos `add_task`, `list_tasks`, `complete_task`, `delete_task`, `load_tasks` y `save_tasks`.

### `ai_service`
Llama a la API de OpenAI con el modelo `gpt-5`, enviando un prompt que solicita entre 3 y 5 subtareas en formato de lista. Parsea la respuesta y devuelve una lista de strings listos para añadir al gestor.

## Tests

La suite cubre las clases `Task` y `TaskManager`. Cada test de `TaskManager` utiliza un archivo temporal para evitar afectar a `tasks.json`.

```bash
python -m unittest test_task_manager.py -v
```

Clases de test incluidas:

| Clase | Qué verifica |
|-------|-------------|
| `TestTask` | Representación en string (pendiente y completada) |
| `TestAddTask` | Añadir tareas, incremento de IDs, persistencia |
| `TestListTasks` | Listado vacío y con tareas |
| `TestCompleteTask` | Completar tareas existentes e inexistentes |
| `TestDeleteTask` | Eliminar tareas existentes e inexistentes |
| `TestLoadTasks` | Carga desde archivo, IDs, archivo no encontrado |
| `TestSaveTasks` | JSON válido y consistencia tras recarga |

### Bugs conocidos documentados en los tests

- `complete_task`: `save_tasks()` se llama **después** del `return`, por lo que el estado completado no se persiste en disco.
- `delete_task`: mismo problema; el `save_tasks()` queda fuera del flujo de éxito.

## Dependencias principales

| Paquete | Versión | Uso |
|---------|---------|-----|
| `openai` | 2.29.0 | Cliente oficial de la API de OpenAI |
| `python-dotenv` | 1.2.2 | Carga de variables de entorno desde `.env` |
| `pydantic` | 2.12.5 | Validación de datos (dependencia interna de openai) |
| `httpx` | 0.28.1 | Cliente HTTP asíncrono (dependencia interna de openai) |
