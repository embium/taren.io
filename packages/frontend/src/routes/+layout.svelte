<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import Toast from '$lib/components/ui/Toast.svelte';
	import { initializeAuth } from '$lib/stores/auth.svelte';
	import { onMount } from 'svelte';

	let { children } = $props();

	// Initialize auth on mount (client-side only)
	onMount(() => {
		initializeAuth();
	});
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<Toast />

{@render children()}

