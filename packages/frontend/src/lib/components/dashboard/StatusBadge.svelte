<script lang="ts">
	import { Check, X, RefreshCw, Cpu, Circle } from '@lucide/svelte';

	let { status, class: className = '' }: { status: string; class?: string } = $props();

	let badgeClass = $derived.by(() => {
		switch (status) {
			case 'done':
				return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
			case 'failed':
				return 'bg-red-500/20 text-red-400 border-red-500/30';
			case 'scraping':
			case 'analyzing':
				return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
			default:
				return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
		}
	});

	let Icon = $derived.by(() => {
		switch (status) {
			case 'done':
				return Check;
			case 'failed':
				return X;
			case 'scraping':
				return RefreshCw;
			case 'analyzing':
				return Cpu;
			default:
				return Circle;
		}
	});
</script>

<span
	class="inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium {badgeClass} {className}"
>
	<Icon size={14} class={status === 'scraping' || status === 'analyzing' ? 'animate-spin' : ''} />
	<span class="capitalize">{status}</span>
</span>
