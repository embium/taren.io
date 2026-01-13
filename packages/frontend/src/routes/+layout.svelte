<script lang="ts">
	import './layout.css';

	import { onMount } from 'svelte';
	import { ModeWatcher } from 'mode-watcher';

	import favicon from '$lib/assets/favicon.svg';
	import { Toaster } from '$lib/components/ui/sonner';
	import { initializeAuth } from '$lib/stores/auth.svelte';

	let { children } = $props();

	// Initialize auth on mount (client-side only)
	onMount(() => {
		initializeAuth();
	});
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<ModeWatcher />
<Toaster />

{@render children()}

