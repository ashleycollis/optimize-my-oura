import { useEffect, useMemo, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { fetchDailySleep, fetchDailyActivity, fetchDailyReadiness, askQuestion } from './api'
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'

function App() {
  const [sleep, setSleep] = useState<any[]>([])
  const [activity, setActivity] = useState<any[]>([])
  const [readiness, setReadiness] = useState<any[]>([])
  const [question, setQuestion] = useState<string>("")
  const [answer, setAnswer] = useState<string>("")
  const [loadingQA, setLoadingQA] = useState<boolean>(false)

  useEffect(() => {
    fetchDailySleep().then((d) => setSleep(d?.data ?? []))
    fetchDailyActivity().then((d) => setActivity(d?.data ?? []))
    fetchDailyReadiness().then((d) => setReadiness(d?.data ?? []))
  }, [])

  const sleepChart = useMemo(() => sleep.map((s: any) => ({ day: s.day, score: s.score })), [sleep])
  const readinessChart = useMemo(() => readiness.map((r: any) => ({ day: r.day, score: r.score })), [readiness])
  const activityChart = useMemo(() => activity.map((a: any) => ({ day: a.day, score: a.score })), [activity])

  return (
    <div style={{ padding: 24 }}>
      <h1>Optimize My Oura</h1>
      <p>Simple dashboard: Sleep, Readiness, Activity (daily scores)</p>

      <section style={{ marginBottom: 24 }}>
        <h2>Ask a question</h2>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., average sleep score last 30 days"
            style={{ flex: 1, padding: 8, fontSize: 14 }}
          />
          <button
            onClick={async () => {
              if (!question.trim()) return
              setLoadingQA(true)
              try {
                const res = await askQuestion(question.trim())
                setAnswer(res?.answer ?? 'No answer')
              } catch (e) {
                setAnswer('Sorry, something went wrong.')
              } finally {
                setLoadingQA(false)
              }
            }}
            disabled={loadingQA}
            style={{ padding: '8px 12px' }}
          >
            {loadingQA ? 'Asking…' : 'Ask'}
          </button>
        </div>
        {answer && (
          <div style={{ marginTop: 8, padding: 8, background: '#f6f8fa', borderRadius: 6 }}>
            <strong>Answer:</strong> {answer}
          </div>
        )}
      </section>

      <section>
        <h2>Sleep Score</h2>
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer>
            <LineChart data={sleepChart} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" minTickGap={16} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="score" stroke="#8884d8" name="Sleep" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section>
        <h2>Readiness Score</h2>
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer>
            <LineChart data={readinessChart} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" minTickGap={16} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="score" stroke="#82ca9d" name="Readiness" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section>
        <h2>Activity Score</h2>
        <div style={{ width: '100%', height: 280 }}>
          <ResponsiveContainer>
            <LineChart data={activityChart} margin={{ top: 10, right: 20, bottom: 0, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" minTickGap={16} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="score" stroke="#ffc658" name="Activity" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  )
}

export default App
