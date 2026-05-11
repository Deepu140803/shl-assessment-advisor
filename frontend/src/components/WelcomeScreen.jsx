/**
 * WelcomeScreen Component
 * Displayed when there are no messages yet.
 */

import { Sparkles, Search, GitCompare, ShieldCheck } from 'lucide-react'

const FEATURES = [
  {
    icon: Search,
    title: 'Smart Recommendations',
    desc: 'Describe your role and I\'ll find the best matching SHL assessments.',
  },
  {
    icon: GitCompare,
    title: 'Compare Assessments',
    desc: 'Ask me to compare any two assessments side-by-side.',
  },
  {
    icon: ShieldCheck,
    title: 'Catalog Grounded',
    desc: 'All recommendations are grounded in real SHL catalog data. No hallucinations.',
  },
]

export default function WelcomeScreen() {
  return (
    <div className="flex flex-col items-center justify-center h-full px-6 py-12 text-center">
      {/* Hero icon */}
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-shl-400 to-shl-700 flex items-center justify-center shadow-glow-shl">
          <Sparkles size={28} className="text-white" />
        </div>
        <div className="absolute -inset-2 rounded-3xl bg-shl-500/15 blur-xl -z-10" />
      </div>

      <h2 className="font-display font-bold text-2xl text-[var(--color-text)] mb-2 leading-tight">
        SHL Assessment Advisor
      </h2>
      <p className="text-[var(--color-text-muted)] text-sm max-w-xs leading-relaxed mb-10">
        Tell me about the role you're hiring for and I'll recommend the right SHL assessments through conversation.
      </p>

      {/* Feature cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-xl">
        {FEATURES.map((f, i) => (
          <div
            key={i}
            className="glass-card rounded-2xl p-4 text-left animate-slide-up"
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            <div className="w-8 h-8 rounded-lg bg-shl-500/15 flex items-center justify-center mb-3">
              <f.icon size={15} className="text-shl-400" />
            </div>
            <h3 className="font-display font-semibold text-sm text-[var(--color-text)] mb-1">
              {f.title}
            </h3>
            <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>

      <p className="mt-10 text-xs text-[var(--color-text-muted)]">
        Try: <em>"I need to hire a senior Java developer"</em> or <em>"What personality tests does SHL offer?"</em>
      </p>
    </div>
  )
}
