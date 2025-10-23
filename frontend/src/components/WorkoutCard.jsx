import React from 'react';

const WorkoutCard = ({ workout }) => {
  const { activity, day, duration_minutes, calories, intensity } = workout;
  
  const date = new Date(day);
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  
  const activityEmoji = {
    'walking': '🚶',
    'running': '🏃',
    'cycling': '🚴',
    'swimming': '🏊',
    'strength_training': '💪',
    'yoga': '🧘',
    'hiking': '🥾',
    'default': '🏃'
  };
  
  const emoji = activityEmoji[activity] || activityEmoji['default'];
  
  const intensityColors = {
    'easy': 'text-green-600 bg-green-50',
    'moderate': 'text-blue-600 bg-blue-50',
    'hard': 'text-red-600 bg-red-50',
  };
  
  const intensityClass = intensityColors[intensity] || 'text-gray-600 bg-gray-50';
  
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{emoji}</span>
          <div>
            <div className="font-semibold text-gray-900 capitalize">{activity.replace('_', ' ')}</div>
            <div className="text-xs text-gray-500">{dateStr}</div>
          </div>
        </div>
        {intensity && (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${intensityClass}`}>
            {intensity}
          </span>
        )}
      </div>
      
      <div className="flex gap-4 text-sm">
        {duration_minutes && (
          <div className="flex items-center gap-1">
            <span className="text-gray-500">⏱️</span>
            <span className="font-medium text-gray-700">{duration_minutes} min</span>
          </div>
        )}
        {calories && (
          <div className="flex items-center gap-1">
            <span className="text-gray-500">🔥</span>
            <span className="font-medium text-gray-700">{Math.round(calories)} cal</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkoutCard;

