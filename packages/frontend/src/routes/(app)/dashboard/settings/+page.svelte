<script lang="ts">
	import { Copy, Check } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { getAuthState, updateUser } from '$lib/stores/auth.svelte';
	import { settingsApi } from '$lib/api/settings.api';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { setMode, mode } from 'mode-watcher';
	import PageContainer from '$lib/components/dashboard/PageContainer.svelte';
	import PageHeader from '$lib/components/dashboard/PageHeader.svelte';
	import PageContent from '$lib/components/dashboard/PageContent.svelte';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import * as Card from '$lib/components/ui/card';
	import * as Dialog from '$lib/components/ui/dialog';

	const authState = getAuthState();

	let displayName = $state(authState.user?.name || '');
	let avatarPreview = $state<string | null>(authState.user?.avatar || null);
	let isSavingName = $state(false);
	let isSavingUsername = $state(false);
	let isCopied = $state(false);
	let showDeleteDialog = $state(false);
	let deletePassword = $state('');
	let isDeleting = $state(false);
	let avatarInput: HTMLInputElement | null = $state(null);
	let username = $state(authState.user?.username || '');

	async function handleAvatarUpload(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;
		if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
			toast.error('Please upload a JPG, PNG, or WebP image');
			return;
		}
		if (file.size > 1024 * 1024) {
			toast.error('Image must be less than 1MB');
			return;
		}
		const reader = new FileReader();
		reader.onload = async (e) => {
			const base64 = e.target?.result as string;
			avatarPreview = base64;
			try {
				await settingsApi.updateProfile({ avatar: base64 });
				updateUser({ avatar: base64 });
				toast.success('Avatar updated');
			} catch {
				toast.error('Failed to upload avatar');
				avatarPreview = authState.user?.avatar || null;
			}
		};
		reader.readAsDataURL(file);
	}

	async function handleSaveName() {
		if (!displayName.trim()) {
			toast.error('Display name cannot be empty');
			return;
		}
		if (displayName.length > 32) {
			toast.error('Display name must be 32 characters or less');
			return;
		}
		isSavingName = true;
		try {
			await settingsApi.updateProfile({ name: displayName });
			updateUser({ name: displayName });
			toast.success('Display name updated');
		} catch {
			toast.error('Failed to update display name');
		} finally {
			isSavingName = false;
		}
	}

	async function copyUserId() {
		if (!authState.user?.id) return;
		try {
			await navigator.clipboard.writeText(authState.user.id);
			isCopied = true;
			toast.success('User ID copied');
			setTimeout(() => {
				isCopied = false;
			}, 2000);
		} catch {
			toast.error('Failed to copy');
		}
	}

	async function handleSaveUsername() {
		if (!username.trim()) {
			toast.error('Username cannot be empty');
			return;
		}
		if (username.length < 3 || username.length > 30) {
			toast.error('Username must be between 3 and 30 characters');
			return;
		}
		isSavingUsername = true;
		try {
			await settingsApi.updateProfile({ username });
			updateUser({ username });
			toast.success('Username updated');
		} catch (error: any) {
			toast.error(error?.message || error?.detail || 'Failed to update username');
		} finally {
			isSavingUsername = false;
		}
	}

	async function handleDeleteAccount() {
		if (!deletePassword.trim()) {
			toast.error('Please enter your password');
			return;
		}
		isDeleting = true;
		try {
			await settingsApi.deleteAccount({ password: deletePassword });
			toast.success('Account deactivated');
			goto('/login');
		} catch {
			toast.error('Failed. Please check your password.');
		} finally {
			isDeleting = false;
		}
	}

	const initials = $derived(() => {
		return (
			authState.user?.name?.[0]?.toUpperCase() || authState.user?.email?.[0]?.toUpperCase() || '?'
		);
	});
</script>

<svelte:head>
	<title>Settings — Taren</title>
</svelte:head>

