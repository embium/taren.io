<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto, invalidateAll } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import {
		Card,
		CardContent,
		CardDescription,
		CardHeader,
		CardTitle
	} from '$lib/components/ui/card';
	import { toast } from 'svelte-sonner';
	import { CheckCircle2, XCircle, Loader2 } from '@lucide/svelte';
	import { authApi } from '$lib/api/auth.api';

	let token = '';
	let verifying = false;
	let verified = false;
	let error = '';

	onMount(async () => {
		token = $page.url.searchParams.get('token') || '';

		if (!token) {
			error = 'No verification token provided';
			return;
		}

		await verifyEmailSubmit();
	});

	async function verifyEmailSubmit() {
		if (!token) return;

		verifying = true;
		error = '';

		try {
			// Call the backend API directly to verify email
			const response = await authApi.verifyEmail({ token });

			if (response.message) {
				verified = true;
				toast.success('Email verified successfully! Redirecting to dashboard...');
				// Auto-login: The verify endpoint returns tokens
				if (response.access_token && response.refresh_token) {
					// Invalidate all load functions to update locals.user
					await invalidateAll();
					// Tokens are now set via cookies, just redirect
					setTimeout(() => goto('/dashboard'), 2000);
				} else {
					// Fallback if no tokens (shouldn't happen)
					setTimeout(() => goto('/login'), 2000);
				}
			} else {
				error = 'Verification failed';
				toast.error(error);
			}
		} catch (err: any) {
			error = err.message || 'Verification failed';
			toast.error(error);
		} finally {
			verifying = false;
		}
	}
</script>

<div class="flex min-h-screen items-center justify-center bg-[#0a0a0a] p-4">
	<Card class="w-full max-w-md border-[#262626] bg-[#171717]">
		<CardHeader class="text-center">
			<CardTitle class="text-2xl text-[#fafafa]">Email Verification</CardTitle>
			<CardDescription class="text-[#a3a3a3]">
				{#if verifying}
					Verifying your email address...
				{:else if verified}
					Your email has been verified
				{:else if error}
					Verification failed
				{:else}
					Processing verification
				{/if}
			</CardDescription>
		</CardHeader>
		<CardContent class="space-y-6">
			{#if verifying}
				<div class="flex justify-center">
					<Loader2 class="h-12 w-12 animate-spin text-blue-500" />
				</div>
			{:else if verified}
				<div class="space-y-4">
					<div class="flex justify-center">
						<CheckCircle2 class="h-16 w-16 text-green-500" />
					</div>
					<p class="text-center text-[#a3a3a3]">
						Your email has been successfully verified! Logging you in...
					</p>
					<p class="text-center text-sm text-[#737373]">Redirecting to dashboard...</p>
				</div>
			{:else if error}
				<div class="space-y-4">
					<div class="flex justify-center">
						<XCircle class="h-16 w-16 text-red-500" />
					</div>
					<p class="text-center font-medium text-[#fafafa]">{error}</p>
					<p class="text-center text-sm text-[#a3a3a3]">
						The verification link may have expired or is invalid.
					</p>
					<div class="flex flex-col gap-2">
						<Button
							onclick={() => goto('/login')}
							variant="outline"
							class="w-full border-[#262626] bg-[#0a0a0a] text-[#fafafa] hover:bg-[#262626]"
						>
							Go to Login
						</Button>
					</div>
				</div>
			{/if}
		</CardContent>
	</Card>
</div>
