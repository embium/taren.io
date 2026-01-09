/**
 * Toast notification store using Svelte 5 runes
 */

export interface Toast {
	id: string;
	type: 'success' | 'error' | 'info' | 'warning';
	message: string;
	duration?: number;
}

// State
let toasts = $state<Toast[]>([]);

/**
 * Add a toast notification
 */
export function addToast(message: string, type: Toast['type'] = 'info', duration = 5000): string {
	const id = `toast-${Date.now()}-${Math.random()}`;

	toasts = [...toasts, { id, type, message, duration }];

	// Auto-dismiss after duration
	if (duration > 0) {
		setTimeout(() => {
			removeToast(id);
		}, duration);
	}

	return id;
}

/**
 * Remove a toast notification
 */
export function removeToast(id: string): void {
	toasts = toasts.filter((t) => t.id !== id);
}

/**
 * Clear all toasts
 */
export function clearToasts(): void {
	toasts = [];
}

/**
 * Convenience methods
 */
export const toast = {
	success: (message: string, duration?: number) => addToast(message, 'success', duration),
	error: (message: string, duration?: number) => addToast(message, 'error', duration),
	info: (message: string, duration?: number) => addToast(message, 'info', duration),
	warning: (message: string, duration?: number) => addToast(message, 'warning', duration)
};

/**
 * Export reactive state
 */
export function getToasts() {
	return {
		get all() {
			return toasts;
		}
	};
}
