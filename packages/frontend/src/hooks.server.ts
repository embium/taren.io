import type { Handle } from '@sveltejs/kit';
import { config } from '$lib/config/env';

export const handle: Handle = async ({ event, resolve }) => {
	// Try to get user from access_token cookie
	const accessToken = event.cookies.get('access_token');

	if (accessToken) {
		try {
			// Validate token by calling backend
			const response = await fetch(`${config.apiUrl}/users/me`, {
				headers: {
					Authorization: `Bearer ${accessToken}`
				}
			});

			if (response.ok) {
				const user = await response.json();
				event.locals.user = user;
			}
		} catch (error) {
			console.error('Failed to validate user token:', error);
			// Clear invalid cookies
			event.cookies.delete('access_token', { path: '/' });
			event.cookies.delete('refresh_token', { path: '/' });
		}
	}

	return resolve(event);
};
