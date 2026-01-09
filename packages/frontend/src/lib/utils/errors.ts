import type { ErrorResponse } from '$lib/types/auth';
import { AuthError, NetworkError } from '$lib/types/auth';

/**
 * Map API error responses to user-friendly messages
 */
export function mapErrorToMessage(error: unknown): string {
	if (error instanceof AuthError) {
		return error.message;
	}

	if (error instanceof NetworkError) {
		return 'Unable to connect to the server. Please check your internet connection.';
	}

	if (error && typeof error === 'object' && 'detail' in error) {
		const errorResponse = error as ErrorResponse;
		return errorResponse.detail;
	}

	if (error instanceof Error) {
		return error.message;
	}

	return 'An unexpected error occurred. Please try again.';
}

/**
 * Categorize errors for different handling strategies
 */
export function categorizeError(error: unknown): {
	type: 'auth' | 'network' | 'validation' | 'unknown';
	message: string;
	recoverable: boolean;
} {
	if (error instanceof AuthError) {
		return {
			type: 'auth',
			message: error.message,
			recoverable: error.statusCode === 401 || error.statusCode === 403
		};
	}

	if (error instanceof NetworkError) {
		return {
			type: 'network',
			message: mapErrorToMessage(error),
			recoverable: true
		};
	}

	return {
		type: 'unknown',
		message: mapErrorToMessage(error),
		recoverable: false
	};
}
