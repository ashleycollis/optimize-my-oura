import React from 'react';

const TrendChart = ({ metrics, insight, loading, metricType = 'readiness', timeRange = 7 }) => {
  if (!metrics || metrics.length === 0) {
    return null;
  }

  const metricConfig = {
    readiness: {
      key: 'readiness_score',
      label: 'Readiness',
      color: 'from-blue-400 to-blue-600',
    },
    sleep: {
      key: 'sleep_score',
      label: 'Sleep Score',
      color: 'from-purple-400 to-purple-600',
    },
    activity: {
      key: 'activity_score',
      label: 'Activity',
      color: 'from-green-400 to-green-600',
    },
  };

  const config = metricConfig[metricType] || metricConfig.readiness;
  const maxValue = Math.max(...metrics.map(m => m[config.key] || 0), 100);
  
  // reverse to show oldest->newest, backend sends newest first
  const orderedMetrics = [...metrics].reverse();
  
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm mb-8">
      <div className="mb-5">
        <h3 className="text-lg font-bold text-gray-900 mb-2">{timeRange}-Day Trend - {config.label}</h3>
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
      
      <div className="h-56 bg-gradient-to-b from-purple-50 to-transparent rounded-xl p-4 flex items-end gap-2">
        {orderedMetrics.map((metric, index) => {
          const scoreValue = metric[config.key];
          const height = scoreValue ? (scoreValue / maxValue) * 100 : 20;
          // parse date this way to avoid timezone issues
          const [year, month, day] = metric.date.split('-').map(Number);
          const date = new Date(year, month - 1, day);
          const dayLabel = date.toLocaleDateString('en-US', { weekday: 'short' });
          const dateLabel = date.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric' });
          
          return (
            <div key={index} className="flex-1 flex flex-col items-center justify-end" style={{ height: '100%' }}>
              <div
                className={`w-full bg-gradient-to-t ${config.color} rounded-t-lg opacity-80 hover:opacity-100 hover:scale-105 transition-all cursor-pointer relative flex items-start justify-center pt-2`}
                style={{ height: `${height}%`, minHeight: '20%' }}
                title={`${metric.date}: ${scoreValue || 'N/A'}`}
              >
                <span className="text-xs font-bold text-white drop-shadow-lg">
                  {scoreValue || '-'}
                </span>
              </div>
              <div className="mt-2 text-center">
                <div className="text-xs font-semibold text-gray-700">{dayLabel}</div>
                <div className="text-xs text-gray-500">{dateLabel}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TrendChart;
