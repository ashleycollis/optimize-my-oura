import React from 'react';

const TrendChart = ({ metrics, insight, loading }) => {
  if (!metrics || metrics.length === 0) {
    return null;
  }

  const maxValue = Math.max(...metrics.map(m => m.readiness_score || 0), 100);
  
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm mb-8">
      <div className="mb-5">
        <h3 className="text-lg font-bold text-gray-900 mb-2">7-Day Trend</h3>
        {loading ? (
          <div className="text-sm text-gray-600">Loading trend analysis...</div>
        ) : insight ? (
          <p className="text-sm text-gray-600 leading-relaxed">
            <strong>{insight.summary}</strong> {insight.takeaways?.join(' ')}
          </p>
        ) : (
          <p className="text-sm text-gray-600 leading-relaxed">
            <strong>Sleep improving steadily.</strong> Up 8 points from last week. Activity dipped—consider light movement today.
          </p>
        )}
      </div>
      
      <div className="h-48 bg-gradient-to-b from-purple-50 to-transparent rounded-xl p-4 flex items-end gap-2">
        {metrics.map((metric, index) => {
          const height = metric.readiness_score ? (metric.readiness_score / maxValue) * 100 : 20;
          return (
            <div
              key={index}
              className="flex-1 bg-gradient-to-t from-[#667eea] to-[#764ba2] rounded-t-lg opacity-80 hover:opacity-100 hover:scale-105 transition-all cursor-pointer"
              style={{ height: `${height}%`, minHeight: '20%' }}
              title={`${metric.date}: ${metric.readiness_score || 'N/A'}`}
            ></div>
          );
        })}
      </div>
    </div>
  );
};

export default TrendChart;
