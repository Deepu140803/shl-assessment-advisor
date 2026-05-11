/**
 * App Component
 * Root application layout: sidebar + chat area.
 */

import { useRef, useEffect, useState } from 'react'
import { Menu, X } from 'lucide-react'
import clsx from 'clsx'
import { useChat } from './hooks/useChat'
import { useTheme } from './hooks/useTheme'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import Sidebar from './components/Sidebar'
import WelcomeScreen from './components/WelcomeScreen'

const MAX_TURNS = 8

export default function App() {
  const { messages, isLoading, error, isConversationEnded, sendMessage, resetConversation } =
    useChat()
  const { isDark, toggleTheme } = useTheme()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const bottomRef = useRef(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const turnCount = messages.filter((m) => m.role === 'user').length

  const handleQuickPrompt = (prompt) => {
    setSidebarOpen(false)
    sendMessage(prompt)
  }

  const handleNewChat = () => {
    setSidebarOpen(false)
    resetConversation()
  }

  return (
    <div className={clsx('noise-overlay bg-animated min-h-dvh flex', isDark ? 'dark' : 'light')}>
      {/* ── Mobile sidebar overlay ── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ── */}
      <aside
        className={clsx(
          'fixed md:relative z-50 md:z-auto h-full md:h-dvh',
          'w-72 flex-shrink-0',
          'glass-card border-r border-[var(--color-border)]',
          'transition-transform duration-300 ease-out',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        <Sidebar
          onNewChat={handleNewChat}
          onQuickPrompt={handleQuickPrompt}
          isDark={isDark}
          onToggleTheme={toggleTheme}
          turnCount={turnCount}
          maxTurns={MAX_TURNS}
        />
      </aside>

      {/* ── Main Chat Area ── */}
      <main className="flex-1 flex flex-col h-dvh min-w-0">
        {/* Top bar (mobile) */}
        <header className="md:hidden flex items-center gap-3 px-4 py-3 border-b border-[var(--color-border)] glass-card">
          <button
            onClick={() => setSidebarOpen(true)}
            className="w-9 h-9 flex items-center justify-center rounded-xl bg-white/5 border border-white/8 text-[var(--color-text-muted)]"
            aria-label="Open sidebar"
          >
            <Menu size={18} />
          </button>
          <span className="font-display font-semibold text-[var(--color-text)]">
            SHL Advisor
          </span>
        </header>

        {/* Message list */}
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6">
          {messages.length === 0 ? (
            <WelcomeScreen />
          ) : (
            messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
          )}

          {/* Error banner */}
          {error && (
            <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-400 text-sm animate-fade-in">
              <span className="w-2 h-2 rounded-full bg-rose-400 flex-shrink-0" />
              {error}
            </div>
          )}

          {/* Conversation ended notice */}
          {isConversationEnded && (
            <div className="flex items-center justify-center animate-fade-in">
              <div className="px-4 py-2 rounded-full glass-card text-xs text-[var(--color-text-muted)] border border-[var(--color-border)]">
                Conversation complete · Start a new chat to continue
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div className="px-4 md:px-8 py-4 border-t border-[var(--color-border)]">
          <div className="max-w-3xl mx-auto">
            <ChatInput
              onSend={sendMessage}
              isLoading={isLoading}
              disabled={isConversationEnded}
            />
          </div>
        </div>
      </main>
    </div>
  )
}
