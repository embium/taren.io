<script lang="ts">
	import Navigation from '$lib/components/Navigation.svelte';
	import { api } from '$lib/api/client';
	import { toast } from 'svelte-sonner';
	import { getAuthState } from '$lib/stores/auth.svelte';
	import { goto } from '$app/navigation';
	import { env } from '$env/dynamic/public';

	const authState = getAuthState();
	let loadingProductId: string | null = null;

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
				throw new Error("Failed to get checkout URL");
			}
		} catch (error: any) {
			console.error('Subscription error:', error);
			toast.error(error?.message || 'Failed to start checkout process');
			loadingProductId = null;
		}
	}
</script>

<svelte:head>
	<title>Taren - Pricing</title>
	<meta name="description" content="Taren Pricing - Choose the plan that fits you best." />
</svelte:head>

<div class="min-h-screen">
	<!-- Navigation -->
	<Navigation />

	<!-- Header Section -->
	<section class="px-6 py-24 lg:px-12 lg:py-32">
		<div class="mx-auto max-w-4xl text-center">
			<h1 class="mb-6 text-5xl font-bold tracking-tight lg:text-7xl">
				Simple, transparent pricing
			</h1>
			<p class="mx-auto max-w-2xl text-lg lg:text-xl">
				No hidden fees. No surprise charges. Choose the plan that's right for you.
			</p>
		</div>
	</section>

	<!-- Pricing Cards Section -->
	<section class="px-6 pb-24 lg:px-12">
		<div class="mx-auto max-w-5xl">
			<div class="grid gap-8 md:grid-cols-2">
				
				<!-- Starter Plan -->
				<div class="flex flex-col rounded-2xl border border-card bg-card p-8 shadow-sm transition-all hover:border-card">
					<h3 class="mb-4 text-2xl font-bold">Starter</h3>
					<div class="mb-6">
						<span class="text-4xl font-bold">$15</span>
						<span>/month</span>
					</div>
					<p class="mb-6">Perfect for individuals getting started.</p>
					
					<ul class="mb-8 flex-1 space-y-4">
						<li class="flex items-center">
							<svg class="mr-3 h-5 w-5 text-[#3b82f6]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
							Basic features
						</li>
						<li class="flex items-center">
							<svg class="mr-3 h-5 w-5 text-[#3b82f6]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
							1 User
						</li>
						<li class="flex items-center">
							<svg class="mr-3 h-5 w-5 text-[#3b82f6]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
							Standard support
						</li>
					</ul>
					
					<button
						onclick={() => subscribe(env.PUBLIC_STRIPE_PRODUCT_ID_STARTER)}
						disabled={loadingProductId !== null}
						class="w-full rounded-lg bg-[#262626] px-6 py-4 text-center font-semibold text-white transition-all hover:bg-[#404040] disabled:opacity-50"
					>
						{loadingProductId === env.PUBLIC_STRIPE_PRODUCT_ID_STARTER ? 'Loading...' : 'Subscribe to Starter'}
					</button>
				</div>

				<!-- Professional Plan -->
				<div class="relative flex flex-col rounded-2xl border border-[#3b82f6] bg-card p-8 shadow-lg transition-all hover:shadow-[#3b82f6]/20">
					<div class="absolute -top-4 left-0 right-0 flex justify-center">
						<span class="rounded-full bg-[#3b82f6] px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">Most Popular</span>
					</div>
					<h3 class="mb-4 text-2xl font-bold">Professional</h3>
					<div class="mb-6">
						<span class="text-4xl font-bold">$49</span>
						<span class="">/month</span>
					</div>
					<p class="mb-6">For professionals and small teams that need more power.</p>
					
					<ul class="mb-8 flex-1 space-y-4">
						<li class="flex items-center">
							<svg class="mr-3 h-5 w-5 text-[#3b82f6]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
							Advanced features
						</li>
						<li class="flex items-center">
							<svg class="mr-3 h-5 w-5 text-[#3b82f6]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
							Up to 5 Users
						</li>
						<li class="flex items-center">
							<svg class="mr-3 h-5 w-5 text-[#3b82f6]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
							Priority support
						</li>
						<li class="flex items-center">
							<svg class="mr-3 h-5 w-5 text-[#3b82f6]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
							Analytics dashboard
						</li>
					</ul>
					
					<button
						onclick={() => subscribe(env.PUBLIC_STRIPE_PRODUCT_ID_PROFESSIONAL)}
						disabled={loadingProductId !== null}
						class="w-full rounded-lg bg-[#3b82f6] px-6 py-4 text-center font-semibold text-white transition-all hover:bg-[#2563eb] disabled:opacity-50"
					>
						{loadingProductId === env.PUBLIC_STRIPE_PRODUCT_ID_PROFESSIONAL ? 'Loading...' : 'Subscribe to Professional'}
					</button>
				</div>
				
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="px-6 py-12 lg:px-12">
		<div class="mx-auto max-w-7xl text-center ">
				<p>&copy; {new Date().getFullYear()} Taren. All rights reserved.</p>
		</div>
	</footer>
</div>
