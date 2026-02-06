<script lang="ts">
	import { Copy, Check } from '@lucide/svelte';
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { updateUser } from '$lib/stores/auth.svelte';
	import { settingsApi } from '$lib/api/settings.api';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import SettingsCard from './components/SettingsCard.svelte';
	import type { LayoutData } from '../$types';

 	const { data }: { data: LayoutData } = $props();

	// Reactive state
	let displayName = $derived(data.user?.name || '');
	let avatarPreview = $derived<string | null>(data.user?.avatar || null);
	let isSavingName = $state(false);
	let isSavingUsername = $state(false);
	let isCopied = $state(false);
	let showDeleteDialog = $state(false);
	let deletePassword = $state('');
	let isDeleting = $state(false);
	let avatarInput: HTMLInputElement | null = $state(null);
	let username = $derived(data.user?.username || '');

	async function handleAvatarUpload(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];

		if (!file) return;

		// Validate file type
		if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
			toast.error('Please upload a JPG, PNG, or WebP image');
			return;
		}

		// Validate file size (1MB max)
		if (file.size > 1024 * 1024) {
			toast.error('Image must be less than 1MB');
			return;
		}

		// Convert to base64
		const reader = new FileReader();
		reader.onload = async (e) => {
			const base64 = e.target?.result as string;
			avatarPreview = base64;

			try {
				await settingsApi.updateProfile({ avatar: base64 });
				// Update local auth state properly to trigger reactivity
				updateUser({ avatar: base64 });
				toast.success('Avatar updated successfully');
			} catch (error) {
				toast.error('Failed to upload avatar');
				avatarPreview = data.user?.avatar || null;
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
			// Update local auth state properly to trigger reactivity
			updateUser({ name: displayName });
			toast.success('Display name updated');
		} catch (error) {
			toast.error('Failed to update display name');
		} finally {
			isSavingName = false;
		}
	}

	async function copyUserId() {
		if (!data.user?.id) return;

		try {
			await navigator.clipboard.writeText(data.user.id);
			isCopied = true;
			toast.success('User ID copied to clipboard');
			setTimeout(() => {
				isCopied = false;
			}, 2000);
		} catch (error) {
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
			// Update local auth state properly to trigger reactivity
			updateUser({ username });
			toast.success('Username updated');
		} catch (error: any) {
			// Handle specific backend errors (like 30-day restriction)
			if (error?.message) {
				toast.error(error.message);
			} else if (error?.detail) {
				toast.error(error.detail);
			} else {
				toast.error('Failed to update username');
			}
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
			toast.success('Account deactivated successfully');
			goto('/login');
		} catch (error) {
			toast.error('Failed to delete account. Please check your password.');
		} finally {
			isDeleting = false;
		}
	}
</script>

<svelte:head>
	<title>Account Settings - Taren</title>
</svelte:head>

