import { api } from './client';
import type {
	LoginRequest,
	LoginResponse,
	RegisterUserRequest,
	RegisterUserResponse,
	RefreshTokenResponse,
	LogoutResponse,
	User
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
	}
};
