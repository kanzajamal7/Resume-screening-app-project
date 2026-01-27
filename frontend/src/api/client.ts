import axios from 'axios'
import { AnalysisResponse, AnalysisSettings } from '../types'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
})

export const analyzeResume = async (
  resumeText: string | File,
  jdText: string,
  settings?: AnalysisSettings
): Promise<AnalysisResponse> => {
  const formData = new FormData()

  if (typeof resumeText === 'string') {
    formData.append('resume_text', resumeText)
  } else {
    formData.append('resume_file', resumeText)
  }

  formData.append('jd_text', jdText)
  
  if (settings) {
    formData.append('settings', JSON.stringify(settings))
  }

  const response = await api.post<AnalysisResponse>('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const getHealthStatus = async () => {
  const response = await api.get('/health')
  return response.data
}

export const downloadJsonReport = async (analysisId: string) => {
  const response = await api.get(`/report/${analysisId}/json`, {
    responseType: 'blob',
  })
  return new Blob([JSON.stringify(response.data, null, 2)], {
    type: 'application/json',
  })
}

export const downloadMarkdownReport = async (analysisId: string) => {
  const response = await api.get(`/report/${analysisId}/markdown`)
  const markdown = response.data.markdown
  return new Blob([markdown], { type: 'text/markdown' })
}

export const downloadPdfReport = async (analysisId: string) => {
  const response = await api.get(`/report/${analysisId}/pdf`, {
    responseType: 'blob',
  })
  return response.data
}

export const getDefaultWeights = async () => {
  const response = await api.get('/admin/weights')
  return response.data
}

export default api
