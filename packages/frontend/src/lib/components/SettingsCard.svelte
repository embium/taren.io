<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { cn } from '$lib/utils';

	type Props = {
		title: string;
		description: string;
		footerText: string;
		destructive?: boolean;
		button?: {
			label: string;
			onclick: () => void;
			disabled?: boolean;
		};
		children?: Snippet;
		class?: string;
	};

	let {
		title,
		description,
		footerText,
		destructive = false,
		button,
		children,
		class: className
	}: Props = $props();
</script>

<div
	class={cn(
		'overflow-hidden border rounded-md',
		destructive ? 'border-red-900/50' : 'border-border/50',
		className
	)}
>
	<div class="p-4">
		<h2 class={cn('mb-2 text-foreground', destructive && 'text-red-500')}>
			{title}
		</h2>
		<p class="text-sm text-muted-foreground">{description}</p>
		
		{#if children}
			<div class="mt-4">
				{@render children()}
			</div>
		{/if}
	</div>

	<div
		class={cn(
			'p-3 text-sm flex items-center justify-between',
			destructive ? 'bg-red-900/30' : 'bg-muted/30'
		)}
	>
		<p class="text-muted-foreground">
			{footerText}
		</p>
		
		{#if button}
			<Button
				variant={destructive ? 'destructive' : 'default'}
				size="sm"
				disabled={button.disabled}
				onclick={button.onclick}
			>
				{button.label}
			</Button>
		{/if}
	</div>
</div>
