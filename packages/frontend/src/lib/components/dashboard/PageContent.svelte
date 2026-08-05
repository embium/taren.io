<script lang="ts">
	import { twMerge } from 'tailwind-merge';

	let { children, class: className = '' } = $props();
</script>

<div class={twMerge("flex-1 overflow-y-auto px-4 py-5 sm:px-6 md:px-8 md:py-6", className)}>
	{@render children?.()}
</div>
