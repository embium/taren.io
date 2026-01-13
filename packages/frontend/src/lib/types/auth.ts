import { z } from 'zod';

/**
 * Authentication-related Zod schemas and TypeScript types
 */

// ============================================================================
// Validation Schemas
// ============================================================================

/**
 * Email validation schema
 */
export const emailSchema = z.string().email('Invalid email format').min(1, 'Email is required');

/**
 * Password validation schema matching backend requirements:
 * - Minimum 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one digit
 * - At least one special character
 */
export const passwordSchema = z
	.string()
	.min(8, 'Password must be at least 8 characters long')
	.regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
	.regex(/[a-z]/, 'Password must contain at least one lowercase letter')
	.regex(/\d/, 'Password must contain at least one digit')
	.regex(
		/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/,
		'Password must contain at least one special character'
	);

// ============================================================================
// Request Schemas
// ============================================================================

export const loginRequestSchema = z.object({
	email: emailSchema,
	password: z.string().min(1, 'Password is required')
});

export const registerUserRequestSchema = z.object({
	email: emailSchema,
	password: passwordSchema
});

export const refreshTokenRequestSchema = z.object({
	refresh_token: z.string().min(1, 'Refresh token is required')
});

export const changePasswordRequestSchema = z.object({
	current_password: z.string().min(1, 'Current password is required'),
	new_password: passwordSchema
});

// ============================================================================
// Response Schemas
// ============================================================================

export const userSchema = z.object({
	id: z.string(),
	email: z.string().email(),
	name: z.string().nullable(),
	avatar: z.string().nullable(),
	created_at: z.string(),
	is_active: z.boolean()
});

export const loginResponseSchema = z.object({
	access_token: z.string(),
	refresh_token: z.string(),
	token_type: z.string(),
	expires_in: z.number(),
	user: userSchema
});

export const registerUserResponseSchema = z.object({
	user_id: z.string(),
	email: z.string().email(),
	created_at: z.string(),
	message: z.string()
});

export const refreshTokenResponseSchema = z.object({
	access_token: z.string(),
	token_type: z.string(),
	expires_in: z.number()
});

export const logoutResponseSchema = z.object({
	message: z.string()
});

export const changePasswordResponseSchema = z.object({
	message: z.string()
});

export const errorResponseSchema = z.object({
	detail: z.string(),
	error_code: z.string().optional()
});

// ============================================================================
// TypeScript Types (inferred from schemas)
// ============================================================================

export type LoginRequest = z.infer<typeof loginRequestSchema>;
export type RegisterUserRequest = z.infer<typeof registerUserRequestSchema>;
export type RefreshTokenRequest = z.infer<typeof refreshTokenRequestSchema>;
export type ChangePasswordRequest = z.infer<typeof changePasswordRequestSchema>;

export type User = z.infer<typeof userSchema>;
export type LoginResponse = z.infer<typeof loginResponseSchema>;
export type RegisterUserResponse = z.infer<typeof registerUserResponseSchema>;
export type RefreshTokenResponse = z.infer<typeof refreshTokenResponseSchema>;
export type LogoutResponse = z.infer<typeof logoutResponseSchema>;
export type ChangePasswordResponse = z.infer<typeof changePasswordResponseSchema>;
export type ErrorResponse = z.infer<typeof errorResponseSchema>;

// ============================================================================
// Error Classes
// ============================================================================

export class AuthError extends Error {
	constructor(
		message: string,
		public code?: string,
		public statusCode?: number
	) {
		super(message);
		this.name = 'AuthError';
	}
}

export class NetworkError extends Error {
	constructor(
		message: string,
		public originalError?: unknown
	) {
		super(message);
		this.name = 'NetworkError';
	}
}

export class ValidationError extends Error {
	constructor(
		message: string,
		public field?: string,
		public issues?: z.ZodIssue[]
	) {
		super(message);
		this.name = 'ValidationError';
	}
}

// ============================================================================
// Token Types
// ============================================================================

export interface TokenPair {
	accessToken: string;
	refreshToken: string;
	expiresIn: number;
}

export interface DecodedToken {
	sub: string; // user_id
	session_id: string;
	exp: number;
	iat: number;
}
