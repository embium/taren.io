<script lang="ts">
	import Navigation from '$lib/components/Navigation.svelte';
	import { api } from '$lib/api/client';
	import { toast } from 'svelte-sonner';
	import { getAuthState } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import { env } from '$env/dynamic/public';
	import { CheckCircle2, Zap, Star, Clock } from '@lucide/svelte';

	const authState = getAuthState();
	let loadingProductId: string | null = $state(null);

	// @ts-ignore - subscription_tier exists on user
	const currentTier = $derived(authState.user?.subscription_tier ?? null);
	const isOnStarter = $derived(currentTier === 'Starter');
	const isOnProfessional = $derived(currentTier === 'Professional');

	const STARTER_ID = env.PUBLIC_STRIPE_PRODUCT_ID_STARTER;
	const PRO_ID = env.PUBLIC_STRIPE_PRODUCT_ID_PROFESSIONAL;

	const starterFeatures = [
		{ text: '14-day free trial — no charge until it ends', highlight: true },
		{ text: '10 scans per day' },
		{ text: 'Up to 3 subreddits per scan' },
		{ text: 'Up to 15 posts scraped per subreddit' },
		{ text: 'Up to 10 evidences per finding' }
		// { text: 'AI-powered detection' },
		// { text: 'Up to 15 evidence quotes per pain point' },
		// { text: 'Export results as CSV' }
	];

	const proFeatures = [
		{ text: 'Unlimited scans per day', highlight: true },
		{ text: 'Up to 10 subreddits per scan' },
		{ text: 'Up to 100 posts per subreddit' },
		{ text: 'Unlimited evidence per finding' }
		// { text: 'AI Startup Idea Reports' },
		// { text: 'CSV & PDF export' },
		// { text: 'Priority support' }
	];

	async function subscribe(productId: string) {
		if (!authState.isAuthenticated) {
			toast.error('Please sign in to subscribe.');
			goto('/login?redirect=/pricing');
			return;
		}

		try {
			loadingProductId = productId;
			const response = await api.post<{ url: string }>('/stripe/create-checkout-session', {
				product_id: productId
			});

			if (response && response.url) {
				window.location.href = response.url;
			} else {
				throw new Error('Failed to get checkout URL');
			}
		} catch (error: any) {
			console.error('Subscription error:', error);
			toast.error(error?.message || 'Failed to start checkout process');
			loadingProductId = null;
		}
	}
</script>

<svelte:head>
	<title>Taren — Pricing</title>
	<meta
		name="description"
		content="Simple, transparent pricing. Start free for 14 days, no card required until your trial ends."
	/>
</svelte:head>

