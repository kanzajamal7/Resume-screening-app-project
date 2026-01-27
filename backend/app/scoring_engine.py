"""
ATS Resume Match Analyzer - Scoring Engine
Implements explainable scoring logic for resume matching against job descriptions.
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CategoryScore:
    """Score for a single category with explanation."""
    score: float
    details: Dict = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)


@dataclass
class KeywordMatch:
    """Details about a matched keyword."""
    term: str
    matched: bool
    evidence: str = ""
    category: str = ""  # must-have or nice-to-have


@dataclass
class AnalysisResult:
    """Complete analysis result."""
    overall_score: float
    label: str
    categories: Dict[str, CategoryScore]
    must_have: List[KeywordMatch]
    nice_to_have: List[KeywordMatch]
    red_flags: List[str]
    actions: Dict
    metadata: Dict


class TextPreprocessor:
    """Preprocess and normalize text."""
    
    @staticmethod
    def preprocess(text: str) -> str:
        """Normalize text: lowercase, remove extra whitespace."""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def extract_words(text: str) -> Set[str]:
        """Extract individual words."""
        text = TextPreprocessor.preprocess(text)
        words = re.findall(r'\b\w+\b', text)
        return set(words)
    
    @staticmethod
    def extract_ngrams(text: str, n: int = 2) -> Set[str]:
        """Extract n-grams (e.g., 2-3 word phrases)."""
        text = TextPreprocessor.preprocess(text)
        words = text.split()
        ngrams = set()
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i + n])
            ngrams.add(ngram)
        return ngrams
    
    @staticmethod
    def find_snippet(text: str, term: str, context_words: int = 10) -> str:
        """Find a term in text and return snippet with context."""
        text_lower = text.lower()
        term_lower = term.lower()
        idx = text_lower.find(term_lower)
        if idx == -1:
            return ""
        
        # Get context around match
        words = text[:idx].split()
        start = max(0, len(words) - context_words)
        start_pos = len(' '.join(words[start:start+1])) + sum(len(w) + 1 for w in words[start:])
        
        end_words = text[idx:].split()
        end = min(len(end_words), context_words + 1)
        end_text = ' '.join(end_words[:end])
        
        return f"...{end_text}..."


class KeywordExtractor:
    """Extract keywords from job descriptions and resumes."""
    
    # Load tech stack dictionary
    TECH_STACK = {
        'languages': ['python', 'java', 'javascript', 'typescript', 'sql', 'scala', 'r', 'c++', 'c#', 'go', 'rust', 'kotlin'],
        'databases': ['mysql', 'postgresql', 'mongodb', 'cassandra', 'dynamodb', 'redis', 'elasticsearch', 'oracle', 'sql server'],
        'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'terraform', 'cloudformation'],
        'bigdata': ['spark', 'hadoop', 'hive', 'kafka', 'flink', 'airflow', 'dbt', 'talend', 'informatica'],
        'ml': ['tensorflow', 'pytorch', 'scikit-learn', 'xgboost', 'nlp', 'neural network', 'machine learning'],
        'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'jira', 'confluence'],
    }
    
    # Flatten for easier lookup
    ALL_TECH = set()
    for category, items in TECH_STACK.items():
        ALL_TECH.update(items)
    
    @staticmethod
    def extract_must_haves(text: str) -> List[str]:
        """Extract must-have keywords from job description."""
        text = TextPreprocessor.preprocess(text)
        lines = text.split('\n')
        
        must_haves = []
        must_keywords = ['must have', 'required', 'requirement', 'minimum', 'need ', 'experience with', 'expertise in']
        
        for line in lines:
            if any(kw in line for kw in must_keywords):
                # Extract technical terms and skills
                terms = KeywordExtractor._extract_tech_terms(line)
                must_haves.extend(terms)
                # Also extract quoted terms and specific role keywords
                quoted = re.findall(r'"([^"]+)"', line)
                must_haves.extend(quoted)
        
        return list(set(must_haves))  # Remove duplicates
    
    @staticmethod
    def extract_nice_to_haves(text: str) -> List[str]:
        """Extract nice-to-have keywords from job description."""
        text = TextPreprocessor.preprocess(text)
        lines = text.split('\n')
        
        nice_to_haves = []
        nice_keywords = ['preferred', 'plus', 'bonus', 'nice to have', 'additional', 'beneficial']
        
        for line in lines:
            if any(kw in line for kw in nice_keywords):
                terms = KeywordExtractor._extract_tech_terms(line)
                nice_to_haves.extend(terms)
        
        return list(set(nice_to_haves))
    
    @staticmethod
    def _extract_tech_terms(text: str) -> List[str]:
        """Extract technical terms from text."""
        terms = []
        text_lower = text.lower()
        
        for tech in KeywordExtractor.ALL_TECH:
            if tech in text_lower:
                terms.append(tech)
        
        # Also capture uppercase acronyms
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        terms.extend([a.lower() for a in acronyms])
        
        return list(set(terms))
    
    @staticmethod
    def extract_years_required(text: str) -> Optional[int]:
        """Extract required years of experience from job description."""
        text = TextPreprocessor.preprocess(text)
        
        # Look for patterns like "3+ years", "3 years", "5-7 years"
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    return int(matches[0][0])  # Return first number of range
                else:
                    return int(matches[0])
        
        return None
    
    @staticmethod
    def extract_degree_requirements(text: str) -> List[str]:
        """Extract degree/certification requirements."""
        text = TextPreprocessor.preprocess(text)
        
        degrees = []
        degree_patterns = ['bachelor', 'master', 'phd', 'certificate', 'certification', 'degree']
        
        for degree in degree_patterns:
            if degree in text:
                degrees.append(degree)
        
        return degrees
    
    @staticmethod
    def extract_role_keywords(text: str) -> List[str]:
        """Extract role/title keywords from job description."""
        text = TextPreprocessor.preprocess(text)
        
        roles = []
        role_patterns = ['engineer', 'developer', 'analyst', 'manager', 'architect', 'specialist', 'lead', 'senior']
        
        for role in role_patterns:
            if role in text:
                roles.append(role)
        
        return roles


class ResumeParser:
    """Parse resume text to extract structured information."""
    
    @staticmethod
    def extract_work_experience(text: str) -> List[Dict]:
        """Extract work experience section with dates and descriptions."""
        experiences = []
        
        # Split by common section headers
        section_pattern = r'(experience|work\s*history|professional\s*experience)([\s\S]*?)(?=\n[A-Z][A-Z\s]*\n|\Z)'
        matches = re.finditer(section_pattern, text, re.IGNORECASE)
        
        for match in matches:
            section_text = match.group(2)
            # Split into individual jobs
            job_pattern = r'([A-Za-z\s]+?)(?:\(|,)?(\d{4})[^0-9]*(\d{4})?[^\n]*\n((?:[^\n]*(?:(?!\n[A-Za-z]{2,})|$))*)'
            job_matches = re.finditer(job_pattern, section_text)
            
            for job_match in job_matches:
                job_title = job_match.group(1).strip()
                start_year = int(job_match.group(2))
                end_year = int(job_match.group(3)) if job_match.group(3) else datetime.now().year
                description = job_match.group(4).strip()
                
                experiences.append({
                    'title': job_title,
                    'start_year': start_year,
                    'end_year': end_year,
                    'years': end_year - start_year,
                    'description': description,
                    'recency': datetime.now().year - end_year
                })
        
        return experiences
    
    @staticmethod
    def extract_education(text: str) -> List[Dict]:
        """Extract education section."""
        education = []
        
        section_pattern = r'(education|qualifications)([\s\S]*?)(?=\n[A-Z][A-Z\s]*\n|\Z)'
        match = re.search(section_pattern, text, re.IGNORECASE)
        
        if match:
            section_text = match.group(2)
            # Look for degree keywords
            for degree_type in ['bachelor', 'master', 'phd', 'certificate']:
                if degree_type in section_text.lower():
                    education.append({'type': degree_type})
        
        return education
    
    @staticmethod
    def calculate_total_years(experiences: List[Dict]) -> float:
        """Calculate total years of experience."""
        if not experiences:
            return 0
        
        total = sum(exp['years'] for exp in experiences)
        return total


class ScoringEngine:
    """Main scoring engine for ATS resume analysis."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None, strict_mode: bool = False):
        """Initialize scoring engine with optional custom weights."""
        self.weights = weights or self._default_weights()
        self.strict_mode = strict_mode
    
    @staticmethod
    def _default_weights() -> Dict[str, float]:
        """Default scoring weights."""
        return {
            'keyword_skills': 0.30,
            'experience_relevance': 0.20,
            'role_match': 0.10,
            'seniority_match': 0.10,
            'education_match': 0.10,
            'tooling_stack_match': 0.10,
            'recency_match': 0.05,
            'red_flags': 0.05,
        }
    
    def analyze(
        self,
        resume_text: str,
        jd_text: str,
        settings: Optional[Dict] = None
    ) -> AnalysisResult:
        """Run complete analysis of resume against job description."""
        
        # Extract keywords from JD
        must_haves = KeywordExtractor.extract_must_haves(jd_text)
        nice_to_haves = KeywordExtractor.extract_nice_to_haves(jd_text)
        
        # Parse resume
        experiences = ResumeParser.extract_work_experience(resume_text)
        education = ResumeParser.extract_education(resume_text)
        total_years = ResumeParser.calculate_total_years(experiences)
        
        # Score each category
        scores = {}
        
        scores['keyword_skills'] = self._score_keyword_skills(
            resume_text, must_haves, nice_to_haves
        )
        scores['experience_relevance'] = self._score_experience_relevance(
            resume_text, experiences, jd_text
        )
        scores['role_match'] = self._score_role_match(
            resume_text, experiences, jd_text
        )
        scores['seniority_match'] = self._score_seniority_match(
            total_years, jd_text
        )
        scores['education_match'] = self._score_education_match(
            education, jd_text
        )
        scores['tooling_stack_match'] = self._score_tooling_match(
            resume_text, jd_text
        )
        scores['recency_match'] = self._score_recency_match(experiences)
        
        # Detect red flags
        red_flags = self._detect_red_flags(
            resume_text, experiences, must_haves
        )
        scores['red_flags'] = CategoryScore(
            score=max(0, 100 - len(red_flags) * 15),
            details={'flags_count': len(red_flags)},
            evidence=red_flags
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(scores)
        
        # Apply strict mode penalty
        if self.strict_mode and len(red_flags) > 0:
            overall_score = max(0, overall_score - 20)
        
        # Generate label
        label = self._get_label(overall_score)
        
        # Generate actions
        actions = self._generate_actions(
            resume_text, jd_text, must_haves, nice_to_haves, scores
        )
        
        # Create keyword matches
        must_have_matches = self._create_keyword_matches(
            resume_text, must_haves, 'must-have'
        )
        nice_to_have_matches = self._create_keyword_matches(
            resume_text, nice_to_haves, 'nice-to-have'
        )
        
        return AnalysisResult(
            overall_score=overall_score,
            label=label,
            categories={k: v for k, v in scores.items()},
            must_have=must_have_matches,
            nice_to_have=nice_to_have_matches,
            red_flags=red_flags,
            actions=actions,
            metadata={
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'settings_used': {
                    'strict_mode': self.strict_mode,
                    'weights': self.weights
                }
            }
        )
    
    def _score_keyword_skills(
        self,
        resume_text: str,
        must_haves: List[str],
        nice_to_haves: List[str]
    ) -> CategoryScore:
        """Score A: Keyword & skills match."""
        resume_lower = resume_text.lower()
        
        matched_must = sum(1 for kw in must_haves if kw.lower() in resume_lower)
        matched_nice = sum(1 for kw in nice_to_haves if kw.lower() in resume_lower)
        
        total_must = len(must_haves) if must_haves else 1
        total_nice = len(nice_to_haves) if nice_to_haves else 1
        
        if must_haves:
            score = (matched_must / total_must) * 70 + (matched_nice / total_nice) * 30
        else:
            score = (matched_nice / total_nice) * 100
        
        score = min(100, max(0, score))
        
        # Collect evidence
        evidence = []
        for kw in must_haves:
            if kw.lower() in resume_lower:
                snippet = TextPreprocessor.find_snippet(resume_text, kw)
                evidence.append(f"✓ {kw}: {snippet}")
        
        return CategoryScore(
            score=score,
            details={
                'matched_must': matched_must,
                'total_must': total_must,
                'matched_nice': matched_nice,
                'total_nice': total_nice
            },
            evidence=evidence
        )
    
    def _score_experience_relevance(
        self,
        resume_text: str,
        experiences: List[Dict],
        jd_text: str
    ) -> CategoryScore:
        """Score B: Experience relevance match."""
        if not experiences:
            return CategoryScore(score=0, details={'error': 'No experience found'})
        
        role_keywords = KeywordExtractor.extract_role_keywords(jd_text)
        tech_terms = []
        for category, items in KeywordExtractor.TECH_STACK.items():
            tech_terms.extend(items)
        
        total_score = 0
        evidence = []
        
        for exp in experiences:
            desc_lower = (exp['description'] + ' ' + exp['title']).lower()
            
            # Calculate recency weight
            if exp['recency'] <= 3:
                weight = 1.0
            elif exp['recency'] <= 7:
                weight = 0.7
            else:
                weight = 0.4
            
            # Count matches
            matches = 0
            for keyword in role_keywords + tech_terms:
                if keyword.lower() in desc_lower:
                    matches += 1
            
            relevance = (matches / max(len(role_keywords) + len(tech_terms), 1)) * weight
            total_score += relevance
            
            if matches > 0:
                evidence.append(f"✓ {exp['title']} ({exp['start_year']}-{exp['end_year']}): {matches} relevant keywords")
        
        score = min(100, (total_score / len(experiences)) * 100)
        
        return CategoryScore(
            score=score,
            details={'relevant_experiences': len([e for e in experiences if e['recency'] <= 3])},
            evidence=evidence
        )
    
    def _score_role_match(
        self,
        resume_text: str,
        experiences: List[Dict],
        jd_text: str
    ) -> CategoryScore:
        """Score C: Role/title match."""
        resume_roles = [exp['title'].lower() for exp in experiences if experiences]
        
        # Extract target role from JD (first meaningful sentence)
        jd_lines = jd_text.split('\n')
        target_role = jd_lines[0].lower() if jd_lines else ""
        
        score = 0
        evidence = []
        
        for role in resume_roles:
            # Exact match
            if role in target_role or target_role in role:
                score = 95
                evidence.append(f"✓ Exact role match: {role}")
            # Partial match
            elif any(keyword in role for keyword in ['engineer', 'developer', 'analyst', 'lead']):
                score = max(score, 70)
                evidence.append(f"~ Adjacent role: {role}")
        
        if not evidence:
            score = 20
            evidence.append(f"✗ Limited role overlap")
        
        return CategoryScore(
            score=score,
            details={'resume_roles': resume_roles},
            evidence=evidence
        )
    
    def _score_seniority_match(
        self,
        total_years: float,
        jd_text: str
    ) -> CategoryScore:
        """Score D: Seniority/years match."""
        required_years = KeywordExtractor.extract_years_required(jd_text)
        
        if required_years is None:
            return CategoryScore(
                score=50,
                details={'warning': 'Could not extract required years'},
                evidence=['Unable to determine exact requirement']
            )
        
        gap = total_years - required_years
        
        if gap >= 0:
            score = min(100, 90 + (gap * 2))
        elif gap >= -1:
            score = 70 + (gap * 15)
        else:
            score = max(0, 60 + (gap * 20))
        
        evidence = [f"Resume: {total_years:.1f} years, Required: {required_years} years"]
        
        return CategoryScore(
            score=max(0, min(100, score)),
            details={
                'resume_years': total_years,
                'required_years': required_years,
                'gap': gap
            },
            evidence=evidence
        )
    
    def _score_education_match(
        self,
        education: List[Dict],
        jd_text: str
    ) -> CategoryScore:
        """Score E: Education/certs match."""
        required_degrees = KeywordExtractor.extract_degree_requirements(jd_text)
        
        if not required_degrees:
            return CategoryScore(
                score=75,
                details={'no_requirement': True},
                evidence=['No specific degree requirement in JD']
            )
        
        if not education:
            return CategoryScore(
                score=30,
                details={'missing_education': True},
                evidence=['No education found in resume']
            )
        
        found_degrees = set(e['type'] for e in education)
        matched = sum(1 for req in required_degrees if any(req in found for found in found_degrees))
        
        score = (matched / len(required_degrees)) * 100 if required_degrees else 50
        
        evidence = [f"Found: {', '.join(found_degrees)}"]
        
        return CategoryScore(
            score=score,
            details={
                'found_degrees': list(found_degrees),
                'required_degrees': required_degrees
            },
            evidence=evidence
        )
    
    def _score_tooling_match(
        self,
        resume_text: str,
        jd_text: str
    ) -> CategoryScore:
        """Score F: Tooling/stack match."""
        resume_lower = resume_text.lower()
        
        matched_tools = []
        for category, tools in KeywordExtractor.TECH_STACK.items():
            for tool in tools:
                if tool in resume_lower:
                    matched_tools.append(tool)
        
        jd_lower = jd_text.lower()
        jd_tools = []
        for category, tools in KeywordExtractor.TECH_STACK.items():
            for tool in tools:
                if tool in jd_lower:
                    jd_tools.append(tool)
        
        if not jd_tools:
            return CategoryScore(
                score=50,
                details={'no_tools_in_jd': True},
                evidence=['No specific tools mentioned in JD']
            )
        
        matched = sum(1 for tool in jd_tools if tool in matched_tools)
        score = (matched / len(jd_tools)) * 100
        
        evidence = [f"Matched {matched}/{len(jd_tools)} required tools"]
        
        return CategoryScore(
            score=score,
            details={
                'matched_tools': matched,
                'required_tools': len(jd_tools)
            },
            evidence=evidence
        )
    
    def _score_recency_match(
        self,
        experiences: List[Dict]
    ) -> CategoryScore:
        """Score G: Recency match."""
        if not experiences:
            return CategoryScore(score=0, details={'no_experience': True})
        
        # Score higher if relevant experience is recent
        recent_count = sum(1 for exp in experiences if exp['recency'] <= 3)
        score = (recent_count / len(experiences)) * 100
        
        evidence = [f"{recent_count} roles within last 3 years"]
        
        return CategoryScore(
            score=score,
            details={'recent_experience_count': recent_count},
            evidence=evidence
        )
    
    def _detect_red_flags(
        self,
        resume_text: str,
        experiences: List[Dict],
        must_haves: List[str]
    ) -> List[str]:
        """Score H: Detect red flags."""
        flags = []
        resume_lower = resume_text.lower()
        
        # Missing must-haves
        missing_must = [kw for kw in must_haves if kw.lower() not in resume_lower]
        if missing_must:
            flags.append(f"Missing {len(missing_must)} must-have keywords: {', '.join(missing_must[:3])}")
        
        # Job hopping
        short_jobs = sum(1 for exp in experiences if exp['years'] < 1)
        if short_jobs >= 2:
            flags.append(f"Potential job hopping: {short_jobs} positions < 1 year")
        
        # Unexplained gaps
        for i in range(len(experiences) - 1):
            gap = experiences[i]['start_year'] - experiences[i + 1]['end_year']
            if gap > 1:
                flags.append(f"Employment gap: {gap} years ({experiences[i + 1]['end_year']}-{experiences[i]['start_year']})")
        
        # Over-claiming detection
        weak_keywords = ['familiar with', 'knowledge of', 'basic', 'some experience']
        for keyword in weak_keywords:
            if keyword in resume_lower and any(must in resume_lower for must in must_haves):
                flags.append(f"Weak claim detected: '{keyword}' used for required skills")
        
        return flags
    
    def _calculate_overall_score(self, scores: Dict[str, CategoryScore]) -> float:
        """Calculate weighted overall score."""
        total = 0
        for category, weight in self.weights.items():
            if category in scores:
                total += scores[category].score * weight
        return round(total, 1)
    
    def _get_label(self, overall_score: float) -> str:
        """Determine match label based on score."""
        if overall_score >= 75:
            return 'STRONG_MATCH'
        elif overall_score >= 50:
            return 'MEDIUM_MATCH'
        else:
            return 'WEAK_MATCH'
    
    def _generate_actions(
        self,
        resume_text: str,
        jd_text: str,
        must_haves: List[str],
        nice_to_haves: List[str],
        scores: Dict[str, CategoryScore]
    ) -> Dict:
        """Generate actionable recommendations."""
        resume_lower = resume_text.lower()
        
        # Good fit summary
        good_fit = []
        if scores['keyword_skills'].score >= 70:
            good_fit.append("Strong keyword and skills alignment")
        if scores['experience_relevance'].score >= 70:
            good_fit.append("Relevant professional experience")
        if scores['role_match'].score >= 70:
            good_fit.append("Matching role background")
        
        # Gaps
        gaps = []
        for kw in must_haves:
            if kw.lower() not in resume_lower:
                gaps.append(f"Missing required skill: {kw}")
        
        # Tailoring suggestions
        suggestions = []
        missing_nice = [kw for kw in nice_to_haves if kw.lower() not in resume_lower]
        if missing_nice:
            suggestions.append(f"Add nice-to-have skills if applicable: {', '.join(missing_nice[:3])}")
        
        if scores['seniority_match'].details.get('gap', 0) < 0:
            suggestions.append("Highlight achievements to demonstrate advanced capability")
        
        # ATS keywords to add
        ats_keywords = [kw for kw in must_haves if kw.lower() not in resume_lower][:5]
        
        return {
            'good_fit_summary': good_fit,
            'gaps': gaps,
            'resume_tailoring_suggestions': suggestions,
            'ats_keywords_to_add': ats_keywords
        }
    
    def _create_keyword_matches(
        self,
        resume_text: str,
        keywords: List[str],
        category: str
    ) -> List[KeywordMatch]:
        """Create keyword match objects."""
        matches = []
        resume_lower = resume_text.lower()
        
        for keyword in keywords:
            matched = keyword.lower() in resume_lower
            evidence = ""
            if matched:
                evidence = TextPreprocessor.find_snippet(resume_text, keyword)
            
            matches.append(KeywordMatch(
                term=keyword,
                matched=matched,
                evidence=evidence,
                category=category
            ))
        
        return matches


def to_dict(result: AnalysisResult) -> Dict:
    """Convert AnalysisResult to dictionary."""
    return {
        'overall_score': result.overall_score,
        'label': result.label,
        'categories': {
            k: {
                'score': v.score,
                'details': v.details,
                'evidence': v.evidence
            }
            for k, v in result.categories.items()
        },
        'must_have': [
            {
                'term': kw.term,
                'matched': kw.matched,
                'evidence': kw.evidence,
                'category': kw.category
            }
            for kw in result.must_have
        ],
        'nice_to_have': [
            {
                'term': kw.term,
                'matched': kw.matched,
                'evidence': kw.evidence,
                'category': kw.category
            }
            for kw in result.nice_to_have
        ],
        'red_flags': result.red_flags,
        'actions': result.actions,
        'metadata': result.metadata
    }
