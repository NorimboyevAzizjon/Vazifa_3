import React from 'react';

export interface Task {
  id: number;
  description: string;
  deadline: string;
  completed: boolean;
}

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (id: number) => void;
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onToggleComplete, onDelete, onEdit }) => {
  return (
    <ul>
      {tasks.map(task => (
        <li key={task.id} style={{ marginBottom: '0.5rem' }}>
          <span
            className={`task-desc${task.completed ? ' completed' : ''}`}
            onClick={() => onToggleComplete(task.id)}
            title="Bajarilgan deb belgilash"
          >
            {task.description} (muddat: {task.deadline})
          </span>
          <button onClick={() => onEdit(task.id)} style={{ marginLeft: 8 }}>Tahrirlash</button>
          <button onClick={() => onDelete(task.id)} style={{ marginLeft: 4 }}>O‘chirish</button>
        </li>
      ))}
    </ul>
  );
};

export default TaskList;
