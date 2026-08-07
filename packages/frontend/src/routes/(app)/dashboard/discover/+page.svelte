<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { redditApi, type UsageResponse } from '$lib/api/reddit.api';
	import type { ProfessionResponse, SubredditDetailResponse } from '$lib/types/reddit';
	import { Search, Users, Activity } from '@lucide/svelte';

	let professions = $state<ProfessionResponse[]>([]);
	let selectedSlug = $state<string>('');
	let subreddits = $state<SubredditDetailResponse[]>([]);
	let loadingProfessions = $state(true);
	let loadingSubreddits = $state(false);
	let selectedSubreddits = $state<string[]>([]);
	let usage = $state<UsageResponse | null>(null);
	let searched = $state(false);

	let searchQuery = $state('');
	let showDropdown = $state(false);

	const filteredProfessions = $derived(
		professions.filter((p) => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
	);

	function selectProfession(prof: ProfessionResponse) {
		searchQuery = prof.name;
		selectedSlug = prof.slug;
		showDropdown = false;
		// aiSearchQuery = ''; // clear AI search query when picking a profession
		onProfessionChange();
	}

	let aiSearchQuery = $state('');
	let isAiSearching = $state(false);

	async function runAiSearch() {
		if (!aiSearchQuery.trim()) return;
		isAiSearching = true;
		subreddits = [];
		selectedSlug = ''; // clear profession selection
		searchQuery = ''; // clear profession input

		try {
			const res = await redditApi.searchSubreddits(aiSearchQuery);
			if (!res.success || !res.job_id) {
				toast.error('Failed to start AI search.');
				isAiSearching = false;
				return;
			}

			// Poll for status
			const jobId = res.job_id;
			let isComplete = false;

			while (!isComplete) {
				await new Promise((r) => setTimeout(r, 2500));

				const statusRes = await redditApi.getSearchSubredditsStatus(jobId);
				if (statusRes.status === 'complete') {
					subreddits = statusRes.subreddits || [];
					isComplete = true;
					searched = true;
				} else if (statusRes.status === 'failed') {
					toast.error('AI search failed. Please try again.');
					isComplete = true;
					searched = true;
				}
			}
		} catch (e) {
			console.error('Failed to run AI search', e);
			toast.error('AI search failed. Please try again.');
		} finally {
			isAiSearching = false;
		}
	}

	// Derived plan caps (with safe fallbacks while loading)
	const tier = $derived(usage?.tier || '');
	const isProfessional = $derived(tier === 'Professional');
	const isStarter = $derived(tier === 'Starter');
	const maxSubs = $derived(usage ? (isProfessional ? 10 : isStarter ? 3 : 0) : 3);

	onMount(async () => {
		try {
			const [profRes, usageRes] = await Promise.all([
				redditApi.listProfessions(),
				redditApi.getUsage().catch(() => null)
			]);
			professions = profRes;
			if (usageRes) usage = usageRes;
		} catch (e) {
			console.error('Failed to load professions', e);
		} finally {
			loadingProfessions = false;
		}
	});

	async function onProfessionChange() {
		if (!selectedSlug) {
			subreddits = [];
			return;
		}

		loadingSubreddits = true;
		try {
			const res = await redditApi.getProfessionSubreddits(selectedSlug);
			subreddits = res.subreddits || [];
		} catch (e) {
			console.error('Failed to load subreddits', e);
			subreddits = [];
		} finally {
			loadingSubreddits = false;
		}
	}

	function toggleSubredditSelection(subName: string) {
		if (selectedSubreddits.includes(subName)) {
			selectedSubreddits = selectedSubreddits.filter((s) => s !== subName);
		} else {
			if (selectedSubreddits.length >= maxSubs) {
				toast.error(
					`You can only scan up to ${maxSubs} subreddits at a time on your current plan.`
				);
				return;
			}
			selectedSubreddits = [...selectedSubreddits, subName];
		}
	}

	function scanSelected() {
		if (selectedSubreddits.length === 0) return;
		goto(`/dashboard/scan?add=${encodeURIComponent(selectedSubreddits.join(','))}`);
	}
</script>

<svelte:head>
	<title>Discover Niches — Taren</title>
</svelte:head>

<div class="flex h-full flex-col">
	<div
		class="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-4 sm:px-6 md:px-8 md:py-5"
	>
		<h1 class="text-lg font-semibold">Discover Niches</h1>
	</div>

	<div class="flex-1 overflow-y-auto px-4 py-5 sm:px-6 md:px-8 md:py-6">
		<div class="mb-8">
			<h2 class="text-2xl font-bold">Find Communities</h2>
			<p class="mt-1 text-muted-foreground">
				Select a profession to discover highly relevant subreddits to scan for pain points.
			</p>
		</div>

		<div class="mb-8 grid gap-6 md:max-w-4xl md:grid-cols-2">
			<div>
				<label for="profession" class="mb-2 block text-sm font-medium text-foreground">
					Curated Professions
				</label>
				<div class="relative">
					<input
						id="profession"
						type="text"
						bind:value={searchQuery}
						oninput={() => {
							showDropdown = true;
							selectedSlug = '';
							subreddits = [];
							// aiSearchQuery = '';
						}}
						onfocus={() => (showDropdown = true)}
						onblur={() => setTimeout(() => (showDropdown = false), 150)}
						disabled={loadingProfessions}
						placeholder={loadingProfessions
							? 'Loading professions...'
							: 'Search for a profession...'}
						autocomplete="off"
						class="w-full rounded-xl border border-border bg-card px-4 py-3 pr-10 text-sm font-medium shadow-sm transition-colors focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 focus:outline-none disabled:opacity-50"
					/>
					<div
						class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-muted-foreground"
					>
						<Search class="h-4 w-4" />
					</div>

					{#if showDropdown && filteredProfessions.length > 0}
						<ul
							class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-xl border border-border bg-card py-1 text-sm shadow-lg focus:outline-none"
						>
							{#each filteredProfessions as prof}
								<!-- svelte-ignore a11y_click_events_have_key_events -->
								<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
								<li
									class="cursor-pointer px-4 py-2 select-none hover:bg-orange-500/10 hover:text-orange-500"
									onclick={() => selectProfession(prof)}
								>
									{prof.name}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
			</div>

			<div>
				<label
					for="ai-search"
					class="mb-2 block flex items-center gap-2 text-sm font-medium text-foreground"
				>
					<svg class="h-4 w-4 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"
						><path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 10V3L4 14h7v7l9-11h-7z"
						/></svg
					>
					AI Subreddit Search
				</label>
				<div class="relative flex gap-2">
					<div class="relative flex-1">
						<input
							id="ai-search"
							type="text"
							bind:value={aiSearchQuery}
							onkeydown={(e) => {
								if (e.key === 'Enter') runAiSearch();
							}}
							disabled={isAiSearching}
							placeholder="Enter any topic or keyword..."
							autocomplete="off"
							class="w-full rounded-xl border border-border bg-card px-4 py-3 text-sm font-medium shadow-sm transition-colors focus:border-pink-500 focus:ring-2 focus:ring-pink-500/20 focus:outline-none disabled:opacity-50"
						/>
					</div>
					<button
						onclick={runAiSearch}
						disabled={isAiSearching || !aiSearchQuery.trim()}
						class="flex shrink-0 items-center justify-center rounded-xl bg-pink-500 px-5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-pink-600 focus:ring-2 focus:ring-pink-500/20 focus:outline-none disabled:opacity-50"
					>
						{#if isAiSearching}
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
						{:else}
							Search
						{/if}
					</button>
				</div>
			</div>
		</div>

		{#if selectedSubreddits.length > 0}
			<div class="mb-8 rounded-xl border border-border bg-card p-5 shadow-sm">
				<div class="mb-3 flex items-center justify-between">
					<div class="flex flex-col">
						<h3 class="text-sm font-semibold text-foreground">Selected for Scan</h3>
						<span class="text-xs text-muted-foreground">
							{selectedSubreddits.length} of {maxSubs} max subreddits
						</span>
					</div>
					<button
						onclick={scanSelected}
						class="rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-sm shadow-orange-500/20 transition-all hover:bg-orange-600"
					>
						Scan Selected
					</button>
				</div>
				<div class="flex flex-wrap gap-2">
					{#each selectedSubreddits as sub}
						<div
							class="flex items-center gap-1.5 rounded-full border border-orange-500/30 bg-orange-500/10 px-3 py-1 text-xs font-medium text-orange-500 transition-colors"
						>
							r/{sub}
							<button
								onclick={() => toggleSubredditSelection(sub)}
								class="ml-1 cursor-pointer text-orange-500/70 hover:text-orange-500 focus:outline-none"
								aria-label="Remove subreddit"
							>
								<svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M6 18L18 6M6 6l12 12"
									/>
								</svg>
							</button>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		{#if loadingSubreddits || isAiSearching}
			<div class="flex items-center justify-center py-12">
				<div class="flex flex-col items-center gap-3 text-muted-foreground">
					<svg
						class="h-8 w-8 animate-spin {isAiSearching ? 'text-pink-500' : 'text-orange-500'}"
						fill="none"
						viewBox="0 0 24 24"
					>
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
						></circle>
						<path
							class="opacity-75"
							fill="currentColor"
							d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
						></path>
					</svg>
					<p class="text-sm font-medium">
						{isAiSearching ? 'AI is searching the web...' : 'Finding communities...'}
					</p>
				</div>
			</div>
		{:else if (selectedSlug && subreddits.length === 0) || (searched && aiSearchQuery && !isAiSearching && subreddits.length === 0 && !showDropdown)}
			<div class="rounded-xl border border-dashed border-border bg-card/50 p-12 text-center">
				<Search class="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
				<h3 class="text-lg font-medium">No subreddits found</h3>
				<p class="mt-1 text-sm text-muted-foreground">
					We couldn't find any communities for this search.
				</p>
			</div>
		{:else if subreddits.length > 0}
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each subreddits as sub}
					<div
						class="group flex h-full flex-col rounded-xl border border-border bg-card p-5 transition-all hover:border-orange-500/50 hover:shadow-md"
					>
						<div class="mb-3 flex items-start justify-between gap-2">
							<h3 class="text-base font-bold text-foreground">r/{sub.name}</h3>
							<button
								onclick={() => toggleSubredditSelection(sub.name)}
								class={selectedSubreddits.includes(sub.name)
									? 'cursor-pointer rounded-full bg-orange-500 px-3 py-1 text-xs font-semibold text-white shadow-sm transition-all focus:outline-none'
									: 'cursor-pointer rounded-full bg-orange-500/10 px-3 py-1 text-xs font-semibold text-orange-500 opacity-100 transition-all group-hover:opacity-100 hover:bg-orange-500 hover:text-white focus:opacity-100 focus:outline-none lg:opacity-0'}
							>
								{selectedSubreddits.includes(sub.name) ? 'Selected' : 'Add to list'}
							</button>
						</div>

						{#if !sub.description && !sub.subscribers && !sub.activity_level}
							<p class="mb-4 line-clamp-3 text-sm text-muted-foreground">
								We need more information about this subreddit to provide relevant information.
							</p>
						{/if}

						{#if sub.description}
							<p class="mb-4 line-clamp-3 text-sm text-muted-foreground">
								{sub.description}
							</p>
						{/if}

						<div class="mt-auto flex items-center gap-4 text-xs font-medium text-muted-foreground">
							{#if sub.subscribers}
								<div class="flex items-center gap-1.5">
									<Users class="h-3.5 w-3.5" />
									<span>{(sub.subscribers / 1000).toFixed(0)}k</span>
								</div>
							{/if}
							{#if sub.activity_level}
								<div class="flex items-center gap-1.5">
									<Activity class="h-3.5 w-3.5" />
									<span class="capitalize">{sub.activity_level}</span>
								</div>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>
