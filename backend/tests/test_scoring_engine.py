"""
Tests for the ATS Scoring Engine
"""

import pytest
from pathlib import Path
from app.scoring_engine import (
    TextPreprocessor,
    KeywordExtractor,
    ResumeParser,
    ScoringEngine,
    to_dict
)


# Load fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"

with open(FIXTURES_DIR / "sample_resume.txt", "r") as f:
    SAMPLE_RESUME = f.read()

with open(FIXTURES_DIR / "sample_jd.txt", "r") as f:
    SAMPLE_JD = f.read()


class TestTextPreprocessor:
    """Test text preprocessing functionality."""
    
    def test_preprocess_lowercase(self):
        """Test text is converted to lowercase."""
        text = "HELLO World"
        result = TextPreprocessor.preprocess(text)
        assert result == "hello world"
    
    def test_preprocess_whitespace(self):
        """Test extra whitespace is removed."""
        text = "hello   world\n\ntest"
        result = TextPreprocessor.preprocess(text)
        assert result == "hello world test"
    
    def test_extract_words(self):
        """Test word extraction."""
        text = "Python and SQL are great"
        words = TextPreprocessor.extract_words(text)
        assert "python" in words
        assert "sql" in words
        assert len(words) == 5
    
    def test_extract_ngrams(self):
        """Test n-gram extraction."""
        text = "Apache Spark is great"
        ngrams = TextPreprocessor.extract_ngrams(text, n=2)
        assert "apache spark" in ngrams
        assert "spark is" in ngrams
    
    def test_find_snippet(self):
        """Test snippet extraction with context."""
        text = "I have experience with Python and Java"
        snippet = TextPreprocessor.find_snippet(text, "Python")
        assert "python" in snippet.lower()


class TestKeywordExtractor:
    """Test keyword extraction from JD and resume."""
    
    def test_extract_must_haves(self):
        """Test extraction of must-have keywords."""
        jd = """Must have 5 years of experience.
        Required: Apache Spark and Python expertise.
        Minimum SQL knowledge needed."""
        
        must_haves = KeywordExtractor.extract_must_haves(jd)
        assert len(must_haves) > 0
        # Should contain technical terms
        assert any("spark" in term.lower() or "python" in term.lower() 
                  for term in must_haves)
    
    def test_extract_nice_to_haves(self):
        """Test extraction of nice-to-have keywords."""
        jd = """Preferred: AWS certification.
        Bonus points for Docker experience.
        Nice to have: Kubernetes knowledge."""
        
        nice = KeywordExtractor.extract_nice_to_haves(jd)
        assert len(nice) > 0
    
    def test_extract_years_required(self):
        """Test extraction of required years of experience."""
        jd1 = "Minimum 5+ years of experience required"
        jd2 = "3-5 years of professional experience"
        jd3 = "7 years experience needed"
        
        assert KeywordExtractor.extract_years_required(jd1) == 5
        assert KeywordExtractor.extract_years_required(jd2) == 3
        assert KeywordExtractor.extract_years_required(jd3) == 7
    
    def test_extract_degree_requirements(self):
        """Test extraction of degree requirements."""
        jd = "Bachelor's degree in Computer Science required. Master's preferred."
        
        degrees = KeywordExtractor.extract_degree_requirements(jd)
        assert "bachelor" in degrees
        assert "master" in degrees
    
    def test_extract_tech_terms(self):
        """Test extraction of technology keywords."""
        text = "Experience with Python, Apache Spark, and AWS S3"
        
        terms = KeywordExtractor._extract_tech_terms(text)
        assert "python" in terms
        assert "spark" in terms
        assert "aws" in terms


class TestResumeParser:
    """Test resume parsing."""
    
    def test_extract_work_experience(self):
        """Test extraction of work experience."""
        experiences = ResumeParser.extract_work_experience(SAMPLE_RESUME)
        
        assert len(experiences) > 0
        assert all('title' in exp for exp in experiences)
        assert all('start_year' in exp for exp in experiences)
        assert all('end_year' in exp for exp in experiences)
    
    def test_extract_education(self):
        """Test extraction of education."""
        education = ResumeParser.extract_education(SAMPLE_RESUME)
        
        assert len(education) > 0
        assert any('bachelor' in edu['type'].lower() for edu in education)
    
    def test_calculate_total_years(self):
        """Test calculation of total years of experience."""
        experiences = ResumeParser.extract_work_experience(SAMPLE_RESUME)
        total = ResumeParser.calculate_total_years(experiences)
        
        # Sample resume has ~7 years total
        assert total > 5
        assert total < 10
    
    def test_empty_experience_parsing(self):
        """Test parsing resume with no experience section."""
        empty_resume = "Name: John\nEducation: BS in CS"
        experiences = ResumeParser.extract_work_experience(empty_resume)
        
        # Should handle gracefully
        assert isinstance(experiences, list)


