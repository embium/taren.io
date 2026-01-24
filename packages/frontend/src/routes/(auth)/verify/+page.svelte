<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { PUBLIC_API_URL } from '$env/static/public';
	import { Button } from '$lib/components/ui/button';
	import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '$lib/components/ui/card';
	import { toast } from 'svelte-sonner';
	import { CheckCircle2, XCircle, Loader2 } from '@lucide/svelte';

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

		await verifyEmail();
	});

	async function verifyEmail() {
		if (!token) return;

		verifying = true;
		error = '';

		try {
			const response = await fetch(`${PUBLIC_API_URL}/auth/verify-email`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token })
			});

			const data = await response.json();

			if (response.ok) {
				verified = true;
				toast.success('Email verified successfully!');
				// Redirect to login after 3 seconds
				setTimeout(() => goto('/login'), 3000);
			} else {
				error = data.detail || 'Verification failed';
				toast.error(data.detail || 'Verification failed');
			}
		} catch (err) {
			error = 'Failed to connect to server';
			toast.error('Failed to connect to server');
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
						Your email has been successfully verified! You can now log in to your account.
					</p>
					<p class="text-center text-sm text-[#737373]">
						Redirecting to login page...
					</p>
				</div>
			{:else if error}
				<div class="space-y-4">
					<div class="flex justify-center">
						<XCircle class="h-16 w-16 text-red-500" />
					</div>
					<p class="text-center text-[#fafafa] font-medium">{error}</p>
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
