/**
 * SHL Recommender API Client
 * Communicates with the FastAPI backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api'

/**
 * Send a chat message (with full conversation history) to the backend.
 *
 * @param {Array<{role: string, content: string}>} messages - Full conversation history
 * @returns {Promise<{reply: string, recommendations: Array, end_of_conversation: boolean}>}
 */
export async function sendChat(messages) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ messages }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `API error: ${response.status}`)
  }

  return response.json()
}

/**
 * Check if the backend is healthy.
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const resp = await fetch(`${API_BASE}/health`, { method: 'GET' })
    if (!resp.ok) return false
    const data = await resp.json()
    return data.status === 'ok'
  } catch {
    return false
  }
}
