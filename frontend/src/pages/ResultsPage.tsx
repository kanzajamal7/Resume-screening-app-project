import { useState } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import {
  downloadJsonReport,
  downloadMarkdownReport,
  downloadPdfReport,
} from '../api/client'
import { AnalysisResult } from '../types'
import {
  RadialBarChart,
  RadialBar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts'

export default function ResultsPage() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const location = useLocation()
  const navigate = useNavigate()
  const [downloading, setDownloading] = useState(false)

  const result: AnalysisResult | undefined = location.state?.result

  if (!result) {
    return (
      <div className="text-center">
        <p className="text-red-600 mb-4">No analysis results found</p>
        <button
          onClick={() => navigate('/')}
          className="button-primary"
        >
          Back to Analysis
        </button>
      </div>
    )
  }

  const handleDownload = async (format: 'json' | 'markdown' | 'pdf') => {
    if (!analysisId) return

    setDownloading(true)
    try {
      let blob: Blob
      const timestamp = new Date().toISOString().split('T')[0]
      const filename = `ats-report-${timestamp}`

      if (format === 'json') {
        blob = await downloadJsonReport(analysisId)
        downloadFile(blob, `${filename}.json`)
      } else if (format === 'markdown') {
        blob = await downloadMarkdownReport(analysisId)
        downloadFile(blob, `${filename}.md`)
      } else {
        blob = await downloadPdfReport(analysisId)
        downloadFile(blob, `${filename}.pdf`)
      }
    } catch (error) {
      alert(`Failed to download ${format} report`)
    } finally {
      setDownloading(false)
    }
  }

  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  const getScoreColor = (score: number) => {
    if (score >= 75) return '#10b981' // green
    if (score >= 50) return '#f59e0b' // yellow
    return '#ef4444' // red
  }

  const getLabelColor = (label: string) => {
    if (label === 'STRONG_MATCH') return 'bg-green-100 text-green-800'
    if (label === 'MEDIUM_MATCH') return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  const categoryNames: Record<string, string> = {
    keyword_skills: 'Keywords & Skills',
    experience_relevance: 'Experience Relevance',
    role_match: 'Role/Title Match',
    seniority_match: 'Seniority/Years',
    education_match: 'Education/Certs',
    tooling_stack_match: 'Tooling/Stack',
    recency_match: 'Recency',
    red_flags: 'Red Flags',
  }

  // Prepare data for charts
  const scoreData = [{
    name: 'Score',
    value: result.overall_score,
    fill: getScoreColor(result.overall_score),
  }]

  const categoryData = Object.entries(result.categories).map(([key, category]) => ({
    name: categoryNames[key] || key,
    score: Math.round(category.score),
    fill: getScoreColor(category.score),
  }))

  const mustHaveMatched = result.must_have.filter(kw => kw.matched).length
  const mustHaveTotal = result.must_have.length
  const niceToHaveMatched = result.nice_to_have.filter(kw => kw.matched).length
  const niceToHaveTotal = result.nice_to_have.length

  const keywordMatchData = [
    {
      name: 'Must-Have Keywords',
      matched: mustHaveMatched,
      missing: mustHaveTotal - mustHaveMatched,
    },
    {
      name: 'Nice-to-Have Keywords',
      matched: niceToHaveMatched,
      missing: niceToHaveTotal - niceToHaveMatched,
    },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header with Score Gauge */}
      <div className="card mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left: Score Gauge */}
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">Overall Match Score</h2>
            <ResponsiveContainer width="100%" height={250}>
              <RadialBarChart
                cx="50%"
                cy="50%"
                innerRadius="60%"
                outerRadius="100%"
                barSize={30}
                data={scoreData}
                startAngle={180}
                endAngle={0}
              >
                <RadialBar
                  minAngle={15}
                  background
                  clockWise
                  dataKey="value"
                />
                <text
                  x="50%"
                  y="50%"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="text-5xl font-bold"
                  fill={getScoreColor(result.overall_score)}
                >
                  {result.overall_score}
                </text>
              </RadialBarChart>
            </ResponsiveContainer>
            <div className={`inline-block ${getLabelColor(result.label)} px-6 py-2 rounded-lg text-xl font-semibold mt-4`}>
              {result.label.replace(/_/g, ' ')}
            </div>
          </div>

          {/* Right: Download Buttons */}
          <div className="flex flex-col justify-center">
            <h3 className="text-2xl font-bold mb-4">Export Results</h3>
            <div className="space-y-3">
              <button
                onClick={() => handleDownload('pdf')}
                disabled={downloading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 transition"
              >
                Download PDF Report
              </button>
              <button
                onClick={() => handleDownload('json')}
                disabled={downloading}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 transition"
              >
                Download JSON Data
              </button>
              <button
                onClick={() => handleDownload('markdown')}
                disabled={downloading}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg disabled:opacity-50 transition"
              >
                Download Markdown
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Category Breakdown Chart */}
      <div className="card mb-8">
        <h3 className="text-2xl font-bold mb-6">Category Breakdown</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={categoryData} layout="horizontal">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis dataKey="name" type="category" width={150} />
            <Tooltip />
            <Bar dataKey="score" radius={[0, 8, 8, 0]}>
              {categoryData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Keyword Matching Chart */}
      <div className="card mb-8">
        <h3 className="text-2xl font-bold mb-6">Keyword Matching Overview</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={keywordMatchData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="matched" stackId="a" fill="#10b981" name="Matched" />
            <Bar dataKey="missing" stackId="a" fill="#ef4444" name="Missing" />
          </BarChart>
        </ResponsiveContainer>
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className="text-3xl font-bold text-green-600">{mustHaveMatched}/{mustHaveTotal}</div>
            <div className="text-sm text-gray-600 mt-1">Must-Have Keywords Matched</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className="text-3xl font-bold text-blue-600">{niceToHaveMatched}/{niceToHaveTotal}</div>
            <div className="text-sm text-gray-600 mt-1">Nice-to-Have Keywords Matched</div>
          </div>
        </div>
      </div>

      {/* Detailed Category Cards */}
      <div className="card mb-8">
        <h3 className="text-2xl font-bold mb-6">Detailed Category Scores</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(result.categories).map(([key, category]) => (
            <div key={key} className="border rounded-lg p-4 bg-gray-50">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-lg">{categoryNames[key]}</h4>
                <div className="text-2xl font-bold" style={{ color: getScoreColor(category.score) }}>
                  {category.score.toFixed(1)}
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
                <div
                  className="h-3 rounded-full transition-all"
                  style={{
                    width: `${category.score}%`,
                    backgroundColor: getScoreColor(category.score),
                  }}
                ></div>
              </div>

              {/* Evidence */}
              {category.evidence && category.evidence.length > 0 && (
                <div className="text-sm text-gray-700 space-y-1 max-h-32 overflow-y-auto">
                  {category.evidence.slice(0, 3).map((ev, i) => (
                    <p key={i} className="truncate" title={ev}>• {ev}</p>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Keyword Lists */}
      <div className="card mb-8">
        <h3 className="text-2xl font-bold mb-6">Keyword Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Must-Have */}
          <div>
            <h4 className="font-bold text-lg mb-4 flex items-center">
              <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm mr-2">Required</span>
              Must-Have Keywords
            </h4>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {result.must_have.map((kw, i) => (
                <div key={i} className={`flex items-center p-3 rounded-lg ${kw.matched ? 'bg-green-50' : 'bg-red-50'}`}>
                  <span className={`text-2xl mr-3 ${kw.matched ? 'text-green-600' : 'text-red-600'}`}>
                    {kw.matched ? '✓' : '✗'}
                  </span>
                  <span className={`font-medium ${kw.matched ? 'text-gray-800' : 'text-gray-500'}`}>
                    {kw.term}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Nice-to-Have */}
          <div>
            <h4 className="font-bold text-lg mb-4 flex items-center">
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm mr-2">Optional</span>
              Nice-to-Have Keywords
            </h4>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {result.nice_to_have.map((kw, i) => (
                <div key={i} className={`flex items-center p-3 rounded-lg ${kw.matched ? 'bg-green-50' : 'bg-gray-50'}`}>
                  <span className={`text-2xl mr-3 ${kw.matched ? 'text-green-600' : 'text-gray-400'}`}>
                    {kw.matched ? '✓' : '○'}
                  </span>
                  <span className={`font-medium ${kw.matched ? 'text-gray-800' : 'text-gray-500'}`}>
                    {kw.term}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Red Flags */}
      {result.red_flags && result.red_flags.length > 0 && (
        <div className="card mb-8 bg-red-50 border-2 border-red-200">
          <h3 className="text-2xl font-bold mb-4 text-red-700 flex items-center">
            <span className="text-3xl mr-2">⚠️</span>
            Red Flags Detected
          </h3>
          <ul className="space-y-2">
            {result.red_flags.map((flag, i) => (
              <li key={i} className="flex items-start bg-white p-3 rounded-lg">
                <span className="text-red-600 mr-2 text-xl">•</span>
                <span className="text-gray-800">{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      <div className="card mb-8">
        <h3 className="text-2xl font-bold mb-6">Recommendations</h3>

        {result.actions.good_fit_summary && result.actions.good_fit_summary.length > 0 && (
          <div className="mb-6 bg-green-50 p-6 rounded-lg border-l-4 border-green-500">
            <h4 className="font-bold text-lg mb-3 text-green-700 flex items-center">
              <span className="text-2xl mr-2">✓</span>
              Strengths
            </h4>
            <ul className="space-y-2">
              {result.actions.good_fit_summary.map((item, i) => (
                <li key={i} className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.actions.gaps && result.actions.gaps.length > 0 && (
          <div className="mb-6 bg-red-50 p-6 rounded-lg border-l-4 border-red-500">
            <h4 className="font-bold text-lg mb-3 text-red-700 flex items-center">
              <span className="text-2xl mr-2">✗</span>
              Gaps to Address
            </h4>
            <ul className="space-y-2">
              {result.actions.gaps.map((item, i) => (
                <li key={i} className="flex items-start">
                  <span className="text-red-600 mr-2">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.actions.resume_tailoring_suggestions &&
          result.actions.resume_tailoring_suggestions.length > 0 && (
            <div className="mb-6 bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
              <h4 className="font-bold text-lg mb-3 text-blue-700 flex items-center">
                <span className="text-2xl mr-2">💡</span>
                Tailoring Suggestions
              </h4>
              <ul className="space-y-2">
                {result.actions.resume_tailoring_suggestions.map((item, i) => (
                  <li key={i} className="flex items-start">
                    <span className="text-blue-600 mr-2">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

        {result.actions.ats_keywords_to_add && result.actions.ats_keywords_to_add.length > 0 && (
          <div className="bg-purple-50 p-6 rounded-lg border-l-4 border-purple-500">
            <h4 className="font-bold text-lg mb-3 text-purple-700 flex items-center">
              <span className="text-2xl mr-2">🔑</span>
              Keywords to Consider Adding
            </h4>
            <div className="flex flex-wrap gap-2">
              {result.actions.ats_keywords_to_add.map((keyword, i) => (
                <span key={i} className="bg-purple-200 text-purple-900 px-4 py-2 rounded-full text-sm font-medium">
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="card text-center">
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg text-lg transition"
        >
          Analyze Another Resume
        </button>
      </div>
    </div>
  )
}
