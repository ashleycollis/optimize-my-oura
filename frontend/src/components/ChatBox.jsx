import React, { useState } from 'react';

const ChatBox = ({ onSendMessage, response, loading }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <h3 className="text-lg font-bold text-gray-900 mb-5">Ask Your AI Coach</h3>
      
      {response && (
        <div className="bg-gray-50 rounded-xl p-4 mb-5 border-l-4 border-[#667eea]">
          <p className="text-sm text-gray-700 leading-relaxed break-words whitespace-pre-wrap">
            {response}
          </p>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask about your health data..."
          className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#667eea] focus:outline-none transition-colors text-sm"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="px-6 py-3 bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white font-semibold text-sm rounded-xl hover:shadow-lg hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </form>
    </div>
  );
};

export default ChatBox;
