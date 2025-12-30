<script lang="ts">
	import { onMount } from 'svelte';

	let scrollY = $state(0);
	let mounted = $state(false);

	onMount(() => {
		mounted = true;

		const handleScroll = () => {
			scrollY = window.scrollY;
		};

		window.addEventListener('scroll', handleScroll);
		return () => window.removeEventListener('scroll', handleScroll);
	});
</script>

<svelte:head>
	<title>Taren - The Future is Here</title>
	<meta
		name="description"
		content="Taren - Experience the next generation of  innovation. Join us in shaping tomorrow."
	/>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link
		href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap"
		rel="stylesheet"
	/>
</svelte:head>

<div class="relative min-h-screen overflow-hidden">
	<!-- Animated Mesh Gradient Background -->
	<div class="fixed inset-0 -z-10">
		<div class="absolute inset-0 bg-[#0a0a0f]">
			<!-- Large animated gradient blobs -->
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

		<!-- Grid overlay -->
		<div
			class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.02)_1px,transparent_1px)] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000,transparent)] bg-[size:64px_64px]"
		></div>
	</div>

	<!-- Hero Section -->
	<section class="relative flex min-h-screen items-center px-6 py-20 lg:px-12">
		<div class="mx-auto w-full max-w-7xl">
			<div class="grid items-center gap-16 lg:grid-cols-2">
				<!-- Left Column - Text Content -->
				<div class="space-y-8">
					<!-- Brand Name -->
					<div class:text-reveal={mounted} style="animation-delay: 0.1s;">
						<h1 class="text-8xl font-black tracking-tight lg:text-9xl">
							<span class="gradient-text">Taren</span>
						</h1>
					</div>

					<!-- Tagline -->
					<div class:text-reveal={mounted} style="animation-delay: 0.3s;">
						<h2 class="text-4xl leading-tight font-bold text-gray-100 lg:text-5xl">
							Building Tomorrow,<br />
							<span class="text-gray-400">Today</span>
						</h2>
					</div>

					<!-- Description -->
					<div class:text-reveal={mounted} style="animation-delay: 0.5s;">
						<p class="max-w-lg text-xl leading-relaxed text-gray-400">
							Experience the future of innovation. We're creating something extraordinary that will
							transform the way you work and connect.
						</p>
					</div>

					<!-- CTA Buttons -->
					<div class:text-reveal={mounted} style="animation-delay: 0.7s;">
						<div class="flex flex-wrap gap-4">
							<button
								class="group relative overflow-hidden rounded-2xl bg-gradient-to-r from-pink-500 to-purple-600 px-8 py-4 text-lg font-semibold transition-all duration-300 hover:scale-105 hover:shadow-[0_20px_80px_-15px_rgba(236,72,153,0.5)]"
							>
								<span class="relative z-10 flex items-center gap-2">
									Get Early Access
									<svg
										class="h-5 w-5 transition-transform group-hover:translate-x-1"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M17 8l4 4m0 0l-4 4m4-4H3"
										/>
									</svg>
								</span>
							</button>

							<button
								class="glass rounded-2xl border-2 border-white/10 px-8 py-4 text-lg font-semibold transition-all duration-300 hover:scale-105 hover:border-white/20"
							>
								Learn More
							</button>
						</div>
					</div>

					<!-- Stats Row -->
					<div class:text-reveal={mounted} style="animation-delay: 0.9s;">
						<div class="flex gap-12 pt-8">
							<div>
								<div class="gradient-text text-3xl font-black">10k+</div>
								<div class="mt-1 text-sm text-gray-500">Early Users</div>
							</div>
							<div>
								<div class="gradient-text text-3xl font-black">99.9%</div>
								<div class="mt-1 text-sm text-gray-500">Uptime</div>
							</div>
							<div>
								<div class="gradient-text text-3xl font-black">24/7</div>
								<div class="mt-1 text-sm text-gray-500">Support</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Right Column - Floating Visual Element -->
				<div class="relative hidden lg:block">
					<div class:animate-scale-in={mounted} style="animation-delay: 0.5s;">
						<div class="relative aspect-square">
							<!-- Large floating card -->
							<div
								class="card-3d glass border-dance absolute inset-0 flex items-center justify-center rounded-[3rem] p-12"
							>
								<div class="space-y-6 text-center">
									<div
										class="animate-float mx-auto flex h-32 w-32 items-center justify-center rounded-3xl bg-gradient-to-br from-pink-500 to-purple-600"
									>
										<svg
											class="h-16 w-16"
											fill="none"
											stroke="currentColor"
											stroke-width="2"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="M13 10V3L4 14h7v7l9-11h-7z"
											/>
										</svg>
									</div>
									<div>
										<div class="gradient-text text-4xl font-black">Innovation</div>
										<div class="mt-2 text-gray-400">Powered by Tomorrow</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Bento Box Features Section -->
	<section class="relative px-6 py-32 lg:px-12">
		<div class="mx-auto max-w-7xl">
			<!-- Section Header -->
			<div class="mb-20 text-center">
				<h2 class="mb-6 text-5xl font-black lg:text-6xl">
					<span class="gradient-text">Why Taren?</span>
				</h2>
				<p class="mx-auto max-w-2xl text-xl text-gray-400">
					Innovative features designed to elevate your experience
				</p>
			</div>

			<!-- Bento Grid -->
			<div class="bento-grid">
				<!-- Large Feature Card -->
				<div
					class="bento-item-large card-3d glass group rounded-3xl p-8 transition-colors duration-300 hover:border-pink-500/50 lg:p-12"
				>
					<div class="flex h-full flex-col justify-between">
						<div>
							<div
								class="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-pink-500 to-purple-600 transition-transform group-hover:scale-110"
							>
								<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M13 10V3L4 14h7v7l9-11h-7z"
									/>
								</svg>
							</div>
							<h3 class="mb-4 text-3xl font-bold">Lightning Performance</h3>
							<p class="text-lg text-gray-400">
								Experience blazing-fast speeds with our optimized infrastructure. Built for scale,
								designed for speed.
							</p>
						</div>
						<div
							class="mt-8 flex items-center gap-2 font-semibold text-pink-400 transition-all group-hover:gap-4"
						>
							<span>Explore</span>
							<svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M17 8l4 4m0 0l-4 4m4-4H3"
								/>
							</svg>
						</div>
					</div>
				</div>

				<!-- Tall Feature Card -->
				<div
					class="bento-item-tall card-3d glass group rounded-3xl p-8 transition-colors duration-300 hover:border-purple-500/50"
				>
					<div class="flex h-full flex-col justify-between">
						<div>
							<div
								class="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-blue-600 transition-transform group-hover:scale-110"
							>
								<svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
									/>
								</svg>
							</div>
							<h3 class="mb-4 text-2xl font-bold">Secure by Design</h3>
							<p class="text-gray-400">
								Enterprise-grade security protecting your data with industry-leading encryption and
								best practices.
							</p>
						</div>
					</div>
				</div>

				<!-- Wide Feature Cards -->
				<div
					class="bento-item-wide card-3d glass group rounded-3xl p-8 transition-colors duration-300 hover:border-blue-500/50"
				>
					<div
						class="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 transition-transform group-hover:scale-110"
					>
						<svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
							/>
						</svg>
					</div>
					<h3 class="mb-2 text-xl font-bold">Team Collaboration</h3>
					<p class="text-sm text-gray-400">Real-time collaboration that keeps everyone in sync</p>
				</div>

				<div
					class="bento-item-wide card-3d glass group rounded-3xl p-8 transition-colors duration-300 hover:border-pink-500/50"
				>
					<div
						class="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-pink-500 to-rose-500 transition-transform group-hover:scale-110"
					>
						<svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
							/>
						</svg>
					</div>
					<h3 class="mb-2 text-xl font-bold">Fully Customizable</h3>
					<p class="text-sm text-gray-400">Tailor every aspect to match your workflow</p>
				</div>

				<!-- Small Feature Cards -->
				<div
					class="bento-item-small card-3d glass group flex items-center gap-4 rounded-3xl p-6 transition-colors duration-300 hover:border-purple-500/50"
				>
					<div
						class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 transition-transform group-hover:scale-110"
					>
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
							/>
						</svg>
					</div>
					<div>
						<h3 class="mb-1 font-bold">Smart AI</h3>
						<p class="text-xs text-gray-400">Powered insights</p>
					</div>
				</div>

				<div
					class="bento-item-small card-3d glass group flex items-center gap-4 rounded-3xl p-6 transition-colors duration-300 hover:border-blue-500/50"
				>
					<div
						class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 transition-transform group-hover:scale-110"
					>
						<svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
							/>
						</svg>
					</div>
					<div>
						<h3 class="mb-1 font-bold">Analytics</h3>
						<p class="text-xs text-gray-400">Deep insights</p>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- CTA Section -->
	<section class="relative px-6 py-32 lg:px-12">
		<div class="mx-auto max-w-4xl">
			<div
				class="glass relative overflow-hidden rounded-[3rem] border-2 border-white/5 p-12 text-center lg:p-16"
			>
				<!-- Decorative gradient -->
				<div
					class="absolute inset-0 bg-gradient-to-br from-pink-500/10 via-purple-500/10 to-blue-500/10"
				></div>

				<div class="relative z-10">
					<h2 class="mb-6 text-5xl font-black lg:text-6xl">
						Ready for <span class="gradient-text">Taren</span>?
					</h2>
					<p class="mx-auto mb-12 max-w-2xl text-xl text-gray-300">
						Join thousands already experiencing the future. Be part of something extraordinary.
					</p>

					<!-- Email Signup -->
					<form class="mx-auto mb-8 flex max-w-xl flex-col gap-4 sm:flex-row">
						<input
							type="email"
							placeholder="Enter your email"
							class="glass flex-1 rounded-2xl border-2 border-white/10 bg-white/5 px-6 py-4 text-white placeholder-gray-500 transition-colors focus:border-pink-500/50 focus:outline-none"
						/>
						<button
							type="submit"
							class="rounded-2xl bg-gradient-to-r from-pink-500 to-purple-600 px-8 py-4 font-semibold whitespace-nowrap transition-all duration-300 hover:scale-105 hover:shadow-[0_20px_80px_-15px_rgba(236,72,153,0.5)]"
						>
							Join Waitlist
						</button>
					</form>

					<p class="text-sm text-gray-500">No spam, ever. Unsubscribe anytime.</p>
				</div>
			</div>
		</div>
	</section>

	<!-- Footer -->
	<footer class="relative border-t border-white/5 px-6 py-16 lg:px-12">
		<div class="mx-auto max-w-7xl">
			<div class="mb-12 grid gap-12 md:grid-cols-4">
				<!-- Brand -->
				<div class="md:col-span-2">
					<h3 class="gradient-text mb-4 text-3xl font-black">Taren</h3>
					<p class="mb-6 max-w-sm text-gray-400">
						Building the future of innovation, one breakthrough at a time.
					</p>
					<div class="flex gap-4">
						<a
							href="https://twitter.com"
							target="_blank"
							rel="noopener"
							aria-label="Twitter"
							class="glass flex h-10 w-10 items-center justify-center rounded-xl border border-white/5 transition-transform hover:scale-110 hover:border-pink-500/50"
						>
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path
									d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"
								/>
							</svg>
						</a>
						<a
							href="https://github.com"
							target="_blank"
							rel="noopener"
							aria-label="GitHub"
							class="glass flex h-10 w-10 items-center justify-center rounded-xl border border-white/5 transition-transform hover:scale-110 hover:border-pink-500/50"
						>
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path
									d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"
								/>
							</svg>
						</a>
						<a
							href="https://linkedin.com"
							target="_blank"
							rel="noopener"
							aria-label="LinkedIn"
							class="glass flex h-10 w-10 items-center justify-center rounded-xl border border-white/5 transition-transform hover:scale-110 hover:border-pink-500/50"
						>
							<svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
								<path
									d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"
								/>
							</svg>
						</a>
					</div>
				</div>

				<!-- Links -->
				<div>
					<h4 class="mb-4 font-semibold text-white">Product</h4>
					<ul class="space-y-2 text-gray-400">
						<li><a href="#features" class="transition-colors hover:text-pink-400">Features</a></li>
						<li><a href="#pricing" class="transition-colors hover:text-pink-400">Pricing</a></li>
						<li><a href="#docs" class="transition-colors hover:text-pink-400">Documentation</a></li>
						<li><a href="#updates" class="transition-colors hover:text-pink-400">Updates</a></li>
					</ul>
				</div>

				<div>
					<h4 class="mb-4 font-semibold text-white">Company</h4>
					<ul class="space-y-2 text-gray-400">
						<li><a href="#about" class="transition-colors hover:text-pink-400">About</a></li>
						<li><a href="#blog" class="transition-colors hover:text-pink-400">Blog</a></li>
						<li><a href="#careers" class="transition-colors hover:text-pink-400">Careers</a></li>
						<li><a href="#contact" class="transition-colors hover:text-pink-400">Contact</a></li>
					</ul>
				</div>
			</div>

			<!-- Copyright -->
			<div class="border-t border-white/5 pt-8 text-center text-gray-500">
				<p>&copy; {new Date().getFullYear()} Taren. All rights reserved.</p>
			</div>
		</div>
	</footer>
</div>
