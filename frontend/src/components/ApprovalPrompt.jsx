import React, { useState } from 'react';

export const ApprovalPrompt = ({ approval, onSubmitDecision }) => {
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!approval) return null;

  const handleAction = async (approved) => {
    setIsSubmitting(true);
    await onSubmitDecision(approval.approval_id, approved, reason);
    setIsSubmitting(false);
    setReason('');
  };

  return (
    <div className="my-4 p-5 bg-amber-950/40 border border-amber-600/50 rounded-xl shadow-lg">
      <div className="flex items-center gap-2 mb-3 text-amber-400 font-semibold text-base">
        <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse"></span>
        Human Approval Required
      </div>
      
      <p className="text-sm text-slate-300 mb-2">
        <strong>Tool:</strong> <code className="bg-slate-800 px-1.5 py-0.5 rounded text-amber-300">{approval.tool_name}</code>
      </p>

      <div className="mb-4">
        <p className="text-xs text-slate-400 mb-1">Proposed Input Payload:</p>
        <pre className="p-3 bg-slate-900 rounded-lg text-xs text-slate-200 overflow-x-auto border border-slate-800">
          {JSON.stringify(approval.tool_input, null, 2)}
        </pre>
      </div>

      <div className="mb-4">
        <input
          type="text"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Rejection reason or adjustments (optional if approving)..."
          className="w-full p-2.5 bg-slate-900 border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-amber-500"
        />
      </div>

      <div className="flex justify-end gap-3">
        <button
          onClick={() => handleAction(false)}
          disabled={isSubmitting}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-lg transition-colors disabled:opacity-50"
        >
          Reject Action
        </button>
        <button
          onClick={() => handleAction(true)}
          disabled={isSubmitting}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition-colors disabled:opacity-50"
        >
          Approve Action
        </button>
      </div>
    </div>
  );
};