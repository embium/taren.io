<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { redditApi } from '$lib/api/reddit.api';
	import type { JobResponse } from '$lib/types/reddit';

	let subredditsInput = $state('');
	let scrapeLimit = $state(25);
	let isSubmitting = $state(false);

	const parsedSubreddits = $derived(
		subredditsInput
			.split(/[\n,]+/)
			.map((s) => s.trim().replace(/^r\//, ''))
			.filter(Boolean)
	);

	async function submitJob() {
		if (parsedSubreddits.length === 0) {
			toast.error('Please enter at least one subreddit.');
			return;
		}
		isSubmitting = true;
		try {
			const job = await redditApi.createJob(parsedSubreddits, scrapeLimit);
			subredditsInput = '';
			toast.success(`Job #${job.id} started — scraping ${parsedSubreddits.length} subreddit(s)`);
			goto(`/dashboard/results?job=${job.id}`);
		} catch (e: any) {
			toast.error(e?.message || 'Failed to start job');
		} finally {
			isSubmitting = false;
		}
	}
</script>

<svelte:head>
	<title>Scan - Taren</title>
</svelte:head>

<div class="flex h-full flex-col">
	<div class="flex shrink-0 items-center justify-between flex-wrap gap-2 border-b border-border px-4 py-4 sm:px-6 md:px-8 md:py-5">
		<h1 class="text-lg font-semibold">Scan</h1>
	</div>

	<div class="flex-1 overflow-y-auto px-4 py-5 sm:px-6 md:px-8 md:py-6">
		<div class="mb-6">
			<h2 class="text-2xl font-bold">New Analysis</h2>
			<p class="mt-1 text-muted-foreground">Scrape subreddits and use AI to identify pain points and market opportunities.</p>
		</div>

		<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
			<!-- Left: form -->
			<div class="space-y-4 lg:col-span-2">
				<!-- Subreddits -->
				<div class="rounded-xl border border-border bg-card p-5">
					<p class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-3">Subreddits</p>
					<textarea
						id="subreddits-input"
						bind:value={subredditsInput}
						placeholder="learnprogramming, Python, webdev"
						rows={7}
						class="w-full resize-none rounded-lg border border-border bg-background px-3 py-2 font-mono text-sm placeholder-muted-foreground transition-colors focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20"
					></textarea>
					<p class="mt-2 text-xs text-muted-foreground">One per line or comma-separated. The <code class="rounded bg-secondary px-1 py-0.5">r/</code> prefix is optional.</p>

					{#if parsedSubreddits.length > 0}
						<div class="mt-3 flex flex-wrap gap-1.5">
							{#each parsedSubreddits as sub}
								<span class="inline-flex items-center rounded-full border border-orange-500/30 bg-orange-500/10 px-2.5 py-0.5 text-xs font-medium text-orange-500">
									r/{sub}
								</span>
							{/each}
						</div>
					{/if}
				</div>

				<!-- Posts limit -->
				<div class="rounded-xl border border-border bg-card p-5">
					<div class="mb-4 flex items-center justify-between">
						<p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Posts per subreddit</p>
						<span class="rounded-full border border-orange-500/30 bg-orange-500/10 px-2.5 py-0.5 text-xs font-bold text-orange-500">{scrapeLimit}</span>
					</div>
					<input
						id="scrape-limit"
						type="range"
						min="5"
						max="100"
						step="5"
						bind:value={scrapeLimit}
						class="h-2 w-full cursor-pointer appearance-none rounded-full bg-secondary accent-orange-500"
					/>
					<div class="mt-2 flex justify-between text-xs text-muted-foreground">
						<span>5 — quick</span>
						<span>100 — thorough</span>
					</div>
				</div>
			</div>

			<!-- Right: summary + submit -->
			<div class="lg:col-span-1">
				<div class="rounded-xl border border-border bg-card p-5">
					<p class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-4">Summary</p>

					<div class="space-y-3 mb-6">
						<div class="flex items-center justify-between">
							<span class="text-sm text-muted-foreground">Subreddits</span>
							<span class="text-sm font-semibold">{parsedSubreddits.length > 0 ? parsedSubreddits.length : '—'}</span>
						</div>
						<div class="flex items-center justify-between">
							<span class="text-sm text-muted-foreground">Posts each</span>
							<span class="text-sm font-semibold">{scrapeLimit}</span>
						</div>
						<div class="flex items-center justify-between">
							<span class="text-sm text-muted-foreground">Est. posts total</span>
							<span class="text-sm font-semibold">{parsedSubreddits.length > 0 ? parsedSubreddits.length * scrapeLimit : '—'}</span>
						</div>
					</div>

					<div class="h-px bg-border mb-5"></div>

					<button
						id="start-analysis-btn"
						onclick={submitJob}
						disabled={isSubmitting || parsedSubreddits.length === 0}
						class="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-orange-500 to-pink-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-orange-500/20 transition hover:from-orange-600 hover:to-pink-700 disabled:cursor-not-allowed disabled:opacity-50"
					>
						{#if isSubmitting}
							<svg class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
							</svg>
							Starting…
						{:else}
							<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
							</svg>
							Start Analysis
						{/if}
					</button>

					<p class="mt-3 text-center text-xs text-muted-foreground">
						Results appear in the <a href="/dashboard/results" class="text-foreground underline-offset-2 hover:underline">Results</a> tab.
					</p>
				</div>
			</div>
		</div>
	</div>
</div>
