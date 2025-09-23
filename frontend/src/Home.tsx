import { useEffect, useState } from 'react'

export default function Home() {
  const [health, setHealth] = useState<string>('checking...')

  useEffect(() => {
    fetch('/api/health/')
      .then((r) => r.json())
      .then((d) => setHealth(d.status ?? 'ok'))
      .catch(() => setHealth('unreachable'))
  }, [])

  return (
    <div style={{ padding: 24 }}>
      <h1>Optimize My Oura</h1>
      <p>Backend health: {health}</p>
      <div style={{ marginTop: 16 }}>
        <a href="/api/auth/oura/login/">
          <button>Connect Oura</button>
        </a>
      </div>
    </div>
  )
}


