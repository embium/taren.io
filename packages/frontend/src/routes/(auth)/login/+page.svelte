<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/button/button.svelte';
	import Input from '$lib/components/ui/input/input.svelte';
	import Label from '$lib/components/ui/label/label.svelte';
	import { login, getAuthState } from '$lib/stores/auth.svelte';
	import { validateEmail } from '$lib/utils/validation';
	import { mapErrorToMessage } from '$lib/utils/errors';
	import { env } from '$env/dynamic/public';

	const authState = getAuthState();

	let email = $state('');
	let password = $state('');
	let emailError = $state('');
	let passwordError = $state('');
	let isSubmitting = $state(false);
	const PUBLIC_API_URL = env.PUBLIC_API_URL;

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

	function handleGoogleLogin() {
		window.location.href = `${PUBLIC_API_URL}/auth/google`;
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

			<!-- OR Divider -->
			<div class="or-divider">
				<span>OR</span>
			</div>

			<!-- Google Button -->
			<button
				id="google-login-btn"
				type="button"
				onclick={handleGoogleLogin}
				class="google-btn"
				disabled={isSubmitting}
			>
				<svg class="google-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
					<path
						d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
						fill="#4285F4"
					/>
					<path
						d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
						fill="#34A853"
					/>
					<path
						d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
						fill="#FBBC05"
					/>
					<path
						d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
						fill="#EA4335"
					/>
				</svg>
				Google
			</button>

			<!-- Footer -->
			<div class="mt-6 text-center">
				<p class="text-[#737373]">
					Don't have an account?
					<a href="/register" class="font-medium text-[#3b82f6] hover:text-[#2563eb]"
						>Create an account</a
					>
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

	.or-divider {
		display: flex;
		align-items: center;
		margin: 1.5rem 0 1rem;
		gap: 0.75rem;
		color: #525252;
		font-size: 0.75rem;
		font-weight: 500;
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	.or-divider::before,
	.or-divider::after {
		content: '';
		flex: 1;
		height: 1px;
		background: #262626;
	}

	.google-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.625rem;
		width: 100%;
		padding: 0.625rem 1rem;
		background: #0a0a0a;
		border: 1px solid #333333;
		border-radius: 0.5rem;
		color: #e5e5e5;
		font-size: 0.9375rem;
		font-weight: 500;
		cursor: pointer;
		transition:
			background 0.15s ease,
			border-color 0.15s ease,
			transform 0.1s ease;
	}

	.google-btn:hover:not(:disabled) {
		background: #141414;
		border-color: #444444;
	}

	.google-btn:active:not(:disabled) {
		transform: scale(0.99);
	}

	.google-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.google-icon {
		width: 1.125rem;
		height: 1.125rem;
		flex-shrink: 0;
	}
</style>
