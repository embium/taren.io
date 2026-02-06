import { config } from '$lib/config/env';
import type { RequestEvent } from '@sveltejs/kit';

/**
 * Server-side API client - uses cookies automatically
 * This client is used in +page.server.ts and +layout.server.ts files
 */
export function createServerApi(event: RequestEvent) {
	const baseUrl = config.apiUrl;

	async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
		const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;

		// Forward cookies from the incoming request
		const headers: HeadersInit = {
			'Content-Type': 'application/json',
			...options.headers,
			// Forward cookies to backend
			cookie: event.request.headers.get('cookie') || ''
		};

		const response = await fetch(url, {
			...options,
			headers,
			credentials: 'include' // Important: include cookies
		});

		if (!response.ok) {
			const error = await response.json().catch(() => ({
				detail: `HTTP ${response.status}`
			}));
			throw new Error(error.detail || 'API request failed');
		}

		return response.json();
	}

	return {
		get: <T>(endpoint: string) => request<T>(endpoint, { method: 'GET' }),
		post: <T>(endpoint: string, data?: unknown) =>
			request<T>(endpoint, {
				method: 'POST',
				body: data ? JSON.stringify(data) : undefined
			}),
		put: <T>(endpoint: string, data?: unknown) =>
			request<T>(endpoint, {
				method: 'PUT',
				body: data ? JSON.stringify(data) : undefined
			}),
		patch: <T>(endpoint: string, data?: unknown) =>
			request<T>(endpoint, {
				method: 'PATCH',
				body: data ? JSON.stringify(data) : undefined
			}),
		delete: <T>(endpoint: string) => request<T>(endpoint, { method: 'DELETE' })
	};
}
