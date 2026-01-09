<script lang="ts">
	import { removeToast, getToasts } from '$lib/stores/toast.svelte';

	const toastsState = getToasts();
</script>

<div class="toast-container" role="region" aria-label="Notifications">
	{#each toastsState.all as toast (toast.id)}
		<div
			class="toast toast-{toast.type}"
			role="alert"
			aria-live="polite"
			aria-atomic="true"
		>
			<div class="toast-content">
				<div class="toast-icon">
					{#if toast.type === 'success'}
						✓
					{:else if toast.type === 'error'}
						✕
					{:else if toast.type === 'warning'}
						⚠
					{:else}
						ℹ
					{/if}
				</div>
				<p class="toast-message">{toast.message}</p>
			</div>
			<button
				class="toast-close"
				onclick={() => removeToast(toast.id)}
				aria-label="Close notification"
			>
				×
			</button>
		</div>
	{/each}
</div>

<style>
	.toast-container {
		position: fixed;
		top: 1rem;
		right: 1rem;
		z-index: 9999;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		max-width: 24rem;
	}

	.toast {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		padding: 1rem;
		border-radius: 0.5rem;
		background: white;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
		animation: slide-in 0.3s ease-out;
	}

	@keyframes slide-in {
		from {
			transform: translateX(100%);
			opacity: 0;
		}
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}

	.toast-content {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		flex: 1;
	}

	.toast-icon {
		flex-shrink: 0;
		width: 1.5rem;
		height: 1.5rem;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: bold;
		font-size: 0.875rem;
	}

	.toast-success .toast-icon {
		background-color: #d1fae5;
		color: #065f46;
	}

	.toast-error .toast-icon {
		background-color: #fee2e2;
		color: #991b1b;
	}

	.toast-warning .toast-icon {
		background-color: #fef3c7;
		color: #92400e;
	}

	.toast-info .toast-icon {
		background-color: #dbeafe;
		color: #1e40af;
	}

	.toast-message {
		margin: 0;
		font-size: 0.875rem;
		color: #374151;
		line-height: 1.5;
	}

	.toast-close {
		flex-shrink: 0;
		background: none;
		border: none;
		font-size: 1.5rem;
		line-height: 1;
		color: #9ca3af;
		cursor: pointer;
		padding: 0;
		width: 1.5rem;
		height: 1.5rem;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: color 0.2s;
	}

	.toast-close:hover {
		color: #4b5563;
	}

	@media (max-width: 640px) {
		.toast-container {
			left: 1rem;
			right: 1rem;
			max-width: none;
		}
	}
</style>
