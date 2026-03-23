from task_manager import TaskManager
from ai_service import create_simple_tasks
def print_menu():
    print("\n---Gestor de Tareas Inteligente---")
    print("1. Añadir Tarea")
    print("2. Añadir tarea compleja")
    print("3. Listar Tareas")
    print("4. Marcar Tarea como Completada")
    print("5. Eliminar Tarea")
    print("6. Salir")

def main():
    manager = TaskManager()
    while True:
        print_menu()
        try:       
            choice = int(input("Seleccione una opción: "))
            match choice:
                case 1:
                    description = input("Descripción de la tarea: ")
                    manager.add_task(description)
                case 2:
                    description = input("Descripción de la tarea compleja: ")
                    subtasks = create_simple_tasks(description)
                    for subtask in subtasks:
                        if not subtask.startswith("Error:"):
                            manager.add_task(subtask)
                        else:
                            print(subtask)
                            break;
                case 2:
                    manager.list_tasks()
                case 3:
                    id = int(input("ID de la tarea: "))
                    manager.complete_task(id)
                case 4:
                    id = int(input("ID de la tarea: "))
                    manager.delete_task(id)
                case 5:
                    print("Saliendo...")
                    break
                case _:
                    print("Opción no válida. Por favor, seleccione una opción válida.")
        except ValueError:
            print("Opción no válida. Por favor, seleccione una opción válida.")
if __name__ == "__main__":
    main()
