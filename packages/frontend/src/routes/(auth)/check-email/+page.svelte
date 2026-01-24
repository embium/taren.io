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
	import { Mail, ArrowRight } from '@lucide/svelte';
	import { onMount } from 'svelte';

	let email = '';

	onMount(() => {
		// Get email from sessionStorage
		email = sessionStorage.getItem('pendingVerificationEmail') || '';
		
		// If no email found, redirect to register
		if (!email) {
			goto('/register');
		} else {
			// Clear from sessionStorage after reading
			sessionStorage.removeItem('pendingVerificationEmail');
		}
	});
</script>

<svelte:head>
	<title>Check Your Email - Taren</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-[#0a0a0a] p-4">
	<Card class="w-full max-w-md border-[#262626] bg-[#171717]">
		<CardHeader class="text-center">
			<div class="mb-4 flex justify-center">
				<div class="rounded-full bg-blue-500/10 p-4">
					<Mail class="h-12 w-12 text-blue-500" />
				</div>
			</div>
			<CardTitle class="text-2xl text-[#fafafa]">Check Your Email</CardTitle>
			<CardDescription class="text-[#a3a3a3]">
				We've sent a verification link to your email
			</CardDescription>
		</CardHeader>
		<CardContent class="space-y-6">
			<div class="space-y-4 text-center">
				<p class="text-[#fafafa]">
					A verification email has been sent to:
				</p>
				<p class="font-mono text-blue-500 break-all">
					{email}
				</p>
				<div class="rounded-lg bg-[#0a0a0a] border border-[#262626] p-4 text-left space-y-2">
					<p class="text-sm text-[#a3a3a3]">
						<strong class="text-[#fafafa]">Next steps:</strong>
					</p>
					<ol class="text-sm text-[#a3a3a3] space-y-1 list-decimal list-inside">
						<li>Check your email inbox</li>
						<li>Click the verification link</li>
						<li>Return here to sign in</li>
					</ol>
				</div>
				<p class="text-xs text-[#737373]">
					The verification link will expire in 24 hours.
				</p>
			</div>

			<div class="space-y-3">
				<Button
					onclick={() => goto('/login')}
					class="w-full bg-blue-600 hover:bg-blue-700"
				>
					Go to Login
					<ArrowRight class="ml-2 h-4 w-4" />
				</Button>
				
				<div class="text-center">
					<p class="text-sm text-[#737373]">
						Didn't receive the email?
						<a href="/register" class="text-blue-500 hover:text-blue-400 ml-1">
							Try again
						</a>
					</p>
				</div>
			</div>
		</CardContent>
	</Card>
</div>
