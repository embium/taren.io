import { api } from './client';

export interface UpdateProfileRequest {
	name?: string;
	email?: string;
	avatar?: string; // base64 encoded image
	username?: string;
}

export interface DeleteAccountRequest {
	password: string;
}

export interface DeleteAccountResponse {
	message: string;
}

/**
 * Settings API service
 */
export const settingsApi = {
	/**
	 * Update user profile
	 */
	async updateProfile(data: UpdateProfileRequest) {
		return api.patch('/users/me', data);
	},

	/**
	 * Delete user account (soft delete)
	 */
	async deleteAccount(data: DeleteAccountRequest): Promise<DeleteAccountResponse> {
		return api.delete<DeleteAccountResponse>('/users/me', data);
	}
};
