import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import AICoachCard from './components/AICoachCard';
import ScoreCard from './components/ScoreCard';
import TrendChart from './components/TrendChart';
import PatternCard from './components/PatternCard';
import ChatBox from './components/ChatBox';
import { apiService } from './services/api';

function App() {
  // State
  const [metrics, setMetrics] = useState([]);
  const [coachSummary, setCoachSummary] = useState({
    explanation: '',
    suggestions: []
  });
  const [trendInsight, setTrendInsight] = useState(null);
  const [chatResponse, setChatResponse] = useState('');
  const [loading, setLoading] = useState({
    metrics: false,
    coach: false,
    trend: false,
    chat: false,
  });
  const [lastSynced, setLastSynced] = useState('just now');
  const [selectedMetric, setSelectedMetric] = useState('readiness'); // 'readiness', 'sleep', or 'activity'

  // Load data on mount
  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    await Promise.all([
      fetchMetrics(),
      fetchCoachSummary(),
      fetchTrendInsight(),
    ]);
  };

  const fetchMetrics = async () => {
    setLoading(prev => ({ ...prev, metrics: true }));
    try {
      const data = await apiService.getMetrics();
      setMetrics(data.metrics || []);
      setLastSynced('just now');
    } catch (error) {
      console.error('Error fetching metrics:', error);
      // Use mock data for demo
      setMetrics(generateMockMetrics());
    } finally {
      setLoading(prev => ({ ...prev, metrics: false }));
    }
  };

  const fetchCoachSummary = async (force = false) => {
    setLoading(prev => ({ ...prev, coach: true }));
    try {
      const data = await apiService.getCoachSummary(force);
      setCoachSummary(data);
    } catch (error) {
      console.error('Error fetching coach summary:', error);
      // Use mock data for demo
      setCoachSummary({
        explanation: "You're trending up in sleep but down in movement. Your body is recovering well but needs more activity today.",
        suggestions: [
          "Try a 20-min walk before noon",
          "Aim for lights out by 10:15 PM tonight"
        ]
      });
    } finally {
      setLoading(prev => ({ ...prev, coach: false }));
    }
  };

  const fetchTrendInsight = async () => {
    setLoading(prev => ({ ...prev, trend: true }));
    try {
      const data = await apiService.getTrendInsight();
      setTrendInsight(data);
    } catch (error) {
      console.error('Error fetching trend insight:', error);
      setTrendInsight({
        summary: "Sleep improving steadily.",
        takeaways: [
          "Up 8 points from last week.",
          "Activity dipped on Thursday and Friday—consider light movement today."
        ]
      });
    } finally {
      setLoading(prev => ({ ...prev, trend: false }));
    }
  };

  const handleRegenerateCoach = async () => {
    await fetchCoachSummary(true); // force=true to bypass cache
  };

  const handleSendChat = async (message) => {
    setLoading(prev => ({ ...prev, chat: true }));
    setChatResponse('');
    try {
      const data = await apiService.sendChatMessage(message);
      setChatResponse(data.response);
    } catch (error) {
      console.error('Error sending chat:', error);
      setChatResponse("I'm having trouble processing that question right now. Please try again.");
    } finally {
      setLoading(prev => ({ ...prev, chat: false }));
    }
  };

  // Calculate 30-day average scores from all metrics
  const calculate30DayAverage = (scoreKey) => {
    if (!metrics.length) return 0;
    const total = metrics.reduce((sum, m) => sum + (m[scoreKey] || 0), 0);
    return Math.round(total / metrics.length);
  };
  
  const scores = {
    readiness: calculate30DayAverage('readiness_score') || 78,
    sleep: calculate30DayAverage('sleep_score') || 85,
    activity: calculate30DayAverage('activity_score') || 72,
  };

  // Calculate patterns
  const patterns = calculatePatterns(metrics);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#667eea] to-[#764ba2] py-12 px-8 pb-24">
      <div className="max-w-6xl mx-auto rounded-3xl shadow-2xl">
        <div className="bg-white rounded-t-3xl">
          <Header lastSynced={lastSynced} />
        </div>
        
        <div className="px-8 pt-8 pb-24 bg-gray-50 rounded-b-3xl">
          <AICoachCard
            explanation={coachSummary.explanation}
            suggestions={coachSummary.suggestions}
            onRegenerate={handleRegenerateCoach}
            loading={loading.coach}
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
            <ScoreCard
              label="Readiness"
              value={scores.readiness}
              meta="Your 30-day average"
              type="readiness"
              isSelected={selectedMetric === 'readiness'}
              onClick={() => setSelectedMetric('readiness')}
            />
            <ScoreCard
              label="Sleep Score"
              value={scores.sleep}
              meta="Your 30-day average"
              type="sleep"
              isSelected={selectedMetric === 'sleep'}
              onClick={() => setSelectedMetric('sleep')}
            />
            <ScoreCard
              label="Activity"
              value={scores.activity}
              meta="Your 30-day average"
              type="activity"
              isSelected={selectedMetric === 'activity'}
              onClick={() => setSelectedMetric('activity')}
            />
          </div>

          <TrendChart
            metrics={metrics.slice(0, 7)}
            insight={trendInsight}
            loading={loading.trend}
            metricType={selectedMetric}
          />

          <h2 className="text-xl font-bold text-gray-900 mb-5 mt-8">Your Patterns</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
            <PatternCard
              icon="🛏️"
              label="Optimal Sleep"
              value={patterns.optimalSleep}
            />
            <PatternCard
              icon="🌙"
              label="Best Bedtime"
              value={patterns.bestBedtime}
            />
            <PatternCard
              icon="👟"
              label="Daily Steps"
              value={patterns.avgSteps}
            />
          </div>

          <ChatBox
            onSendMessage={handleSendChat}
            response={chatResponse}
            loading={loading.chat}
          />
        </div>
      </div>
    </div>
  );
}

