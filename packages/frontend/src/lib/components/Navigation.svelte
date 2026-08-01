<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from "svelte-sonner";
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/button/button.svelte';
	import { getAuthState, logout, initializeAuth } from '$lib/stores/auth.svelte';
	import UserMenu from '$lib/components/UserMenu.svelte';

	const authState = getAuthState();
	let mobileMenuOpen = $state(false);

	onMount(async () => {
		await initializeAuth();
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
<header>
	<div class="px-6 py-4 flex justify-between items-center">
		<h1 class="text-2xl font-bold text-gray-900 dark:text-[#fafafa]">Taren</h1>

		{#if authState.isAuthenticated && authState.user}
			<UserMenu />
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
</header>