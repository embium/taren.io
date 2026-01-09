<script lang="ts">
	import { goto } from '$app/navigation';
	import Button from '$lib/components/ui/button/button.svelte';
	import Input from '$lib/components/ui/input/input.svelte';
	import Label from '$lib/components/ui/label/label.svelte';
	import { register, getAuthState } from '$lib/stores/auth.svelte';
	import { toast } from '$lib/stores/toast.svelte';
	import {
		validateEmail,
		validatePassword,
		validatePasswordConfirmation,
		getPasswordStrength,
		getPasswordStrengthInfo
	} from '$lib/utils/validation';
	import { mapErrorToMessage } from '$lib/utils/errors';
	import { onMount } from 'svelte';

	const authState = getAuthState();

	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let emailError = $state('');
	let passwordError = $state('');
	let confirmPasswordError = $state('');
	let isSubmitting = $state(false);
	let mounted = $state(false);

	const passwordStrength = $derived(getPasswordStrength(password));
	const strengthInfo = $derived(getPasswordStrengthInfo(passwordStrength));

	onMount(() => {
		mounted = true;
	});

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

		const passwordValidation = validatePassword(password);
		if (!passwordValidation.valid) {
			passwordError = passwordValidation.error || '';
			isValid = false;
		} else {
			passwordError = '';
		}

		const confirmValidation = validatePasswordConfirmation(password, confirmPassword);
		if (!confirmValidation.valid) {
			confirmPasswordError = confirmValidation.error || '';
			isValid = false;
		} else {
			confirmPasswordError = '';
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
			await register({ email, password });
			toast.success('Account created successfully! Redirecting...');
			goto('/dashboard');
		} catch (error) {
			const errorMessage = mapErrorToMessage(error);
			toast.error(errorMessage);
			console.error('Registration error:', error);
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

	function handleConfirmPasswordInput() {
		if (confirmPasswordError) confirmPasswordError = '';
	}
</script>

<svelte:head>
	<title>Create Account - Taren</title>
</svelte:head>

<!-- Animated Background -->
<div class="page-container">
	<div class="fixed inset-0 -z-10">
		<div class="absolute inset-0 bg-[#0a0a0f]">
			<div
				class="mesh-gradient-1 absolute top-0 -left-20 h-[600px] w-[600px] rounded-full bg-gradient-to-br from-pink-500/20 to-purple-500/20 mix-blend-screen blur-[120px] filter"
			></div>
			<div
				class="mesh-gradient-2 absolute top-1/4 right-0 h-[700px] w-[700px] rounded-full bg-gradient-to-br from-purple-500/20 to-blue-500/20 mix-blend-screen blur-[120px] filter"
			></div>
			<div
				class="mesh-gradient-1 absolute bottom-0 left-1/3 h-[650px] w-[650px] rounded-full bg-gradient-to-br from-blue-500/20 to-pink-500/20 mix-blend-screen blur-[120px] filter"
				style="animation-delay: -10s;"
			></div>
		</div>

		<div
			class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.02)_1px,transparent_1px)] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000,transparent)] bg-[size:64px_64px]"
		></div>
	</div>

	<div class="content-wrapper">
		<div class="auth-card glass" class:animate-scale-in={mounted}>
			<div class="card-header">
				<h1 class="gradient-text text-5xl font-black mb-3">Join Taren</h1>
				<p class="text-gray-400 text-lg">Create your account to get started</p>
			</div>

			<form onsubmit={handleSubmit} class="space-y-5">
				<div class="space-y-2">
					<Label for="email" class="text-gray-300 font-medium">Email</Label>
					<Input
						id="email"
						type="email"
						placeholder="you@example.com"
						bind:value={email}
						oninput={handleEmailInput}
						disabled={isSubmitting}
						class="glass-input {emailError ? 'border-red-500/50' : ''}"
						required
					/>
					{#if emailError}
						<p class="text-sm text-red-400">{emailError}</p>
					{/if}
				</div>

				<div class="space-y-2">
					<Label for="password" class="text-gray-300 font-medium">Password</Label>
					<Input
						id="password"
						type="password"
						placeholder="Create a strong password"
						bind:value={password}
						oninput={handlePasswordInput}
						disabled={isSubmitting}
						class="glass-input {passwordError ? 'border-red-500/50' : ''}"
						required
					/>
					{#if password}
						<div class="strength-indicator">
							<div class="strength-bar">
								<div
									class="strength-fill"
									style="width: {(passwordStrength / 4) * 100}%; background-color: {strengthInfo.color}"
								></div>
							</div>
							<p class="text-xs text-gray-400">
								Strength: <span style="color: {strengthInfo.color}">{strengthInfo.label}</span>
							</p>
						</div>
					{/if}
					{#if passwordError}
						<p class="text-sm text-red-400">{passwordError}</p>
					{:else}
						<p class="text-xs text-gray-500">
							Min 8 characters with uppercase, lowercase, number & special character
						</p>
					{/if}
				</div>

				<div class="space-y-2">
					<Label for="confirmPassword" class="text-gray-300 font-medium">Confirm Password</Label>
					<Input
						id="confirmPassword"
						type="password"
						placeholder="Confirm your password"
						bind:value={confirmPassword}
						oninput={handleConfirmPasswordInput}
						disabled={isSubmitting}
						class="glass-input {confirmPasswordError ? 'border-red-500/50' : ''}"
						required
					/>
					{#if confirmPasswordError}
						<p class="text-sm text-red-400">{confirmPasswordError}</p>
					{/if}
				</div>

				<Button
					type="submit"
					class="gradient-button w-full"
					disabled={isSubmitting || authState.loading}
				>
					{#if isSubmitting || authState.loading}
						<span class="loading-spinner"></span>
						Creating account...
					{:else}
						Create Account
					{/if}
				</Button>
			</form>

			<div class="card-footer">
				<p class="text-gray-400">
					Already have an account?
					<a href="/login" class="text-link">Sign in</a>
				</p>
			</div>
		</div>
	</div>
</div>

<style>
	.page-container {
		min-height: 100vh;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem;
	}

	.content-wrapper {
		width: 100%;
		max-width: 28rem;
		position: relative;
		z-index: 10;
	}

	.auth-card {
		padding: 3rem 2.5rem;
		border-radius: 2rem;
		border: 2px solid rgba(255, 255, 255, 0.1);
	}

	.card-header {
		text-align: center;
		margin-bottom: 2.5rem;
	}

	.card-footer {
		text-align: center;
		margin-top: 2rem;
		padding-top: 2rem;
		border-top: 1px solid rgba(255, 255, 255, 0.1);
	}

	:global(.glass-input) {
		background: rgba(255, 255, 255, 0.05) !important;
		border: 1px solid rgba(255, 255, 255, 0.1) !important;
		color: white !important;
		transition: all 0.3s ease;
	}

	:global(.glass-input:focus) {
		background: rgba(255, 255, 255, 0.08) !important;
		border-color: rgba(236, 72, 153, 0.5) !important;
		box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.1);
	}

	:global(.glass-input::placeholder) {
		color: rgba(156, 163, 175, 0.6);
	}

	:global(.gradient-button) {
		background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 50%, #3b82f6 100%) !important;
		border: none !important;
		font-weight: 600;
		padding: 0.75rem 1.5rem;
		font-size: 1rem;
		transition: all 0.3s ease;
	}

	:global(.gradient-button:hover:not(:disabled)) {
		transform: translateY(-2px);
		box-shadow: 0 20px 40px -15px rgba(236, 72, 153, 0.4);
	}

	:global(.gradient-button:active:not(:disabled)) {
		transform: translateY(0);
	}

	:global(.gradient-button:disabled) {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.text-link {
		color: #ec4899;
		font-weight: 500;
		transition: color 0.2s;
	}

	.text-link:hover {
		color: #8b5cf6;
	}

	.strength-indicator {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.strength-bar {
		height: 4px;
		background-color: rgba(255, 255, 255, 0.1);
		border-radius: 2px;
		overflow: hidden;
	}

	.strength-fill {
		height: 100%;
		transition: all 0.3s ease;
		border-radius: 2px;
	}

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
