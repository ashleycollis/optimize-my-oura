import React from 'react';

const PatternCard = ({ icon, label, value }) => {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm text-center hover:shadow-lg hover:-translate-y-2 transition-all duration-300">
      <div className="text-3xl mb-3">{icon}</div>
      <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-2">
        {label}
      </div>
      <div className="text-2xl font-bold bg-gradient-to-r from-[#667eea] to-[#764ba2] bg-clip-text text-transparent">
        {value}
      </div>
    </div>
  );
};

export default PatternCard;
