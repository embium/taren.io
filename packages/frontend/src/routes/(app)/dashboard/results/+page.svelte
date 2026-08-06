<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { page } from '$app/state';
	import { goto } from "$app/navigation";
	import { Check, RefreshCw, Cpu, Circle } from '@lucide/svelte';
	import { redditApi } from '$lib/api/reddit.api';
	import type { JobResponse, JobResultsResponse } from '$lib/types/reddit';
	import PageContainer from '$lib/components/dashboard/PageContainer.svelte';
	import PageHeader from '$lib/components/dashboard/PageHeader.svelte';
	import PageContent from '$lib/components/dashboard/PageContent.svelte';
	import StatCard from '$lib/components/dashboard/StatCard.svelte';
	import StatusBadge from '$lib/components/dashboard/StatusBadge.svelte';

	let jobs = $state<JobResponse[]>([]);
	let loadingJobs = $state(true);
	let selectedJob = $state<JobResponse | null>(null);
	let results = $state<JobResultsResponse | null>(null);
	let loadingResults = $state(false);
	let expandedPainPoints = $state<Set<number>>(new Set());
	let pollInterval: ReturnType<typeof setInterval> | null = null;

	const hasActiveJobs = $derived(
		jobs.some((j) => j.status === 'pending' || j.status === 'scraping' || j.status === 'analyzing')
	);

	onMount(async () => {
		await fetchJobs();
		// Auto-select job from ?job= query param (e.g. redirected from Scan page)
		const jobIdParam = page.url.searchParams.get('job');
		if (jobIdParam) {
			const target = jobs.find((j) => j.id === jobIdParam);
			if (target) await selectJob(target);
		}
		startPolling();
	});

	onDestroy(() => stopPolling());

	function startPolling() {
		stopPolling();
		pollInterval = setInterval(async () => {
			if (hasActiveJobs) {
				await fetchJobs();
				if (selectedJob && selectedJob.status !== 'done') {
					const updated = jobs.find((j) => j.id === selectedJob!.id);
					if (updated?.status === 'done') {
						selectedJob = updated;
						await loadResults(updated.id);
					} else if (updated) {
						selectedJob = updated;
					}
				}
			}
		}, 5000);
	}

	function stopPolling() {
		if (pollInterval) {
			clearInterval(pollInterval);
			pollInterval = null;
		}
	}

	async function fetchJobs() {
		try {
			jobs = await redditApi.listJobs();
		} catch {
			/* silent */
		} finally {
			loadingJobs = false;
		}
	}

	async function loadResults(jobId: string) {
		loadingResults = true;
		try {
			results = await redditApi.getResults(jobId);
		} catch (e: any) {
			toast.error(e?.message || 'Failed to load results');
		} finally {
			loadingResults = false;
		}
	}

	async function selectJob(job: JobResponse) {
		selectedJob = job;
		results = null;
		goto("/dashboard/results?job=" + job.id);
		if (job.status === 'done') {
			await loadResults(job.id);
		}
	}

	function togglePainPoint(id: number) {
		const next = new Set(expandedPainPoints);
		if (next.has(id)) next.delete(id);
		else next.add(id);
		expandedPainPoints = next;
	}

	function severityColor(s: number) {
		if (s >= 80) return 'text-red-400';
		if (s >= 60) return 'text-orange-400';
		if (s >= 40) return 'text-yellow-400';
		return 'text-emerald-400';
	}
	function severityBarColor(s: number) {
		if (s >= 80) return 'bg-red-500';
		if (s >= 60) return 'bg-orange-500';
		if (s >= 40) return 'bg-yellow-500';
		return 'bg-emerald-500';
	}
	function severityLabel(s: number) {
		if (s >= 80) return 'Critical';
		if (s >= 60) return 'High';
		if (s >= 40) return 'Medium';
		return 'Low';
	}

	function formatDate(iso: string) {
		return new Date(iso).toLocaleString(undefined, {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
	function subredditList(raw: string) {
		return raw
			.split(',')
			.map((s) => s.trim())
			.filter(Boolean);
	}
</script>

<svelte:head>
	<title>Results — Taren</title>
</svelte:head>

<PageContainer>
	<PageHeader title="Results">
		{#snippet actions()}
			{#if hasActiveJobs}
				<div class="flex items-center gap-1.5">
					<span class="h-2 w-2 animate-pulse rounded-full bg-blue-400"></span>
					<span class="text-xs font-medium text-blue-400">Live</span>
				</div>
			{/if}
		{/snippet}
	</PageHeader>

	<PageContent class="overflow-hidden">
		<div class="flex h-full gap-5">
			<!-- Left: Job list -->
			<div
				class="w-full shrink-0 flex-col overflow-hidden rounded-xl border border-border bg-card md:w-72 {selectedJob
					? 'hidden md:flex'
					: 'flex'}"
			>
				<div class="flex shrink-0 items-center justify-between border-b border-border px-5 py-3">
					<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">Jobs</p>
					<span class="text-xs text-muted-foreground">{jobs.length}</span>
				</div>
				<div class="flex-1 divide-y divide-border overflow-y-auto">
					{#if loadingJobs}
						{#each [1, 2, 3] as _}
							<div class="animate-pulse px-5 py-4">
								<div class="mb-2 h-3 w-2/3 rounded-lg bg-secondary"></div>
								<div class="h-2.5 w-1/3 rounded-lg bg-secondary/60"></div>
							</div>
						{/each}
					{:else if jobs.length === 0}
						<div class="flex flex-col items-center justify-center px-5 py-12 text-center">
							<p class="text-sm text-muted-foreground">No jobs yet.</p>
							<a href="/dashboard/scan" class="mt-1 text-xs text-orange-500 hover:underline"
								>Start a scan →</a
							>
						</div>
					{:else}
						{#each jobs as job (job.id)}
							<button
								id="job-{job.id}-btn"
								onclick={() => selectJob(job)}
								class="cursor-pointer group w-full px-5 py-3.5 text-left transition hover:bg-accent/50 {selectedJob?.id ===
								job.id
									? 'bg-orange-500/10'
									: ''}"
							>
								<div class="mb-1 flex items-start justify-between gap-2">
									<p class="truncate text-sm font-medium">
										{subredditList(job.subreddits)
											.map((s) => `r/${s}`)
											.join(', ')}
									</p>
									<StatusBadge status={job.status} class="shrink-0" />
								</div>
								<div class="flex items-center gap-2 text-xs text-muted-foreground">
									{#if job.status === 'done'}
										<span class="text-orange-500"
											>{job.pain_point_count} pain point{job.pain_point_count !== 1
												? 's'
												: ''}</span
										>
									{:else if job.status === 'failed'}
										<span class="text-red-400">Failed</span>
									{:else}
										<span>{job.post_count} post{job.post_count !== 1 ? 's' : ''}</span>
									{/if}
								</div>
								<p class="mt-0.5 text-xs text-muted-foreground/60">{formatDate(job.created_at)}</p>
							</button>
						{/each}
					{/if}
				</div>
			</div>

			<!-- Right: Results panel -->
			<div class="flex-1 overflow-y-auto {selectedJob ? 'block' : 'hidden md:block'}">
				{#if selectedJob}
					<button
						class="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground md:hidden"
						onclick={() => {
							selectedJob = null;
							results = null;
						}}
					>
						<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M10 19l-7-7m0 0l7-7m-7 7h18"
							/>
						</svg>
						Back to jobs
					</button>
				{/if}

				{#if !selectedJob}
					<div
						class="flex h-full min-h-[300px] flex-col items-center justify-center rounded-xl border border-border bg-card"
					>
						<div class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-secondary">
							<svg
								class="h-6 w-6 text-muted-foreground"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
								/>
							</svg>
						</div>
						<p class="text-sm font-medium">Select a job to view results</p>
						<p class="mt-1 text-xs text-muted-foreground">
							Or <a href="/dashboard/scan" class="text-orange-500 hover:underline"
								>start a new scan</a
							>
						</p>
					</div>
				{:else if selectedJob.status === 'pending' || selectedJob.status === 'scraping' || selectedJob.status === 'analyzing'}
					{@const stepIndex = ['pending', 'scraping', 'analyzing', 'done'].indexOf(selectedJob.status)}
					{@const progressWidth = Math.max(0, (stepIndex / 3) * 100)}
					<div class="rounded-xl border border-border bg-card p-5">
						<div class="mb-8 flex items-center gap-4">
							<div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-500/10">
								<svg class="h-6 w-6 animate-spin text-blue-500" fill="none" viewBox="0 0 24 24">
									<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
									<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
								</svg>
							</div>
							<div class="min-w-0">
								<h3 class="truncate text-lg font-semibold" title={selectedJob.id}>
									Job #{selectedJob.id.substring(0, 8)} in progress
								</h3>
								<p class="text-sm font-medium text-blue-500 capitalize">{selectedJob.status}…</p>
							</div>
						</div>

						<!-- Horizontal Stepper -->
						<div class="relative mb-10 hidden px-2 sm:block">
							<!-- Connecting line -->
							<div class="absolute left-[12.5%] right-[12.5%] top-6 z-0 h-[2px] bg-secondary">
								<div class="h-full bg-blue-500 transition-all duration-1000 ease-in-out" style="width: {progressWidth}%"></div>
							</div>
							
							<div class="relative z-10 flex justify-between">
								{#each [{s: 'pending', label: 'Queued', Icon: Circle}, {s: 'scraping', label: 'Scraping', Icon: RefreshCw}, {s: 'analyzing', label: 'Analysis', Icon: Cpu}, {s: 'done', label: 'Complete', Icon: Check}] as {s, label, Icon}, i}
									<div class="flex w-1/4 flex-col items-center">
										<!-- Background wrapper blocks line bleed-through -->
										<div class="rounded-full bg-card p-1">
											<div class="flex h-10 w-10 items-center justify-center rounded-full transition-all duration-500
												{i < stepIndex ? 'bg-emerald-500/20 text-emerald-500' : 
												 i === stepIndex ? 'bg-blue-500 text-white shadow-md shadow-blue-500/20 ring-4 ring-blue-500/20' : 
												 'bg-secondary text-muted-foreground'}
											">
												<Icon size={16} />
											</div>
										</div>
										<p class="mt-2 text-xs font-semibold tracking-wide uppercase
											{i < stepIndex ? 'text-emerald-500' : 
											 i === stepIndex ? 'text-blue-500' : 
											 'text-muted-foreground'}
										">
											{label}
										</p>
									</div>
								{/each}
							</div>
						</div>

						<!-- Mobile Vertical Stepper -->
						<div class="mb-8 space-y-4 sm:hidden">
							{#each [{s: 'pending', label: 'Queued', Icon: Circle}, {s: 'scraping', label: 'Scraping Reddit', Icon: RefreshCw}, {s: 'analyzing', label: 'AI Analysis', Icon: Cpu}, {s: 'done', label: 'Complete', Icon: Check}] as {s, label, Icon}, i}
								<div class="flex items-center gap-3">
									<div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full font-bold
										{i < stepIndex ? 'bg-emerald-500/20 text-emerald-500' : 
										 i === stepIndex ? 'bg-blue-500 text-white shadow-sm ring-2 ring-blue-500/20' : 
										 'bg-secondary text-muted-foreground'}">
										<Icon size={14} />
									</div>
									<p class="text-sm font-medium {i < stepIndex ? 'text-emerald-500' : i === stepIndex ? 'text-blue-500' : 'text-muted-foreground'}">
										{label}
									</p>
								</div>
							{/each}
						</div>

						<!-- Live Metrics -->
						<div class="grid grid-cols-2 gap-4">
							<div class="rounded-xl border border-border bg-card p-5 text-center">
								<p class="text-2xl font-bold">{selectedJob.post_count}</p>
								<p class="mt-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
									Posts scraped
								</p>
							</div>
							<div class="rounded-xl border border-border bg-card p-5 text-center">
								<p class="text-2xl font-bold">{selectedJob.comment_count}</p>
								<p class="mt-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
									Comments
								</p>
							</div>
						</div>
						
						<!-- Footer Text -->
						<p class="mt-6 flex items-center justify-center gap-2 text-xs text-muted-foreground">
							<RefreshCw size={12} class="animate-spin opacity-70" />
							<span>Auto-refreshing every 5 seconds…</span>
						</p>
					</div>
				{:else if selectedJob.status === 'failed'}
					<div class="rounded-xl border border-red-500/20 bg-card p-8">
						<div class="flex items-center gap-4">
							<div class="flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10">
								<svg
									class="h-6 w-6 text-red-400"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
									/>
								</svg>
							</div>
							<div>
								<h3 class="text-lg font-semibold">Job Failed</h3>
								<p class="mt-1 text-sm text-red-400">
									{selectedJob.error_message || 'An unexpected error occurred.'}
								</p>
							</div>
						</div>
					</div>
				{:else if selectedJob.status === 'done'}
					<div class="space-y-5">
						<!-- Stats -->
						<div class="grid grid-cols-2 gap-4 sm:grid-cols-3">
							<StatCard title="Pain Points" value={selectedJob.pain_point_count} valueClass="text-orange-400" class="col-span-2 sm:col-span-1" />
							<StatCard title="Posts" value={selectedJob.post_count} valueClass="text-blue-400" />
							<StatCard title="Evidence" value={selectedJob.comment_count} valueClass="text-purple-400" />
						</div>

						<!-- Pain points -->
						{#if loadingResults}
							<div class="space-y-3">
								{#each [1, 2, 3] as _}
									<div class="animate-pulse rounded-xl border border-border bg-card p-5">
										<div class="mb-3 flex items-center justify-between">
											<div class="h-4 w-1/2 rounded-lg bg-secondary"></div>
											<div class="h-6 w-16 rounded-full bg-secondary/60"></div>
										</div>
										<div class="h-3 w-full rounded-lg bg-secondary/60"></div>
									</div>
								{/each}
							</div>
						{:else if results && results.pain_points.length > 0}
							<div class="rounded-xl border border-border bg-card">
								<div class="border-b border-border px-5 py-3">
									<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">
										Pain Points
									</p>
								</div>
								<div class="divide-y divide-border">
									{#each results.pain_points as pp (pp.id)}
										<div class="overflow-hidden">
											<button
												id="painpoint-{pp.id}-toggle"
												onclick={() => togglePainPoint(pp.id)}
												class="cursor-pointer w-full px-5 py-4 text-left transition hover:bg-accent/50"
											>
												<div class="flex items-start justify-between gap-4">
													<div class="min-w-0 flex-1">
														<div class="mb-1.5 flex flex-wrap items-center gap-2">
															<span
																class="inline-flex items-center rounded-full border border-orange-500/30 bg-orange-500/10 px-2.5 py-0.5 text-xs font-medium text-orange-500"
																>r/{pp.subreddit}</span
															>
															<span class="text-xs text-muted-foreground"
																>{pp.evidence.length} evidence{pp.evidence.length !== 1
																	? 's'
																	: ''}</span
															>
														</div>
														<h3 class="text-sm font-semibold">{pp.title}</h3>
													</div>
													<div class="flex shrink-0 flex-col items-end gap-1">
														<span class="text-xl font-bold {severityColor(pp.severity)}"
															>{pp.severity}</span
														>
														<span class="text-xs {severityColor(pp.severity)}"
															>{severityLabel(pp.severity)}</span
														>
													</div>
												</div>
												<div class="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
													<div
														class="h-full rounded-full {severityBarColor(pp.severity)}"
														style="width: {pp.severity}%"
													></div>
												</div>
											</button>
											{#if expandedPainPoints.has(pp.id)}
												<div class="border-t border-border bg-card/50 px-5 pt-4 pb-5">
													<div class="mb-6">
														<p
															class="mb-2 text-xs font-medium tracking-wide text-muted-foreground uppercase"
														>
															Description
														</p>
														<p class="text-sm leading-relaxed text-foreground/90">
															{pp.description}
														</p>
													</div>
													<div class="mb-6">
														<p
															class="mb-2 text-xs font-medium tracking-wide text-muted-foreground uppercase"
														>
															Target Audience
														</p>
														<p class="text-sm leading-relaxed text-foreground/90">
															{pp.target_audience}
														</p>
													</div>
													<div class="space-y-4">
														{#if pp.evidence.length > 0}
															<div>
																<p
																	class="mb-2 text-xs font-medium tracking-wide text-muted-foreground uppercase"
																>
																	Evidence ({pp.evidence.length})
																</p>
																<div class="space-y-2">
																	{#each pp.evidence as ev (ev.id)}
																		<div class="rounded-xl border border-border bg-card p-3">
																			<p class="text-sm leading-relaxed text-foreground/80">
																				"{ev.quote}"
																			</p>
																			<a
																				href={ev.link}
																				target="_blank"
																				rel="noopener noreferrer"
																				class="mt-2 inline-flex items-center gap-1 text-xs text-orange-500 hover:underline"
																			>
																				View on Reddit
																				<svg
																					class="h-3 w-3"
																					fill="none"
																					stroke="currentColor"
																					viewBox="0 0 24 24"
																				>
																					<path
																						stroke-linecap="round"
																						stroke-linejoin="round"
																						stroke-width="2"
																						d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
																					/>
																				</svg>
																			</a>
																		</div>
																	{/each}
																</div>
															</div>
														{/if}
													</div>
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{:else}
							<div
								class="flex flex-col items-center justify-center rounded-xl border border-border bg-card py-12"
							>
								<p class="text-sm text-muted-foreground">
									No pain points were identified for this job.
								</p>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		</div>
	</PageContent>
</PageContainer>
