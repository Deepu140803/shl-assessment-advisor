/**
 * ChatMessage Component
 * Renders a single chat message (user or assistant) with optional assessment cards.
 */

import { Bot, User } from 'lucide-react'
import clsx from 'clsx'
import AssessmentCard from './AssessmentCard'
import TypingIndicator from './TypingIndicator'

/**
 * Formats assistant message text with simple markdown-like styling.
 */
function FormattedText({ text }) {
  // Split on double newlines for paragraphs
  const paragraphs = text.split(/\n\n+/)

  return (
    <div className="space-y-2">
      {paragraphs.map((para, pi) => {
        // Bold **text**
        const parts = para.split(/(\*\*[^*]+\*\*)/)
        return (
          <p key={pi} className="text-sm leading-relaxed text-[var(--color-text)]">
            {parts.map((part, i) =>
              part.startsWith('**') && part.endsWith('**') ? (
                <strong key={i} className="font-semibold text-[var(--color-text)]">
                  {part.slice(2, -2)}
                </strong>
              ) : (
                <span key={i}>{part}</span>
              )
            )}
          </p>
        )
      })}
    </div>
  )
}

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  const isStreaming = message.isStreaming
  const hasRecommendations =
    message.recommendations && message.recommendations.length > 0

  return (
    <div
      className={clsx(
        'flex gap-3 animate-slide-up',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          'flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center text-sm',
          isUser
            ? 'bg-shl-500 text-white'
            : 'bg-white/8 border border-white/10 text-shl-400'
        )}
      >
        {isUser ? <User size={15} /> : <Bot size={15} />}
      </div>

      {/* Content */}
      <div
        className={clsx(
          'flex-1 max-w-[85%] md:max-w-[75%]',
          isUser ? 'items-end' : 'items-start'
        )}
      >
        {/* Bubble */}
        <div
          className={clsx(
            'rounded-2xl px-4 py-3 mb-2',
            isUser
              ? 'msg-user rounded-tr-sm ml-auto'
              : 'msg-assistant rounded-tl-sm'
          )}
        >
          {isStreaming ? (
            <TypingIndicator />
          ) : isUser ? (
            <p className="text-sm leading-relaxed text-white">{message.content}</p>
          ) : (
            <FormattedText text={message.content} />
          )}
        </div>

        {/* Recommendation Cards (grid below the bubble) */}
        {!isStreaming && hasRecommendations && (
          <div className="space-y-2 mt-2">
            <div className="flex items-center gap-2 px-1">
              <div className="h-px flex-1 bg-[var(--color-border)]" />
              <span className="text-xs text-[var(--color-text-muted)] font-medium uppercase tracking-wide">
                {message.recommendations.length} Assessment{message.recommendations.length > 1 ? 's' : ''} Recommended
              </span>
              <div className="h-px flex-1 bg-[var(--color-border)]" />
            </div>
            <div className="grid grid-cols-1 gap-2">
              {message.recommendations.map((rec, i) => (
                <AssessmentCard key={`${rec.name}-${i}`} assessment={rec} index={i} />
              ))}
            </div>
          </div>
        )}

        {/* Timestamp */}
        {!isStreaming && message.timestamp && (
          <p
            className={clsx(
              'text-[11px] text-[var(--color-text-muted)] mt-1 px-1',
              isUser ? 'text-right' : 'text-left'
            )}
          >
            {new Date(message.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        )}
      </div>
    </div>
  )
}
