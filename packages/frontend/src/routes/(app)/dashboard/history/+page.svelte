<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Check, X, RefreshCw, Cpu, Circle } from '@lucide/svelte';
	import { redditApi } from '$lib/api/reddit.api';
	import type { JobResponse } from '$lib/types/reddit';

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

	function statusBadgeClass(status: string) {
		switch (status) {
			case 'done':
				return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
			case 'failed':
				return 'bg-red-500/20 text-red-400 border-red-500/30';
			case 'scraping':
			case 'analyzing':
				return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
			default:
				return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
		}
	}
	function statusIcon(status: string) {
		switch (status) {
			case 'done':
				return Check;
			case 'failed':
				return X;
			case 'scraping':
				return RefreshCw;
			case 'analyzing':
				return Cpu;
			default:
				return Circle;
		}
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

	const doneJobs = $derived(jobs.filter((j) => j.status === 'done').length);
	const failedJobs = $derived(jobs.filter((j) => j.status === 'failed').length);
	const totalPainPoints = $derived(jobs.reduce((acc, j) => acc + (j.pain_point_count ?? 0), 0));
</script>

<svelte:head>
	<title>Scan History — Taren</title>
</svelte:head>

<div class="flex h-full flex-col">
	<div
		class="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-4 sm:px-6 md:px-8 md:py-5"
	>
		<h1 class="text-lg font-semibold">History</h1>
	</div>

	<div class="flex-1 overflow-y-auto px-4 py-5 sm:px-6 md:px-8 md:py-6">
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
				<div class="rounded-xl border border-border bg-card p-5">
					<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
						Total Scans
					</p>
					<p class="text-2xl font-bold">{jobs.length}</p>
				</div>
				<div class="rounded-xl border border-border bg-card p-5">
					<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
						Completed
					</p>
					<p class="text-2xl font-bold text-emerald-400">{doneJobs}</p>
				</div>
				<div class="rounded-xl border border-border bg-card p-5">
					<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
						Pain Points Found
					</p>
					<p class="text-2xl font-bold text-orange-400">{totalPainPoints}</p>
				</div>
				<div class="rounded-xl border border-border bg-card p-5">
					<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
						Failed
					</p>
					<p class="text-2xl font-bold {failedJobs > 0 ? 'text-red-400' : 'text-muted-foreground'}">
						{failedJobs}
					</p>
				</div>
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
								{@const Icon = statusIcon(job.status)}
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
										<span
											class="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium {statusBadgeClass(
												job.status
											)}"
										>
											<Icon size={14} class={job.status === 'scraping' || job.status === 'analyzing' ? 'animate-spin' : ''} />
											{job.status}
										</span>
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
	</div>
</div>
