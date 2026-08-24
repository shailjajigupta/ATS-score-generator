import React from 'react'
import ScoreRing from './ScoreRing.jsx'
import SkillPills from './SkillPills.jsx'

const PARAM_LABELS = {
  skills_match: 'Skills Match',
  semantic_similarity: 'Semantic Similarity',
  experience_relevance: 'Experience Relevance',
  keyword_match: 'Keyword Match',
  education_match: 'Education Match',
}

export default function ResultsPanel({ result, onReset }) {
  const {
    overall_score,
    score_breakdown,
    weights,
    matched_skills,
    missing_skills,
    matched_keywords,
    missing_keywords,
    experience_details,
    education_details,
    suggestions,
  } = result

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-2">
        <h3 className="mb-0">Compatibility Report</h3>
        <button className="btn btn-outline-light btn-sm" onClick={onReset}>
          ← Analyze another
        </button>
      </div>

      <div className="text-center mb-4">
        <ScoreRing score={overall_score} caption="Overall Match Score" />
      </div>

      <div className="section-label">
        <span className="dash"></span> Score Breakdown
      </div>
      <div className="row justify-content-center text-center mb-2">
        {Object.entries(score_breakdown).map(([key, value]) => (
          <div className="col-6 col-md-2 mb-3" key={key}>
            <ScoreRing score={value} caption={PARAM_LABELS[key]} size="small" />
            <div className="small text-faint mt-1" style={{ color: 'var(--text-faint)' }}>
              {Math.round(weights[key] * 100)}% weight
            </div>
          </div>
        ))}
      </div>

      {/* Experience detail line */}
      {experience_details.method === 'years_comparison' && experience_details.candidate_years !== null && (
        <div className="text-center text-muted small mb-2">
          Experience: role requires <strong>{experience_details.required_years}</strong> years · resume shows{' '}
          <strong>{experience_details.candidate_years}</strong> years
        </div>
      )}
      {experience_details.method === 'years_comparison' && experience_details.candidate_years === null && experience_details.resume_self_identifies_as_fresher && (
        <div className="text-center text-muted small mb-2">
          Experience: role requires <strong>{experience_details.required_years}</strong> years · resume self-identifies as fresher / entry-level
        </div>
      )}
      {experience_details.method === 'no_years_stated_partial_credit' && (
        <div className="text-center text-muted small mb-2">
          Experience: role requires <strong>{experience_details.required_years}</strong> years · resume doesn't state years explicitly (estimated)
        </div>
      )}
      {experience_details.method === 'semantic_similarity_fallback' && (
        <div className="text-center text-muted small mb-2">
          Experience: JD doesn't state required years - scored via overall content similarity
        </div>
      )}

      {/* Education detail line */}
      {education_details.method === 'no_requirement_stated' && (
        <div className="text-center text-muted small mb-4">
          Education: JD doesn't state a specific degree requirement
        </div>
      )}
      {education_details.method === 'resume_omits_education' && (
        <div className="text-center text-muted small mb-4">
          Education: role requires <strong>{education_details.required_degree}</strong> · resume doesn't mention a degree
        </div>
      )}
      {(education_details.method === 'meets_or_exceeds_requirement' || education_details.method === 'below_requirement') && (
        <div className="text-center text-muted small mb-4">
          Education: role requires <strong>{education_details.required_degree}</strong> · resume shows{' '}
          <strong>{education_details.candidate_degree}</strong>
        </div>
      )}

      <div className="row">
        <div className="col-md-6 mb-4">
          <div className="section-label">
            <span className="dash"></span> Matched Skills
          </div>
          <SkillPills skills={matched_skills} variant="matched" />
        </div>
        <div className="col-md-6 mb-4">
          <div className="section-label">
            <span className="dash"></span> Missing Skills
          </div>
          <SkillPills skills={missing_skills} variant="missing" />
        </div>
      </div>

      <div className="row">
        <div className="col-md-6 mb-4">
          <div className="section-label">
            <span className="dash"></span> Matched Keywords
          </div>
          <SkillPills skills={matched_keywords} variant="matched" />
        </div>
        <div className="col-md-6 mb-4">
          <div className="section-label">
            <span className="dash"></span> Missing Keywords
          </div>
          <SkillPills skills={missing_keywords} variant="missing" />
        </div>
      </div>

      <div className="section-label">
        <span className="dash"></span> AI Resume Improvement Suggestions
      </div>
      <div className="suggestions-card">{suggestions}</div>
    </div>
  )
}
