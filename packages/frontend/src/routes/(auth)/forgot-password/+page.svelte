<script lang="ts">
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
	import { Loader2, Mail } from '@lucide/svelte';
	import { forgotPassword } from '$lib/stores/auth.svelte';

	let email = '';
	let loading = false;
	let emailSent = false;

	async function handleSubmit(e: Event) {
		e.preventDefault();

		if (!email) {
			toast.error('Please enter your email address');
			return;
		}

		loading = true;

		try {
			const data = await forgotPassword({ email });

			if (data.message) {
				emailSent = true;
				toast.success('Password reset email sent!');
			} else {
				toast.error('Failed to send reset email');
			}
		} catch (err) {
			toast.error('Failed to connect to server');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Forgot Password — Taren</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-[#0a0a0a] p-4">
	<Card class="w-full max-w-md border-[#262626] bg-[#171717]">
		<CardHeader class="text-center">
			<CardTitle class="text-2xl text-[#fafafa]">Forgot Password</CardTitle>
			<CardDescription class="text-[#a3a3a3]">
				{#if emailSent}
					Check your email for reset instructions
				{:else}
					Enter your email to receive a password reset link
				{/if}
			</CardDescription>
		</CardHeader>
		<CardContent>
			{#if emailSent}
				<div class="space-y-4 text-center">
					<div class="flex justify-center">
						<Mail class="h-16 w-16 text-blue-500" />
					</div>
					<p class="text-[#a3a3a3]">
						If that email exists in our system, we've sent a password reset link to <strong
							class="text-[#fafafa]">{email}</strong
						>.
					</p>
					<p class="text-sm text-[#737373]">The link will expire in 1 hour for security reasons.</p>
					<div class="space-y-2 pt-4">
						<Button onclick={() => goto('/login')} class="w-full bg-blue-600 hover:bg-blue-700">
							Back to Login
						</Button>
						<Button
							onclick={() => (emailSent = false)}
							variant="outline"
							class="w-full border-[#262626] bg-[#0a0a0a] text-[#fafafa] hover:bg-[#262626]"
						>
							Send Another Email
						</Button>
					</div>
				</div>
			{:else}
				<form on:submit={handleSubmit} class="space-y-4">
					<div class="space-y-2">
						<Label for="email" class="text-[#fafafa]">Email</Label>
						<Input
							id="email"
							type="email"
							bind:value={email}
							placeholder="you@example.com"
							disabled={loading}
							required
							class="border-[#262626] bg-[#0a0a0a] text-[#fafafa] placeholder:text-[#737373]"
						/>
					</div>

					<Button type="submit" disabled={loading} class="w-full bg-blue-600 hover:bg-blue-700">
						{#if loading}
							<Loader2 class="mr-2 h-4 w-4 animate-spin" />
							Sending...
						{:else}
							Send Reset Link
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
