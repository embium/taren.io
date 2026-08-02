<script lang="ts">
	import { onMount } from 'svelte';
	import { beforeNavigate, goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { getAuthState, initializeAuth, fetchCurrentUser } from '$lib/stores/auth.svelte';
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

	// Re-validate session on every client-side navigation within the dashboard.
	// This catches the case where the layout stays mounted (no re-mount = no onMount)
	// but the session has expired in the background.
	beforeNavigate(async ({ cancel, to }) => {
		// Only guard navigations that stay inside the app (dashboard) routes
		if (!to?.route.id?.startsWith('/(app)')) return;

		if (!authState.isAuthenticated) {
			cancel();
			toast.error('Your session has expired. Please log in again.');
			goto('/login');
			return;
		}

		// Proactively verify the session is still alive with the server
		try {
			await fetchCurrentUser();
		} catch {
			// fetchCurrentUser clears auth on 401, the $effect below will redirect
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
