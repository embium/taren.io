import { goto } from '$app/navigation';
import { toast } from 'svelte-sonner';
import { clearTokens } from '$lib/api/client';
import { clearAuthState } from '$lib/stores/auth.svelte';
import { storage, STORAGE_KEYS } from '$lib/stores/storage';

/**
 * Handles complete logout including clearing state, showing notifications, and redirecting
 * @param message - Optional message to display to the user
 * @param redirect - Optional redirect path (defaults to /login)
 */
export async function handleSessionExpired(
	message: string = 'Your session has expired. Please log in again.',
	redirect: string = '/login'
): Promise<void> {
	// Clear all authentication state
	clearTokens();
	clearAuthState();
	storage.removeItem(STORAGE_KEYS.USER);
	storage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);

	// Show notification to user
	toast.error(message);

	// Redirect to login page
	await goto(redirect);
}
