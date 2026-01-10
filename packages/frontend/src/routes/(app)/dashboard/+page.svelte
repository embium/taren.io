<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/button/button.svelte';
	import { getAuthState, logout } from '$lib/stores/auth.svelte';
	import { toast } from '$lib/stores/toast.svelte';
	import { onMount } from 'svelte';

	const authState = getAuthState();
	let mounted = $state(false);

	onMount(() => {
		mounted = true;
	});

	$effect(() => {
		if (!authState.isAuthenticated) {
			goto('/login');
		}
	});

	async function handleLogout() {
		try {
			await logout();
			toast.success('Logged out successfully');
			goto('/login');
		} catch (error) {
			console.error('Logout error:', error);
			toast.error('Logout failed');
		}
	}
</script>

<svelte:head>
	<title>Dashboard - Taren</title>
</svelte:head>

{#if authState.isAuthenticated && authState.user}
	<!-- Animated Background -->
	<div class="min-h-screen relative">
		<div class="fixed inset-0 -z-10">
			<div class="absolute inset-0 bg-[#0a0a0f]">
				<div
					class="mesh-gradient-1 absolute top-0 -left-20 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-pink-500/20 to-purple-500/20 mix-blend-screen blur-[120px] filter"
				></div>
				<div
					class="mesh-gradient-2 absolute top-1/4 right-0 h-[700px] w-[700px] rounded-full bg-gradient-to-br from-purple-500/20 to-blue-500/20 mix-blend-screen blur-[120px] filter"
				></div>
				<div
					class="mesh-gradient-1 absolute bottom-0 left-1/3 h-[650px] w-[650px] rounded-full bg-gradient-to-br from-blue-500/20 to-pink-500/20 mix-blend-screen blur-[120px] filter"
					style="animation-delay: -10s;"
				></div>
			</div>

			<div
				class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.02)_1px,transparent_1px)] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000,transparent)] bg-[size:64px_64px]"
			></div>
		</div>

		<div class="relative z-10">
			<!-- Header -->
			<header class="border-b border-gray-800">
				<div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
					<div>
						<h1 class="gradient-text text-3xl font-black">Taren</h1>
					</div>
					<Button variant="outline" onclick={handleLogout} class="glass-button">
						<svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
							/>
						</svg>
						Log Out
					</Button>
				</div>
			</header>

			<!-- Main Content -->
			<main class="max-w-7xl mx-auto px-6 py-12">
				<div class:text-reveal={mounted} style="animation-delay: 0.1s;">
					<h2 class="text-5xl font-black text-white mb-4">
						Welcome back, <span class="gradient-text">{authState.user.email.split('@')[0]}</span>
					</h2>
					<p class="text-gray-400 text-xl mb-12">Here's your account overview</p>
				</div>

				<!-- Stats Grid -->
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
					<div
						class="glass card-3d rounded-2xl p-6 border border-white/10"
						class:animate-scale-in={mounted}
						style="animation-delay: 0.2s;"
					>
						<div class="flex items-center justify-between mb-4">
							<div
								class="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center"
							>
								<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
									/>
								</svg>
							</div>
							<span class="badge-active">Active</span>
						</div>
						<h3 class="text-gray-400 text-sm font-medium mb-1">Account Status</h3>
						<p class="text-white text-2xl font-bold">Verified</p>
					</div>

					<div
						class="glass card-3d rounded-2xl p-6 border border-white/10"
						class:animate-scale-in={mounted}
						style="animation-delay: 0.3s;"
					>
						<div class="flex items-center justify-between mb-4">
							<div
								class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center"
							>
								<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
									/>
								</svg>
							</div>
						</div>
						<h3 class="text-gray-400 text-sm font-medium mb-1">Email</h3>
						<p class="text-white text-lg font-semibold truncate">{authState.user.email}</p>
					</div>

					<div
						class="glass card-3d rounded-2xl p-6 border border-white/10"
						class:animate-scale-in={mounted}
						style="animation-delay: 0.4s;"
					>
						<div class="flex items-center justify-between mb-4">
							<div
								class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center"
							>
								<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
									/>
								</svg>
							</div>
						</div>
						<h3 class="text-gray-400 text-sm font-medium mb-1">Member Since</h3>
						<p class="text-white text-lg font-semibold">
							{new Date(authState.user.created_at).toLocaleDateString('en-US', {
								month: 'short',
								year: 'numeric'
							})}
						</p>
					</div>

					<div
						class="glass card-3d rounded-2xl p-6 border border-white/10"
						class:animate-scale-in={mounted}
						style="animation-delay: 0.5s;"
					>
						<div class="flex items-center justify-between mb-4">
							<div
								class="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center"
							>
								<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
									/>
								</svg>
							</div>
						</div>
						<h3 class="text-gray-400 text-sm font-medium mb-1">User ID</h3>
						<p class="text-white text-sm font-mono truncate">{authState.user.id}</p>
					</div>
				</div>

				<!-- Welcome Card -->
				<div
					class="glass rounded-3xl p-8 lg:p-12 border border-white/10"
					class:animate-scale-in={mounted}
					style="animation-delay: 0.6s;"
				>
					<div class="text-center max-w-2xl mx-auto">
						<div
							class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center animate-float"
						>
							<svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M13 10V3L4 14h7v7l9-11h-7z"
								/>
							</svg>
						</div>
						<h3 class="gradient-text text-3xl font-black mb-4">You're All Set!</h3>
						<p class="text-gray-400 text-lg mb-8">
							Welcome to Taren. Your account is active and ready to go. This is a protected area that
							only authenticated users can access.
						</p>
						<div class="flex flex-wrap gap-4 justify-center">
							<a href="/" class="gradient-button inline-flex items-center px-6 py-3 rounded-xl">
								<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
									/>
								</svg>
								Go to Home
							</a>
						</div>
					</div>
				</div>
			</main>
		</div>
	</div>
{:else}
	<div class="min-h-screen flex items-center justify-center bg-[#0a0a0f]">
		<div class="text-center">
			<div class="spinner mx-auto mb-4"></div>
			<p class="text-gray-400">Loading...</p>
		</div>
	</div>
{/if}

<style>
	:global(.glass-button) {
		background: rgba(255, 255, 255, 0.05) !important;
		border: 1px solid rgba(255, 255, 255, 0.1) !important;
		color: white !important;
		transition: all 0.3s ease;
	}

	:global(.glass-button:hover) {
		background: rgba(255, 255, 255, 0.1) !important;
		border-color: rgba(236, 72, 153, 0.5) !important;
	}

	.badge-active {
		display: inline-block;
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 500;
		background-color: rgba(16, 185, 129, 0.1);
		color: #10b981;
		border: 1px solid rgba(16, 185, 129, 0.2);
	}

	:global(.gradient-button) {
		background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%) !important;
		border: none !important;
		color: white;
		font-weight: 600;
		transition: all 0.3s ease;
		text-decoration: none;
	}

	:global(.gradient-button:hover) {
		transform: translateY(-2px);
		box-shadow: 0 20px 40px -15px rgba(236, 72, 153, 0.4);
	}

	.spinner {
		width: 2rem;
		height: 2rem;
		border: 3px solid rgba(255, 255, 255, 0.1);
		border-top-color: #ec4899;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
