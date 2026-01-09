import { env } from '$env/dynamic/public';

/**
 * Environment configuration with type-safe access and validation
 */
export const config = {
	/**
	 * Backend API base URL
	 * @default 'http://localhost:8000'
	 */
	apiUrl: env.PUBLIC_API_URL || 'http://localhost:8000',

	/**
	 * API request timeout in milliseconds
	 * @default 30000
	 */
	apiTimeout: parseInt(env.PUBLIC_API_TIMEOUT || '30000', 10)
} as const;

/**
 * Validate environment configuration
 * @throws {Error} If required environment variables are missing or invalid
 */
export function validateEnv(): void {
	if (!config.apiUrl) {
		throw new Error('PUBLIC_API_URL is required');
	}

	// Validate URL format
	try {
		new URL(config.apiUrl);
	} catch {
		throw new Error(`Invalid PUBLIC_API_URL: ${config.apiUrl}`);
	}

	// Validate timeout
	if (isNaN(config.apiTimeout) || config.apiTimeout <= 0) {
		throw new Error(`Invalid PUBLIC_API_TIMEOUT: ${config.apiTimeout}`);
	}
}
