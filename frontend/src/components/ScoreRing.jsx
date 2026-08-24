import React from 'react'

/**
 * A circular progress ring showing a 0-100 score, with a caption underneath.
 * `size` controls the overall ring diameter class ('normal' | 'small').
 */
export default function ScoreRing({ score, caption, size = 'normal' }) {
  const radius = 58
  const circumference = 2 * Math.PI * radius
  const clamped = Math.max(0, Math.min(100, score))
  const offset = circumference - (clamped / 100) * circumference

  const color = clamped >= 70 ? 'var(--green)' : clamped >= 40 ? 'var(--orange)' : 'var(--red)'

  return (
    <div className="score-ring-wrap">
      <div className={`score-ring ${size === 'small' ? 'small' : ''}`}>
        <svg viewBox="0 0 140 140" width="100%" height="100%">
          <circle className="ring-bg" cx="70" cy="70" r={radius} />
          <circle
            className="ring-value"
            cx="70"
            cy="70"
            r={radius}
            style={{ stroke: color }}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="ring-label">
          <div className="ring-number">{clamped.toFixed(0)}</div>
          <div className="ring-percent">/ 100</div>
        </div>
      </div>
      {caption && <div className="score-ring-caption">{caption}</div>}
    </div>
  )
}
