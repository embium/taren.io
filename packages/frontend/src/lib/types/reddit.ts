// Types for the Reddit analysis feature

export interface CreateJobRequest {
	subreddits: string[];
	scrape_limit?: number;
}

export interface JobResponse {
	id: string;
	user_id: string;
	subreddits: string; // comma-separated
	scrape_limit: number;
	status: 'pending' | 'scraping' | 'analyzing' | 'done' | 'failed';
	error_message?: string;
	post_count: number;
	comment_count: number;
	pain_point_count: number;
	created_at: string;
	updated_at: string;
}

export interface EvidenceResponse {
	id: number;
	comment_id?: string;
	quote: string;
	link: string;
}

export interface PainPointResponse {
	id: number;
	job_id: string;
	subreddit: string;
	title: string;
	description: string;
	severity: number; // 0–100
	target_audience: string;
	created_at: string;
	evidence: EvidenceResponse[];
}

export interface JobResultsResponse {
	job_id: string;
	status: string;
	pain_points: PainPointResponse[];
}