// Helper functions
function calculatePatterns(metrics) {
  if (!metrics.length) {
    return {
      optimalSleep: '7.5h',
      bestBedtime: '10 PM',
      avgSteps: '0',
    };
  }

  const avgSleep = metrics.reduce((sum, m) => sum + (m.sleep_duration || 0), 0) / metrics.length;
  const avgSteps = metrics.reduce((sum, m) => sum + (m.steps || 0), 0) / metrics.length;
  
  // Calculate best bedtime from bedtime_start timestamps
  const bedtimes = metrics
    .filter(m => m.bedtime_start)
    .map(m => {
      const date = new Date(m.bedtime_start);
      return date.getHours() + date.getMinutes() / 60;
    });
  
  let bestBedtime = '10 PM';
  if (bedtimes.length > 0) {
    const avgBedtimeHour = bedtimes.reduce((sum, h) => sum + h, 0) / bedtimes.length;
    const hour = Math.floor(avgBedtimeHour);
    const minute = Math.round((avgBedtimeHour - hour) * 60);
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour > 12 ? hour - 12 : (hour === 0 ? 12 : hour);
    bestBedtime = `${displayHour}:${minute.toString().padStart(2, '0')} ${period}`;
  }

  return {
    optimalSleep: `${avgSleep.toFixed(1)}h`,
    bestBedtime: bestBedtime,
    avgSteps: Math.round(avgSteps).toLocaleString(),
  };
}

function generateMockMetrics() {
  const metrics = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    metrics.push({
      date: date.toISOString().split('T')[0],
      readiness_score: 70 + Math.floor(Math.random() * 20),
      sleep_score: 75 + Math.floor(Math.random() * 20),
      activity_score: 65 + Math.floor(Math.random() * 25),
      sleep_duration: 6.5 + Math.random() * 2,
      hrv: 45 + Math.floor(Math.random() * 20),
    });
  }
  return metrics;
}

export default App;

