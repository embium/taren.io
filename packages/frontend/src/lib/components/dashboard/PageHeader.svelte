<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		title,
		actions,
		children,
		class: className = ''
	}: { title: string; actions?: Snippet; children?: Snippet; class?: string } = $props();
</script>

<div
	class="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-4 sm:px-6 md:px-8 md:py-5 {className}"
>
	<div class="flex items-center gap-3">
		<h1 class="text-lg font-semibold">{title}</h1>
		{@render children?.()}
	</div>
	{#if actions}
		<div class="flex items-center gap-2">
			{@render actions()}
		</div>
	{/if}
</div>