<PageContainer>
	<PageHeader title="Settings" />

	<PageContent>
		{#if !authState.user}
			<div class="mb-8">
				<Skeleton class="mb-2 h-8 w-48" />
				<Skeleton class="h-4 w-64" />
			</div>
			<div class="max-w-2xl space-y-4">
				{#each [1, 2, 3, 4] as _}
					<Card.Root>
						<div class="border-b border-border px-5 py-3">
							<Skeleton class="h-4 w-24" />
						</div>
						<div class="px-5 py-5">
							<Skeleton class="h-10 w-full" />
						</div>
					</Card.Root>
				{/each}
			</div>
		{:else}
		<div class="mb-8">
			<h2 class="text-2xl font-bold">Account Settings</h2>
			<p class="mt-1 text-muted-foreground">
				Manage your profile, username, and account preferences.
			</p>
		</div>

		<div class="max-w-2xl space-y-4">
			<!-- Avatar -->
				<Card.Root>
					<div class="items-center justify-between border-b border-border px-5 py-3">
					<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">Avatar</p>
					</div>
				<div class="gap-4">
					<div class="flex items-center gap-4 px-5 py-5">
					<button
						onclick={() => avatarInput?.click()}
						aria-label="Upload avatar"
						class="relative h-16 w-16 shrink-0 overflow-hidden rounded-full border-2 border-border transition hover:border-orange-500 hover:opacity-90"
					>
						{#if avatarPreview}
							<img src={avatarPreview} alt="Avatar" class="h-full w-full object-cover" />
						{:else}
							<div
								class="flex h-full w-full items-center justify-center text-2xl font-bold"
								style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;"
							>
								{initials()}
							</div>
						{/if}
					</button>
					<div>
						<p class="text-sm font-medium">{authState.user?.name ?? 'User'}</p>
						<p class="text-xs text-muted-foreground">{authState.user?.email ?? ''}</p>
					</div>
					</div>
					<p class="border-t border-border py-3 px-5 text-sm text-muted-foreground bg-muted/20 rounded-b-xl">
						Click to upload a custom image (JPG, PNG, or WebP · max 1MB).
					</p>
				</div>
				<input
					bind:this={avatarInput}
					accept="image/jpeg,image/png,image/webp"
					onchange={handleAvatarUpload}
					type="file"
					class="hidden"
					aria-label="Upload avatar file"
				/>
			</Card.Root>

			<!-- Display Name -->

			
			<Card.Root>
				<div class="flex items-center justify-between border-b border-border px-5 py-3">
					<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">Display Name</p>
					<Button
						size="sm"
						variant="outline"
						disabled={isSavingName}
						onclick={handleSaveName}
						class="shrink-0"
					>
						{isSavingName ? 'Saving…' : 'Save'}
					</Button>
				</div>
				<div class="gap-4">
					<div class="px-5 py-5">
						<Input bind:value={displayName} maxlength={32} placeholder="Your name" type="text" />
					</div>
					<p class="border-t border-border py-3 px-5 text-sm text-muted-foreground bg-muted/20 rounded-b-xl">
						Your public name shown across Taren. Max 32 characters.
					</p>
				</div>
			</Card.Root>

			<!-- Username
			<div class="rounded-xl border border-border bg-card p-5">
				<div class="mb-4 flex items-start justify-between gap-4">
					<div>
						<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
							Username
						</p>
						<p class="text-sm text-muted-foreground">
							Alphanumeric, underscore, and hyphen only. 3–30 characters.
						</p>
					</div>
					<Button
						size="sm"
						variant="outline"
						disabled={isSavingUsername}
						onclick={handleSaveUsername}
						class="shrink-0"
					>
						{isSavingUsername ? 'Saving…' : 'Save'}
					</Button>
				</div>
				<Input bind:value={username} maxlength={30} placeholder="your_username" type="text" />
			</div>
			-->

			<!-- Email -->
			<Card.Root>
				<div class="flex items-center justify-between border-b border-border px-5 py-3">
					<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">Email Address</p>
				</div>
				<div class="gap-4">
					<div class="flex items-center gap-3 px-5 py-5">
						<div
							class="flex-1 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm font-medium"
						>
							{authState.user?.email}
						</div>
						<span
							class="inline-flex items-center rounded-full border border-emerald-600 bg-emerald-600/20 px-2.5 py-0.5 text-xs font-medium text-emerald-500"
							>Verified</span
						>
					</div>
					<p class="border-t border-border py-3 px-5 text-sm text-muted-foreground bg-muted/20 rounded-b-xl">
						The email you use to sign in to Taren.
					</p>
				</div>
			</Card.Root>

			<!-- User ID
			<div class="rounded-xl border border-border bg-card p-5">
				<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
					User ID
				</p>
				<p class="mb-4 text-sm text-muted-foreground">Your unique identifier for the Taren API.</p>
				<div class="flex items-center gap-3">
					<code
						class="flex-1 rounded-lg border border-border bg-secondary/30 px-3 py-2 font-mono text-sm break-all text-muted-foreground"
					>
						{authState.user?.id}
					</code>
					<Button
						variant="outline"
						size="sm"
						onclick={copyUserId}
						aria-label="Copy user ID"
						class="h-9 w-9 shrink-0 p-0"
					>
						{#if isCopied}<Check class="h-4 w-4" />{:else}<Copy class="h-4 w-4" />{/if}
					</Button>
				</div>
			</div>
			-->

			<!-- Danger Zone -->
			<Card.Root class="border-red-500/30">
				<div class="flex items-center justify-between border-b border-red-500/30 px-5 py-3">
					<p class="text-xs font-medium tracking-wide text-red-400 uppercase">Danger Zone</p>
					<Button
						variant="destructive"
						size="sm"
						onclick={() => (showDeleteDialog = true)}
						class="shrink-0"
					>
						Delete Account
					</Button>
				</div>
				<div class="gap-4">
					<p class="border-t border-red-500/30 py-3 px-5 text-sm text-muted-foreground bg-red-500/5 rounded-b-xl">
						Permanently deactivate your account. This action cannot be undone.
					</p>
				</div>
			</Card.Root>
		</div>
		<div class="mt-8 mb-8">
			<h2 class="text-2xl font-bold">Appearance Settings</h2>
			<p class="mt-1 text-muted-foreground">Manage your appearance preferences.</p>
		</div>
		<div class="max-w-2xl space-y-4">
			<Card.Root>
				<div class="flex items-center justify-between border-b border-border px-5 py-3">
					<p class="text-xs font-medium tracking-wide text-muted-foreground uppercase">Theme</p>
				</div>
				<div class="gap-4">
					<div class="grid grid-cols-2 gap-2 px-5 py-5">
					{#each ['light', 'dark'] as t}
						<Button
							onclick={() => setMode(t as any)}
							class="flex flex-col items-center gap-2 rounded-lg border border-border p-3 text-sm font-medium capitalize transition-colors hover:bg-accent {mode ==
							null
								? ''
								: (mode as any) === t || (mode as any).current === t
									? 'text-bg border-primary bg-accent'
									: 'text-muted'}"
						>
							{t}
						</Button>
					{/each}
					</div>
					<p class="border-t border-border py-3 px-5 text-sm text-muted-foreground bg-muted/20 rounded-b-xl">
						Update your theme.
					</p>
				</div>
			</Card.Root>
		</div>
		{/if}
	</PageContent>
</PageContainer>

<!-- Delete Confirmation Dialog -->
<Dialog.Root bind:open={showDeleteDialog}>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>Delete Account</Dialog.Title>
			<Dialog.Description>
				This will permanently deactivate your account. You will not be able to log in again.
			</Dialog.Description>
		</Dialog.Header>
		<div class="grid gap-4 py-4">
			<div class="grid gap-2">
				<Label for="delete-password">Enter your password to confirm</Label>
				<Input
					bind:value={deletePassword}
					id="delete-password"
					placeholder="Password"
					type="password"
				/>
			</div>
		</div>
		<Dialog.Footer>
			<Button
				variant="outline"
				disabled={isDeleting}
				onclick={() => {
					showDeleteDialog = false;
					deletePassword = '';
				}}
			>
				Cancel
			</Button>
			<Button variant="destructive" disabled={isDeleting} onclick={handleDeleteAccount}>
				{isDeleting ? 'Deleting…' : 'Delete Account'}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
