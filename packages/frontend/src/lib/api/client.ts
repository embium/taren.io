import { config } from '$lib/config/env';
import { AuthError, NetworkError, type ErrorResponse } from '$lib/types/auth';
import { errorResponseSchema } from '$lib/types/auth';
import { storage, STORAGE_KEYS } from '$lib/stores/storage';

/**
 * API Client with automatic token injection, refresh, and retry logic
 */

let accessToken: string | null = null;
let refreshToken: string | null = null;
let tokenRefreshPromise: Promise<string> | null = null;

/**
 * Set tokens in memory
 */
export function setTokens(access: string, refresh: string): void {
	accessToken = access;
	refreshToken = refresh;
}

/**
 * Get current access token
 */
export function getAccessToken(): string | null {
	return accessToken;
}

/**
 * Get current refresh token
 */
export function getRefreshToken(): string | null {
	return refreshToken;
}

/**
 * Clear tokens from memory
 */
export function clearTokens(): void {
	accessToken = null;
	refreshToken = null;
	tokenRefreshPromise = null;
}

/**
 * Refresh the access token using the refresh token
 */
async function refreshAccessToken(): Promise<string> {
	if (!refreshToken) {
		throw new AuthError('No refresh token available', 'NO_REFRESH_TOKEN', 401);
	}

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
				body: JSON.stringify({ refresh_token: refreshToken })
			});

			if (!response.ok) {
				throw new AuthError('Failed to refresh token', 'REFRESH_FAILED', response.status);
			}

			const data = await response.json();
			accessToken = data.access_token;
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

	// Add authorization header if not skipping auth
	if (!skipAuth && accessToken) {
		headers['Authorization'] = `Bearer ${accessToken}`;
	}

	try {
		const response = await fetch(url, {
			...fetchOptions,
			headers,
			credentials: 'include', // CRITICAL: Send cookies with requests
			signal: AbortSignal.timeout(config.apiTimeout)
		});

		// Handle 401 Unauthorized - try to refresh token
		if (response.status === 401 && !skipAuth && refreshToken && retries > 0) {
			try {
				// Refresh the token
				await refreshAccessToken();

				// Retry the request with new token
				return apiRequest<T>(endpoint, { ...options, retries: retries - 1 });
			} catch (refreshError) {
				// If refresh fails, clear all auth state including localStorage
				clearTokens();
				storage.removeItem(STORAGE_KEYS.USER);
				storage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
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
