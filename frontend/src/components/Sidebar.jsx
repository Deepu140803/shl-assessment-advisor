/**
 * Sidebar Component
 * Shows app branding, quick-start prompts, and conversation controls.
 */

import { RefreshCw, Sun, Moon, Sparkles, BookOpen, Users, Code2, Brain } from 'lucide-react'
import clsx from 'clsx'

const QUICK_PROMPTS = [
  {
    icon: Code2,
    label: 'Hire a Python developer',
    prompt: 'I need to hire a senior Python/Django developer. What assessments should I use?',
  },
  {
    icon: Brain,
    label: 'Graduate aptitude tests',
    prompt: 'What cognitive ability tests does SHL offer for graduate recruitment?',
  },
  {
    icon: Users,
    label: 'Sales personality',
    prompt: 'I need personality assessments for a sales team hiring drive.',
  },
  {
    icon: BookOpen,
    label: 'Compare OPQ vs SJT',
    prompt: 'What is the difference between the OPQ32r and a Situational Judgement Test?',
  },
]

export default function Sidebar({ onNewChat, onQuickPrompt, isDark, onToggleTheme, turnCount, maxTurns }) {
  return (
    <aside className="flex flex-col h-full p-5 gap-5">
      {/* Brand */}
      <div>
        <div className="flex items-center gap-2.5 mb-1">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-shl-400 to-shl-600 flex items-center justify-center shadow-glow-shl">
            <Sparkles size={15} className="text-white" />
          </div>
          <div>
            <h1 className="font-display font-bold text-base text-[var(--color-text)] leading-none">
              SHL Advisor
            </h1>
            <p className="text-[11px] text-[var(--color-text-muted)] leading-none mt-0.5">
              Assessment Recommender
            </p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex gap-2">
        <button
          onClick={onNewChat}
          className={clsx(
            'flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-sm font-medium',
            'bg-shl-500/10 text-shl-400 border border-shl-500/20',
            'hover:bg-shl-500/20 hover:border-shl-500/35 transition-all duration-200'
          )}
        >
          <RefreshCw size={13} />
          New Chat
        </button>
        <button
          onClick={onToggleTheme}
          className={clsx(
            'w-10 flex items-center justify-center rounded-xl text-sm',
            'bg-white/5 border border-white/8 text-[var(--color-text-muted)]',
            'hover:bg-white/10 transition-all duration-200'
          )}
          aria-label="Toggle theme"
        >
          {isDark ? <Sun size={15} /> : <Moon size={15} />}
        </button>
      </div>

      {/* Turn counter */}
      {turnCount > 0 && (
        <div className="glass-card rounded-xl p-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-[var(--color-text-muted)]">Conversation turns</span>
            <span className="text-xs font-mono text-[var(--color-text)]">
              {turnCount}/{maxTurns}
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-white/8 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-shl-500 to-shl-400 transition-all duration-500"
              style={{ width: `${(turnCount / maxTurns) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Quick Prompts */}
      <div className="flex-1">
        <p className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-2.5">
          Quick Start
        </p>
        <div className="space-y-1.5">
          {QUICK_PROMPTS.map((qp, i) => (
            <button
              key={i}
              onClick={() => onQuickPrompt(qp.prompt)}
              className={clsx(
                'w-full text-left flex items-start gap-2.5 px-3 py-2.5 rounded-xl text-sm',
                'text-[var(--color-text-muted)] hover:text-[var(--color-text)]',
                'bg-white/0 hover:bg-white/5 border border-transparent hover:border-white/8',
                'transition-all duration-200 group'
              )}
            >
              <qp.icon
                size={14}
                className="flex-shrink-0 mt-0.5 text-shl-400 group-hover:text-shl-300 transition-colors"
              />
              <span className="leading-snug">{qp.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="text-[11px] text-[var(--color-text-muted)] leading-relaxed">
        <p>Recommendations are based on the SHL Individual Test Solutions catalog only.</p>
      </div>
    </aside>
  )
}
