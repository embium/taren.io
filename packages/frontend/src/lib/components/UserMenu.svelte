<script lang="ts">
	import type { User } from '$lib/types/auth';
	import { House, LogOut } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';
	import { goto, invalidateAll } from '$app/navigation';
	import { getAuthState } from '$lib/stores/auth.svelte';
	import { logout } from '$lib/stores/auth.svelte';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import ThemeSelector from './ThemeSelector.svelte';
	import { authApi } from '$lib/api/auth.api';

	let { user }: { user: User } = $props();

	let userAvatar = $derived(user?.avatar || null);

	async function handleLogout() {
		try {
			await authApi.logout();
			// Invalidate all load functions to clear locals.user
			await invalidateAll();
			toast.success('Logged out successfully');
			goto('/login');
		} catch (error) {
			console.error('Logout error:', error);
			toast.error('Logout failed');
		}
	}
</script>

{#if user}
	<DropdownMenu.Root>
		<DropdownMenu.Trigger>
			{#snippet child({ props })}
				<button class="avatar-container" {...props}>
					{#if userAvatar}
						<img src={userAvatar} alt="Avatar" class="avatar-image" />
					{:else}
						<div class="avatar-placeholder">
							<span class="text-md font-bold"
								>{user?.name?.[0]?.toUpperCase() || user?.email[0].toUpperCase()}</span
							>
						</div>
					{/if}
				</button>
			{/snippet}
		</DropdownMenu.Trigger>
		<DropdownMenu.Content class="w-64" align="end">
			<div class="mb-1 px-3 py-3">
				<p class="mb-0.5 text-base font-semibold text-gray-900 dark:text-[#fafafa]">
					{user.name || user.email.split('@')[0]}
				</p>
				<p class="truncate text-sm text-gray-500 dark:text-[#737373]">{user.email}</p>
			</div>

			<DropdownMenu.Separator />

			<DropdownMenu.Item>
				<a href="/dashboard" class="flex w-full">Dashboard</a>
			</DropdownMenu.Item>

			<DropdownMenu.Item>
				<a href="/settings" class="flex w-full">Account Settings</a>
			</DropdownMenu.Item>

			<DropdownMenu.Separator />

			<ThemeSelector />

			<DropdownMenu.Separator />

			<DropdownMenu.Item>
				<span class="flex w-full items-center justify-between">
					<a href="/" class="flex w-full">Home Page</a>
					<House />
				</span>
			</DropdownMenu.Item>

			<DropdownMenu.Item onclick={handleLogout}>
				<span class="flex w-full items-center justify-between">
					<span>Log Out</span>
					<LogOut />
				</span>
			</DropdownMenu.Item>
		</DropdownMenu.Content>
	</DropdownMenu.Root>
{/if}

<style>
	.avatar-container {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		overflow: hidden;
		border: none;
		cursor: pointer;
		transition: transform 0.2s;
	}

	.avatar-placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
	}
</style>
