/**
 * Secure storage utility for tokens with SSR compatibility
 */

const isBrowser = typeof window !== 'undefined';

export const storage = {
	/**
	 * Get item from localStorage (SSR-safe)
	 */
	getItem(key: string): string | null {
		if (!isBrowser) return null;
		try {
			return localStorage.getItem(key);
		} catch (error) {
			console.error('Error reading from localStorage:', error);
			return null;
		}
	},

	/**
	 * Set item in localStorage (SSR-safe)
	 */
	setItem(key: string, value: string): void {
		if (!isBrowser) return;
		try {
			localStorage.setItem(key, value);
		} catch (error) {
			console.error('Error writing to localStorage:', error);
		}
	},

	/**
	 * Remove item from localStorage (SSR-safe)
	 */
	removeItem(key: string): void {
		if (!isBrowser) return;
		try {
			localStorage.removeItem(key);
		} catch (error) {
			console.error('Error removing from localStorage:', error);
		}
	},

	/**
	 * Clear all items from localStorage (SSR-safe)
	 */
	clear(): void {
		if (!isBrowser) return;
		try {
			localStorage.clear();
		} catch (error) {
			console.error('Error clearing localStorage:', error);
		}
	}
};

/**
 * Token storage keys
 */
export const STORAGE_KEYS = {
	REFRESH_TOKEN: 'auth_refresh_token',
	USER: 'auth_user'
} as const;
