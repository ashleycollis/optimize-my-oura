import React from 'react';

const WorkoutCard = ({ workout }) => {
  const { activity, day, duration_minutes, calories, intensity } = workout;
  
  const date = new Date(day);
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  
  const intensityColors = {
    'easy': 'text-green-600 bg-green-50',
    'moderate': 'text-blue-600 bg-blue-50',
    'hard': 'text-red-600 bg-red-50',
  };
  
  const intensityClass = intensityColors[intensity] || 'text-gray-600 bg-gray-50';
  
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="font-semibold text-gray-900 capitalize">{activity.replace('_', ' ')}</div>
          <div className="text-xs text-gray-500">{dateStr}</div>
        </div>
        {intensity && (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${intensityClass}`}>
            {intensity}
          </span>
        )}
      </div>
      
      <div className="flex gap-4 text-sm">
        {duration_minutes && (
          <div className="font-medium text-gray-700">{duration_minutes} min</div>
        )}
        {calories && (
          <div className="font-medium text-gray-700">{Math.round(calories)} cal</div>
        )}
      </div>
    </div>
  );
};

export default WorkoutCard;

