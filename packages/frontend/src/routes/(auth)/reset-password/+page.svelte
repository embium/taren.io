<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import {
		Card,
		CardContent,
		CardDescription,
		CardHeader,
		CardTitle
	} from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { toast } from 'svelte-sonner';
	import { Loader2, Eye, EyeOff, CheckCircle2 } from '@lucide/svelte';
	import { resetPassword } from '$lib/stores/auth.svelte';

	let token = '';
	let newPassword = '';
	let confirmPassword = '';
	let showPassword = false;
	let showConfirmPassword = false;
	let loading = false;
	let resetSuccess = false;

	onMount(() => {
		token = $page.url.searchParams.get('token') || '';

		if (!token) {
			toast.error('No reset token provided');
			setTimeout(() => goto('/forgot-password'), 2000);
		}
	});

	function validatePassword(password: string): string | null {
		if (password.length < 8) {
			return 'Password must be at least 8 characters';
		}
		if (!/[A-Z]/.test(password)) {
			return 'Password must contain at least one uppercase letter';
		}
		if (!/[a-z]/.test(password)) {
			return 'Password must contain at least one lowercase letter';
		}
		if (!/[0-9]/.test(password)) {
			return 'Password must contain at least one number';
		}
		if (!/[^A-Za-z0-9]/.test(password)) {
			return 'Password must contain at least one special character';
		}
		return null;
	}

	async function handleSubmit(e: Event) {
		e.preventDefault();

		if (!newPassword || !confirmPassword) {
			toast.error('Please fill in all fields');
			return;
		}

		if (newPassword !== confirmPassword) {
			toast.error('Passwords do not match');
			return;
		}

		const passwordError = validatePassword(newPassword);
		if (passwordError) {
			toast.error(passwordError);
			return;
		}

		loading = true;

		try {
			const data = await resetPassword({ token, new_password: newPassword });

			if (data.message) {
				resetSuccess = true;
				toast.success('Password reset successfully!');
				setTimeout(() => goto('/login'), 3000);
			} else {
				toast.error('Failed to reset password');
			}
		} catch (err) {
			toast.error('Failed to connect to server');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Reset Password — Taren</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-[#0a0a0a] p-4">
	<Card class="w-full max-w-md border-[#262626] bg-[#171717]">
		<CardHeader class="text-center">
			<CardTitle class="text-2xl text-[#fafafa]">Reset Password</CardTitle>
			<CardDescription class="text-[#a3a3a3]">
				{#if resetSuccess}
					Your password has been reset
				{:else}
					Enter your new password
				{/if}
			</CardDescription>
		</CardHeader>
		<CardContent>
			{#if resetSuccess}
				<div class="space-y-4 text-center">
					<div class="flex justify-center">
						<CheckCircle2 class="h-16 w-16 text-green-500" />
					</div>
					<p class="text-[#fafafa]">Your password has been successfully reset!</p>
					<p class="text-sm text-[#a3a3a3]">Redirecting to login page...</p>
				</div>
			{:else}
				<form on:submit={handleSubmit} class="space-y-4">
					<div class="space-y-2">
						<Label for="new-password" class="text-[#fafafa]">New Password</Label>
						<div class="relative">
							<Input
								id="new-password"
								type={showPassword ? 'text' : 'password'}
								bind:value={newPassword}
								placeholder="Enter new password"
								disabled={loading}
								required
								class="border-[#262626] bg-[#0a0a0a] pr-10 text-[#fafafa] placeholder:text-[#737373]"
							/>
							<button
								type="button"
								on:click={() => (showPassword = !showPassword)}
								class="absolute top-1/2 right-3 -translate-y-1/2 text-[#737373] hover:text-[#fafafa]"
								tabindex="-1"
							>
								{#if showPassword}
									<EyeOff class="h-4 w-4" />
								{:else}
									<Eye class="h-4 w-4" />
								{/if}
							</button>
						</div>
						<p class="text-xs text-[#737373]">
							Must be at least 8 characters with uppercase, lowercase, number, and special character
						</p>
					</div>

					<div class="space-y-2">
						<Label for="confirm-password" class="text-[#fafafa]">Confirm Password</Label>
						<div class="relative">
							<Input
								id="confirm-password"
								type={showConfirmPassword ? 'text' : 'password'}
								bind:value={confirmPassword}
								placeholder="Confirm new password"
								disabled={loading}
								required
								class="border-[#262626] bg-[#0a0a0a] pr-10 text-[#fafafa] placeholder:text-[#737373]"
							/>
							<button
								type="button"
								on:click={() => (showConfirmPassword = !showConfirmPassword)}
								class="absolute top-1/2 right-3 -translate-y-1/2 text-[#737373] hover:text-[#fafafa]"
								tabindex="-1"
							>
								{#if showConfirmPassword}
									<EyeOff class="h-4 w-4" />
								{:else}
									<Eye class="h-4 w-4" />
								{/if}
							</button>
						</div>
					</div>

					<Button type="submit" disabled={loading} class="w-full bg-blue-600 hover:bg-blue-700">
						{#if loading}
							<Loader2 class="mr-2 h-4 w-4 animate-spin" />
							Resetting Password...
						{:else}
							Reset Password
						{/if}
					</Button>

					<div class="text-center">
						<Button
							onclick={() => goto('/login')}
							variant="link"
							class="text-[#a3a3a3] hover:text-[#fafafa]"
						>
							Back to Login
						</Button>
					</div>
				</form>
			{/if}
		</CardContent>
	</Card>
</div>
