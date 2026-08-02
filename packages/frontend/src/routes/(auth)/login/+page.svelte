<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/button/button.svelte';
	import Input from '$lib/components/ui/input/input.svelte';
	import Label from '$lib/components/ui/label/label.svelte';
	import { login, getAuthState } from '$lib/stores/auth.svelte';
	import { validateEmail } from '$lib/utils/validation';
	import { mapErrorToMessage } from '$lib/utils/errors';

	const authState = getAuthState();

	let email = $state('');
	let password = $state('');
	let emailError = $state('');
	let passwordError = $state('');
	let isSubmitting = $state(false);

	// Redirect if already authenticated
	$effect(() => {
		if (authState.isAuthenticated) {
			goto('/dashboard');
		}
	});

	function validateForm(): boolean {
		let isValid = true;

		const emailValidation = validateEmail(email);
		if (!emailValidation.valid) {
			emailError = emailValidation.error || '';
			isValid = false;
		} else {
			emailError = '';
		}

		if (!password) {
			passwordError = 'Password is required';
			isValid = false;
		} else {
			passwordError = '';
		}

		return isValid;
	}

	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();

		if (!validateForm()) {
			return;
		}

		isSubmitting = true;

		try {
			await login({ email, password });
			toast.success('Login successful! Redirecting...');
			goto('/dashboard');
		} catch (error) {
			const errorMessage = mapErrorToMessage(error);
			toast.error(errorMessage);
			console.error('Login error:', error);
		} finally {
			isSubmitting = false;
		}
	}

	function handleEmailInput() {
		if (emailError) emailError = '';
	}

	function handlePasswordInput() {
		if (passwordError) passwordError = '';
	}
</script>

<svelte:head>
	<title>Sign In — Taren</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-[#0a0a0a] px-4 py-12">
	<div class="w-full max-w-md">
		<div class="rounded-lg border border-[#262626] bg-[#171717] p-8">
			<!-- Header -->
			<div class="mb-8 text-center">
				<h1 class="mb-2 text-3xl font-bold text-[#fafafa]">Welcome Back</h1>
				<p class="text-[#737373]">Sign in to continue to Taren</p>
			</div>

			<!-- Form -->
			<form onsubmit={handleSubmit} class="space-y-6">
				<div class="space-y-2">
					<Label for="email" class="font-medium text-[#fafafa]">Email</Label>
					<Input
						id="email"
						type="email"
						placeholder="you@example.com"
						bind:value={email}
						oninput={handleEmailInput}
						disabled={isSubmitting}
						class="border-[#262626] bg-[#0a0a0a] text-[#fafafa] focus:border-[#3b82f6] focus:ring-[#3b82f6] {emailError
							? 'border-red-500'
							: ''}"
						required
					/>
					{#if emailError}
						<p class="text-sm text-red-500">{emailError}</p>
					{/if}
				</div>

				<div class="space-y-2">
					<Label for="password" class="font-medium text-[#fafafa]">Password</Label>
					<Input
						id="password"
						type="password"
						placeholder="Enter your password"
						bind:value={password}
						oninput={handlePasswordInput}
						disabled={isSubmitting}
						class="border-[#262626] bg-[#0a0a0a] text-[#fafafa] focus:border-[#3b82f6] focus:ring-[#3b82f6] {passwordError
							? 'border-red-500'
							: ''}"
						required
					/>
					{#if passwordError}
						<p class="text-sm text-red-500">{passwordError}</p>
					{/if}
				</div>

				<Button
					type="submit"
					class="w-full bg-[#3b82f6] text-white hover:bg-[#2563eb]"
					disabled={isSubmitting || authState.loading}
				>
					{#if isSubmitting || authState.loading}
						<span class="loading-spinner"></span>
						Signing in...
					{:else}
						Sign In
					{/if}
				</Button>
			</form>

			<!-- Footer -->
			<div class="mt-6 border-t border-[#262626] pt-6 text-center">
				<p class="text-[#737373]">
					Don't have an account?
					<a href="/register" class="font-medium text-[#3b82f6] hover:text-[#2563eb]">Create one</a>
				</p>
			</div>
		</div>
	</div>
</div>

<style>
	.loading-spinner {
		display: inline-block;
		width: 1rem;
		height: 1rem;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-top-color: #ffffff;
		border-radius: 50%;
		animation: spin 0.6s linear infinite;
		margin-right: 0.5rem;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
