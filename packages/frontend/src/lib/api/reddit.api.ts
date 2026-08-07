import { api } from './client';
import type {
	CreateJobRequest,
	JobResponse,
	JobResultsResponse,
	ProfessionResponse,
	ProfessionSubredditsResponse,
	SubredditSearchRequest,
	SubredditSearchJobResponse,
	SubredditSearchJobStatusResponse
} from '$lib/types/reddit';

export interface UsageResponse {
	tier: string | null;
	daily_scans: number | null;      // null = unlimited
	max_subreddits: number | null;
	max_posts: number | null;
	scans_today: number;
	scans_remaining: number | null;  // null = unlimited
}

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
	},

	/**
	 * Get the user's plan limits and today's scan usage
	 */
	async getUsage(): Promise<UsageResponse> {
		return api.get<UsageResponse>('/reddit/usage');
	},

	/**
	 * List all discovered professions
	 */
	async listProfessions(): Promise<ProfessionResponse[]> {
		return api.get<ProfessionResponse[]>('/reddit/professions');
	},

	/**
	 * Get subreddits for a specific profession
	 */
	async getProfessionSubreddits(slug: string): Promise<ProfessionSubredditsResponse> {
		return api.get<ProfessionSubredditsResponse>(`/reddit/professions/${slug}/subreddits`);
	},

	/**
	 * Search for subreddits using AI based on a keyword (starts background job)
	 */
	async searchSubreddits(keyword: string, model?: string): Promise<SubredditSearchJobResponse> {
		return api.post<SubredditSearchJobResponse>('/reddit/search-subreddits', {
			keyword,
			model
		} satisfies SubredditSearchRequest);
	},

	/**
	 * Check status of an AI subreddit search job
	 */
	async getSearchSubredditsStatus(jobId: string): Promise<SubredditSearchJobStatusResponse> {
		return api.get<SubredditSearchJobStatusResponse>(`/reddit/search-subreddits/${jobId}`);
	}
};
