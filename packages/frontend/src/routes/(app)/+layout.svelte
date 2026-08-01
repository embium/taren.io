<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { getAuthState, initializeAuth } from '$lib/stores/auth.svelte';
	import DashboardSidebar from '$lib/components/DashboardSidebar.svelte';

	let { children } = $props();

	const authState = getAuthState();
	let isValidating = $state(true);

	onMount(async () => {
		await initializeAuth();
		isValidating = false;

		if (!authState.isAuthenticated) {
			toast.error('Session expired. Please log in again.');
			goto('/login');
		}
	});

	$effect(() => {
		if (!isValidating && !authState.isAuthenticated) {
			toast.error('Your session has expired. Please log in again.');
			goto('/login');
		}
	});
</script>

{#if isValidating}
	<div class="flex h-screen items-center justify-center bg-background">
		<div class="text-muted-foreground">Loading…</div>
	</div>
{:else if authState.isAuthenticated && authState.user}
	<div class="flex flex-row h-screen overflow-hidden bg-background">
		<!-- Sidebar — always visible on desktop, off-canvas on mobile -->
		<DashboardSidebar />

		<!-- Content area — offset top on mobile for the fixed header bar -->
		<div class="flex flex-col flex-1 min-w-0 overflow-hidden pt-14 md:pt-0">
			<main class="flex-1 overflow-hidden">
				{@render children()}
			</main>
		</div>
	</div>
{/if}
