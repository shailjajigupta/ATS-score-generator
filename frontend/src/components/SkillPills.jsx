import React from 'react'

export default function SkillPills({ skills, variant }) {
  if (!skills || skills.length === 0) {
    return (
      <div className="text-muted small">
        {variant === 'matched' ? 'No matched skills found.' : 'None - great, no gaps found!'}
      </div>
    )
  }

  return (
    <div className="skill-pill-list">
      {skills.map((skill) => (
        <span key={skill} className={`skill-pill ${variant}`}>
          {variant === 'matched' ? '✓ ' : '✕ '}
          {skill}
        </span>
      ))}
    </div>
  )
}
