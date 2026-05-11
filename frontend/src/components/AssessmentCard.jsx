/**
 * AssessmentCard Component
 * Displays a single SHL assessment recommendation with rich detail.
 */

import { ExternalLink, Clock, Tag, Layers, BarChart2 } from 'lucide-react'
import clsx from 'clsx'

/** Map test type codes to human-readable labels */
const TEST_TYPE_LABELS = {
  A: 'Ability & Aptitude',
  B: 'Situational Judgement',
  C: 'Competencies',
  D: 'Development & 360',
  E: 'Assessment Exercises',
  K: 'Knowledge & Skills',
  M: 'Motivational',
  P: 'Personality & Behavior',
  S: 'Simulations',
}

/**
 * Confidence score display as a pill.
 */
function ConfidencePill({ score }) {
  if (score == null) return null
  const pct = Math.round(score * 100)
  const color =
    pct >= 85
      ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/25'
      : pct >= 65
      ? 'text-amber-400 bg-amber-400/10 border-amber-400/25'
      : 'text-rose-400 bg-rose-400/10 border-rose-400/25'

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-mono border',
        color
      )}
    >
      <BarChart2 size={11} />
      {pct}% match
    </span>
  )
}

export default function AssessmentCard({ assessment, index }) {
  const {
    name,
    url,
    test_type,
    description,
    duration,
    skills_measured,
    confidence_score,
  } = assessment

  const typeLabel = TEST_TYPE_LABELS[test_type] || test_type
  const badgeClass = `badge-${test_type}` in document.createElement('div').style
    ? `badge-${test_type}`
    : 'badge-K'

  return (
    <div
      className="assessment-card rounded-2xl p-4 cursor-default animate-slide-up"
      style={{ animationDelay: `${index * 0.06}s` }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-display font-semibold text-[var(--color-text)] text-base leading-snug truncate">
            {name}
          </h3>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <span className={clsx('px-2 py-0.5 rounded-md text-xs font-medium', `badge-${test_type}`)}>
              {test_type} · {typeLabel}
            </span>
            <ConfidencePill score={confidence_score} />
          </div>
        </div>

        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-shl-500/10 text-shl-400 border border-shl-500/20 hover:bg-shl-500/20 hover:border-shl-500/40 transition-all duration-200"
          onClick={(e) => e.stopPropagation()}
        >
          View
          <ExternalLink size={11} />
        </a>
      </div>

      {/* Description */}
      {description && (
        <p className="text-sm text-[var(--color-text-muted)] leading-relaxed mb-3 line-clamp-2">
          {description}
        </p>
      )}

      {/* Meta row */}
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-[var(--color-text-muted)]">
        {duration && (
          <span className="flex items-center gap-1.5">
            <Clock size={12} className="text-shl-400" />
            {duration}
          </span>
        )}
      </div>

      {/* Skills */}
      {skills_measured && skills_measured.length > 0 && (
        <div className="mt-3 pt-3 border-t border-[var(--color-border)]">
          <div className="flex items-center gap-1.5 mb-2">
            <Layers size={11} className="text-[var(--color-text-muted)]" />
            <span className="text-xs text-[var(--color-text-muted)] font-medium uppercase tracking-wide">
              Skills
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {skills_measured.slice(0, 6).map((skill, i) => (
              <span
                key={i}
                className="px-2 py-0.5 rounded-md text-xs bg-white/5 border border-white/8 text-[var(--color-text-muted)]"
              >
                {skill}
              </span>
            ))}
            {skills_measured.length > 6 && (
              <span className="px-2 py-0.5 rounded-md text-xs text-[var(--color-text-muted)]">
                +{skills_measured.length - 6} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
