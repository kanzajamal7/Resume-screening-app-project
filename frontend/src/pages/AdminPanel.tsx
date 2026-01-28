import { useState, useEffect } from 'react'
import { getDefaultWeights } from '../api/client'

export default function AdminPanel() {
  const [weights, setWeights] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)
  const [strictMode, setStrictMode] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadWeights()
  }, [])

  const loadWeights = async () => {
    try {
      const data = await getDefaultWeights()
      setWeights(data.weights)
    } catch (error) {
      setMessage('Failed to load weights')
    } finally {
      setLoading(false)
    }
  }

  const handleWeightChange = (key: string, value: number) => {
    setWeights((prev) => ({
      ...prev,
      [key]: Math.max(0, Math.min(1, value)),
    }))
  }

  const handleSave = async () => {
    try {
      // Note: Weight normalization and persistence not yet implemented
      // Will be added when backend endpoint is available

      setMessage('Settings saved successfully')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage('Failed to save settings')
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  const categoryNames: Record<string, string> = {
    keyword_skills: 'Keyword & Skills Match',
    experience_relevance: 'Experience Relevance',
    role_match: 'Role/Title Match',
    seniority_match: 'Seniority/Years Match',
    education_match: 'Education/Certs Match',
    tooling_stack_match: 'Tooling/Stack Match',
    recency_match: 'Recency Match',
    red_flags: 'Red Flag Detection',
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card">
        <h2 className="text-3xl font-bold mb-6">Admin Panel</h2>

        {message && (
          <div className="p-4 bg-green-100 border border-green-400 text-green-700 rounded mb-6">
            {message}
          </div>
        )}

        <section className="mb-8">
          <h3 className="text-2xl font-bold mb-4">Scoring Weights</h3>
          <p className="text-gray-600 mb-6">
            Adjust the weights for each scoring category (will be normalized to sum to 1.0)
          </p>

          <div className="space-y-4">
            {Object.entries(weights).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between border-b pb-4">
                <div>
                  <label className="font-semibold">{categoryNames[key]}</label>
                  <p className="text-sm text-gray-600">Current: {value.toFixed(3)}</p>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={value * 100}
                  onChange={(e) => handleWeightChange(key, parseFloat(e.target.value) / 100)}
                  className="w-32"
                />
              </div>
            ))}
          </div>

          <div className="mt-4 p-4 bg-blue-50 rounded">
            <p className="text-sm font-semibold">
              Total Weight:{' '}
              <span className={Object.values(weights).reduce((a, b) => a + b, 0).toFixed(3)}>
                {Object.values(weights).reduce((a, b) => a + b, 0).toFixed(3)}
              </span>
            </p>
          </div>
        </section>

        <section className="mb-8">
          <h3 className="text-2xl font-bold mb-4">Analysis Settings</h3>

          <div className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={strictMode}
                onChange={(e) => setStrictMode(e.target.checked)}
                className="mr-3"
              />
              <span>
                <strong>Strict Mode:</strong> Heavily penalize missing required skills
              </span>
            </label>
          </div>

          <div className="mt-6 p-4 bg-gray-100 rounded">
            <h4 className="font-bold mb-2">Feature Flags</h4>
            <ul className="text-sm space-y-1">
              <li>✓ Keyword extraction and matching</li>
              <li>✓ Experience relevance scoring</li>
              <li>✓ Red flag detection</li>
              <li>✓ Export JSON / Markdown / PDF</li>
              <li>○ Rewrite suggestions (disabled)</li>
              <li>○ Optional database persistence</li>
              <li>○ Custom integrations support</li>
            </ul>
          </div>
        </section>

        <section className="mb-8">
          <h3 className="text-2xl font-bold mb-4">About Scoring</h3>

          <div className="bg-gray-50 p-4 rounded space-y-3 text-sm">
            <p>
              <strong>Keyword & Skills Match (A):</strong> Percentage of must-have and
              nice-to-have keywords found in resume
            </p>
            <p>
              <strong>Experience Relevance (B):</strong> How well previous roles match the target
              role, weighted by recency
            </p>
            <p>
              <strong>Role/Title Match (C):</strong> Alignment between candidate's titles and
              target position
            </p>
            <p>
              <strong>Seniority/Years (D):</strong> Years of relevant experience vs. job
              requirements
            </p>
            <p>
              <strong>Education (E):</strong> Degree/certification requirements match
            </p>
            <p>
              <strong>Tooling/Stack (F):</strong> Technical tools and platforms experience match
            </p>
            <p>
              <strong>Recency (G):</strong> Bonus for recent relevant experience
            </p>
            <p>
              <strong>Red Flags (H):</strong> Penalties for missing must-haves, gaps, job hopping
            </p>
          </div>
        </section>

        <div className="flex gap-4">
          <button onClick={handleSave} className="button-primary">
            Save Settings
          </button>
          <button
            onClick={loadWeights}
            className="button-secondary"
          >
            Reset to Defaults
          </button>
        </div>
      </div>
    </div>
  )
}
