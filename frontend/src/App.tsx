import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import AnalysisForm from './pages/AnalysisForm'
import ResultsPage from './pages/ResultsPage'
import AdminPanel from './pages/AdminPanel'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <nav className="max-w-7xl mx-auto px-4 py-6">
            <h1 className="text-3xl font-bold text-gray-900">
              ATS Resume Match Analyzer
            </h1>
            <p className="text-gray-600 mt-2">
              Analyze how well your resume matches a job description
            </p>
          </nav>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-12">
          <Routes>
            <Route path="/" element={<AnalysisForm />} />
            <Route path="/results/:analysisId" element={<ResultsPage />} />
            <Route path="/admin" element={<AdminPanel />} />
          </Routes>
        </main>

        <footer className="bg-gray-100 mt-12 py-6">
          <div className="max-w-7xl mx-auto px-4 text-center text-gray-600 text-sm">
            <p>ATS Resume Match Analyzer v1.0.0</p>
            <p className="mt-2">
              For demonstration and internal hiring use only
            </p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
