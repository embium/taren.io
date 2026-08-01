<script lang="ts">
	import { goto } from '$app/navigation';
	import Navigation from '$lib/components/Navigation.svelte';
</script>

<svelte:head>
	<title>Taren - The Future is Here</title>
	<meta
		name="description"
		content="Taren - Experience the next generation of innovation. Join us in shaping tomorrow."
	/>
</svelte:head>

<div class="min-h-screen">
	<!-- Navigation -->
	<Navigation />

	<!-- Hero Section -->
	<section class="px-6 py-32 lg:px-12 lg:py-40">
		<div class="mx-auto max-w-4xl text-center">
			<h1 class="mb-6 text-7xl font-bold tracking-tight lg:text-8xl">
				Taren
			</h1>
			<p class="mb-4 text-2xl font-medium lg:text-3xl">
				Building Tomorrow, Today
			</p>
			<p class="mx-auto mb-12 max-w-2xl text-lg leading-relaxed">
				Experience the future of innovation. We're creating something extraordinary that will
				transform the way you work and connect.
			</p>
			<button
				onclick={() => goto('/register')}
				class="rounded-lg bg-[#3b82f6] px-8 py-4 text-lg font-semibold text-white transition-all hover:bg-[#2563eb]"
			>
				Get Started
			</button>
		</div>
	</section>

	<!-- Features Section -->
	<section id="features" class="px-6 py-24 lg:px-12">
		<div class="mx-auto max-w-7xl">
			<div class="mb-16 text-center">
				<h2 class="mb-4 text-4xl font-bold lg:text-5xl">
					Why Taren?
				</h2>
				<p class="mx-auto max-w-2xl text-lg">
					Simple, powerful features designed to elevate your experience
				</p>
			</div>

			<div class="simple-grid">
				<!-- Feature Card 1 -->
				<div class="card p-8">
					<div class="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-card">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13 10V3L4 14h7v7l9-11h-7z"
							/>
						</svg>
					</div>
					<h3 class="mb-2 text-xl font-semibold text-[#fafafa]">Lightning Fast</h3>
					<p class="text-[#737373]">
						Optimized performance that keeps you productive
					</p>
				</div>

				<!-- Feature Card 2 -->
				<div class="card p-8">
					<div class="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-card">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
							/>
						</svg>
					</div>
					<h3 class="mb-2 text-xl font-semibold text-[#fafafa]">Secure by Design</h3>
					<p class="text-[#737373]">
						Enterprise-grade security for your peace of mind
					</p>
				</div>

				<!-- Feature Card 3 -->
				<div class="card p-8">
					<div class="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-card">
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
							/>
						</svg>
					</div>
					<h3 class="mb-2 text-xl font-semibold text-[#fafafa]">Team Collaboration</h3>
					<p class="text-[#737373]">
						Work together seamlessly with your team
					</p>
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
