<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import { getAuthState, initializeAuth } from '$lib/stores/auth.svelte';
	import UserMenu from '$lib/components/UserMenu.svelte';
	import type { LayoutData } from './$types';

	let { children, data }: { children: any, data: LayoutData } = $props();
</script>

{#if data.user}
	<div class="min-h-screen bg-white dark:bg-[#0a0a0a]">
		<!-- Shared Header/Navigation -->
		<header class="border-b border-gray-200 dark:border-[#262626] bg-white dark:bg-[#0a0a0a]">
			<div class="px-6 py-4 flex justify-between items-center">
				<h1 class="text-2xl font-bold text-gray-900 dark:text-[#fafafa]">Taren</h1>
				<UserMenu user={data.user} />
			</div>
		</header>

		<!-- Page Content -->
		{@render children()}
	</div>
{/if}
