import json
import os
import tempfile
import unittest
from unittest.mock import patch

from task_manager import Task, TaskManager


class TestTask(unittest.TestCase):
    def test_str_pending(self):
        task = Task(1, "Comprar leche")
        self.assertEqual(str(task), "[ ] #1: Comprar leche")

    def test_str_completed(self):
        task = Task(2, "Lavar ropa", completed=True)
        self.assertEqual(str(task), "[✓] #2: Lavar ropa")

    def test_default_not_completed(self):
        task = Task(1, "Algo")
        self.assertFalse(task.completed)


class TestTaskManagerWithTempFile(unittest.TestCase):
    """Base que redirige FILENAME a un archivo temporal por cada test."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        )
        self.tmp.write("[]")
        self.tmp.close()
        TaskManager.FILENAME = self.tmp.name
        self.manager = TaskManager()

    def tearDown(self):
        os.unlink(self.tmp.name)
        TaskManager.FILENAME = "tasks.json"


class TestAddTask(TestTaskManagerWithTempFile):
    def test_add_single_task(self):
        self.manager.add_task("Estudiar Python")
        self.assertEqual(len(self.manager._tasks), 1)
        self.assertEqual(self.manager._tasks[0].description, "Estudiar Python")

    def test_add_increments_id(self):
        self.manager.add_task("Tarea A")
        self.manager.add_task("Tarea B")
        ids = [t.id for t in self.manager._tasks]
        self.assertEqual(ids, [1, 2])

    def test_add_multiple_tasks(self):
        descriptions = ["A", "B", "C"]
        for d in descriptions:
            self.manager.add_task(d)
        self.assertEqual(len(self.manager._tasks), 3)

    def test_add_persists_to_file(self):
        self.manager.add_task("Tarea persistida")
        with open(self.tmp.name) as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["description"], "Tarea persistida")


class TestListTasks(TestTaskManagerWithTempFile):
    def test_list_empty(self, mock_print=None):
        with patch("builtins.print") as mock_print:
            self.manager.list_tasks()
            mock_print.assert_called_once_with("No hay tareas pendientes.")

    def test_list_with_tasks(self):
        self.manager.add_task("Tarea 1")
        with patch("builtins.print") as mock_print:
            self.manager.list_tasks()
            # list_tasks hace print(task), el mock recibe el objeto Task
            args, _ = mock_print.call_args
            self.assertEqual(str(args[0]), "[ ] #1: Tarea 1")


class TestCompleteTask(TestTaskManagerWithTempFile):
    def test_complete_existing_task(self):
        self.manager.add_task("Hacer ejercicio")
        self.manager.complete_task(1)
        self.assertTrue(self.manager._tasks[0].completed)

    def test_complete_not_found_prints_message(self):
        with patch("builtins.print") as mock_print:
            self.manager.complete_task(99)
            mock_print.assert_called_with("Tarea no encontrada: #99")

    def test_complete_does_not_affect_other_tasks(self):
        self.manager.add_task("A")
        self.manager.add_task("B")
        self.manager.complete_task(1)
        self.assertFalse(self.manager._tasks[1].completed)

    # BUG conocido: save_tasks() no se llama al completar con éxito
    # (el return ocurre antes del save_tasks al final del método)
    def test_complete_save_bug(self):
        self.manager.add_task("Tarea con bug")
        self.manager.complete_task(1)
        new_manager = TaskManager()
        # Con el bug actual, la tarea no se guarda como completada
        self.assertFalse(
            new_manager._tasks[0].completed,
            "BUG: save_tasks no se llama al completar una tarea con éxito",
        )


class TestDeleteTask(TestTaskManagerWithTempFile):
    def test_delete_existing_task(self):
        self.manager.add_task("Borrar esto")
        self.manager.delete_task(1)
        self.assertEqual(len(self.manager._tasks), 0)

    def test_delete_not_found_prints_message(self):
        with patch("builtins.print") as mock_print:
            self.manager.delete_task(42)
            mock_print.assert_called_with("Tarea no encontrada: #42")

    def test_delete_correct_task(self):
        self.manager.add_task("A")
        self.manager.add_task("B")
        self.manager.delete_task(1)
        self.assertEqual(len(self.manager._tasks), 1)
        self.assertEqual(self.manager._tasks[0].description, "B")

    # BUG conocido: save_tasks() no se llama al eliminar con éxito
    def test_delete_save_bug(self):
        self.manager.add_task("Tarea con bug")
        self.manager.delete_task(1)
        new_manager = TaskManager()
        # Con el bug actual, la tarea sigue en el archivo
        self.assertEqual(
            len(new_manager._tasks),
            1,
            "BUG: save_tasks no se llama al eliminar una tarea con éxito",
        )


class TestLoadTasks(TestTaskManagerWithTempFile):
    def test_load_from_existing_file(self):
        data = [{"id": 1, "description": "Cargada", "completed": False}]
        with open(self.tmp.name, "w") as f:
            json.dump(data, f)
        self.manager.load_tasks()
        self.assertEqual(len(self.manager._tasks), 1)
        self.assertEqual(self.manager._tasks[0].description, "Cargada")

    def test_load_sets_next_id(self):
        data = [
            {"id": 1, "description": "A", "completed": False},
            {"id": 5, "description": "B", "completed": True},
        ]
        with open(self.tmp.name, "w") as f:
            json.dump(data, f)
        self.manager.load_tasks()
        self.assertEqual(self.manager._next_id, 6)

    def test_load_empty_file_sets_next_id_1(self):
        self.assertEqual(self.manager._next_id, 1)

    def test_load_file_not_found(self):
        TaskManager.FILENAME = "/ruta/inexistente/tasks.json"
        manager = TaskManager()
        self.assertEqual(manager._tasks, [])
        TaskManager.FILENAME = self.tmp.name

    def test_load_preserves_completed_state(self):
        data = [{"id": 1, "description": "Completada", "completed": True}]
        with open(self.tmp.name, "w") as f:
            json.dump(data, f)
        self.manager.load_tasks()
        self.assertTrue(self.manager._tasks[0].completed)


class TestSaveTasks(TestTaskManagerWithTempFile):
    def test_save_creates_valid_json(self):
        self.manager.add_task("Guardada")
        with open(self.tmp.name) as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(data[0]["description"], "Guardada")
        self.assertFalse(data[0]["completed"])

    def test_save_and_reload_consistency(self):
        self.manager.add_task("Consistente")
        new_manager = TaskManager()
        self.assertEqual(len(new_manager._tasks), 1)
        self.assertEqual(new_manager._tasks[0].description, "Consistente")


if __name__ == "__main__":
    unittest.main()
