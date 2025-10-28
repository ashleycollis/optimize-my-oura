import React from 'react';

const AICoachCard = ({ coachData, onRegenerate, loading }) => {
  return (
    <div className="bg-gradient-to-br from-[#667eea] to-[#764ba2] rounded-2xl p-6 text-white shadow-lg mb-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg font-bold">AI Coach Summary</span>
      </div>
      
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        </div>
      ) : (
        <>
          {/* Main Summary */}
          <div className="text-base font-semibold leading-relaxed mb-5">
            {coachData?.summary || "Loading your personalized insights..."}
          </div>

          {/* Receipts (The Numbers) */}
          {coachData?.receipts && Array.isArray(coachData.receipts) && coachData.receipts.length > 0 && (
            <div className="bg-white/20 backdrop-blur-md rounded-xl p-4 border border-white/30 mb-4">
              <div className="text-xs font-bold mb-2 opacity-90">THE NUMBERS</div>
              <ul className="space-y-1">
                {coachData.receipts.map((receipt, idx) => (
                  <li key={idx} className="text-sm leading-relaxed">• {receipt}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Why It Matters */}
          {coachData?.why_it_matters && (
            <div className="text-sm italic leading-relaxed mb-4 border-l-4 border-white/40 pl-4 opacity-90">
              {coachData.why_it_matters}
            </div>
          )}

          {/* Moves for This Week */}
          {coachData?.moves_for_this_week && (
            <div className="bg-white/20 backdrop-blur-md rounded-xl p-4 border border-white/30 mb-4 space-y-3">
              <div className="text-sm font-bold">YOUR MOVES THIS WEEK</div>
              
              {coachData.moves_for_this_week.non_negotiables && Array.isArray(coachData.moves_for_this_week.non_negotiables) && (
                <div>
                  <div className="text-xs font-semibold mb-2 opacity-90">Non-Negotiables:</div>
                  <ul className="space-y-1.5">
                    {coachData.moves_for_this_week.non_negotiables.map((item, idx) => (
                      <li key={idx} className="text-sm flex items-start gap-2">
                        <span className="flex-shrink-0">✓</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                {coachData.moves_for_this_week.training && (
                  <div>
                    <div className="font-semibold mb-1">Training:</div>
                    <div className="opacity-90">{coachData.moves_for_this_week.training}</div>
                  </div>
                )}
                {coachData.moves_for_this_week.nutrition && (
                  <div>
                    <div className="font-semibold mb-1">Nutrition:</div>
                    <div className="opacity-90">{coachData.moves_for_this_week.nutrition}</div>
                  </div>
                )}
                {coachData.moves_for_this_week.recovery && (
                  <div>
                    <div className="font-semibold mb-1">Recovery:</div>
                    <div className="opacity-90">{coachData.moves_for_this_week.recovery}</div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Watchouts */}
          {coachData?.watchouts && Array.isArray(coachData.watchouts) && coachData.watchouts.length > 0 && (
            <div className="bg-yellow-500/30 backdrop-blur-md rounded-xl p-4 border border-yellow-400/40 mb-4">
              <div className="text-xs font-bold mb-2">WATCH OUT FOR</div>
              <ul className="space-y-1">
                {coachData.watchouts.map((item, idx) => (
                  <li key={idx} className="text-sm">{item}</li>
                ))}
              </ul>
            </div>
          )}

          {/* 1% Upgrade */}
          {coachData?.one_percent_upgrade && (
            <div className="bg-green-500/30 backdrop-blur-md rounded-xl p-4 border border-green-400/40 mb-4">
              <div className="text-xs font-bold mb-1">1% UPGRADE</div>
              <p className="text-sm">{coachData.one_percent_upgrade}</p>
            </div>
          )}

          {/* Data Missing Info */}
          {coachData?.if_data_missing && coachData.if_data_missing.reason_for_gap && (
            <div className="bg-white/10 rounded-xl p-3 text-xs mb-4">
              <strong>Data Gap:</strong> {coachData.if_data_missing.reason_for_gap}
              {coachData.if_data_missing.quick_fix && (
                <div className="mt-1"><strong>Fix:</strong> {coachData.if_data_missing.quick_fix}</div>
              )}
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