<!-- Main Content -->
<div class="mx-auto max-w-7xl px-6 py-8">
	<h1 class="mb-8 text-2xl font-bold text-gray-900 dark:text-[#fafafa]">Account Settings</h1>

	<div class="flex gap-8">
		<!-- Sidebar Navigation -->
		<aside class="w-64 shrink-0">
			<nav class="space-y-1">
				<button class="nav-item active">General</button>
				<button class="nav-item disabled" disabled>Authentication</button>
				<button class="nav-item disabled" disabled>Sign-out of other logins</button>
				<button class="nav-item disabled" disabled>Billing plans</button>
				<button class="nav-item disabled" disabled>Invoices</button>
				<button class="nav-item disabled text-red-600 dark:text-red-500" disabled>Delete</button>
			</nav>
		</aside>

		<main class="max-w-3xl flex-1 space-y-6">
			<SettingsCard
				title="Avatar"
				description="This is your avatar. Click on the avatar to upload a custom one from your files."
				footerText="An avatar is optional but strongly recommended."
			>
				<div class="flex items-start justify-between gap-6">
					<button
						class="avatar-container shrink-0"
						onclick={() => avatarInput?.click()}
						aria-label="Upload avatar"
					>
						{#if avatarPreview}
							<img src={avatarPreview} alt="Avatar" class="avatar-image" />
						{:else}
							<div class="avatar-placeholder">
								<span class="text-2xl font-bold"
									>{data.user?.name?.[0]?.toUpperCase() ||
										data.user?.email[0].toUpperCase()}</span
								>
							</div>
						{/if}
					</button>
				</div>

				<input
					bind:this={avatarInput}
					accept="image/jpeg,image/png,image/webp"
					onchange={handleAvatarUpload}
					type="file"
					class="hidden"
					aria-label="Upload avatar file"
				/></SettingsCard
			>

			<SettingsCard
				title="Display Name"
				description="Please enter your full name, or a display name you are comfortable with."
				footerText="Please use 32 characters at maximum."
				button={{
					label: isSavingName ? 'Saving...' : 'Save',
					onclick: handleSaveName,
					disabled: isSavingName
				}}
			>
				<Input
					bind:value={displayName}
					maxlength={32}
					placeholder="Michael Mooney"
					type="text"
					class="max-w-md"
				/></SettingsCard
			>

			<SettingsCard
				title="Email"
				description="This is the email address you use to sign in to Taren."
				footerText="Emails that can be used to sign in to your account will be marked as verified."
			>
				<div class="flex items-center gap-3">
					<div class="email-badge">{data.user?.email}</div>
					<span class="badge-verified">Verified</span>
					<span class="badge-primary">Primary</span>
				</div>
			</SettingsCard>

			<SettingsCard
				title="Username"
				description="Please enter your username that you are comfortable with."
				footerText="Please use alphanumeric, underscore, and hyphen characters and a length between 3 and 30 characters"
				button={{
					label: isSavingUsername ? 'Saving...' : 'Save',
					onclick: handleSaveUsername,
					disabled: isSavingUsername
				}}
			>
				<Input
					bind:value={username}
					maxlength={32}
					placeholder="mikey"
					type="text"
					class="max-w-md"
				/></SettingsCard
			>

			<SettingsCard
				title="User ID"
				description="This is your user ID within Taren."
				footerText="Used when interacting with the Taren API."
			>
				<div class="flex items-center gap-3">
					<code class="user-id">{data.user?.id}</code>
					<Button
						variant="outline"
						size="sm"
						onclick={copyUserId}
						aria-label="Copy user ID"
						class="h-8 w-8 p-0"
					>
						{#if isCopied}
							<Check class="h-4 w-4" />
						{:else}
							<Copy class="h-4 w-4" />
						{/if}
					</Button>
				</div>
			</SettingsCard>

			<SettingsCard
				destructive
				title="Delete Account"
				description="Permanently deactivate your Taren Account and remove access to all files."
				footerText="This action is not reversible, so please continue with caution."
				button={{
					label: 'Delete Personal Account',
					onclick: () => (showDeleteDialog = true)
				}}
			/>
		</main>
	</div>
</div>

<!-- Delete Confirmation Dialog -->
{#if showDeleteDialog}
	<div
		class="modal-overlay"
		role="dialog"
		aria-modal="true"
		tabindex="-1"
		onkeydown={(e) => e.key === 'Escape' && (showDeleteDialog = false)}
	>
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<div
			class="modal-overlay-backdrop"
			onclick={() => (showDeleteDialog = false)}
			aria-label="Close dialog"
		></div>
		<div class="modal-content" role="document">
			<h3 class="mb-2 text-lg font-semibold">Delete Account</h3>
			<p class="mb-4 text-sm text-muted-foreground">
				This will permanently deactivate your account. You will not be able to log in again. Are you
				sure?
			</p>

			<div class="space-y-2">
				<Label for="delete-password">Enter your password to confirm</Label>
				<Input
					bind:value={deletePassword}
					id="delete-password"
					placeholder="Password"
					type="password"
				/>
			</div>

			<div class="mt-6 flex justify-end gap-3">
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
					{isDeleting ? 'Deleting...' : 'Delete Account'}
				</Button>
			</div>
		</div>
	</div>
{/if}

<style>
	.nav-item {
		display: block;
		width: 100%;
		text-align: left;
		padding: 0.625rem 0.75rem;
		font-size: 0.875rem;
		color: oklch(var(--muted-foreground));
		background: transparent;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		transition: all 0.15s;
	}

	.nav-item:hover:not(.disabled) {
		background: oklch(var(--accent));
		color: oklch(var(--accent-foreground));
	}

	.nav-item.active {
		background: oklch(var(--accent));
		color: oklch(var(--accent-foreground));
		font-weight: 500;
	}

	.nav-item.disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.avatar-container {
		width: 5rem;
		height: 5rem;
		border-radius: 50%;
		overflow: hidden;
		border: none;
		cursor: pointer;
		transition: transform 0.2s;
	}

	.avatar-container:hover {
		transform: scale(1.05);
	}

	.avatar-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
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

	.email-badge {
		padding: 0.375rem 0.75rem;
		background: var(--muted);
		border: 1px solid var(--border);
		border-radius: 0.375rem;
		color: var(--foreground);
		font-size: 0.875rem;
	}

	.badge-verified,
	.badge-primary {
		padding: 0.25rem 0.5rem;
		font-size: 0.75rem;
		border-radius: 0.25rem;
		font-weight: 500;
	}

	.badge-verified {
		background: #166534;
		color: #86efac;
	}

	.badge-primary {
		background: #1e40af;
		color: #93c5fd;
	}

	.user-id {
		font-family: 'Courier New', monospace;
		font-size: 0.875rem;
		padding: 0.375rem 0.625rem;
		background: var(--muted);
		border: 1px solid var(--border);
		border-radius: 0.375rem;
		color: var(--muted-foreground);
	}

	/* Modal Styles */
	.modal-overlay {
		position: fixed;
		inset: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 50;
	}

	.modal-overlay-backdrop {
		position: absolute;
		inset: 0;
		background: rgba(0, 0, 0, 0.75);
		cursor: pointer;
	}

	.modal-content {
		position: relative;
		z-index: 1;
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: 0.5rem;
		padding: 1.5rem;
		max-width: 28rem;
		width: 90%;
	}
</style>
