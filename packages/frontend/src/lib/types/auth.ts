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
 * Username validation schema matching backend requirements:
 * - Minimum 3 characters
 * - Maximum 30 characters
 * - Only letters, numbers, and underscores
 * - Must start with a letter
 */
export const usernameSchema = z
	.string()
	.min(3, 'Username must be at least 3 characters long')
	.max(30, 'Username must be at most 30 characters long')
	.regex(
		/^[a-zA-Z][a-zA-Z0-9_]*$/,
		'Username must start with a letter and contain only letters, numbers, and underscores'
	);

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

export const verifyEmailRequestSchema = z.object({
	token: z.string().min(1, 'Token is required')
});

export const forgotPasswordRequestSchema = z.object({
	email: emailSchema
});

export const resendVerificationEmailRequestSchema = z.object({
	email: emailSchema
});

export const resetPasswordRequestSchema = z.object({
	token: z.string().min(1, 'Token is required'),
	new_password: passwordSchema
});

// ============================================================================
// Response Schemas
// ============================================================================

export const userSchema = z.object({
	id: z.string(),
	email: z.email(),
	username: z.string(),
	name: z.string().nullable(),
	avatar: z.string().nullable(),
	created_at: z.string(),
	is_active: z.boolean(),
	is_email_verified: z.boolean(),
	subscription_tier: z.string().nullable().optional()
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
	email: z.email(),
	created_at: z.string(),
	message: z.string().optional()
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

export const verifyEmailResponseSchema = z.object({
	message: z.string(),
	email: z.string(),
	access_token: z.string().optional(),
	refresh_token: z.string().optional(),
	token_type: z.string().optional(),
	expires_in: z.number().optional()
});

export const forgotPasswordResponseSchema = z.object({
	message: z.string()
});

export const resendVerificationEmailResponseSchema = z.object({
	message: z.string()
});

export const resetPasswordResponseSchema = z.object({
	message: z.string()
});

// ============================================================================
// TypeScript Types (inferred from schemas)
// ============================================================================

export type LoginRequest = z.infer<typeof loginRequestSchema>;
export type RegisterUserRequest = z.infer<typeof registerUserRequestSchema>;
export type RefreshTokenRequest = z.infer<typeof refreshTokenRequestSchema>;
export type ChangePasswordRequest = z.infer<typeof changePasswordRequestSchema>;
export type VerifyEmailRequest = z.infer<typeof verifyEmailRequestSchema>;
export type ForgotPasswordRequest = z.infer<typeof forgotPasswordRequestSchema>;
export type ResendVerificationEmailRequest = z.infer<typeof resendVerificationEmailRequestSchema>;
export type ResetPasswordRequest = z.infer<typeof resetPasswordRequestSchema>;

export type User = z.infer<typeof userSchema>;
export type LoginResponse = z.infer<typeof loginResponseSchema>;
export type RegisterUserResponse = z.infer<typeof registerUserResponseSchema>;
export type RefreshTokenResponse = z.infer<typeof refreshTokenResponseSchema>;
export type LogoutResponse = z.infer<typeof logoutResponseSchema>;
export type ChangePasswordResponse = z.infer<typeof changePasswordResponseSchema>;
export type ErrorResponse = z.infer<typeof errorResponseSchema>;
export type VerifyEmailResponse = z.infer<typeof verifyEmailResponseSchema>;
export type ForgotPasswordResponse = z.infer<typeof forgotPasswordResponseSchema>;
export type ResendVerificationEmailResponse = z.infer<typeof resendVerificationEmailResponseSchema>;
export type ResetPasswordResponse = z.infer<typeof resetPasswordResponseSchema>;

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
