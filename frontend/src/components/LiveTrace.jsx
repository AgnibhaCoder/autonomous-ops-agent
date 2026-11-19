import React, { useEffect, useRef } from 'react';

export const LiveTrace = ({ messages, isConnected }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 bg-slate-800/80 border-b border-slate-700">
        <h2 className="text-sm font-semibold text-slate-200">Execution Trace Stream</h2>
        <div className="flex items-center gap-2 text-xs">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-rose-500'}`} />
          <span className="text-slate-400">{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-3 font-mono text-xs">
        {messages.length === 0 ? (
          <p className="text-slate-500 italic font-sans text-sm">No trace logs yet. Select or trigger a task to start execution.</p>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className="p-3 bg-slate-950 rounded-lg border border-slate-800/80">
              <div className="text-slate-400 font-semibold mb-1 uppercase tracking-wider text-[10px]">
                [{msg.type || 'EVENT'}]
              </div>
              <pre className="text-slate-200 whitespace-pre-wrap break-words">
                {typeof msg.payload === 'object' ? JSON.stringify(msg.payload, null, 2) : msg.payload}
              </pre>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};