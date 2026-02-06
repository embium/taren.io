<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { getAuthState, initializeAuth } from '$lib/stores/auth.svelte';
	import UserMenu from '$lib/components/UserMenu.svelte';

	let { children } = $props();

	const authState = getAuthState();
	let isValidating = $state(true);

	onMount(async () => {
		// Ensure auth is initialized and validated
		await initializeAuth();
		isValidating = false;

		// If not authenticated after initialization, redirect to login
		if (!authState.isAuthenticated) {
			toast.error('Session expired. Please log in again.');
			goto('/login');
		}
	});

	// Watch for auth state changes (e.g., token expiration during usage)
	$effect(() => {
		if (!isValidating && !authState.isAuthenticated) {
			toast.error('Your session has expired. Please log in again.');
			goto('/login');
		}
	});
</script>

{#if isValidating}
	<div class="flex min-h-screen items-center justify-center bg-white dark:bg-[#0a0a0a]">
		<div class="text-gray-500 dark:text-[#a3a3a3]">Loading...</div>
	</div>
{:else if authState.isAuthenticated && authState.user}
	<div class="min-h-screen bg-white dark:bg-[#0a0a0a]">
		<!-- Shared Header/Navigation -->
		<header class="border-b border-gray-200 bg-white dark:border-[#262626] dark:bg-[#0a0a0a]">
			<div class="flex items-center justify-between px-6 py-4">
				<h1 class="text-2xl font-bold text-gray-900 dark:text-[#fafafa]">Taren</h1>
				<UserMenu />
			</div>
		</header>

		<!-- Page Content -->
		{@render children()}
	</div>
{/if}
