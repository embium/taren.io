<script lang="ts">
	import { Copy, Check } from '@lucide/svelte';
	import { toast } from "svelte-sonner";
	import { goto } from '$app/navigation';
	import { getAuthState, updateUser } from '$lib/stores/auth.svelte';
	import { settingsApi } from '$lib/api/settings.api';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	
	const authState = getAuthState();
	
	// Reactive state
	let displayName = $state(authState.user?.name || '');
	let avatarPreview = $state<string | null>(authState.user?.avatar || null);
	let isSavingName = $state(false);
	let isCopied = $state(false);
	let showDeleteDialog = $state(false);
	let deletePassword = $state('');
	let isDeleting = $state(false);
	let avatarInput: HTMLInputElement | null = $state(null);
	
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
		if (!authState.user?.id) return;
		
		try {
			await navigator.clipboard.writeText(authState.user.id);
			isCopied = true;
			toast.success('User ID copied to clipboard');
			setTimeout(() => {
				isCopied = false;
			}, 2000);
		} catch (error) {
			toast.error('Failed to copy');
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
<div class="max-w-7xl mx-auto px-6 py-8">
	<h1 class="text-2xl font-bold text-gray-900 dark:text-[#fafafa] mb-8">Account Settings</h1>
	
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

						<!-- Content Area -->
			<main class="flex-1 max-w-3xl space-y-6">
				<!-- Avatar Section -->
			<div class="settings-card">
				<div class="card-content">
					<div class="flex items-start justify-between gap-6">
						<div class="flex-1">
							<h2 class="section-title">Avatar</h2>
							<p class="section-description">This is your avatar.<br/>Click on the avatar to upload a custom one from your files.</p>
						</div>
						
						<button
							class="avatar-container shrink-0"
							onclick={() => avatarInput?.click()}
							aria-label="Upload avatar"
						>
							{#if avatarPreview}
								<img src={avatarPreview} alt="Avatar" class="avatar-image" />
							{:else}
								<div class="avatar-placeholder">
									<span class="text-2xl font-bold">{authState.user?.name?.[0]?.toUpperCase() || authState.user?.email[0].toUpperCase()}</span>
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
					/>
					</div>
					
					<div class="card-footer">
						<p class="text-xs text-muted-foreground">
							An avatar is optional but strongly recommended.
						</p>
					</div>
				</div>

				<!-- Display Name Section -->
				<div class="settings-card">
					<div class="card-content">
						<h2 class="section-title">Display Name</h2>
						<p class="section-description">Please enter your full name, or a display name you are comfortable with.</p>
						
						<Input
							bind:value={displayName}
							maxlength={32}
							placeholder="Michael Mooney"
							type="text"
							class="max-w-md mt-4"
						/>
					</div>
					
					<div class="card-footer flex items-center justify-between">
						<p class="text-xs text-muted-foreground">
							Please use 32 characters at maximum.
						</p>
						<Button
							size="sm"
							disabled={isSavingName}
							onclick={handleSaveName}
						>
							{isSavingName ? 'Saving...' : 'Save'}
						</Button>
					</div>
				</div>

				<!-- Email Section -->
				<div class="settings-card">
					<div class="card-content">
						<h2 class="section-title">Email</h2>
						<p class="section-description">Enter the email address you use to sign in to Taren. Your primary email will be used for account-related notifications.</p>
						
						<div class="flex items-center gap-3 mt-4">
							<div class="email-badge">{authState.user?.email}</div>
							<span class="badge-verified">Verified</span>
							<span class="badge-primary">Primary</span>
						</div>
					</div>
					
					<div class="card-footer">
						<p class="text-xs text-muted-foreground">
							Emails that can be used to sign in to your account will be marked as verified.
						</p>
					</div>
				</div>

				<!-- User ID Section -->
				<div class="settings-card">
					<div class="card-content">
						<h2 class="section-title">User ID</h2>
						<p class="section-description">This is your user ID within Taren.</p>
						
						<div class="flex items-center gap-3 mt-4">
							<code class="user-id">{authState.user?.id}</code>
							<Button
								variant="outline"
								size="sm"
								onclick={copyUserId}
								aria-label="Copy user ID"
								class="h-8 w-8 p-0"
							>
								{#if isCopied}
									<Check class="w-4 h-4" />
								{:else}
									<Copy class="w-4 h-4" />
								{/if}
							</Button>
						</div>
					</div>
					
					<div class="card-footer">
						<p class="text-xs text-muted-foreground">
							Used when interacting with the Taren API.
						</p>
					</div>
				</div>

				<!-- Delete Account Section -->
				<div class="settings-card border-destructive/50">
					<div class="card-content">
						<h2 class="section-title text-destructive">Delete Account</h2>
						<p class="section-description">Permanently deactivate your Taren Account and remove access to all files.</p>
					</div>
					
					<div class="card-footer flex items-center justify-between">
						<p class="text-xs text-muted-foreground">
							This action is not reversible, so please continue with caution.
						</p>
						<Button
							variant="destructive"
							size="sm"
							onclick={() => (showDeleteDialog = true)}
						>
							Delete Personal Account
						</Button>
					</div>
				</div>
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
			<div 
				class="modal-content" 
				role="document"
			>
				<h3 class="text-lg font-semibold mb-2">Delete Account</h3>
				<p class="text-sm text-muted-foreground mb-4">
					This will permanently deactivate your account. You will not be able to log in again. Are you sure?
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
				
				<div class="flex gap-3 mt-6 justify-end">
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
					<Button
						variant="destructive"
						disabled={isDeleting}
						onclick={handleDeleteAccount}
					>
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
		color: #737373;
		background: transparent;
		border: none;
		border-radius: 0.375rem;
		cursor: pointer;
		transition: all 0.15s;
	}
	
	.nav-item:hover:not(.disabled) {
		background: #171717;
		color: #fafafa;
	}
	
	.nav-item.active {
		background: #171717;
		color: #fafafa;
		font-weight: 500;
	}
	
	.nav-item.disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
	
	.settings-card {
		background: #0a0a0a;
		border: 1px solid #262626;
		border-radius: 0.5rem;
		overflow: hidden;
	}
	
	.card-content {
		padding: 1.5rem;
	}
	
	.card-footer {
		padding: 1rem 1.5rem;
		background: rgba(23, 23, 23, 0.5);
		border-top: 1px solid #262626;
	}
	
	.section-title {
		font-size: 0.875rem;
		font-weight: 600;
		color: #fafafa;
		margin-bottom: 0.5rem;
	}
	
	.section-description {
		font-size: 0.875rem;
		color: #737373;
		line-height: 1.5;
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
		background: #171717;
		border: 1px solid #262626;
		border-radius: 0.375rem;
		color: #fafafa;
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
		background: #171717;
		border: 1px solid #262626;
		border-radius: 0.375rem;
		color: #a3a3a3;
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
		background: #0a0a0a;
		border: 1px solid #262626;
		border-radius: 0.5rem;
		padding: 1.5rem;
		max-width: 28rem;
		width: 90%;
	}
</style>
