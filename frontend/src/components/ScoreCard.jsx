import React from 'react';

const ScoreCard = ({ label, value, meta, type, isSelected, onClick }) => {
  const colors = {
    readiness: {
      border: 'border-l-blue-500',
      text: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    sleep: {
      border: 'border-l-purple-500',
      text: 'text-purple-600',
      bg: 'bg-purple-50',
    },
    activity: {
      border: 'border-l-green-500',
      text: 'text-green-600',
      bg: 'bg-green-50',
    },
  };

  const color = colors[type] || colors.readiness;

  return (
    <div 
      onClick={onClick}
      className={`${isSelected ? color.bg : 'bg-white'} rounded-2xl p-6 shadow-sm border-l-4 ${color.border} hover:shadow-lg hover:-translate-y-1 transition-all duration-300 cursor-pointer ${isSelected ? 'ring-2 ring-offset-2 ring-' + type : ''}`}
    >
      <div className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3">
        {label}
      </div>
      <div className={`text-5xl font-bold ${color.text} mb-2 leading-none`}>
        {value}
      </div>
      <div className="text-xs text-gray-600">
        {meta}
      </div>
    </div>
  );
};

export default ScoreCard;
