<script lang="ts">
	import { goto } from '$app/navigation';
	import { authApi } from '$lib/api/auth.api';
	import { storage, STORAGE_KEYS } from '$lib/stores/storage';
	import { setTokens } from '$lib/api/client';

	let statusMessage = $state('Completing sign-in...');
	let failed = $state(false);

	$effect(() => {
		bootstrapSession();
	});

	async function bootstrapSession() {
		try {
			// The browser automatically sends the httpOnly cookies set by the backend.
			// No Bearer token needed — the dependency reads auth from the cookie.
			const user = await authApi.getCurrentUser();

			// Persist user to localStorage so the auth store can restore on next load.
			storage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
			storage.setItem(STORAGE_KEYS.REFRESH_TOKEN, '__cookie__');
			setTokens('', '__cookie__');

			goto('/dashboard', { replaceState: true });
		} catch (err) {
			console.error('OAuth session bootstrap failed:', err);
			statusMessage = 'Sign-in failed. Please try again.';
			failed = true;
			setTimeout(() => goto('/login', { replaceState: true }), 2500);
		}
	}
</script>

<svelte:head>
	<title>Signing in… — Taren</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-[#0a0a0a]">
	<div class="text-center space-y-4">
		{#if !failed}
			<div class="spinner"></div>
		{/if}
		<p class="text-[#737373] text-sm">{statusMessage}</p>
	</div>
</div>

<style>
	.spinner {
		width: 2rem;
		height: 2rem;
		border: 2px solid #262626;
		border-top-color: #3b82f6;
		border-radius: 50%;
		animation: spin 0.7s linear infinite;
		margin: 0 auto;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
