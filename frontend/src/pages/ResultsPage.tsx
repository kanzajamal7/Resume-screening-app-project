import React, { useState } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import {
  downloadJsonReport,
  downloadMarkdownReport,
  downloadPdfReport,
} from '../api/client'
import { AnalysisResult } from '../types'

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
    if (score >= 75) return 'text-green-600'
    if (score >= 50) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getLabelColor = (label: string) => {
    if (label === 'STRONG_MATCH') return 'bg-green-100 text-green-800'
    if (label === 'MEDIUM_MATCH') return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  const categoryNames: Record<string, string> = {
    keyword_skills: 'A) Keyword & Skills Match',
    experience_relevance: 'B) Experience Relevance',
    role_match: 'C) Role/Title Match',
    seniority_match: 'D) Seniority/Years Match',
    education_match: 'E) Education/Certs Match',
    tooling_stack_match: 'F) Tooling/Stack Match',
    recency_match: 'G) Recency Match',
    red_flags: 'H) Red Flag Detection',
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="card mb-8 text-center">
        <h2 className="text-4xl font-bold mb-4">
          Analysis Results
        </h2>

        <div className={`inline-block ${getLabelColor(result.label)} px-6 py-3 rounded-lg mb-4`}>
          <div className="text-5xl font-bold">{result.overall_score}</div>
          <div className="text-xl">{result.label.replace(/_/g, ' ')}</div>
        </div>

        <div className="mt-6 flex justify-center gap-3 flex-wrap">
          <button
            onClick={() => handleDownload('json')}
            disabled={downloading}
            className="button-secondary disabled:opacity-50"
          >
            📥 JSON
          </button>
          <button
            onClick={() => handleDownload('markdown')}
            disabled={downloading}
            className="button-secondary disabled:opacity-50"
          >
            📄 Markdown
          </button>
          <button
            onClick={() => handleDownload('pdf')}
            disabled={downloading}
            className="button-secondary disabled:opacity-50"
          >
            📋 PDF
          </button>
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="card mb-8">
        <h3 className="text-2xl font-bold mb-6">Category Breakdown</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(result.categories).map(([key, category]) => (
            <div key={key} className="border rounded-lg p-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold">{categoryNames[key]}</h4>
                <div className={`text-2xl font-bold ${getScoreColor(category.score)}`}>
                  {category.score.toFixed(1)}
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div
                  className={`h-2 rounded-full transition-all ${
                    category.score >= 75
                      ? 'bg-green-500'
                      : category.score >= 50
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${category.score}%` }}
                ></div>
              </div>

              {/* Evidence */}
              {category.evidence && category.evidence.length > 0 && (
                <div className="text-sm text-gray-700 space-y-1">
                  {category.evidence.slice(0, 3).map((ev, i) => (
                    <p key={i}>• {ev}</p>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Keyword Matching */}
      <div className="card mb-8">
        <h3 className="text-2xl font-bold mb-6">Keyword Matching</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Must-Have */}
          <div>
            <h4 className="font-bold text-lg mb-4">Must-Have Keywords</h4>
            <div className="space-y-2">
              {result.must_have.map((kw, i) => (
                <div key={i} className="flex items-center text-sm p-2 bg-gray-50 rounded">
                  <span className={`text-lg mr-2 ${kw.matched ? 'text-green-600' : 'text-red-600'}`}>
                    {kw.matched ? '✓' : '✗'}
                  </span>
                  <span className={kw.matched ? 'text-gray-800' : 'text-gray-500'}>
                    {kw.term}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Nice-to-Have */}
          <div>
            <h4 className="font-bold text-lg mb-4">Nice-to-Have Keywords</h4>
            <div className="space-y-2">
              {result.nice_to_have.slice(0, 10).map((kw, i) => (
                <div key={i} className="flex items-center text-sm p-2 bg-gray-50 rounded">
                  <span className={`text-lg mr-2 ${kw.matched ? 'text-green-600' : 'text-gray-400'}`}>
                    {kw.matched ? '✓' : '○'}
                  </span>
                  <span className={kw.matched ? 'text-gray-800' : 'text-gray-500'}>
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
        <div className="card mb-8 bg-red-50 border border-red-200">
          <h3 className="text-2xl font-bold mb-4 text-red-700">⚠️ Red Flags</h3>
          <ul className="space-y-2">
            {result.red_flags.map((flag, i) => (
              <li key={i} className="flex items-start">
                <span className="text-red-600 mr-2">•</span>
                <span>{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      <div className="card mb-8">
        <h3 className="text-2xl font-bold mb-6">Recommendations</h3>

        {result.actions.good_fit_summary && result.actions.good_fit_summary.length > 0 && (
          <div className="mb-6">
            <h4 className="font-bold text-lg mb-3 text-green-700">✓ Strengths</h4>
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
          <div className="mb-6">
            <h4 className="font-bold text-lg mb-3 text-red-700">✗ Gaps to Address</h4>
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
            <div className="mb-6">
              <h4 className="font-bold text-lg mb-3 text-blue-700">💡 Tailoring Suggestions</h4>
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
          <div>
            <h4 className="font-bold text-lg mb-3 text-purple-700">🔑 Keywords to Consider Adding</h4>
            <div className="flex flex-wrap gap-2">
              {result.actions.ats_keywords_to_add.map((keyword, i) => (
                <span key={i} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
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
          className="button-primary"
        >
          Analyze Another Resume
        </button>
      </div>
    </div>
  )
}
