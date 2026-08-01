import { api } from './client';
import type {
	CreateJobRequest,
	JobResponse,
	JobResultsResponse
} from '$lib/types/reddit';

/**
 * Reddit Analysis API service
 */
export const redditApi = {
	/**
	 * Start a new scrape + analysis job
	 */
	async createJob(subreddits: string[], scrapeLimit = 25): Promise<JobResponse> {
		return api.post<JobResponse>('/reddit/jobs', {
			subreddits,
			scrape_limit: scrapeLimit
		} satisfies CreateJobRequest);
	},

	/**
	 * List all jobs (newest first)
	 */
	async listJobs(): Promise<JobResponse[]> {
		return api.get<JobResponse[]>('/reddit/jobs');
	},

	/**
	 * Get a single job by ID
	 */
	async getJob(id: string): Promise<JobResponse> {
		return api.get<JobResponse>(`/reddit/jobs/${id}`);
	},

	/**
	 * Get pain points + evidence for a completed job
	 */
	async getResults(id: string): Promise<JobResultsResponse> {
		return api.get<JobResultsResponse>(`/reddit/jobs/${id}/results`);
	}
};
