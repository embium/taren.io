import { api } from './client';
import type {
	LoginRequest,
	LoginResponse,
	RegisterUserRequest,
	RegisterUserResponse,
	RefreshTokenResponse,
	LogoutResponse,
	ForgotPasswordResponse,
	User,
	ResetPasswordResponse,
	ResendVerificationEmailResponse,
	VerifyEmailResponse,
	VerifyEmailRequest,
	ForgotPasswordRequest,
	ResetPasswordRequest
} from '$lib/types/auth';

/**
 * Authentication API service
 */
export const authApi = {
	/**
	 * Register a new user
	 */
	async register(data: RegisterUserRequest): Promise<RegisterUserResponse> {
		return api.post<RegisterUserResponse>('/auth/register', data, { skipAuth: true });
	},

	/**
	 * Login user and get tokens
	 */
	async login(data: LoginRequest): Promise<LoginResponse> {
		return api.post<LoginResponse>('/auth/login', data, { skipAuth: true });
	},

	/**
	 * Logout current user
	 */
	async logout(): Promise<LogoutResponse> {
		return api.post<LogoutResponse>('/auth/logout');
	},

	/**
	 * Refresh access token
	 */
	async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
		return api.post<RefreshTokenResponse>(
			'/api/auth/refresh',
			{ refresh_token: refreshToken },
			{ skipAuth: true }
		);
	},

	/**
	 * Get current user profile
	 */
	async getCurrentUser(): Promise<User> {
		return api.get<User>('/users/me');
	},

	/**
	 * Verify email
	 */
	async verifyEmail(request: VerifyEmailRequest): Promise<VerifyEmailResponse> {
		return api.post<VerifyEmailResponse>('/auth/verify-email', request);
	},

	/**
	 * Forgot password
	 */
	async forgotPassword(request: ForgotPasswordRequest): Promise<ForgotPasswordResponse> {
		return api.post<ForgotPasswordResponse>('/auth/forgot-password', request);
	},

	/**
	 * Resend verification email
	 */
	async resendVerificationEmail(email: string): Promise<ResendVerificationEmailResponse> {
		return api.post<ResendVerificationEmailResponse>('/auth/resend-verification-email', { email });
	},

	/**
	 * Reset password
	 */
	async resetPassword(request: ResetPasswordRequest): Promise<ResetPasswordResponse> {
		return api.post<ResetPasswordResponse>('/auth/reset-password', request);
	}
};
