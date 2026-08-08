<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { redditApi, type UsageResponse } from '$lib/api/reddit.api';
	import type { TemplateResponse } from '$lib/types/reddit';
	import { AlertTriangle, Zap } from '@lucide/svelte';

	let subredditsInput = $state('');
	let isSubmitting = $state(false);
	let usage = $state<UsageResponse | null>(null);

	let analysisType = $state<'template' | 'custom'>('template');
	let templates = $state<TemplateResponse[]>([]);
	let selectedTemplateId = $state<string>('pain_points');
	let customObjective = $state('');

	// Derived plan caps (with safe fallbacks while loading)
	const tier = $derived(usage?.tier || '');
	const isProfessional = $derived(tier === 'Professional');
	const isStarter = $derived(tier === 'Starter');

	const maxPosts = $derived(usage ? (isProfessional ? 100 : isStarter ? 15 : 0) : 25);
	const maxSubs = $derived(usage ? (isProfessional ? 10 : isStarter ? 3 : 0) : 3);
	const scansToday = $derived(usage?.scans_today ?? 0);
	const scansTotal = $derived(usage ? (isProfessional ? null : isStarter ? 10 : 0) : null);
	const scansLeft = $derived(
		usage ? (isProfessional ? null : isStarter ? Math.max(0, 10 - scansToday) : 0) : null
	);
	const isUnlimited = $derived(usage ? isProfessional : true);
	const isAtLimit = $derived(usage ? !isUnlimited && scansLeft !== null && scansLeft <= 0 : false);

	// Slider value clamped to plan max
	let scrapeLimit = $state(15);
	$effect(() => {
		if (scrapeLimit > maxPosts) scrapeLimit = maxPosts;
	});

	const parsedSubreddits = $derived(
		subredditsInput
			.split(/[\n,]+/)
			.map((s) => s.trim().replace(/^r\//, ''))
			.filter(Boolean)
			.slice(0, maxSubs) // silently cap to plan limit
	);

	onMount(async () => {
		try {
			usage = await redditApi.getUsage();
		} catch {
			// ignore — limits will show fallbacks
		}

		try {
			templates = await redditApi.getTemplates();
			if (templates.length > 0) selectedTemplateId = templates[0].id;
		} catch {
			// ignore
		}

		// Handle adding subreddit from query parameter
		const addSub = $page.url.searchParams.get('add');
		if (addSub) {
			const toAdd = addSub
				.split(',')
				.map((s) => s.trim())
				.filter(Boolean);
			const current = subredditsInput
				.split(/[\n,]+/)
				.map((s) => s.trim())
				.filter(Boolean);

			for (const sub of toAdd) {
				if (!current.includes(sub)) {
					current.push(sub);
				}
			}

			subredditsInput = current.join('\n');

			// Remove the query parameter without reloading the page
			const newUrl = new URL($page.url);
			newUrl.searchParams.delete('add');
			goto(newUrl, { replaceState: true, keepFocus: true });
		}
	});

	async function submitJob() {
		if (parsedSubreddits.length === 0) {
			toast.error('Please enter at least one subreddit.');
			return;
		}
		if (isAtLimit) {
			toast.error('Daily scan limit reached. Upgrade to Professional for unlimited scans.');
			return;
		}
		if (analysisType === 'custom' && !customObjective.trim()) {
			toast.error('Please enter a custom objective.');
			return;
		}
		isSubmitting = true;
		try {
			const job = await redditApi.createJob(
				parsedSubreddits,
				scrapeLimit,
				analysisType,
				analysisType === 'template' ? selectedTemplateId : undefined,
				analysisType === 'custom' ? customObjective : undefined
			);
			subredditsInput = '';
			toast.success(`Job #${job.id} started — scraping ${parsedSubreddits.length} subreddit(s)`);
			// Refresh usage count
			usage = await redditApi.getUsage();
			goto(`/dashboard/results?job=${job.id}`);
		} catch (e: any) {
			toast.error(e?.message || 'Failed to start job');
		} finally {
			isSubmitting = false;
		}
	}

	function scanUsageColor() {
		if (isUnlimited || scansLeft === null) return 'text-emerald-400';
		if (scansLeft === 0) return 'text-red-400';
		if (scansLeft <= 3) return 'text-amber-400';
		return 'text-emerald-400';
	}
</script>

<svelte:head>
	<title>Scan — Taren</title>
</svelte:head>

<div class="flex h-full flex-col">
	<div
		class="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-4 sm:px-6 md:px-8 md:py-5"
	>
		<h1 class="text-lg font-semibold">Scan</h1>

		<!-- Scan quota pill (top-right of header) -->
		{#if usage}
			<div class="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5">
				<Zap class="h-3.5 w-3.5 {isAtLimit ? 'text-red-400' : 'text-primary'}" />
				{#if isUnlimited}
					<span class="text-xs font-medium">Unlimited scans</span>
				{:else}
					<span class="text-xs font-medium {scanUsageColor()}">
						{scansLeft} of {scansTotal} scans left today
					</span>
				{/if}
			</div>
		{/if}
	</div>

	<div class="flex-1 overflow-y-auto px-4 py-5 sm:px-6 md:px-8 md:py-6">
		<div class="mb-6">
			<h2 class="text-2xl font-bold">New Analysis</h2>
			<p class="mt-1 text-muted-foreground">
				Scrape subreddits and use AI to identify market opportunities.
			</p>
		</div>

		<!-- Limit exceeded banner -->
		{#if isAtLimit}
			<div
				class="mb-5 flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4"
			>
				<AlertTriangle class="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
				<div>
					<p class="text-sm font-semibold text-red-300">Daily scan limit reached</p>
					<p class="mt-0.5 text-sm text-red-400/80">
						{#if tier === ''}
							You must be on a paid plan to run scans.
						{:else}
							You've used all {scansTotal} scans for today.
						{/if}
						<a
							href="/dashboard/subscription"
							class="font-medium text-red-300 underline underline-offset-2"
							>Upgrade to Professional</a
						> for unlimited scans.
					</p>
				</div>
			</div>
		{/if}

		<div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
			<!-- Left: form -->
			<div class="space-y-4 lg:col-span-2">
				<!-- Analysis Objective -->
				<div class="rounded-xl border border-border bg-card">
					<div class="flex items-center justify-between border-b border-border px-5 py-3">
						<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">
							Analysis Objective
						</p>
						<div class="flex items-center gap-2 rounded-lg bg-secondary p-1">
							<button
								class="rounded-md px-3 py-1 text-xs font-medium transition-colors {analysisType ===
								'template'
									? 'bg-background text-foreground shadow-sm'
									: 'text-muted-foreground hover:text-foreground'}"
								onclick={() => (analysisType = 'template')}>Template</button
							>
							<button
								class="rounded-md px-3 py-1 text-xs font-medium transition-colors {analysisType ===
								'custom'
									? 'bg-background text-foreground shadow-sm'
									: 'text-muted-foreground hover:text-foreground'}"
								onclick={() => (analysisType = 'custom')}>Custom</button
							>
						</div>
					</div>
					<div class="p-5">
						{#if analysisType === 'template'}
							<div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
								{#each templates as template}
									<button
										class="flex flex-col rounded-lg border p-3 text-left transition-colors {selectedTemplateId ===
										template.id
											? 'border-orange-500 bg-orange-500/5'
											: 'border-border bg-background hover:border-orange-500/50'}"
										onclick={() => (selectedTemplateId = template.id)}
									>
										<span class="text-sm font-semibold">{template.name}</span>
										<span class="mt-1 text-xs text-muted-foreground">{template.description}</span>
									</button>
								{/each}
							</div>
						{:else}
							<textarea
								bind:value={customObjective}
								placeholder="E.g., Find mentions of what users dislike about existing products..."
								rows={4}
								class="w-full resize-none rounded-lg border border-border bg-background px-3 py-2 text-sm placeholder-muted-foreground transition-colors focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 focus:outline-none"
							></textarea>
							<p class="mt-2 text-xs text-muted-foreground">
								Provide clear instructions on what the AI should look for in the scraped data.
							</p>
						{/if}
					</div>
				</div>

				<!-- Subreddits -->

				<div class="rounded-xl border border-border bg-card">
					<div class="flex items-center justify-between border-b border-border px-5 py-3">
						<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">
							Subreddits
						</p>
						{#if usage}
							<span class="text-xs text-muted-foreground">
								Max <span class="font-semibold text-foreground">{maxSubs}</span> per scan
								{#if parsedSubreddits.length >= maxSubs}
									<span class="ml-1 text-amber-400">(limit reached)</span>
								{/if}
							</span>
						{/if}
					</div>
					<div class="overflow-x-auto p-5">
						<textarea
							id="subreddits-input"
							bind:value={subredditsInput}
							placeholder="learnprogramming, Python, webdev"
							rows={7}
							class="w-full resize-none rounded-lg border border-border bg-background px-3 py-2 font-mono text-sm placeholder-muted-foreground transition-colors focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 focus:outline-none"
						></textarea>
						<p class="mt-2 text-xs text-muted-foreground">
							One per line or comma-separated. The <code class="rounded bg-secondary px-1 py-0.5"
								>r/</code
							>
							prefix is optional.
							{#if usage && parsedSubreddits.length >= maxSubs}
								<span class="font-medium text-amber-400">
									Only the first {maxSubs} will be used.</span
								>
							{/if}
						</p>

						{#if parsedSubreddits.length > 0}
							<div class="mt-3 flex flex-wrap gap-1.5">
								{#each parsedSubreddits as sub}
									<span
										class="inline-flex items-center rounded-full border border-orange-500/30 bg-orange-500/10 px-2.5 py-0.5 text-xs font-medium text-orange-500"
									>
										r/{sub}
									</span>
								{/each}
							</div>
						{/if}
					</div>
				</div>

				<!-- Posts per subreddit -->

				<div class="rounded-xl border border-border bg-card">
					<div class="flex items-center justify-between border-b border-border px-5 py-3">
						<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">
							Posts per subreddit
						</p>
						<div class="flex items-center gap-2">
							{#if usage}
								<span class="text-xs text-muted-foreground"
									>Plan max: <span class="font-semibold text-foreground">{maxPosts}</span></span
								>
							{/if}
							<span
								class="rounded-full border border-orange-500/30 bg-orange-500/10 px-2.5 py-0.5 text-xs font-bold text-orange-500"
								>{scrapeLimit}</span
							>
						</div>
					</div>
					<div class="p-5">
						<input
							id="scrape-limit"
							type="range"
							min="5"
							max={Math.max(5, maxPosts)}
							step="5"
							bind:value={scrapeLimit}
							class="h-2 w-full cursor-pointer appearance-none rounded-full bg-secondary accent-orange-500"
						/>
						<div class="mt-2 flex justify-between text-xs text-muted-foreground">
							<span>5 — quick</span>
							<span>{maxPosts} — max ({usage?.tier ?? '…'})</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Right: summary + submit -->
			<div class="lg:col-span-1">
				<div class="rounded-xl border border-border bg-card">
					<div class="flex items-center justify-between border-b border-border px-5 py-3">
						<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">Summary</p>
					</div>
					<div class="space-y-3 p-5">
						<div class="flex items-center justify-between">
							<span class="text-sm text-muted-foreground">Subreddits</span>
							<span class="text-sm font-semibold">
								{parsedSubreddits.length > 0 ? parsedSubreddits.length : '—'}
								{#if usage}<span class="text-xs text-muted-foreground">/ {maxSubs} max</span>{/if}
							</span>
						</div>
						<div class="flex items-center justify-between">
							<span class="text-sm text-muted-foreground">Posts each</span>
							<span class="text-sm font-semibold">
								{scrapeLimit}
								{#if usage}<span class="text-xs text-muted-foreground">/ {maxPosts} max</span>{/if}
							</span>
						</div>
						<div class="flex items-center justify-between">
							<span class="text-sm text-muted-foreground">Est. posts total</span>
							<span class="text-sm font-semibold"
								>{parsedSubreddits.length > 0 ? parsedSubreddits.length * scrapeLimit : '—'}</span
							>
						</div>
						<div class="flex items-center justify-between">
							<span class="text-sm text-muted-foreground">Analysis Mode</span>
							<span class="text-sm font-semibold capitalize">{analysisType}</span>
						</div>

						<!-- Scan usage meter -->
						{#if usage && !isUnlimited && scansTotal !== null}
							<div class="mb-5 rounded-lg border border-border p-3">
								<div class="mb-2 flex items-center justify-between">
									<span class="text-xs font-medium text-muted-foreground">Scans today</span>
									<span class="text-xs font-bold {scanUsageColor()}"
										>{scansToday} / {scansTotal}</span
									>
								</div>
								<div class="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
									<div
										class="h-full rounded-full transition-all {scansLeft === 0
											? 'bg-red-500'
											: scansLeft! <= 3
												? 'bg-amber-500'
												: 'bg-primary'}"
										style="width: {scansTotal > 0
											? Math.min(100, (scansToday / scansTotal) * 100)
											: 100}%"
									></div>
								</div>
								{#if scansLeft !== null && scansLeft <= 3 && scansLeft > 0}
									<p class="mt-2 text-xs text-amber-400">
										{scansLeft} scan{scansLeft === 1 ? '' : 's'} left today
									</p>
								{/if}
							</div>
						{:else if usage && isUnlimited}
							<div class="mb-5 rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3">
								<p class="flex items-center gap-1.5 text-xs font-medium text-emerald-400">
									<Zap class="h-3.5 w-3.5" />
									Unlimited scans on {usage.tier}
								</p>
							</div>
						{/if}

						<div class="mb-4 h-px bg-border"></div>

						<button
							id="start-analysis-btn"
							onclick={submitJob}
							disabled={isSubmitting || parsedSubreddits.length === 0 || isAtLimit}
							class="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-orange-500 to-pink-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md shadow-orange-500/20 transition hover:from-orange-600 hover:to-pink-700 disabled:cursor-not-allowed disabled:opacity-50"
						>
							{#if isSubmitting}
								<svg class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
									<circle
										class="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										stroke-width="4"
									></circle>
									<path
										class="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
									></path>
								</svg>
								Starting…
							{:else if isAtLimit}
								Limit reached for today
							{:else}
								<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M13 10V3L4 14h7v7l9-11h-7z"
									/>
								</svg>
								Start Analysis
							{/if}
						</button>

						<p class="mt-3 text-center text-xs text-muted-foreground">
							Results appear in the <a
								href="/dashboard/results"
								class="text-foreground underline-offset-2 hover:underline">Results</a
							> tab.
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
