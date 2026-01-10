<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/button/button.svelte';
	import { getAuthState, logout, initializeAuth } from '$lib/stores/auth.svelte';
	import { toast } from '$lib/stores/toast.svelte';
	import { onMount } from 'svelte';

	const authState = getAuthState();
	let mobileMenuOpen = $state(false);

	onMount(() => {
		initializeAuth();
	});

	async function handleLogout() {
		try {
			await logout();
			toast.success('Logged out successfully');
			mobileMenuOpen = false;
		} catch (error) {
			console.error('Logout error:', error);
			toast.error('Logout failed');
		}
	}

	function navigateTo(path: string) {
		goto(path);
		mobileMenuOpen = false;
	}
</script>

<!-- Navigation Bar -->
<nav class="navbar fixed top-0 left-0 right-0 z-50 border-b border-gray-800">
	<div class="nav-container">
		<!-- Text Logo -->
		<a href="/" class="logo-link">
			<span class="gradient-text text-2xl font-black tracking-tight">Taren</span>
		</a>

		<!-- Desktop Navigation -->
		<div class="nav-links">
			{#if authState.isAuthenticated && authState.user}
				<!-- Authenticated User Menu -->
				<div class="user-menu">
					<span class="user-email">{authState.user.email}</span>
					<Button
						variant="outline"
						size="sm"
						class="glass-button"
						onclick={() => navigateTo('/dashboard')}
					>
						Dashboard
					</Button>
					<Button variant="outline" size="sm" class="glass-button" onclick={handleLogout}>
						Log Out
					</Button>
				</div>
			{:else}
				<!-- Guest Links -->
				<div class="auth-links">
					<Button variant="ghost" size="sm" class="ghost-button" onclick={() => navigateTo('/login')}>
						Sign In
					</Button>
					<Button size="sm" class="gradient-button" onclick={() => navigateTo('/register')}>
						Get Started
					</Button>
				</div>
			{/if}
		</div>

		<!-- Mobile Menu Button -->
		<button
			class="mobile-menu-btn"
			onclick={() => (mobileMenuOpen = !mobileMenuOpen)}
			aria-label="Toggle menu"
		>
			{#if mobileMenuOpen}
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			{:else}
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
				</svg>
			{/if}
		</button>
	</div>

	<!-- Mobile Menu -->
	{#if mobileMenuOpen}
		<div class="mobile-menu glass">
			{#if authState.isAuthenticated && authState.user}
				<div class="mobile-menu-content">
					<p class="mobile-user-email">{authState.user.email}</p>
					<Button class="w-full gradient-button mb-2" onclick={() => navigateTo('/dashboard')}>
						Dashboard
					</Button>
					<Button variant="outline" class="w-full glass-button" onclick={handleLogout}>
						Log Out
					</Button>
				</div>
			{:else}
				<div class="mobile-menu-content">
					<Button class="w-full ghost-button mb-3" onclick={() => navigateTo('/login')}>
						Sign In
					</Button>
					<Button class="w-full gradient-button" onclick={() => navigateTo('/register')}>
						Get Started
					</Button>
				</div>
			{/if}
		</div>
	{/if}
</nav>

<style>
	.navbar {
		backdrop-filter: blur(12px);
		background: rgba(10, 10, 15, 0.8);
	}

	.nav-container {
		max-width: 1400px;
		margin: 0 auto;
		padding: 1rem 1.5rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.logo-link {
		display: flex;
		align-items: center;
		text-decoration: none;
		transition: opacity 0.2s;
	}

	.logo-link:hover {
		opacity: 0.8;
	}

	.nav-links {
		display: none;
	}

	@media (min-width: 768px) {
		.nav-links {
			display: flex;
			align-items: center;
			gap: 1rem;
		}
	}

	.user-menu,
	.auth-links {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.user-email {
		color: #9ca3af;
		font-size: 0.875rem;
		margin-right: 0.5rem;
	}

	.mobile-menu-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0.5rem;
		background: none;
		border: none;
		color: white;
		cursor: pointer;
		transition: opacity 0.2s;
	}

	.mobile-menu-btn:hover {
		opacity: 0.7;
	}

	@media (min-width: 768px) {
		.mobile-menu-btn {
			display: none;
		}
	}

	.mobile-menu {
		border-top: 1px solid rgba(255, 255, 255, 0.05);
		padding: 1rem 1.5rem;
	}

	.mobile-menu-content {
		max-width: 400px;
		margin: 0 auto;
	}

	.mobile-user-email {
		color: #9ca3af;
		font-size: 0.875rem;
		margin-bottom: 1rem;
		text-align: center;
	}

	:global(.glass-button) {
		background: rgba(255, 255, 255, 0.05) !important;
		border: 1px solid rgba(255, 255, 255, 0.1) !important;
		color: white !important;
		transition: all 0.2s;
	}

	:global(.glass-button:hover) {
		background: rgba(255, 255, 255, 0.1) !important;
		border-color: rgba(236, 72, 153, 0.5) !important;
	}

	:global(.ghost-button) {
		background: transparent !important;
		border: none !important;
		color: white !important;
		transition: all 0.2s;
	}

	:global(.ghost-button:hover) {
		background: rgba(255, 255, 255, 0.05) !important;
	}

	:global(.gradient-button) {
		background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%) !important;
		border: none !important;
		color: white !important;
		font-weight: 600;
		transition: all 0.2s;
	}

	:global(.gradient-button:hover) {
		transform: translateY(-1px);
		box-shadow: 0 10px 25px -5px rgba(236, 72, 153, 0.4);
	}
</style>
