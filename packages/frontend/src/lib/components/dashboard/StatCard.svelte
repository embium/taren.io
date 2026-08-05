<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		title,
		value,
		valueClass = '',
		class: className = '',
		children
	}: { title: string; value: string | number; valueClass?: string; class?: string; children?: Snippet } =
		$props();
</script>

<div
	class="rounded-xl border border-border bg-card p-5 transition-shadow hover:shadow-sm {className}"
>
	<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
		{title}
	</p>
	<p class="text-2xl font-bold {valueClass}">{value}</p>
	{@render children?.()}
</div>