<div class="min-h-screen bg-background">
	<Navigation />

	<!-- Header -->
	<section class="px-6 py-20 text-center lg:px-12 lg:py-28">
		<div class="mx-auto max-w-3xl">
			<p
				class="mb-4 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary"
			>
				<Zap class="h-3.5 w-3.5" />
				Priced to beat the competition
			</p>
			<h1 class="mb-5 text-5xl font-bold tracking-tight lg:text-6xl">
				Simple, transparent pricing
			</h1>
			<p class="mx-auto max-w-2xl text-lg text-muted-foreground">
				No hidden fees. No surprise charges. Start with a 14-day free trial on Starter — no card
				charged until it ends.
			</p>
		</div>
	</section>

	<!-- Cards -->
	<section class="px-6 pb-28 lg:px-12">
		<div class="mx-auto max-w-5xl">
			<div class="grid items-start gap-8 md:grid-cols-2">
				<!-- Starter -->
				<div
					class={[
						'relative flex flex-col rounded-2xl border p-8 transition-all',
						isOnStarter
							? 'border-emerald-500/50 bg-emerald-500/5'
							: 'border-border bg-card shadow-sm hover:border-border/80'
					].join(' ')}
				>
					{#if isOnStarter}
						<div class="absolute -top-3.5 left-1/2 -translate-x-1/2">
							<span
								class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500 px-3 py-1 text-xs font-semibold text-white shadow"
							>
								<CheckCircle2 class="h-3 w-3" />
								Current Plan
							</span>
						</div>
					{/if}

					<!-- Trial badge -->
					<div class="mb-5 flex items-center gap-2">
						<span
							class="inline-flex items-center gap-1.5 rounded-full border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-400"
						>
							<Clock class="h-3 w-3" />
							14-day free trial
						</span>
					</div>

					<h3 class="mb-1 text-2xl font-bold">Starter</h3>
					<p class="mb-5 text-sm text-muted-foreground">Perfect for founders validating ideas</p>

					<div class="mb-6 flex items-baseline gap-1">
						<span class="text-5xl font-bold">$15</span>
						<span class="text-muted-foreground">/month</span>
						<span
							class="ml-2 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary"
							>Save $4 vs competitors</span
						>
					</div>

					{#if isOnStarter}
						<p class="mb-5 flex items-center gap-1.5 text-sm font-medium text-emerald-400">
							<CheckCircle2 class="h-4 w-4" />
							Already subscribed to this plan
						</p>
					{/if}

					<ul class="mb-8 flex-1 space-y-3">
						{#each starterFeatures as feature}
							<li class="flex items-start gap-3">
								<CheckCircle2
									class={[
										'mt-0.5 h-4 w-4 shrink-0',
										feature.highlight ? 'text-amber-400' : 'text-primary'
									].join(' ')}
								/>
								<span
									class={[
										'text-sm',
										feature.highlight ? 'font-medium text-foreground' : 'text-muted-foreground'
									].join(' ')}
								>
									{feature.text}
								</span>
							</li>
						{/each}
					</ul>

					{#if isOnStarter}
						<a
							href="/dashboard/subscription"
							class="block w-full rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-6 py-3.5 text-center text-sm font-semibold text-emerald-400 transition-colors hover:bg-emerald-500/20"
						>
							Manage Subscription
						</a>
					{:else}
						<button
							id="subscribe-starter-btn"
							onclick={() => subscribe(STARTER_ID)}
							disabled={loadingProductId !== null || isOnProfessional}
							class="w-full rounded-xl bg-foreground px-6 py-3.5 text-center text-sm font-semibold text-background transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
						>
							{#if loadingProductId === STARTER_ID}
								Starting trial…
							{:else if isOnProfessional}
								Downgrade not available
							{:else}
								Start 14-day free trial
							{/if}
						</button>
					{/if}
				</div>

				<!-- Professional -->
				<div
					class={[
						'relative flex flex-col rounded-2xl border p-8 transition-all',
						isOnProfessional
							? 'border-emerald-500/50 bg-emerald-500/5'
							: 'border-primary bg-card shadow-lg shadow-primary/10'
					].join(' ')}
				>
					{#if isOnProfessional}
						<div class="absolute -top-3.5 left-1/2 -translate-x-1/2">
							<span
								class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500 px-3 py-1 text-xs font-semibold text-white shadow"
							>
								<CheckCircle2 class="h-3 w-3" />
								Current Plan
							</span>
						</div>
					{:else}
						<div class="absolute -top-3.5 left-1/2 -translate-x-1/2">
							<span
								class="inline-flex items-center gap-1.5 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground shadow"
							>
								<Star class="h-3 w-3" />
								Most Popular
							</span>
						</div>
					{/if}

					<div class="mb-5 h-[28px]"></div>
					<!-- spacer to align with starter badge -->

					<h3 class="mb-1 text-2xl font-bold">Professional</h3>
					<p class="mb-5 text-sm text-muted-foreground">For teams and agencies who need scale</p>

					<div class="mb-6 flex items-baseline gap-1">
						<span class="text-5xl font-bold">$39</span>
						<span class="text-muted-foreground">/month</span>
						<span
							class="ml-2 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-semibold text-primary"
							>Save $10 vs competitors</span
						>
					</div>

					{#if isOnProfessional}
						<p class="mb-5 flex items-center gap-1.5 text-sm font-medium text-emerald-400">
							<CheckCircle2 class="h-4 w-4" />
							Already subscribed to this plan
						</p>
					{:else}
						<div class="mb-5 h-[24px]"></div>
					{/if}

					<ul class="mb-8 flex-1 space-y-3">
						{#each proFeatures as feature}
							<li class="flex items-start gap-3">
								<CheckCircle2
									class={[
										'mt-0.5 h-4 w-4 shrink-0',
										feature.highlight ? 'text-primary' : 'text-primary/70'
									].join(' ')}
								/>
								<span
									class={[
										'text-sm',
										feature.highlight ? 'font-medium text-foreground' : 'text-muted-foreground'
									].join(' ')}
								>
									{feature.text}
								</span>
							</li>
						{/each}
					</ul>

					{#if isOnProfessional}
						<a
							href="/dashboard/subscription"
							class="block w-full rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-6 py-3.5 text-center text-sm font-semibold text-emerald-400 transition-colors hover:bg-emerald-500/20"
						>
							Manage Subscription
						</a>
					{:else}
						<button
							id="subscribe-professional-btn"
							onclick={() => subscribe(PRO_ID)}
							disabled={loadingProductId !== null}
							class="w-full rounded-xl bg-primary px-6 py-3.5 text-center text-sm font-semibold text-primary-foreground transition-all hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
						>
							{loadingProductId === PRO_ID ? 'Redirecting…' : 'Subscribe to Professional'}
						</button>
					{/if}
				</div>
			</div>

			<!-- Bottom note -->
			<p class="mt-10 text-center text-sm text-muted-foreground">
				All plans include a 30-day money-back guarantee. Questions?
				<a
					href="mailto:support@taren.io"
					class="text-primary underline underline-offset-2 hover:opacity-80">Contact support</a
				>
			</p>
		</div>
	</section>

	<!-- ───── FOOTER ───── -->
	<footer class="border-t border-border px-6 py-10 lg:px-12">
		<div class="mx-auto flex max-w-7xl flex-col items-center gap-3 sm:flex-row sm:justify-between">
			<p class="text-sm font-bold">Taren</p>
			<div class="flex flex-wrap justify-center gap-6 text-sm text-muted-foreground">
				<a href="/pricing" class="transition-colors hover:text-foreground">Pricing</a>
				<a href="/login" class="transition-colors hover:text-foreground">Sign in</a>
				<a href="/register" class="transition-colors hover:text-foreground">Get started</a>
				<a href="/privacy" class="transition-colors hover:text-foreground">Privacy Policy</a>
				<a href="/terms" class="transition-colors hover:text-foreground">Terms of Service</a>
			</div>
			<p class="text-sm text-muted-foreground">
				&copy; {new Date().getFullYear()} Taren. All rights reserved.
			</p>
		</div>
	</footer>
</div>
