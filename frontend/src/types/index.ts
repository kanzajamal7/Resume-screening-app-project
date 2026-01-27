export interface AnalysisResult {
  overall_score: number
  label: 'STRONG_MATCH' | 'MEDIUM_MATCH' | 'WEAK_MATCH'
  categories: {
    [key: string]: {
      score: number
      details: Record<string, any>
      evidence: string[]
    }
  }
  must_have: KeywordMatch[]
  nice_to_have: KeywordMatch[]
  red_flags: string[]
  actions: {
    good_fit_summary: string[]
    gaps: string[]
    resume_tailoring_suggestions: string[]
    ats_keywords_to_add: string[]
  }
  metadata: {
    version: string
    timestamp: string
    settings_used: Record<string, any>
  }
}

export interface KeywordMatch {
  term: string
  matched: boolean
  evidence: string
  category: string
}

export interface AnalysisResponse {
  analysis_id: string
  result: AnalysisResult
}

export interface AnalysisSettings {
  strict_mode: boolean
  weights?: Record<string, number>
  toggle_synonyms: boolean
  toggle_rewrite_suggestions: boolean
}
