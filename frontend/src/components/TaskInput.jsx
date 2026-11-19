import React, { useState } from 'react';

export const TaskInput = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSubmit(prompt);
    setPrompt('');
  };

  return (
    <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-md">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <label htmlFor="prompt" className="text-sm font-semibold text-slate-200">
          Agent Task / Goal
        </label>
        <textarea
          id="prompt"
          rows={3}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., Read sandbox/sample_repo/config.json, update the max_retries key to 5, and commit changes."
          className="w-full p-3 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm resize-none"
        />
        <button
          type="submit"
          disabled={isLoading || !prompt.trim()}
          className="self-end px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {isLoading ? 'Submitting...' : 'Run Agent Task'}
        </button>
      </form>
    </div>
  );
};