import React from 'react';

const Header = ({ lastSynced, onSync, syncing }) => {
  return (
    <div className="bg-white px-6 py-5 border-b border-gray-200">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center text-white font-bold text-lg shadow-md">
            O
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-[#667eea] to-[#764ba2] bg-clip-text text-transparent">
            Optimize My Oura
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-green-600 font-medium">
            <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
            Synced {lastSynced}
          </div>
          <button
            onClick={onSync}
            disabled={syncing}
            className="px-4 py-2 bg-gradient-to-r from-[#667eea] to-[#764ba2] text-white text-xs font-semibold rounded-lg hover:shadow-md hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {syncing ? (
              <>
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                Syncing...
              </>
            ) : (
              'Sync Now'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Header;
