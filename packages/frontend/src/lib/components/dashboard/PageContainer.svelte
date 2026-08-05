<script lang="ts">
	let { children, class: className = '' } = $props();
</script>

<div class="flex h-full flex-col {className}">
	{@render children?.()}
</div>
