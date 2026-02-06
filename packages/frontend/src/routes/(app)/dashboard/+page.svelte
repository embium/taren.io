<script lang="ts">
	import type { LayoutData } from '../$types';
	import { toast } from 'svelte-sonner';

	let { data }: { data: LayoutData } = $props();
</script>

<svelte:head>
	<title>Dashboard - Taren</title>
</svelte:head>

{#if data.user && data.user.is_email_verified}
	<!-- Main Content -->
	<main class="max-w-7xl mx-auto px-6 py-12">
		<div class="mb-12">
			<h2 class="text-4xl font-bold text-gray-900 dark:text-[#fafafa] mb-2">
				Welcome back, {data.user.name || data.user.email.split('@')[0]}
			</h2>
			<p class="text-gray-500 dark:text-[#737373] text-lg">Here's your account overview</p>
		</div>

			<!-- Stats Grid -->
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
				<div class="bg-gray-50 dark:bg-[#171717] rounded-lg border border-gray-200 dark:border-[#262626] p-6">
					<div class="flex items-center justify-between mb-4">
						<div class="w-12 h-12 rounded-lg bg-gray-900 dark:bg-[#fafafa] flex items-center justify-center">
							<svg class="w-6 h-6 text-white dark:text-[#0a0a0a]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
								/>
							</svg>
						</div>
						<span class="px-3 py-1 rounded-full text-xs font-medium bg-green-600/30 text-green-600 border border-green-600"
							>Active</span
						>
					</div>
					<h3 class="text-gray-500 dark:text-[#737373] text-sm font-medium mb-1">Account Status</h3>
					<p class="text-gray-900 dark:text-[#fafafa] text-2xl font-bold">{data.user.is_email_verified ? 'Verified' : 'Not Verified'}</p>
				</div>

				<div class="bg-gray-50 dark:bg-[#171717] rounded-lg border border-gray-200 dark:border-[#262626] p-6">
					<div class="flex items-center justify-between mb-4">
						<div class="w-12 h-12 rounded-lg bg-[#fafafa] flex items-center justify-center">
							<svg class="w-6 h-6 text-[#0a0a0a]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
								/>
							</svg>
						</div>
					</div>
					<h3 class="text-gray-500 dark:text-[#737373] text-sm font-medium mb-1">Email</h3>
					<p class="text-gray-900 dark:text-[#fafafa] text-lg font-semibold truncate">{data.user.email}</p>
				</div>

				<div class="bg-gray-50 dark:bg-[#171717] rounded-lg border border-gray-200 dark:border-[#262626] p-6">
					<div class="flex items-center justify-between mb-4">
						<div class="w-12 h-12 rounded-lg bg-[#fafafa] flex items-center justify-center">
							<svg class="w-6 h-6 text-[#0a0a0a]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
								/>
							</svg>
						</div>
					</div>
					<h3 class="text-gray-500 dark:text-[#737373] text-sm font-medium mb-1">Member Since</h3>
					<p class="text-gray-900 dark:text-[#fafafa] text-lg font-semibold">
						{new Date(data.user.created_at).toLocaleDateString('en-US', {
							month: 'short',
							year: 'numeric'
						})}
					</p>
				</div>

				<div class="bg-gray-50 dark:bg-[#171717] rounded-lg border border-gray-200 dark:border-[#262626] p-6">
					<div class="flex items-center justify-between mb-4">
						<div class="w-12 h-12 rounded-lg bg-[#fafafa] flex items-center justify-center">
							<svg class="w-6 h-6 text-[#0a0a0a]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
								/>
							</svg>
						</div>
					</div>
					<h3 class="text-gray-500 dark:text-[#737373] text-sm font-medium mb-1">User ID</h3>
					<p class="text-gray-900 dark:text-[#fafafa] text-sm font-mono truncate">{data.user.id}</p>
				</div>
			</div>

			<!-- Welcome Card -->
			<div class="bg-gray-50 dark:bg-[#171717] rounded-lg border border-gray-200 dark:border-[#262626] p-12">
				<div class="text-center max-w-2xl mx-auto">
					<div class="w-16 h-16 mx-auto mb-6 rounded-lg bg-[#3b82f6] flex items-center justify-center">
						<svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13 10V3L4 14h7v7l9-11h-7z"
							/>
						</svg>
					</div>
					<h3 class="text-2xl font-bold text-gray-900 dark:text-[#fafafa] mb-4">You're All Set!</h3>
					<p class="text-gray-500 dark:text-[#737373] mb-8">
						Welcome to Taren. Your account is active and ready to go. This is a protected area
						that only authenticated users can access.
					</p>
					<a
						href="/"
						class="inline-flex items-center px-6 py-3 rounded-lg bg-[#3b82f6] text-white font-semibold hover:bg-[#2563eb] transition-colors"
					>
						<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
{:else if data.user && !data.user.is_email_verified}
	<!-- Email Verification Reminder -->
	<main class="max-w-2xl mx-auto px-6 py-12">
		<div class="bg-gray-50 dark:bg-[#171717] rounded-lg border border-gray-200 dark:border-[#262626] p-12 text-center">
			<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-yellow-500/20 flex items-center justify-center">
				<svg class="w-10 h-10 text-yellow-600 dark:text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
					/>
				</svg>
			</div>
			
			<h2 class="text-3xl font-bold text-gray-900 dark:text-[#fafafa] mb-4">
				Verify Your Email
			</h2>
			
			<p class="text-lg text-gray-600 dark:text-[#a3a3a3] mb-6">
				Welcome! We've sent a verification email to:
			</p>
			
			<div class="inline-block bg-white dark:bg-[#0a0a0a] border border-gray-200 dark:border-[#262626] rounded-lg px-6 py-3 mb-8">
				<code class="text-gray-900 dark:text-[#fafafa] font-medium">{data.user.email}</code>
			</div>
			
			<p class="text-gray-600 dark:text-[#a3a3a3] mb-8">
				Click the link in the email to verify your account and access all features.
			</p>
			
			<div class="flex flex-col sm:flex-row gap-4 justify-center">
				<button
					onclick={() => {
						toast.info('Resend feature coming soon!');
					}}
					class="px-6 py-3 rounded-lg bg-[#3b82f6] text-white font-semibold hover:bg-[#2563eb] transition-colors"
				>
					Resend Verification Email
				</button>
				
				<a
					href="/settings"
					class="px-6 py-3 rounded-lg border border-gray-300 dark:border-[#262626] text-gray-700 dark:text-[#a3a3a3] font-semibold hover:bg-gray-50 dark:hover:bg-[#171717] transition-colors"
				>
					Update Email Address
				</a>
			</div>
			
			<div class="mt-8 pt-8 border-t border-gray-200 dark:border-[#262626]">
				<p class="text-sm text-gray-500 dark:text-[#737373]">
					Didn't receive the email? Check your spam folder or contact support.
				</p>
			</div>
		</div>
	</main>
{/if}

<style>
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
