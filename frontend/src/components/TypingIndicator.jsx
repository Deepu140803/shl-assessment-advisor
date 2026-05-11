/**
 * TypingIndicator Component
 * Animated three-dot indicator shown while AI is processing.
 */

export default function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3">
      <div className="flex items-center gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="typing-dot w-2 h-2 rounded-full bg-shl-400 block"
            style={{ animationDelay: `${i * 0.2}s` }}
          />
        ))}
      </div>
      <span className="text-xs text-[var(--color-text-muted)] ml-1 font-body">
        SHL Advisor is thinking…
      </span>
    </div>
  )
}