class TestScoringEngine:
    """Test the main scoring engine."""
    
    def test_scoring_engine_initialization(self):
        """Test engine initializes with default weights."""
        engine = ScoringEngine()
        
        assert engine.weights is not None
        assert len(engine.weights) == 8
        assert sum(engine.weights.values()) == 1.0
    
    def test_scoring_engine_custom_weights(self):
        """Test engine accepts custom weights."""
        custom_weights = {
            'keyword_skills': 0.5,
            'experience_relevance': 0.5,
            'role_match': 0,
            'seniority_match': 0,
            'education_match': 0,
            'tooling_stack_match': 0,
            'recency_match': 0,
            'red_flags': 0,
        }
        engine = ScoringEngine(weights=custom_weights)
        
        assert engine.weights == custom_weights
    
    def test_full_analysis(self):
        """Test complete analysis workflow."""
        engine = ScoringEngine()
        result = engine.analyze(SAMPLE_RESUME, SAMPLE_JD)
        
        # Check result structure
        assert result.overall_score >= 0 and result.overall_score <= 100
        assert result.label in ['STRONG_MATCH', 'MEDIUM_MATCH', 'WEAK_MATCH']
        assert len(result.categories) == 8
        assert len(result.must_have) > 0
        assert len(result.nice_to_have) >= 0
        assert isinstance(result.actions, dict)
        assert 'version' in result.metadata
    
    def test_score_keyword_skills(self):
        """Test keyword & skills scoring."""
        engine = ScoringEngine()
        must_haves = ['python', 'spark', 'sql']
        nice_to_haves = ['kubernetes']
        
        score = engine._score_keyword_skills(SAMPLE_RESUME, must_haves, nice_to_haves)
        
        assert score.score >= 0 and score.score <= 100
        assert 'matched_must' in score.details
        assert len(score.evidence) > 0
    
    def test_score_seniority_match(self):
        """Test seniority/years matching."""
        engine = ScoringEngine()
        
        # Test when years exceed requirement
        score1 = engine._score_seniority_match(7, "Minimum 5 years required")
        assert score1.score >= 90
        
        # Test when years match
        score2 = engine._score_seniority_match(5, "Minimum 5 years required")
        assert score2.score >= 85
        
        # Test when years fall short
        score3 = engine._score_seniority_match(3, "Minimum 5 years required")
        assert score3.score < 70
    
    def test_score_role_match(self):
        """Test role matching."""
        engine = ScoringEngine()
        
        role_resume = "Senior Data Engineer"
        role_jd = "Senior Data Engineer"
        
        score = engine._score_role_match(
            f"Job Title: {role_resume}\n...", 
            [],
            f"{role_jd}\n..."
        )
        
        # Should score well for matching roles
        assert score.score > 50
    
    def test_detect_red_flags(self):
        """Test red flag detection."""
        engine = ScoringEngine()
        
        # Resume with missing must-haves
        bad_resume = "I have some experience with software"
        must_haves = ['python', 'spark', 'kubernetes']
        
        flags = engine._detect_red_flags(bad_resume, [], must_haves)
        
        # Should detect missing keywords
        assert len(flags) > 0
        assert any('missing' in flag.lower() for flag in flags)
    
    def test_strict_mode(self):
        """Test strict mode penalty."""
        engine_normal = ScoringEngine(strict_mode=False)
        engine_strict = ScoringEngine(strict_mode=True)
        
        result_normal = engine_normal.analyze(SAMPLE_RESUME, SAMPLE_JD)
        result_strict = engine_strict.analyze(SAMPLE_RESUME, SAMPLE_JD)
        
        # Strict mode should penalize more heavily if red flags exist
        if len(result_strict.red_flags) > 0:
            assert result_strict.overall_score <= result_normal.overall_score
    
    def test_label_assignment(self):
        """Test label assignment based on score."""
        engine = ScoringEngine()
        
        assert engine._get_label(85) == 'STRONG_MATCH'
        assert engine._get_label(60) == 'MEDIUM_MATCH'
        assert engine._get_label(40) == 'WEAK_MATCH'
    
    def test_result_to_dict(self):
        """Test conversion of result to dictionary."""
        engine = ScoringEngine()
        result = engine.analyze(SAMPLE_RESUME, SAMPLE_JD)
        
        result_dict = to_dict(result)
        
        assert isinstance(result_dict, dict)
        assert 'overall_score' in result_dict
        assert 'label' in result_dict
        assert 'categories' in result_dict
        assert 'must_have' in result_dict
        assert 'actions' in result_dict
        assert 'metadata' in result_dict
    
    def test_generate_actions(self):
        """Test action generation."""
        engine = ScoringEngine()
        result = engine.analyze(SAMPLE_RESUME, SAMPLE_JD)
        
        actions = result.actions
        assert 'good_fit_summary' in actions
        assert 'gaps' in actions
        assert 'resume_tailoring_suggestions' in actions
        assert 'ats_keywords_to_add' in actions
    
    def test_education_scoring(self):
        """Test education/certification scoring."""
        engine = ScoringEngine()
        
        education = [{'type': 'bachelor'}]
        jd_with_degree = "Bachelor's degree required"
        
        score = engine._score_education_match(education, jd_with_degree)
        
        assert score.score > 50
    
    def test_empty_inputs(self):
        """Test handling of empty inputs."""
        engine = ScoringEngine()
        
        # Empty resume and JD should not crash
        result = engine.analyze("", "Senior Engineer Required")
        
        assert result.overall_score >= 0
        assert result.label in ['STRONG_MATCH', 'MEDIUM_MATCH', 'WEAK_MATCH']


class TestIntegration:
    """Integration tests with real sample data."""
    
    def test_end_to_end_analysis(self):
        """Test complete analysis with sample data."""
        engine = ScoringEngine()
        result = engine.analyze(SAMPLE_RESUME, SAMPLE_JD)
        
        # Sample resume is a good match for the JD
        assert result.overall_score >= 60  # Should be decent match
        assert result.label in ['STRONG_MATCH', 'MEDIUM_MATCH']
        
        # Should identify matches
        matched_keywords = [kw for kw in result.must_have if kw.matched]
        assert len(matched_keywords) > 0
    
    def test_consistency_across_runs(self):
        """Test that analysis is consistent."""
        engine = ScoringEngine()
        
        result1 = engine.analyze(SAMPLE_RESUME, SAMPLE_JD)
        result2 = engine.analyze(SAMPLE_RESUME, SAMPLE_JD)
        
        assert result1.overall_score == result2.overall_score
        assert result1.label == result2.label


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
