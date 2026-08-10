<script lang="ts">
	import './layout.css';

	import { onMount } from 'svelte';
	import { ModeWatcher } from 'mode-watcher';
	import { browser } from '$app/environment';

	import favicon from '$lib/assets/favicon.svg';
	import { Toaster } from '$lib/components/ui/sonner';
	import { initializeAuth } from '$lib/stores/auth.svelte';

	let { children } = $props();

	// Initialize auth on mount (client-side only)
	onMount(async () => {
		await initializeAuth();
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	{#if browser}
    <script async src="https://googletagmanager.com"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-CV8Q86TPGN');
    </script>
	{/if}
</svelte:head>

<ModeWatcher />
<Toaster />

{@render children()}

