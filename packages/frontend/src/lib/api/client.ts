import { config } from '$lib/config/env';
import { AuthError, NetworkError, type ErrorResponse } from '$lib/types/auth';
import { errorResponseSchema } from '$lib/types/auth';

/**
 * API Client with automatic token injection, refresh, and retry logic
 * Now entirely relies on HttpOnly cookies for tokens!
 */

let tokenRefreshPromise: Promise<string> | null = null;

/**
 * Refresh the access token via cookie
 */
async function refreshAccessToken(): Promise<string> {
	// If a refresh is already in progress, wait for it
	if (tokenRefreshPromise) {
		return tokenRefreshPromise;
	}

	tokenRefreshPromise = (async () => {
		try {
			const response = await fetch(`${config.apiUrl}/auth/refresh`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include' // Send the refresh_token cookie
			});

			if (!response.ok) {
				throw new AuthError('Failed to refresh token', 'REFRESH_FAILED', response.status);
			}

			const data = await response.json();
			return data.access_token;
		} finally {
			tokenRefreshPromise = null;
		}
	})();

	return tokenRefreshPromise;
}

/**
 * Request options interface
 */
interface RequestOptions extends RequestInit {
	skipAuth?: boolean;
	retries?: number;
}

/**
 * Main API request function with retry logic and automatic token refresh
 */
export async function apiRequest<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
	const { skipAuth = false, retries = 1, ...fetchOptions } = options;

	const url = endpoint.startsWith('http') ? endpoint : `${config.apiUrl}${endpoint}`;

	// Prepare headers
	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(fetchOptions.headers as Record<string, string>)
	};

	try {
		const response = await fetch(url, {
			...fetchOptions,
			headers,
			credentials: 'include', // CRITICAL: Send cookies with requests
			signal: AbortSignal.timeout(config.apiTimeout)
		});

		// Handle 401 Unauthorized - try to refresh token
		if (response.status === 401 && !skipAuth && retries > 0) {
			try {
				// Refresh the token via cookie
				await refreshAccessToken();

				// Retry the request
				return apiRequest<T>(endpoint, { ...options, retries: retries - 1 });
			} catch (refreshError) {
				throw new AuthError('Session expired. Please log in again.', 'SESSION_EXPIRED', 401);
			}
		}

		// Handle other error responses
		if (!response.ok) {
			const errorData = await response.json().catch(() => ({
				detail: `HTTP ${response.status}: ${response.statusText}`
			}));

			// Validate and parse error response
			const parsedError = errorResponseSchema.safeParse(errorData);
			const error: ErrorResponse = parsedError.success
				? parsedError.data
				: { detail: errorData.detail || 'An error occurred' };

			throw new AuthError(error.detail, error.error_code, response.status);
		}

		// Parse and return successful response
		return await response.json();
	} catch (err: unknown) {
		// Handle network errors
		if (
			err instanceof TypeError ||
			(err && typeof err === 'object' && 'name' in err && err.name === 'AbortError')
		) {
			throw new NetworkError(
				err && typeof err === 'object' && 'name' in err && err.name === 'AbortError'
					? 'Request timed out. Please try again.'
					: 'Network error. Please check your connection.',
				err
			);
		}

		// Re-throw AuthError and other custom errors
		if (err instanceof AuthError || err instanceof NetworkError) {
			throw err;
		}

		// Wrap unknown errors
		throw new AuthError('An unexpected error occurred', 'UNKNOWN_ERROR');
	}
}

/**
 * Convenience methods for common HTTP verbs
 */
export const api = {
	get: <T>(endpoint: string, options?: RequestOptions) =>
		apiRequest<T>(endpoint, { ...options, method: 'GET' }),

	post: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
		apiRequest<T>(endpoint, {
			...options,
			method: 'POST',
			body: data ? JSON.stringify(data) : undefined
		}),

	put: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
		apiRequest<T>(endpoint, {
			...options,
			method: 'PUT',
			body: data ? JSON.stringify(data) : undefined
		}),

	patch: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
		apiRequest<T>(endpoint, {
			...options,
			method: 'PATCH',
			body: data ? JSON.stringify(data) : undefined
		}),

	delete: <T>(endpoint: string, data?: unknown, options?: RequestOptions) =>
		apiRequest<T>(endpoint, {
			...options,
			method: 'DELETE',
			body: data ? JSON.stringify(data) : undefined
		})
};
