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

	const authState = getAuthState();

	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let emailError = $state('');
	let passwordError = $state('');
	let confirmPasswordError = $state('');
	let isSubmitting = $state(false);

	const passwordStrength = $derived(getPasswordStrength(password));
	const strengthInfo = $derived(getPasswordStrengthInfo(passwordStrength));

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

<div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4 py-12">
	<div class="w-full max-w-md">
		<div class="bg-[#171717] rounded-lg border border-[#262626] p-8">
			<div class="mb-8 text-center">
				<h1 class="text-3xl font-bold text-[#fafafa] mb-2">Join Taren</h1>
				<p class="text-[#737373]">Create your account to get started</p>
			</div>

			<form onsubmit={handleSubmit} class="space-y-5">
				<div class="space-y-2">
					<Label for="email" class="text-[#fafafa] font-medium">Email</Label>
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
					<Label for="password" class="text-[#fafafa] font-medium">Password</Label>
					<Input
						id="password"
						type="password"
						placeholder="Create a strong password"
						bind:value={password}
						oninput={handlePasswordInput}
						disabled={isSubmitting}
						class="border-[#262626] bg-[#0a0a0a] text-[#fafafa] focus:border-[#3b82f6] focus:ring-[#3b82f6] {passwordError
							? 'border-red-500'
							: ''}"
						required
					/>
					{#if password}
						<div class="space-y-1">
							<div class="h-1 w-full bg-[#262626] rounded overflow-hidden">
								<div
									class="h-full transition-all"
									style="width: {(passwordStrength / 4) * 100}%; background-color: {strengthInfo.color}"
								></div>
							</div>
							<p class="text-xs text-[#737373]">
								Strength: <span style="color: {strengthInfo.color}">{strengthInfo.label}</span>
							</p>
						</div>
					{/if}
					{#if passwordError}
						<p class="text-sm text-red-500">{passwordError}</p>
					{:else}
						<p class="text-xs text-[#525252]">
							Min 8 characters with uppercase, lowercase, number & special character
						</p>
					{/if}
				</div>

				<div class="space-y-2">
					<Label for="confirmPassword" class="text-[#fafafa] font-medium">Confirm Password</Label>
					<Input
						id="confirmPassword"
						type="password"
						placeholder="Confirm your password"
						bind:value={confirmPassword}
						oninput={handleConfirmPasswordInput}
						disabled={isSubmitting}
						class="border-[#262626] bg-[#0a0a0a] text-[#fafafa] focus:border-[#3b82f6] focus:ring-[#3b82f6] {confirmPasswordError
							? 'border-red-500'
							: ''}"
						required
					/>
					{#if confirmPasswordError}
						<p class="text-sm text-red-500">{confirmPasswordError}</p>
					{/if}
				</div>

				<Button
					type="submit"
					class="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-white"
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

			<div class="mt-6 text-center border-t border-[#262626] pt-6">
				<p class="text-[#737373]">
					Already have an account?
					<a href="/login" class="text-[#3b82f6] hover:text-[#2563eb] font-medium">Sign in</a>
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
