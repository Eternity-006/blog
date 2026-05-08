// API base URL — configure via VITE_API_URL env var at build time
// Empty = same origin (works for dev proxy and all-in-one deployment)
// Set to "https://your-backend.example.com" for separate frontend/backend deployment
const BASE = import.meta.env.VITE_API_URL || ''

export async function api(path: string, options?: RequestInit): Promise<Response> {
  return fetch(BASE + path, options)
}
