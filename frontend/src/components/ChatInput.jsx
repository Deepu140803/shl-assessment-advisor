/**
 * ChatInput Component
 * Text input bar with send button and keyboard support.
 */

import { useState, useRef, useEffect } from 'react'
import { Send, Square } from 'lucide-react'
import clsx from 'clsx'

export default function ChatInput({ onSend, isLoading, disabled }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`
  }, [value])

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || isLoading || disabled) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="relative">
      <div
        className={clsx(
          'flex items-end gap-2 rounded-2xl border p-2 transition-all duration-200',
          'chat-input',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            disabled
              ? 'Conversation ended. Press New Chat to start over.'
              : 'Ask about SHL assessments… (Shift+Enter for new line)'
          }
          disabled={disabled || isLoading}
          rows={1}
          className={clsx(
            'flex-1 bg-transparent resize-none text-sm leading-relaxed py-2 px-2',
            'placeholder:text-[var(--color-text-muted)] text-[var(--color-text)]',
            'focus:outline-none disabled:cursor-not-allowed',
            'min-h-[40px] max-h-[160px] overflow-y-auto'
          )}
          style={{ fontFamily: 'inherit' }}
        />

        <button
          onClick={handleSend}
          disabled={!value.trim() || isLoading || disabled}
          className={clsx(
            'flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center',
            'transition-all duration-200 font-medium',
            value.trim() && !isLoading && !disabled
              ? 'bg-shl-500 text-white hover:bg-shl-400 shadow-glow-shl hover:scale-105 active:scale-95'
              : 'bg-white/5 text-[var(--color-text-muted)] cursor-not-allowed'
          )}
          aria-label="Send message"
        >
          {isLoading ? (
            <Square size={14} className="animate-pulse" />
          ) : (
            <Send size={14} />
          )}
        </button>
      </div>

      <p className="text-[11px] text-[var(--color-text-muted)] text-center mt-2">
        Powered by SHL catalog · AI recommendations only · Not legal advice
      </p>
    </div>
  )
}
