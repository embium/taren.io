import { z } from 'zod';
import { emailSchema, passwordSchema, usernameSchema } from '$lib/types/auth';
import { ValidationError } from '$lib/types/auth';

/**
 * Validation utilities using Zod schemas
 */

/**
 * Validate email format
 */
export function validateEmail(email: string): { valid: boolean; error?: string } {
	const result = emailSchema.safeParse(email);
	if (!result.success) {
		return { valid: false, error: result.error.issues[0]?.message || 'Invalid email' };
	}
	return { valid: true };
}

/**
 * Validate username format
 */
export function validateUsername(username: string): { valid: boolean; error?: string } {
	const result = usernameSchema.safeParse(username);
	if (!result.success) {
		return { valid: false, error: result.error.issues[0]?.message || 'Invalid username' };
	}
	return { valid: true };
}

/**
 * Validate password strength according to backend requirements
 */
export function validatePassword(password: string): { valid: boolean; error?: string } {
	const result = passwordSchema.safeParse(password);
	if (!result.success) {
		return { valid: false, error: result.error.issues[0]?.message || 'Invalid password' };
	}
	return { valid: true };
}

/**
 * Calculate password strength (0-4)
 * 0 = Very Weak, 1 = Weak, 2 = Fair, 3 = Good, 4 = Strong
 */
export function getPasswordStrength(password: string): number {
	if (!password) return 0;

	let strength = 0;

	// Length check
	if (password.length >= 8) strength++;
	if (password.length >= 12) strength++;

	// Character variety
	if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
	if (/\d/.test(password)) strength++;
	if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) strength++;

	return Math.min(strength, 4);
}

/**
 * Get password strength label and color
 */
export function getPasswordStrengthInfo(strength: number): {
	label: string;
	color: string;
} {
	const info = [
		{ label: 'Very Weak', color: 'red' },
		{ label: 'Weak', color: 'orange' },
		{ label: 'Fair', color: 'yellow' },
		{ label: 'Good', color: 'lightgreen' },
		{ label: 'Strong', color: 'green' }
	];
	return info[strength] || info[0];
}

/**
 * Validate password confirmation
 */
export function validatePasswordConfirmation(
	password: string,
	confirmation: string
): { valid: boolean; error?: string } {
	if (!confirmation) {
		return { valid: false, error: 'Password confirmation is required' };
	}

	if (password !== confirmation) {
		return { valid: false, error: 'Passwords do not match' };
	}

	return { valid: true };
}

/**
 * Validate using Zod schema and return formatted result
 */
export function validateWithSchema<T>(
	schema: z.ZodSchema<T>,
	data: unknown
): { valid: boolean; data?: T; error?: string; issues?: z.ZodIssue[] } {
	const result = schema.safeParse(data);

	if (!result.success) {
		return {
			valid: false,
			error: result.error.issues[0]?.message || 'Validation failed',
			issues: result.error.issues
		};
	}

	return {
		valid: true,
		data: result.data
	};
}

/**
 * Extract field-specific errors from Zod errors
 */
export function getFieldErrors(issues: z.ZodIssue[]): Record<string, string> {
	const errors: Record<string, string> = {};

	for (const issue of issues) {
		const path = issue.path.join('.');
		if (!errors[path]) {
			errors[path] = issue.message;
		}
	}

	return errors;
}

/**
 * Format Zod errors for user display
 */
export function formatValidationErrors(zodError: z.ZodError): string {
	return zodError.issues.map((issue) => issue.message).join(', ');
}
