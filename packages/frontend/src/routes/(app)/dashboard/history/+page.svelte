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
	import { Skeleton } from '$lib/components/ui/skeleton';
	import { Badge } from '$lib/components/ui/badge';
	import * as Card from '$lib/components/ui/card';
	import * as Table from '$lib/components/ui/table';

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
	const totalFindings = $derived(jobs.reduce((acc, j) => acc + (j.finding_count ?? 0), 0));
</script>

<svelte:head>
	<title>Scan History — Taren</title>
</svelte:head>

<PageContainer>
	<PageHeader title="History" />

	<PageContent>
		{#if loadingJobs}
			<div class="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
				{#each [1, 2, 3, 4] as _}
					<Card.Root class="h-24 p-5">
						<Skeleton class="mb-1 h-4 w-24" />
						<Skeleton class="h-8 w-16" />
					</Card.Root>
				{/each}
			</div>
			<Card.Root>
				<div class="border-b border-border px-5 py-3">
					<Skeleton class="h-4 w-24" />
				</div>
				<div class="divide-y divide-border">
					{#each [1, 2, 3, 4, 5] as _}
						<div class="flex items-center justify-between px-5 py-3.5 hidden sm:flex">
							<Skeleton class="h-4 w-16" />
							<div class="flex gap-1"><Skeleton class="h-5 w-16 rounded-full" /></div>
							<Skeleton class="h-5 w-16 rounded-full" />
							<Skeleton class="h-4 w-8" />
							<Skeleton class="h-4 w-8" />
							<Skeleton class="h-4 w-24" />
						</div>
						<div class="flex flex-col gap-2 px-5 py-3.5 sm:hidden">
							<Skeleton class="h-4 w-16" />
							<Skeleton class="h-5 w-16 rounded-full" />
						</div>
					{/each}
				</div>
			</Card.Root>
		{:else if jobs.length === 0}
			<Card.Root
				class="flex flex-col items-center justify-center py-24"
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
			</Card.Root>
		{:else}
			<!-- Summary stats -->
			<div class="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
				<StatCard title="Total Scans" value={jobs.length} />
				<StatCard title="Completed" value={doneJobs} valueClass="text-emerald-400" />
				<StatCard title="Findings Found" value={totalFindings} valueClass="text-orange-400" />
				<StatCard
					title="Failed"
					value={failedJobs}
					valueClass={failedJobs > 0 ? 'text-red-400' : 'text-muted-foreground'}
				/>
			</div>

			<!-- History table -->
			<Card.Root>
				<div class="flex items-center justify-between border-b border-border px-5 py-3">
					<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">All Scans</p>
					<span class="text-xs text-muted-foreground">{jobs.length} total</span>
				</div>
				<div class="overflow-x-auto">
					<Table.Root>
						<Table.Header>
							<Table.Row>
								<Table.Head>Job</Table.Head>
								<Table.Head>Subreddits</Table.Head>
								<Table.Head>Status</Table.Head>
								<Table.Head>Posts</Table.Head>
								<Table.Head>Findings</Table.Head>
								<Table.Head>Date</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each jobs as job (job.id)}
								<Table.Row
									class="cursor-pointer"
									onclick={() => goto(`/dashboard/results?job=${job.id}`)}
								>
									<Table.Cell class="font-mono text-xs text-muted-foreground">#{job.id}</Table.Cell>
									<Table.Cell>
										<div class="flex flex-wrap gap-1">
											{#each subredditList(job.subreddits).slice(0, 3) as sub}
												<Badge variant="outline" class="border-orange-500/30 bg-orange-500/10 text-orange-500">r/{sub}</Badge>
											{/each}
											{#if subredditList(job.subreddits).length > 3}
												<span class="text-xs text-muted-foreground"
													>+{subredditList(job.subreddits).length - 3} more</span
												>
											{/if}
										</div>
									</Table.Cell>
									<Table.Cell>
										<StatusBadge status={job.status} />
									</Table.Cell>
									<Table.Cell class="text-muted-foreground">{job.post_count}</Table.Cell>
									<Table.Cell>
										{#if job.status === 'done'}
											<span class="font-medium text-orange-400">{job.finding_count}</span>
										{:else}
											<span class="text-muted-foreground">—</span>
										{/if}
									</Table.Cell>
									<Table.Cell class="text-xs text-muted-foreground"
										>{formatDate(job.created_at)}</Table.Cell
									>
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			</Card.Root>
		{/if}
	</PageContent>
</PageContainer>
