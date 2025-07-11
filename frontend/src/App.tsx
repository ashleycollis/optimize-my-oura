import { useEffect, useMemo, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { fetchDailySleep, fetchDailyActivity, fetchDailyReadiness } from './api'
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'

function App() {
  const [sleep, setSleep] = useState<any[]>([])
  const [activity, setActivity] = useState<any[]>([])
  const [readiness, setReadiness] = useState<any[]>([])

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
