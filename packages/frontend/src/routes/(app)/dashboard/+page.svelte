<script lang="ts">
	import { onMount } from 'svelte';
	import { getAuthState } from '$lib/stores/auth.svelte';
	import { redditApi } from '$lib/api/reddit.api';
	import type { JobResponse } from '$lib/types/reddit';

	const authState = getAuthState();

	let jobs = $state<JobResponse[]>([]);
	let loadingJobs = $state(true);

	onMount(async () => {
		try {
			jobs = await redditApi.listJobs();
		} catch {
			// ignore
		} finally {
			loadingJobs = false;
		}
	});

	function statusBadgeClass(status: string) {
		switch (status) {
			case 'done': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
			case 'failed': return 'bg-red-500/20 text-red-400 border-red-500/30';
			case 'scraping': case 'analyzing': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
			default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
		}
	}

	function formatDate(iso: string) {
		return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
	}

	function subredditList(raw: string) {
		return raw.split(',').map((s) => s.trim()).filter(Boolean);
	}
</script>

<svelte:head>
	<title>Dashboard - Taren</title>
</svelte:head>

<div class="flex flex-col h-full">
	<!-- Title bar -->
	<div class="flex items-center justify-between flex-wrap gap-2 px-4 sm:px-6 md:px-8 py-4 md:py-5 border-b border-border shrink-0">
		<h1 class="text-lg font-semibold">Overview</h1>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-y-auto px-4 sm:px-6 md:px-8 py-5 md:py-6">
		{#if authState.user?.is_email_verified}
			<!-- Welcome -->
			<div class="mb-8">
				<h2 class="text-2xl font-bold">
					Welcome back, {authState.user.name || authState.user.email.split('@')[0]} 👋
				</h2>
				<p class="mt-1 text-muted-foreground">Here's your account overview.</p>
			</div>

			<!-- Stats grid -->
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
				<!-- Account Status -->
				<div class="rounded-xl border border-border bg-card p-5">
					<div class="mb-3 flex items-center justify-between">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
							<svg class="h-5 w-5 text-primary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
							</svg>
						</div>
						<span class="rounded-full border border-emerald-600 bg-emerald-600/20 px-2.5 py-0.5 text-xs font-medium text-emerald-500">Active</span>
					</div>
					<p class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">Account Status</p>
					<p class="text-xl font-bold">{authState.user.is_email_verified ? 'Verified' : 'Unverified'}</p>
				</div>

				<!-- Email -->
				<div class="rounded-xl border border-border bg-card p-5">
					<div class="mb-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
							<svg class="h-5 w-5 text-secondary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
							</svg>
						</div>
					</div>
					<p class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">Email</p>
					<p class="truncate text-sm font-semibold">{authState.user.email}</p>
				</div>

				<!-- Member Since -->
				<div class="rounded-xl border border-border bg-card p-5">
					<div class="mb-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary">
							<svg class="h-5 w-5 text-secondary-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
							</svg>
						</div>
					</div>
					<p class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">Member Since</p>
					<p class="text-sm font-semibold">{new Date(authState.user.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</p>
				</div>

				<!-- Total Scans -->
				<div class="rounded-xl border border-border bg-card p-5">
					<div class="mb-3">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-500/10">
							<svg class="h-5 w-5 text-orange-500" fill="currentColor" viewBox="0 0 24 24">
								<path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
							</svg>
						</div>
					</div>
					<p class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">Total Scans</p>
					<p class="text-xl font-bold text-orange-400">{loadingJobs ? '—' : jobs.length}</p>
				</div>

				<!-- Subscription -->
				<div class="rounded-xl border border-border bg-card p-5">
					<div class="mb-3 flex items-center justify-between">
						<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/10">
							<svg class="h-5 w-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
							</svg>
						</div>
						<a href="/pricing" class="rounded-full border border-indigo-600/30 bg-indigo-600/10 px-2.5 py-0.5 text-xs font-medium text-indigo-400 hover:bg-indigo-600/20 transition-colors">Upgrade</a>
					</div>
					<p class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">Subscription Plan</p>
					<!-- @ts-ignore - Demonstrating where subscription field would go -->
					<p class="text-xl font-bold">{authState.user.subscription_tier || 'Free'}</p>
				</div>
			</div>

			<!-- Recent scans -->
			{#if !loadingJobs && jobs.length > 0}
				<div class="rounded-xl border border-border bg-card">
					<div class="flex items-center justify-between px-5 py-3 border-b border-border">
						<h3 class="text-sm font-semibold">Recent Scans</h3>
						<a href="/dashboard/history" class="text-xs text-muted-foreground hover:text-foreground transition-colors">View all →</a>
					</div>
					<div class="divide-y divide-border">
						{#each jobs.slice(0, 5) as job (job.id)}
							<div class="flex items-center justify-between px-5 py-3">
								<div class="min-w-0">
									<p class="truncate text-sm font-medium">{subredditList(job.subreddits).map((s) => `r/${s}`).join(', ')}</p>
									<p class="text-xs text-muted-foreground">{formatDate(job.created_at)}</p>
								</div>
								<span class="ml-4 inline-flex shrink-0 items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium {statusBadgeClass(job.status)}">
									{job.status}
								</span>
							</div>
						{/each}
					</div>
				</div>
			{/if}

		{:else if authState.user}
			<!-- Email verification reminder -->
			<div class="mx-auto max-w-lg rounded-xl border border-border bg-card p-10 text-center">
				<div class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-yellow-500/20">
					<svg class="h-8 w-8 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
					</svg>
				</div>
				<h2 class="mb-3 text-2xl font-bold">Verify Your Email</h2>
				<p class="mb-2 text-muted-foreground">We've sent a verification email to</p>
				<p class="font-semibold">{authState.user.email}</p>
				<p class="mt-3 text-sm text-muted-foreground">Click the link in the email to verify your account and access all features.</p>
			</div>
		{/if}
	</div>
</div>
