import { api } from './client';

export interface SubscriptionDetails {
	status: string;
	trial_end: number | null;
	current_period_end: number;
	cancel_at_period_end: boolean;
	amount: number;
	interval: string;
	tier: string;
}

export interface CancelSubscriptionResponse {
	status: string;
	canceled_at: number;
}

/**
 * Stripe API service
 */
export const stripeApi = {
	/**
	 * Get current subscription details
	 */
	async getSubscription(): Promise<SubscriptionDetails | null> {
		return api.get<SubscriptionDetails | null>('/stripe/subscription');
	},

	/**
	 * Cancel current subscription
	 */
	async cancelSubscription(): Promise<CancelSubscriptionResponse> {
		return api.post<CancelSubscriptionResponse>('/stripe/cancel-subscription', {});
	}
};
