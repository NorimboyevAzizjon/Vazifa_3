

import { useState, useEffect } from 'react';
import TaskForm from './TaskForm';
import TaskList, { type Task } from './TaskList';
import './App.css'

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [editId, setEditId] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<{ description: string; deadline: string }>({ description: '', deadline: '' });

  useEffect(() => {
    const stored = localStorage.getItem('tasks');

    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (stored) setTasks(JSON.parse(stored));
  }, []);

  useEffect(() => {
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }, [tasks]);

  const handleAddTask = (task: { description: string; deadline: string }) => {
    if (editId !== null) {
      setTasks(tasks => tasks.map(t => t.id === editId ? { ...t, ...task } : t));
      setEditId(null);
      setEditValues({ description: '', deadline: '' });
    } else {
      setTasks(tasks => [
        ...tasks,
        {
          id: Date.now(),
          description: task.description,
          deadline: task.deadline,
          completed: false,
        },
      ]);
    }
  };

  const handleToggleComplete = (id: number) => {
    setTasks(tasks => tasks.map(task => task.id === id ? { ...task, completed: !task.completed } : task));
  };

  const handleDelete = (id: number) => {
    setTasks(tasks => tasks.filter(task => task.id !== id));
    if (editId === id) {
      setEditId(null);
      setEditValues({ description: '', deadline: '' });
    }
  };

  const handleEdit = (id: number) => {
    const task = tasks.find(t => t.id === id);
    if (task) {
      setEditId(id);
      setEditValues({ description: task.description, deadline: task.deadline });
    }
  };

  return (
    <div className="todo-container">
      <h2>To-Do List</h2>
      <TaskForm
        onAddTask={handleAddTask}
        {...(editId !== null ? { key: editId, ...editValues } : {})}
      />
      <TaskList
        tasks={tasks}
        onToggleComplete={handleToggleComplete}
        onDelete={handleDelete}
        onEdit={handleEdit}
      />
      {editId !== null && <div className="edit-mode">Tahrirlash rejimi: {editValues.description}</div>}
    </div>
  );
}

export default App;
