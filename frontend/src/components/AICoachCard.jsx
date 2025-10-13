import React from 'react';

const AICoachCard = ({ explanation, suggestions, onRegenerate, loading }) => {
  return (
    <div className="bg-gradient-to-br from-[#667eea] to-[#764ba2] rounded-2xl p-6 text-white shadow-lg mb-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">✨</span>
        <span className="text-lg font-bold">AI Coach mmary</span>
      </div>
      
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        </div>
      ) : (
        <>
          <div className="text-base leading-relaxed mb-5">
            {explanation || "Loading your personalized insights..."}
          </div>
          
          {suggestions && suggestions.length > 0 && (
            <div className="bg-white/15 backdrop-blur-md rounded-xl p-4 border border-white/30 mb-4">
              <div className="text-xs font-semibold mb-2 opacity-90">Suggestions:</div>
              {suggestions.map((suggestion, index) => (
                <div key={index} className="flex items-start gap-2 mb-1.5 last:mb-0">
                  <div className="w-1 h-1 bg-white rounded-full flex-shrink-0 mt-1.5"></div>
                  <div className="text-sm leading-relaxed">{suggestion}</div>
                </div>
              ))}
            </div>
          )}
          
          <button
            onClick={onRegenerate}
            disabled={loading}
            className="px-5 py-2.5 bg-white/20 border border-white/40 rounded-lg font-semibold text-xs hover:bg-white/30 transition-all disabled:opacity-50"
          >
            Regenerate Insight
          </button>
        </>
      )}
    </div>
  );
};

export default AICoachCard;
