import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeResume } from '../api/client'
import { AnalysisSettings } from '../types'

export default function AnalysisForm() {
  const navigate = useNavigate()
  const [resumeText, setResumeText] = useState('')
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [jdText, setJdText] = useState('')
  const [useFileUpload, setUseFileUpload] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [strictMode, setStrictMode] = useState(false)
  const [showExtractedText, setShowExtractedText] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setResumeFile(file)
      // Also try to display preview
      if (file.type === 'text/plain') {
        const reader = new FileReader()
        reader.onload = (e) => {
          setResumeText(e.target?.result as string)
        }
        reader.readAsText(file)
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const resume = useFileUpload && resumeFile ? resumeFile : resumeText

      if (!resume) {
        throw new Error('Please provide a resume (text or file)')
      }
      if (!jdText.trim()) {
        throw new Error('Please enter the job description')
      }

      const settings: AnalysisSettings = {
        strict_mode: strictMode,
        toggle_synonyms: true,
        toggle_rewrite_suggestions: false,
      }

      const response = await analyzeResume(resume, jdText, settings)
      navigate(`/results/${response.analysis_id}`, { state: { result: response.result } })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Resume Section */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-4">Your Resume</h2>

          <div className="mb-4">
            <label className="flex items-center mb-2">
              <input
                type="radio"
                checked={!useFileUpload}
                onChange={() => setUseFileUpload(false)}
                className="mr-2"
              />
              <span>Paste Resume Text</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                checked={useFileUpload}
                onChange={() => setUseFileUpload(true)}
                className="mr-2"
              />
              <span>Upload Resume File (PDF, DOCX, TXT)</span>
            </label>
          </div>

          {!useFileUpload ? (
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume text here..."
              className="w-full h-72 p-3 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          ) : (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileChange}
                className="w-full"
              />
              {resumeFile && (
                <p className="mt-3 text-sm text-green-600">
                  [+] Selected: {resumeFile.name}
                </p>
              )}
            </div>
          )}

          {resumeText && (
            <button
              type="button"
              onClick={() => setShowExtractedText(!showExtractedText)}
              className="text-blue-600 text-sm mt-3 hover:underline"
            >
              {showExtractedText ? 'Hide' : 'Show'} Extracted Text Preview
            </button>
          )}

          {showExtractedText && (
            <div className="mt-4 p-4 bg-gray-100 rounded text-sm max-h-40 overflow-y-auto">
              <p className="whitespace-pre-wrap text-xs">{resumeText.substring(0, 500)}...</p>
            </div>
          )}
        </div>

        {/* Job Description Section */}
        <div className="card">
          <h2 className="text-2xl font-bold mb-4">Job Description</h2>

          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste the job description here..."
            className="w-full h-72 p-3 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <div className="mt-4 p-4 bg-blue-50 rounded">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={strictMode}
                onChange={(e) => setStrictMode(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm">
                <strong>Strict Mode:</strong> Heavily penalize missing required skills
              </span>
            </label>
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="mt-8">
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full button-primary py-3 text-lg font-bold disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Analyze Resume'}
        </button>
      </div>

      {/* Sample Data Button */}
      <div className="mt-6 text-center">
        <button
          onClick={() => {
            setResumeText(`JOHN DOE
john.doe@email.com | (555) 123-4567

PROFESSIONAL SUMMARY
Experienced Data Engineer with 6+ years building scalable ETL pipelines.

PROFESSIONAL EXPERIENCE

Senior Data Engineer - Tech Company Inc. (Jan 2022 – Present)
• Designed ETL pipeline using Apache Spark processing 500GB+ daily
• Optimized SQL queries reducing execution time by 40%
• Led migration to AWS

Data Engineer - DataSoft Solutions (Jun 2018 – Dec 2021)
• Developed Python-based data pipelines using Apache Spark
• Implemented MySQL and PostgreSQL schemas
• Created Tableau dashboards

TECHNICAL SKILLS
Languages: Python, SQL, Scala
Big Data: Apache Spark, Hadoop, Hive, Kafka
Cloud: AWS, GCP
Databases: MySQL, PostgreSQL, Cassandra

EDUCATION
Bachelor of Science in Computer Science`)
            setJdText(`Senior Data Engineer Position

REQUIREMENTS
• Minimum 5 years of experience as a Data Engineer
• Expertise in Apache Spark and distributed computing
• Strong SQL and database design skills
• Experience with Python for data pipeline development
• Familiarity with cloud platforms (AWS or GCP)
• Experience with workflow orchestration tools (Airflow)
• Bachelor's degree in Computer Science or related field

PREFERRED
• Kafka for streaming data
• Docker and Kubernetes
• AWS certification`)
          }}
          className="text-blue-600 text-sm hover:underline"
        >
          Load Sample Data
        </button>
      </div>
    </div>
  )
}
