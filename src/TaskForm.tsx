import React, { useState } from 'react';

interface TaskFormProps {
  onAddTask: (task: { description: string; deadline: string }) => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ onAddTask }) => {
  const [description, setDescription] = useState('');
  const [deadline, setDeadline] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim() || !deadline.trim()) {
      setError('Iltimos, barcha maydonlarni to‘ldiring!');
      return;
    }
    onAddTask({ description, deadline });
    setDescription('');
    setDeadline('');
    setError('');
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
      <input
        type="text"
        placeholder="Vazifa tavsifi"
        value={description}
        onChange={e => setDescription(e.target.value)}
      />
      <input
        type="date"
        value={deadline}
        onChange={e => setDeadline(e.target.value)}
      />
      <button type="submit">Qo‘shish</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </form>
  );
};

export default TaskForm;
