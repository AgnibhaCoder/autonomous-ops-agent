import React, { useState, useEffect } from 'react';
import { createTask, getTasks, submitApprovalDecision } from './api/client';
import { useTaskWebSocket } from './hooks/useTaskWebSocket';
import { TaskInput } from './components/TaskInput';
import { LiveTrace } from './components/LiveTrace';
import { ApprovalPrompt } from './components/ApprovalPrompt';

export function App() {
  const [tasks, setTasks] = useState([]);
  const [activeTaskId, setActiveTaskId] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { messages, isConnected, pendingApproval } = useTaskWebSocket(activeTaskId);

  const fetchTasks = async () => {
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleCreateTask = async (prompt) => {
    setIsSubmitting(true);
    try {
      const task = await createTask(prompt);
      setActiveTaskId(task.id);
      await fetchTasks();
    } catch (err) {
      console.error('Failed to create task:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleApprovalDecision = async (approvalId, approved, reason) => {
    if (!activeTaskId) return;
    try {
      await submitApprovalDecision(activeTaskId, approvalId, approved, reason);
    } catch (err) {
      console.error('Failed to submit approval:', err);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar Task History */}
      <div className="w-80 bg-slate-900 border-r border-slate-800 p-4 flex flex-col">
        <h1 className="text-lg font-bold text-slate-100 mb-4">Agent Workspace</h1>
        <div className="flex-1 overflow-y-auto space-y-2">
          {tasks.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTaskId(t.id)}
              className={`w-full text-left p-3 rounded-lg border text-xs transition-colors ${
                activeTaskId === t.id
                  ? 'bg-indigo-950/60 border-indigo-500/80 text-indigo-200'
                  : 'bg-slate-800/50 border-slate-700/50 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <div className="font-semibold truncate mb-1">{t.prompt}</div>
              <div className="text-[10px] text-slate-400 uppercase tracking-wide">{t.status}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Execution View */}
      <div className="flex-1 flex flex-col p-6 gap-4 overflow-hidden">
        <TaskInput onSubmit={handleCreateTask} isLoading={isSubmitting} />

        <ApprovalPrompt
          approval={pendingApproval}
          onSubmitDecision={handleApprovalDecision}
        />

        <div className="flex-1 overflow-hidden">
          <LiveTrace messages={messages} isConnected={isConnected} />
        </div>
      </div>
    </div>
  );
}

export default App;