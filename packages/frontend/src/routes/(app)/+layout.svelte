<script lang="ts">
	import { goto } from '$app/navigation';
	import { getAuthState } from '$lib/stores/auth.svelte';
	import UserMenu from './dashboard/components/UserMenu.svelte';

	let { children } = $props();
	
	const authState = getAuthState();
	
	$effect(() => {
		if (!authState.isAuthenticated) {
			goto('/login');
		}
	});
</script>

{#if authState.isAuthenticated && authState.user}
	<div class="min-h-screen bg-white dark:bg-[#0a0a0a]">
		<!-- Shared Header/Navigation -->
		<header class="border-b border-gray-200 dark:border-[#262626] bg-white dark:bg-[#0a0a0a]">
			<div class="px-6 py-4 flex justify-between items-center">
				<h1 class="text-2xl font-bold text-gray-900 dark:text-[#fafafa]">Taren</h1>
				<UserMenu />
			</div>
		</header>

		<!-- Page Content -->
		{@render children()}
	</div>
{/if}
