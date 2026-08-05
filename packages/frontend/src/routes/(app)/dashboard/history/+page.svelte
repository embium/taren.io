<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { redditApi } from '$lib/api/reddit.api';
	import type { JobResponse } from '$lib/types/reddit';
	import PageContainer from '$lib/components/dashboard/PageContainer.svelte';
	import PageHeader from '$lib/components/dashboard/PageHeader.svelte';
	import PageContent from '$lib/components/dashboard/PageContent.svelte';
	import StatCard from '$lib/components/dashboard/StatCard.svelte';
	import StatusBadge from '$lib/components/dashboard/StatusBadge.svelte';

	let jobs = $state<JobResponse[]>([]);
	let loadingJobs = $state(true);

	onMount(async () => {
		try {
			jobs = await redditApi.listJobs();
		} catch {
			/* ignore */
		} finally {
			loadingJobs = false;
		}
	});


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

	const doneJobs = $derived(jobs.filter((j) => j.status === 'done').length);
	const failedJobs = $derived(jobs.filter((j) => j.status === 'failed').length);
	const totalPainPoints = $derived(jobs.reduce((acc, j) => acc + (j.pain_point_count ?? 0), 0));
</script>

<svelte:head>
	<title>Scan History — Taren</title>
</svelte:head>

<PageContainer>
	<PageHeader title="History" />

	<PageContent>
		{#if loadingJobs}
			<div class="space-y-3">
				{#each [1, 2, 3, 4] as _}
					<div class="h-16 animate-pulse rounded-xl border border-border bg-card p-5"></div>
				{/each}
			</div>
		{:else if jobs.length === 0}
			<div
				class="flex flex-col items-center justify-center rounded-xl border border-border bg-card py-24"
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
							d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				</div>
				<p class="text-sm font-medium">No scan history yet</p>
				<p class="mt-1 text-xs text-muted-foreground">
					<a href="/dashboard/scan" class="text-orange-500 hover:underline"
						>Start your first analysis →</a
					>
				</p>
			</div>
		{:else}
			<!-- Summary stats -->
			<div class="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
				<StatCard title="Total Scans" value={jobs.length} />
				<StatCard title="Completed" value={doneJobs} valueClass="text-emerald-400" />
				<StatCard title="Pain Points Found" value={totalPainPoints} valueClass="text-orange-400" />
				<StatCard title="Failed" value={failedJobs} valueClass={failedJobs > 0 ? 'text-red-400' : 'text-muted-foreground'} />
			</div>

			<!-- History table -->
			<div class="overflow-hidden rounded-xl border border-border bg-card">
				<div class="flex items-center justify-between border-b border-border px-5 py-3">
					<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">All Scans</p>
					<span class="text-xs text-muted-foreground">{jobs.length} total</span>
				</div>
				<div class="overflow-x-auto">
					<table class="w-full text-sm">
						<thead>
							<tr class="border-b border-border">
								<th
									class="px-5 py-3 text-left text-xs font-medium tracking-wide text-muted-foreground uppercase"
									>Job</th
								>
								<th
									class="px-5 py-3 text-left text-xs font-medium tracking-wide text-muted-foreground uppercase"
									>Subreddits</th
								>
								<th
									class="px-5 py-3 text-left text-xs font-medium tracking-wide text-muted-foreground uppercase"
									>Status</th
								>
								<th
									class="px-5 py-3 text-left text-xs font-medium tracking-wide text-muted-foreground uppercase"
									>Posts</th
								>
								<th
									class="px-5 py-3 text-left text-xs font-medium tracking-wide text-muted-foreground uppercase"
									>Pain Points</th
								>
								<th
									class="px-5 py-3 text-left text-xs font-medium tracking-wide text-muted-foreground uppercase"
									>Date</th
								>
							</tr>
						</thead>
						<tbody class="divide-y divide-border">
							{#each jobs as job (job.id)}
								<tr
									class="cursor-pointer transition-colors hover:bg-accent/30"
									onclick={() => goto(`/dashboard/results?job=${job.id}`)}
								>
									<td class="px-5 py-3.5 font-mono text-xs text-muted-foreground">#{job.id}</td>
									<td class="px-5 py-3.5">
										<div class="flex flex-wrap gap-1">
											{#each subredditList(job.subreddits).slice(0, 3) as sub}
												<span
													class="inline-flex items-center rounded-full border border-orange-500/30 bg-orange-500/10 px-2 py-0.5 text-xs font-medium text-orange-500"
													>r/{sub}</span
												>
											{/each}
											{#if subredditList(job.subreddits).length > 3}
												<span class="text-xs text-muted-foreground"
													>+{subredditList(job.subreddits).length - 3} more</span
												>
											{/if}
										</div>
									</td>
									<td class="px-5 py-3.5">
										<StatusBadge status={job.status} />
									</td>
									<td class="px-5 py-3.5 text-muted-foreground">{job.post_count}</td>
									<td class="px-5 py-3.5">
										{#if job.status === 'done'}
											<span class="font-medium text-orange-400">{job.pain_point_count}</span>
										{:else}
											<span class="text-muted-foreground">—</span>
										{/if}
									</td>
									<td class="px-5 py-3.5 text-xs text-muted-foreground"
										>{formatDate(job.created_at)}</td
									>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		{/if}
	</PageContent>
</PageContainer>
