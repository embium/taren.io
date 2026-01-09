import { authApi } from '$lib/api/auth.api';
import { clearTokens, setTokens } from '$lib/api/client';
import { storage, STORAGE_KEYS } from '$lib/stores/storage';
import type { User, LoginRequest, RegisterUserRequest } from '$lib/types/auth';
import { AuthError } from '$lib/types/auth';

/**
 * Authentication store using Svelte 5 runes
 */

// State
let user = $state<User | null>(null);
let loading = $state(false);
let error = $state<string | null>(null);
let initialized = $state(false);

// Derived state
const isAuthenticated = $derived(user !== null);

/**
 * Initialize auth state from storage
 */
export function initializeAuth(): void {
	if (initialized) return;

	const storedUser = storage.getItem(STORAGE_KEYS.USER);
	const storedRefreshToken = storage.getItem(STORAGE_KEYS.REFRESH_TOKEN);

	if (storedUser && storedRefreshToken) {
		try {
			user = JSON.parse(storedUser);
			setTokens('', storedRefreshToken); // Access token will be refreshed on first request
		} catch (err) {
			console.error('Failed to parse stored user:', err);
			clearAuth();
		}
	}

	initialized = true;
}

/**
 * Clear auth state
 */
function clearAuth(): void {
	user = null;
	error = null;
	clearTokens();
	storage.removeItem(STORAGE_KEYS.USER);
	storage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
}

/**
 * Store auth data
 */
function storeAuth(userData: User, accessToken: string, refreshToken: string): void {
	user = userData;
	setTokens(accessToken, refreshToken);
	storage.setItem(STORAGE_KEYS.USER, JSON.stringify(userData));
	storage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken);
}

/**
 * Login user
 */
export async function login(credentials: LoginRequest): Promise<void> {
	loading = true;
	error = null;

	try {
		const response = await authApi.login(credentials);
		storeAuth(response.user, response.access_token, response.refresh_token);
	} catch (err) {
		error = err instanceof AuthError ? err.message : 'Login failed. Please try again.';
		throw err;
	} finally {
		loading = false;
	}
}

/**
 * Register new user
 */
export async function register(credentials: RegisterUserRequest): Promise<void> {
	loading = true;
	error = null;

	try {
		const response = await authApi.register(credentials);

		// After registration, log the user in
		await login({ email: credentials.email, password: credentials.password });
	} catch (err) {
		error = err instanceof AuthError ? err.message : 'Registration failed. Please try again.';
		throw err;
	} finally {
		loading = false;
	}
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
	loading = true;
	error = null;

	try {
		await authApi.logout();
	} catch (err) {
		console.error('Logout error:', err);
		// Continue with local logout even if API call fails
	} finally {
		clearAuth();
		loading = false;
	}
}

/**
 * Get current user
 */
export async function fetchCurrentUser(): Promise<void> {
	if (!isAuthenticated) return;

	loading = true;
	error = null;

	try {
		const userData = await authApi.getCurrentUser();
		user = userData;
		storage.setItem(STORAGE_KEYS.USER, JSON.stringify(userData));
	} catch (err) {
		error = err instanceof AuthError ? err.message : 'Failed to fetch user data. Please try again.';

		// If unauthorized, clear auth
		if (err instanceof AuthError && err.statusCode === 401) {
			clearAuth();
		}

		throw err;
	} finally {
		loading = false;
	}
}

/**
 * Clear error state
 */
export function clearError(): void {
	error = null;
}

/**
 * Export reactive state
 */
export function getAuthState() {
	return {
		get user() {
			return user;
		},
		get loading() {
			return loading;
		},
		get error() {
			return error;
		},
		get isAuthenticated() {
			return isAuthenticated;
		}
	};
}
