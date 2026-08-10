<script lang="ts">
	import type { Snippet } from 'svelte';
	import * as Card from '$lib/components/ui/card';

	let {
		title,
		value,
		valueClass = '',
		class: className = '',
		children
	}: { title: string; value: string | number; valueClass?: string; class?: string; children?: Snippet } =
		$props();
</script>

<Card.Root
	class="p-5 transition-shadow hover:shadow-sm {className}"
>
	<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
		{title}
	</p>
	<p class="text-2xl font-bold {valueClass}">{value}</p>
	{@render children?.()}
</Card.Root>
