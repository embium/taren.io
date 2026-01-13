<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from "svelte-sonner";
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/button/button.svelte';
	import { getAuthState, logout, initializeAuth } from '$lib/stores/auth.svelte';

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
<nav class="navbar">
	<div class="nav-container">
		<!-- Logo -->
		<a href="/" class="logo-link">
			<span class="text-2xl font-bold text-[#fafafa]">Taren</span>
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
						class="border-[#262626] bg-transparent text-[#fafafa] hover:bg-[#1a1a1a] hover:text-[#fafafa]"
						onclick={() => navigateTo('/dashboard')}
					>
						Dashboard
					</Button>
					<Button
						variant="outline"
						size="sm"
						class="border-[#262626] bg-transparent text-[#fafafa] hover:bg-[#1a1a1a] hover:text-[#fafafa]"
						onclick={handleLogout}
					>
						Log Out
					</Button>
				</div>
			{:else}
				<!-- Guest Links -->
				<div class="auth-links">
					<Button
						variant="ghost"
						size="sm"
						class="text-[#a3a3a3] hover:text-[#fafafa] hover:bg-transparent"
						onclick={() => navigateTo('/login')}
					>
						Sign In
					</Button>
					<Button
						size="sm"
						class="bg-[#3b82f6] hover:bg-[#2563eb] text-white"
						onclick={() => navigateTo('/register')}
					>
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
		<div class="mobile-menu">
			{#if authState.isAuthenticated && authState.user}
				<div class="mobile-menu-content">
					<p class="mobile-user-email">{authState.user.email}</p>
					<Button
						class="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-white mb-2"
						onclick={() => navigateTo('/dashboard')}
					>
						Dashboard
					</Button>
					<Button
						variant="outline"
						class="w-full border-[#262626] bg-transparent text-[#fafafa] hover:bg-[#1a1a1a] hover:text-[#fafafa]"
						onclick={handleLogout}
					>
						Log Out
					</Button>
				</div>
			{:else}
				<div class="mobile-menu-content">
					<Button
						variant="outline"
						class="w-full border-[#262626] bg-transparent text-[#fafafa] hover:bg-[#1a1a1a] hover:text-[#fafafa] mb-3"
						onclick={() => navigateTo('/login')}
					>
						Sign In
					</Button>
					<Button
						class="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-white"
						onclick={() => navigateTo('/register')}
					>
						Get Started
					</Button>
				</div>
			{/if}
		</div>
	{/if}
</nav>

<style>
	.navbar {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 50;
		background: #0a0a0a;
		border-bottom: 1px solid #262626;
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
		opacity: 0.7;
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
		color: #737373;
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
		color: #fafafa;
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
		border-top: 1px solid #262626;
		padding: 1rem 1.5rem;
		background: #0a0a0a;
	}

	.mobile-menu-content {
		max-width: 400px;
		margin: 0 auto;
	}

	.mobile-user-email {
		color: #737373;
		font-size: 0.875rem;
		margin-bottom: 1rem;
		text-align: center;
	}
</style>
