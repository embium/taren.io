<script lang="ts">
	import { getAuthState } from '$lib/stores/auth.svelte';
	import { toast } from 'svelte-sonner';

	const authState = getAuthState();
</script>

<svelte:head>
	<title>Dashboard - Taren</title>
</svelte:head>

{#if authState.isAuthenticated && authState.user && authState.user.is_email_verified}
	<!-- Main Content -->
	<main class="mx-auto max-w-7xl px-6 py-12">
		<div class="mb-12">
			<h2 class="mb-2 text-4xl font-bold text-gray-900 dark:text-[#fafafa]">
				Welcome back, {authState.user.name || authState.user.email.split('@')[0]}
			</h2>
			<p class="text-lg text-gray-500 dark:text-[#737373]">Here's your account overview</p>
		</div>

		<!-- Stats Grid -->
		<div class="mb-12 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
			<div
				class="rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-[#262626] dark:bg-[#171717]"
			>
				<div class="mb-4 flex items-center justify-between">
					<div
						class="flex h-12 w-12 items-center justify-center rounded-lg bg-gray-900 dark:bg-[#fafafa]"
					>
						<svg
							class="h-6 w-6 text-white dark:text-[#0a0a0a]"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
							/>
						</svg>
					</div>
					<span
						class="rounded-full border border-green-600 bg-green-600/30 px-3 py-1 text-xs font-medium text-green-600"
						>Active</span
					>
				</div>
				<h3 class="mb-1 text-sm font-medium text-gray-500 dark:text-[#737373]">Account Status</h3>
				<p class="text-2xl font-bold text-gray-900 dark:text-[#fafafa]">
					{authState.user.is_email_verified ? 'Verified' : 'Not Verified'}
				</p>
			</div>

			<div
				class="rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-[#262626] dark:bg-[#171717]"
			>
				<div class="mb-4 flex items-center justify-between">
					<div class="flex h-12 w-12 items-center justify-center rounded-lg bg-[#fafafa]">
						<svg
							class="h-6 w-6 text-[#0a0a0a]"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
							/>
						</svg>
					</div>
				</div>
				<h3 class="mb-1 text-sm font-medium text-gray-500 dark:text-[#737373]">Email</h3>
				<p class="truncate text-lg font-semibold text-gray-900 dark:text-[#fafafa]">
					{authState.user.email}
				</p>
			</div>

			<div
				class="rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-[#262626] dark:bg-[#171717]"
			>
				<div class="mb-4 flex items-center justify-between">
					<div class="flex h-12 w-12 items-center justify-center rounded-lg bg-[#fafafa]">
						<svg
							class="h-6 w-6 text-[#0a0a0a]"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
							/>
						</svg>
					</div>
				</div>
				<h3 class="mb-1 text-sm font-medium text-gray-500 dark:text-[#737373]">Member Since</h3>
				<p class="text-lg font-semibold text-gray-900 dark:text-[#fafafa]">
					{new Date(authState.user.created_at).toLocaleDateString('en-US', {
						month: 'short',
						year: 'numeric'
					})}
				</p>
			</div>

			<div
				class="rounded-lg border border-gray-200 bg-gray-50 p-6 dark:border-[#262626] dark:bg-[#171717]"
			>
				<div class="mb-4 flex items-center justify-between">
					<div class="flex h-12 w-12 items-center justify-center rounded-lg bg-[#fafafa]">
						<svg
							class="h-6 w-6 text-[#0a0a0a]"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
							/>
						</svg>
					</div>
				</div>
				<h3 class="mb-1 text-sm font-medium text-gray-500 dark:text-[#737373]">User ID</h3>
				<p class="truncate font-mono text-sm text-gray-900 dark:text-[#fafafa]">
					{authState.user.id}
				</p>
			</div>
		</div>

		<!-- Welcome Card -->
		<div
			class="rounded-lg border border-gray-200 bg-gray-50 p-12 dark:border-[#262626] dark:bg-[#171717]"
		>
			<div class="mx-auto max-w-2xl text-center">
				<div
					class="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-lg bg-[#3b82f6]"
				>
					<svg class="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M13 10V3L4 14h7v7l9-11h-7z"
						/>
					</svg>
				</div>
				<h3 class="mb-4 text-2xl font-bold text-gray-900 dark:text-[#fafafa]">You're All Set!</h3>
				<p class="mb-8 text-gray-500 dark:text-[#737373]">
					Welcome to Taren. Your account is active and ready to go. This is a protected area that
					only authenticated users can access.
				</p>
				<a
					href="/"
					class="inline-flex items-center rounded-lg bg-[#3b82f6] px-6 py-3 font-semibold text-white transition-colors hover:bg-[#2563eb]"
				>
					<svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
						/>
					</svg>
					Go to Home
				</a>
			</div>
		</div>
	</main>
{:else if authState.user && !authState.user.is_email_verified}
	<!-- Email Verification Reminder -->
	<main class="mx-auto max-w-2xl px-6 py-12">
		<div
			class="rounded-lg border border-gray-200 bg-gray-50 p-12 text-center dark:border-[#262626] dark:bg-[#171717]"
		>
			<div
				class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-yellow-500/20"
			>
				<svg
					class="h-10 w-10 text-yellow-600 dark:text-yellow-500"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
					/>
				</svg>
			</div>

			<h2 class="mb-4 text-3xl font-bold text-gray-900 dark:text-[#fafafa]">Verify Your Email</h2>

			<p class="mb-6 text-lg text-gray-600 dark:text-[#a3a3a3]">
				Welcome! We've sent a verification email to:
			</p>

			<div
				class="mb-8 inline-block rounded-lg border border-gray-200 bg-white px-6 py-3 dark:border-[#262626] dark:bg-[#0a0a0a]"
			>
				<code class="font-medium text-gray-900 dark:text-[#fafafa]">{authState?.user?.email}</code>
			</div>

			<p class="mb-8 text-gray-600 dark:text-[#a3a3a3]">
				Click the link in the email to verify your account and access all features.
			</p>

			<div class="flex flex-col justify-center gap-4 sm:flex-row">
				<button
					onclick={() => {
						toast.info('Resend feature coming soon!');
					}}
					class="rounded-lg bg-[#3b82f6] px-6 py-3 font-semibold text-white transition-colors hover:bg-[#2563eb]"
				>
					Resend Verification Email
				</button>

				<a
					href="/settings"
					class="rounded-lg border border-gray-300 px-6 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-50 dark:border-[#262626] dark:text-[#a3a3a3] dark:hover:bg-[#171717]"
				>
					Update Email Address
				</a>
			</div>

			<div class="mt-8 border-t border-gray-200 pt-8 dark:border-[#262626]">
				<p class="text-sm text-gray-500 dark:text-[#737373]">
					Didn't receive the email? Check your spam folder or contact support.
				</p>
			</div>
		</div>
	</main>
{:else}
	<div class="flex min-h-screen items-center justify-center bg-white dark:bg-[#0a0a0a]">
		<div class="text-center">
			<div class="spinner mx-auto mb-4"></div>
			<p class="text-gray-500 dark:text-[#737373]">Loading...</p>
		</div>
	</div>
{/if}

<style>
	.spinner {
		width: 2rem;
		height: 2rem;
		border: 3px solid #262626;
		border-top-color: #3b82f6;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
