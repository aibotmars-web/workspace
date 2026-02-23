import { useState, useMemo } from 'react'

interface Todo {
  id: number;
  text: string;
  completed: boolean;
  createdAt: Date;
  category?: string;
}

function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState('');
  const [filter, setFilter] = useState<'all' | 'today' | 'pending' | 'completed'>('all');

  const addTodo = () => {
    if (!input.trim()) return;
    setTodos([...todos, { id: Date.now(), text: input, completed: false, createdAt: new Date() }]);
    setInput('');
  };

  const toggleTodo = (id: number) => {
    setTodos(todos.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
  };

  const deleteTodo = (id: number) => {
    setTodos(todos.filter(t => t.id !== id));
  };

  // 統計數據
  const stats = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const todayTodos = todos.filter(t => t.createdAt >= today);
    const completed = todos.filter(t => t.completed);
    const pending = todos.filter(t => !t.completed);
    const completionRate = todos.length > 0 ? Math.round((completed.length / todos.length) * 100) : 0;

    return { todayTodos, completed, pending, completionRate, total: todos.length };
  }, [todos]);

  // 篩選任務
  const filteredTodos = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    switch (filter) {
      case 'today':
        return todos.filter(t => t.createdAt >= today);
      case 'pending':
        return todos.filter(t => !t.completed);
      case 'completed':
        return todos.filter(t => t.completed);
      default:
        return todos;
    }
  }, [todos, filter]);

  return (
    <div className="container">
      <h1>📋 任務儀表板</h1>
      
      {/* 統計卡片 */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-number">{stats.total}</span>
          <span className="stat-label">全部任務</span>
        </div>
        <div className="stat-card pending">
          <span className="stat-number">{stats.pending.length}</span>
          <span className="stat-label">待完成</span>
        </div>
        <div className="stat-card today">
          <span className="stat-number">{stats.todayTodos.length}</span>
          <span className="stat-label">今日新增</span>
        </div>
        <div className="stat-card completed">
          <span className="stat-number">{stats.completionRate}%</span>
          <span className="stat-label">完成率</span>
        </div>
      </div>

      {/* 進度條 */}
      <div className="progress-section">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${stats.completionRate}%` }}
          />
        </div>
        <span className="progress-text">{stats.completed.length} / {stats.total} 完成</span>
      </div>

      {/* 篩選器 */}
      <div className="filter-bar">
        <button 
          className={filter === 'all' ? 'active' : ''} 
          onClick={() => setFilter('all')}
        >全部</button>
        <button 
          className={filter === 'today' ? 'active' : ''} 
          onClick={() => setFilter('today')}
        >今日</button>
        <button 
          className={filter === 'pending' ? 'active' : ''} 
          onClick={() => setFilter('pending')}
        >待完成</button>
        <button 
          className={filter === 'completed' ? 'active' : ''} 
          onClick={() => setFilter('completed')}
        >已完成</button>
      </div>

      {/* 新增任務 */}
      <div className="input-group">
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && addTodo()}
          placeholder="新增任務..."
        />
        <button onClick={addTodo}>新增</button>
      </div>

      {/* 任務列表 */}
      <ul className="todo-list">
        {filteredTodos.map(todo => (
          <li key={todo.id} className={todo.completed ? 'completed' : ''}>
            <span onClick={() => toggleTodo(todo.id)}>{todo.text}</span>
            <span className="todo-date">{todo.createdAt.toLocaleDateString()}</span>
            <button className="delete-btn" onClick={() => deleteTodo(todo.id)}>✕</button>
          </li>
        ))}
        {filteredTodos.length === 0 && (
          <li className="empty-state">暂无任务</li>
        )}
      </ul>
    </div>
  )
}

export default App
