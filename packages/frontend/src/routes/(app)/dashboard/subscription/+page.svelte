<script lang="ts">
	import { onMount } from 'svelte';
	import {
		CreditCard,
		Calendar,
		Clock,
		AlertTriangle,
		CheckCircle2,
		XCircle,
		Zap,
		ChevronRight
	} from '@lucide/svelte';
	import { toast } from 'svelte-sonner';
	import { stripeApi, type SubscriptionDetails } from '$lib/api/stripe.api';

	let subscription = $state<SubscriptionDetails | null>(null);
	let loading = $state(true);
	let cancelling = $state(false);
	let showCancelConfirm = $state(false);

	onMount(async () => {
		try {
			subscription = await stripeApi.getSubscription();
		} catch {
			toast.error('Failed to load subscription details.');
		} finally {
			loading = false;
		}
	});

	function formatDate(unix: number | null | undefined): string {
		if (!unix) return '�';
		return new Date(unix * 1000).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function formatAmount(cents: number | null | undefined): string {
		if (cents == null) return '$0.00';
		return `$${(cents / 100).toFixed(2)}`;
	}

	const isTrialing = $derived(subscription?.status === 'trialing');
	const isActive = $derived(subscription?.status === 'active' || isTrialing);
	const isCancelledAtEnd = $derived(subscription?.cancel_at_period_end === true);
	// Cancelled during a trial: trial ends and they will NOT be charged
	const isTrialingAndCancelled = $derived(isTrialing && isCancelledAtEnd);

	async function handleCancel() {
		cancelling = true;
		try {
			await stripeApi.cancelSubscription();
			toast.success(
				'Subscription cancelled. You will retain access until the end of your billing period.'
			);
			subscription = await stripeApi.getSubscription();
			showCancelConfirm = false;
		} catch {
			toast.error('Failed to cancel subscription. Please try again.');
		} finally {
			cancelling = false;
		}
	}
</script>

<svelte:head>
	<title>Billing — Taren</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Title bar -->
	<div
		class="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-4 sm:px-6 md:px-8 md:py-5"
	>
		<h1 class="text-lg font-semibold">Billing</h1>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-y-auto px-4 py-6 sm:px-6 md:px-8">
		<div class="mx-auto max-w-2xl space-y-5">
			{#if loading}
				<!-- Skeleton -->
				<div class="animate-pulse space-y-4 rounded-xl border border-border bg-card p-6">
					<div class="h-5 w-40 rounded bg-muted"></div>
					<div class="h-10 w-28 rounded bg-muted"></div>
					<div class="h-4 w-64 rounded bg-muted"></div>
					<div class="h-4 w-48 rounded bg-muted"></div>
				</div>
			{:else if !subscription}
				<!-- No subscription -->
				<div class="space-y-4 rounded-xl border border-border bg-card p-10 text-center">
					<div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-muted">
						<CreditCard class="h-7 w-7 text-muted-foreground" />
					</div>
					<h2 class="text-xl font-semibold">No active subscription</h2>
					<p class="text-sm text-muted-foreground">
						You are currently on the free plan. Upgrade to unlock full features.
					</p>
					<a
						href="/pricing"
						class="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
					>
						<Zap class="h-4 w-4" />
						View Plans
					</a>
				</div>
			{:else}
				<!-- Status banner -->
				{#if isTrialingAndCancelled}
					<!-- Cancelled during trial: make it crystal clear they won't be charged -->
					<div
						class="flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4"
					>
						<AlertTriangle class="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
						<div>
							<p class="text-sm font-semibold text-red-300">Trial Ending — No Charge</p>
							<p class="mt-0.5 text-sm text-red-400/80">
								You cancelled during your trial. Your access ends on
								<span class="font-medium text-red-300"
									>{formatDate(subscription.trial_end)}</span
								>. <span class="font-medium text-red-300">You will not be charged.</span>
							</p>
						</div>
					</div>
				{:else if isTrialing}
					<div
						class="flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 px-5 py-4"
					>
						<Clock class="mt-0.5 h-5 w-5 shrink-0 text-amber-400" />
						<div>
							<p class="text-sm font-semibold text-amber-300">Free Trial Active</p>
							<p class="mt-0.5 text-sm text-amber-400/80">
								Your trial ends on <span class="font-medium text-amber-300"
									>{formatDate(subscription.trial_end)}</span
								>. You will be charged
								<span class="font-medium text-amber-300"
									>{formatAmount(subscription.amount)}/{subscription.interval}</span
								> after the trial ends.
							</p>
						</div>
					</div>
				{:else if isCancelledAtEnd}
					<div
						class="flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4"
					>
						<AlertTriangle class="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
						<div>
							<p class="text-sm font-semibold text-red-300">Cancellation Scheduled</p>
							<p class="mt-0.5 text-sm text-red-400/80">
								Your subscription will end on <span class="font-medium text-red-300"
									>{formatDate(subscription.current_period_end)}</span
								>. You retain full access until then.
							</p>
						</div>
					</div>
				{/if}

				<!-- Main card -->
				<div class="overflow-hidden rounded-xl border border-border bg-card">
					<!-- Card header -->
					<div class="flex items-center justify-between border-b border-border px-6 py-5">
						<div class="flex items-center gap-3">
							<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/15">
								<Zap class="h-5 w-5 text-indigo-400" />
							</div>
							<div>
								<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">
									Current Plan
								</p>
								<p class="text-lg font-bold">{subscription.tier}</p>
							</div>
						</div>
						<span
							class={[
								'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold',
								isCancelledAtEnd
									? 'border-red-500/40 bg-red-500/10 text-red-400'
									: isTrialing
										? 'border-amber-500/40 bg-amber-500/10 text-amber-400'
										: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400'
							].join(' ')}
						>
							{#if isCancelledAtEnd}
								<XCircle class="h-3 w-3" />
								Cancelling
							{:else if isTrialing}
								<Clock class="h-3 w-3" />
								Trial
							{:else}
								<CheckCircle2 class="h-3 w-3" />
								Active
							{/if}
						</span>
					</div>

					<!-- Details rows -->
					<div class="divide-y divide-border">
						<!-- Billing amount -->
						<div class="flex items-center justify-between px-6 py-4">
							<div class="flex items-center gap-3">
								<CreditCard class="h-4 w-4 text-muted-foreground" />
								<span class="text-sm text-muted-foreground">Billing amount</span>
							</div>
							<span class="text-sm font-semibold">
								{#if isTrialingAndCancelled}
									<span class="font-bold text-emerald-400">No charge</span>
								{:else if isTrialing}
									<span class="mr-2 font-bold text-emerald-400">$0.00 now</span>
									<span class="text-muted-foreground"
										>then {formatAmount(subscription.amount)}/{subscription.interval}</span
									>
								{:else}
									{formatAmount(subscription.amount)} / {subscription.interval}
								{/if}
							</span>
						</div>

						<!-- Billing interval -->
						<div class="flex items-center justify-between px-6 py-4">
							<div class="flex items-center gap-3">
								<Calendar class="h-4 w-4 text-muted-foreground" />
								<span class="text-sm text-muted-foreground">Billing interval</span>
							</div>
							<span class="text-sm font-semibold capitalize">{subscription.interval}ly</span>
						</div>

						<!-- Trial / next billing dates -->
						{#if isTrialingAndCancelled && subscription.trial_end}
							<!-- Cancelled during trial: show trial end as the access end date -->
							<div class="flex items-center justify-between px-6 py-4">
								<div class="flex items-center gap-3">
									<Clock class="h-4 w-4 text-muted-foreground" />
									<span class="text-sm text-muted-foreground">Access ends</span>
								</div>
								<span class="text-sm font-semibold text-red-400"
									>{formatDate(subscription.trial_end)}</span
								>
							</div>
						{:else if isTrialing && subscription.trial_end}
							<div class="flex items-center justify-between px-6 py-4">
								<div class="flex items-center gap-3">
									<Clock class="h-4 w-4 text-muted-foreground" />
									<span class="text-sm text-muted-foreground">Trial ends</span>
								</div>
								<span class="text-sm font-semibold text-amber-400"
									>{formatDate(subscription.trial_end)}</span
								>
							</div>
							<div class="flex items-center justify-between px-6 py-4">
								<div class="flex items-center gap-3">
									<Calendar class="h-4 w-4 text-muted-foreground" />
									<span class="text-sm text-muted-foreground">First charge on</span>
								</div>
								<span class="text-sm font-semibold">{formatDate(subscription.trial_end)}</span>
							</div>
						{:else}
							<div class="flex items-center justify-between px-6 py-4">
								<div class="flex items-center gap-3">
									<Calendar class="h-4 w-4 text-muted-foreground" />
									<span class="text-sm text-muted-foreground">
										{isCancelledAtEnd ? 'Access ends' : 'Next billing date'}
									</span>
								</div>
								<span class="text-sm font-semibold {isCancelledAtEnd ? 'text-red-400' : ''}"
									>{formatDate(subscription.current_period_end)}</span
								>
							</div>
						{/if}
					</div>

					<!-- Cancel action -->
					{#if !isCancelledAtEnd}
						<div class="border-t border-border bg-muted/30 px-6 py-5">
							{#if !showCancelConfirm}
								<button
									id="cancel-subscription-btn"
									onclick={() => (showCancelConfirm = true)}
									class="flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-destructive"
								>
									<XCircle class="h-4 w-4" />
									Cancel subscription
								</button>
							{:else}
								<div class="space-y-3">
									<p class="text-sm text-muted-foreground">
										{#if isTrialing}
											Are you sure? Your trial access ends on
											<span class="font-medium text-foreground"
												>{formatDate(subscription.trial_end)}</span
											>. <span class="font-medium text-foreground">You will not be charged.</span>
										{:else}
											Are you sure? Your subscription stays active until
											<span class="font-medium text-foreground"
												>{formatDate(subscription.current_period_end)}</span
											>, then ends.
										{/if}
									</p>
									<div class="flex items-center gap-3">
										<button
											id="confirm-cancel-btn"
											onclick={handleCancel}
											disabled={cancelling}
											class="inline-flex items-center gap-2 rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-2 text-sm font-medium text-destructive transition-colors hover:bg-destructive/20 disabled:cursor-not-allowed disabled:opacity-50"
										>
											{#if cancelling}
												<svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
													<circle
														class="opacity-25"
														cx="12"
														cy="12"
														r="10"
														stroke="currentColor"
														stroke-width="4"
													></circle>
													<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"
													></path>
												</svg>
												Cancelling�
											{:else}
												Yes, cancel it
											{/if}
										</button>
										<button
											onclick={() => (showCancelConfirm = false)}
											class="text-sm text-muted-foreground transition-colors hover:text-foreground"
										>
											Keep subscription
										</button>
									</div>
								</div>
							{/if}
						</div>
					{/if}
				</div>

				<!-- Upgrade nudge (trial only, not when already cancelled) -->
				{#if isTrialing && !isCancelledAtEnd}
					<div
						class="flex items-center justify-between gap-4 rounded-xl border border-indigo-500/20 bg-indigo-500/5 px-6 py-4"
					>
						<div>
							<p class="text-sm font-medium">Enjoying Taren?</p>
							<p class="mt-0.5 text-xs text-muted-foreground">
								Upgrade to Professional for more scans and advanced analytics.
							</p>
						</div>
						<a
							href="/pricing"
							class="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-500"
						>
							Upgrade
							<ChevronRight class="h-4 w-4" />
						</a>
					</div>
				{/if}
			{/if}
		</div>
	</div>
</div>
