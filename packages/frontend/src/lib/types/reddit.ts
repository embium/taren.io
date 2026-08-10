// Types for the Reddit analysis feature

export interface CreateJobRequest {
	subreddits: string[];
	scrape_limit?: number;
	analysis_type?: 'template' | 'custom';
	template_id?: string;
	custom_objective?: string;
	sorting_type?: string;
}

export interface JobResponse {
	id: string;
	user_id: string;
	subreddits: string; // comma-separated
	scrape_limit: number;
	status: 'pending' | 'scraping' | 'analyzing' | 'done' | 'failed';
	analysis_type: string;
	template_id?: string;
	custom_objective?: string;
	sorting_type?: string;
	error_message?: string;
	post_count: number;
	comment_count: number;
	finding_count: number;
	created_at: string;
	updated_at: string;
}

export interface EvidenceResponse {
	id: number;
	comment_id?: string;
	quote: string;
	link: string;
}

export interface FindingResponse {
	id: number;
	job_id: string;
	subreddit: string;
	title: string;
	description: string;
	relevance_score: number; // 0–100
	context: string;
	created_at: string;
	evidence: EvidenceResponse[];
}

export interface JobResultsResponse {
	job_id: string;
	status: string;
	findings: FindingResponse[];
}

export interface TemplateResponse {
	id: string;
	name: string;
	description: string;
}

export interface ProfessionResponse {
	name: string;
	slug: string;
}

export interface SubredditDetailResponse {
	name: string;
	description?: string;
	subscribers?: number;
	activity_level?: string;
}

export interface ProfessionSubredditsResponse {
	success: boolean;
	name: string;
	subreddits: SubredditDetailResponse[];
}

export interface SubredditSearchRequest {
	keyword: string;
	model?: string;
}

export interface SubredditSearchJobResponse {
	success: boolean;
	job_id: string;
}

export interface SubredditSearchJobStatusResponse {
	status: 'pending' | 'complete' | 'failed';
	keyword?: string;
	subreddits?: SubredditDetailResponse[];
}
