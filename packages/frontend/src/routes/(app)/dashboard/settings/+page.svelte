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

<div class="flex h-full flex-col">
	<div
		class="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b border-border px-4 py-4 sm:px-6 md:px-8 md:py-5"
	>
		<h1 class="text-lg font-semibold">Settings</h1>
	</div>

	<div class="flex-1 overflow-y-auto px-4 py-5 sm:px-6 md:px-8 md:py-6">
		<div class="mb-8">
			<h2 class="text-2xl font-bold">Account Settings</h2>
			<p class="mt-1 text-muted-foreground">
				Manage your profile, username, and account preferences.
			</p>
		</div>

		<div class="max-w-2xl space-y-4">
			<!-- Avatar -->
			<div class="rounded-xl border border-border bg-card p-5">
				<div class="mb-4 flex items-center justify-between">
					<div>
						<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
							Avatar
						</p>
						<p class="text-sm text-muted-foreground">
							Click to upload a custom image (JPG, PNG, or WebP · max 1MB).
						</p>
					</div>
				</div>
				<div class="flex items-center gap-4">
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
				<input
					bind:this={avatarInput}
					accept="image/jpeg,image/png,image/webp"
					onchange={handleAvatarUpload}
					type="file"
					class="hidden"
					aria-label="Upload avatar file"
				/>
			</div>

			<!-- Display Name -->
			<div class="rounded-xl border border-border bg-card p-5">
				<div class="mb-4 flex items-start justify-between gap-4">
					<div>
						<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
							Display Name
						</p>
						<p class="text-sm text-muted-foreground">
							Your public name shown across Taren. Max 32 characters.
						</p>
					</div>
					<Button size="sm" disabled={isSavingName} onclick={handleSaveName} class="shrink-0">
						{isSavingName ? 'Saving…' : 'Save'}
					</Button>
				</div>
				<Input bind:value={displayName} maxlength={32} placeholder="Your name" type="text" />
			</div>

			<!-- Username -->
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
						disabled={isSavingUsername}
						onclick={handleSaveUsername}
						class="shrink-0"
					>
						{isSavingUsername ? 'Saving…' : 'Save'}
					</Button>
				</div>
				<Input bind:value={username} maxlength={30} placeholder="your_username" type="text" />
			</div>

			<!-- Email -->
			<div class="rounded-xl border border-border bg-card p-5">
				<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">
					Email Address
				</p>
				<p class="mb-4 text-sm text-muted-foreground">The email you use to sign in to Taren.</p>
				<div class="flex items-center gap-3">
					<div
						class="flex-1 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm font-medium"
					>
						{authState.user?.email}
					</div>
					<span
						class="inline-flex items-center rounded-full border border-emerald-600 bg-emerald-600/20 px-2.5 py-0.5 text-xs font-medium text-emerald-500"
						>Verified</span
					>
					<span
						class="inline-flex items-center rounded-full border border-blue-600/30 bg-blue-500/10 px-2.5 py-0.5 text-xs font-medium text-blue-400"
						>Primary</span
					>
				</div>
			</div>

			<!-- User ID -->
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

			<div class="rounded-xl border border-border bg-card p-5">
				<p class="mb-1 text-xs font-medium tracking-wide text-muted-foreground uppercase">Theme</p>
				<p class="mb-4 text-sm text-muted-foreground">Update your theme.</p>
				<div class="grid grid-cols-2 gap-2">
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
			</div>

			<!-- Danger Zone -->
			<div class="rounded-xl border border-red-500/30 bg-card p-5">
				<div class="flex items-start justify-between gap-4">
					<div>
						<p class="mb-1 text-xs font-medium tracking-wide text-red-400 uppercase">Danger Zone</p>
						<p class="text-sm text-muted-foreground">
							Permanently deactivate your account. This action cannot be undone.
						</p>
					</div>
					<Button
						variant="destructive"
						size="sm"
						onclick={() => (showDeleteDialog = true)}
						class="shrink-0"
					>
						Delete Account
					</Button>
				</div>
			</div>
		</div>
	</div>
</div>

<!-- Delete Confirmation Dialog -->
{#if showDeleteDialog}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center"
		role="dialog"
		aria-modal="true"
		tabindex="-1"
		onkeydown={(e) => e.key === 'Escape' && (showDeleteDialog = false)}
	>
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<div
			class="absolute inset-0 cursor-pointer bg-black/75"
			onclick={() => (showDeleteDialog = false)}
			aria-label="Close dialog"
		></div>
		<div
			class="relative z-10 mx-4 w-full max-w-md rounded-xl border border-border bg-card p-6"
			role="document"
		>
			<h3 class="mb-2 text-lg font-semibold">Delete Account</h3>
			<p class="mb-4 text-sm text-muted-foreground">
				This will permanently deactivate your account. You will not be able to log in again.
			</p>
			<div class="mb-6 space-y-2">
				<Label for="delete-password">Enter your password to confirm</Label>
				<Input
					bind:value={deletePassword}
					id="delete-password"
					placeholder="Password"
					type="password"
				/>
			</div>
			<div class="flex justify-end gap-3">
				<Button
					variant="outline"
					disabled={isDeleting}
					onclick={() => {
						showDeleteDialog = false;
						deletePassword = '';
					}}>Cancel</Button
				>
				<Button variant="destructive" disabled={isDeleting} onclick={handleDeleteAccount}>
					{isDeleting ? 'Deleting…' : 'Delete Account'}
				</Button>
			</div>
		</div>
	</div>
{/if}
