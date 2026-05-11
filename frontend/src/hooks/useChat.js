/**
 * useChat Hook
 * Manages conversation state, API calls, and message history.
 */

import { useState, useCallback, useRef } from 'react'
import { sendChat } from '../utils/api'

/**
 * @typedef {Object} ChatMessage
 * @property {string} id - Unique message ID
 * @property {'user'|'assistant'} role - Message sender role
 * @property {string} content - Message text
 * @property {Array} recommendations - Assessment recommendations (assistant only)
 * @property {boolean} isStreaming - Whether message is still loading
 * @property {number} timestamp - Unix timestamp
 */

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isConversationEnded, setIsConversationEnded] = useState(false)
  const messagesRef = useRef([])

  /**
   * Send a user message and receive an AI response.
   * @param {string} content - User's message text
   */
  const sendMessage = useCallback(async (content) => {
    if (!content.trim() || isLoading || isConversationEnded) return

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      recommendations: [],
      timestamp: Date.now(),
    }

    // Add user message
    const newMessages = [...messagesRef.current, userMessage]
    messagesRef.current = newMessages
    setMessages([...newMessages])
    setError(null)
    setIsLoading(true)

    // Add placeholder for assistant response
    const placeholderId = `assistant-${Date.now()}`
    const placeholder = {
      id: placeholderId,
      role: 'assistant',
      content: '',
      recommendations: [],
      isStreaming: true,
      timestamp: Date.now(),
    }
    setMessages([...newMessages, placeholder])

    try {
      // Build API message format (only role + content for API)
      const apiMessages = newMessages.map((m) => ({
        role: m.role,
        content: m.content,
      }))

      const response = await sendChat(apiMessages)

      const assistantMessage = {
        id: placeholderId,
        role: 'assistant',
        content: response.reply || '',
        recommendations: response.recommendations || [],
        isStreaming: false,
        timestamp: Date.now(),
      }

      // Replace placeholder with real response
      const finalMessages = [...newMessages, assistantMessage]
      messagesRef.current = finalMessages
      setMessages([...finalMessages])

      if (response.end_of_conversation) {
        setIsConversationEnded(true)
      }
    } catch (err) {
      console.error('Chat error:', err)
      setError(err.message || 'Failed to get a response. Please try again.')

      // Remove placeholder
      setMessages([...newMessages])
      messagesRef.current = newMessages
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, isConversationEnded])

  /**
   * Reset the conversation to start fresh.
   */
  const resetConversation = useCallback(() => {
    setMessages([])
    messagesRef.current = []
    setError(null)
    setIsLoading(false)
    setIsConversationEnded(false)
  }, [])

  return {
    messages,
    isLoading,
    error,
    isConversationEnded,
    sendMessage,
    resetConversation,
  }
}
