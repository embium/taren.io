<script lang="ts">
	import Navigation from '$lib/components/Navigation.svelte';
	import { goto } from '$app/navigation';
	import { Search, Brain, BarChart2, Zap, ArrowRight, CheckCircle2 } from '@lucide/svelte';
</script>

<svelte:head>
	<title>Taren — Discover What People Really Want</title>
	<meta
		name="description"
		content="Taren scrapes Reddit and uses AI to surface hidden insights in any community. Find your next product idea in minutes, not months."
	/>
</svelte:head>

<div class="min-h-screen bg-background text-foreground">
	<Navigation />

	<!-- ───── HERO ───── -->
	<section class="relative overflow-hidden px-6 pt-24 pb-24 lg:px-12 lg:pt-32 lg:pb-36">
		<!-- Subtle radial glow — adapts to dark/light via opacity -->
		<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
			<div
				class="h-[600px] w-[600px] rounded-full bg-orange-500/10 blur-3xl dark:bg-orange-500/5"
			></div>
		</div>

		<div class="relative mx-auto max-w-4xl text-center">
			<p
				class="mb-5 inline-flex items-center gap-2 rounded-full border border-orange-500/30 bg-orange-500/10 px-4 py-1.5 text-sm font-medium text-orange-500"
			>
				<Zap class="h-3.5 w-3.5" />
				AI-powered Reddit market research
			</p>

			<h1 class="mb-6 text-5xl font-bold tracking-tight text-foreground lg:text-7xl">
				Discover what people
				<span class="bg-gradient-to-r from-orange-500 to-pink-500 bg-clip-text text-transparent">
					actually care about
				</span>
			</h1>

			<p class="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-muted-foreground lg:text-xl">
				Taren scrapes Reddit communities and applies AI analysis to surface real, validated
				insights, market opportunities, and feature requests — so you can build products people are
				already asking for.
			</p>

			<div class="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
				<button
					id="hero-cta-btn"
					onclick={() => goto('/register')}
					class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 to-pink-500 px-7 py-3.5 text-base font-semibold text-white shadow-lg shadow-orange-500/25 transition-all hover:from-orange-600 hover:to-pink-600 hover:shadow-orange-500/40"
				>
					Start free trial
					<ArrowRight class="h-4 w-4" />
				</button>
				<a
					href="/pricing"
					class="inline-flex items-center gap-2 rounded-xl border border-border bg-card px-7 py-3.5 text-base font-semibold text-foreground transition-colors hover:bg-secondary"
				>
					View pricing
				</a>
			</div>

			<p class="mt-5 text-sm text-muted-foreground">
				14-day free trial · No card charged until trial ends
			</p>
		</div>
	</section>

	<!-- ───── HOW IT WORKS ───── -->
	<section class="border-t border-border px-6 py-24 lg:px-12">
		<div class="mx-auto max-w-5xl">
			<div class="mb-16 text-center">
				<h2 class="mb-4 text-4xl font-bold lg:text-5xl">How it works</h2>
				<p class="mx-auto max-w-xl text-lg text-muted-foreground">
					Three steps from subreddit to insight
				</p>
			</div>

			<div class="grid gap-8 md:grid-cols-3">
				<!-- Step 1 -->
				<div
					class="group relative flex flex-col rounded-2xl border border-border bg-card p-7 transition-all hover:border-orange-500/40 hover:shadow-lg hover:shadow-orange-500/5"
				>
					<div
						class="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-orange-500/10 ring-1 ring-orange-500/20"
					>
						<Search class="h-6 w-6 text-orange-500" />
					</div>
					<div class="mb-2 flex items-center gap-3">
						<span class="text-xs font-bold tracking-widest text-orange-500 uppercase">Step 1</span>
					</div>
					<h3 class="mb-2 text-xl font-semibold">Pick your subreddits</h3>
					<p class="text-sm leading-relaxed text-muted-foreground">
						Enter any subreddit name — a niche community, a competitor's audience, or a broad topic.
						Taren handles up to 10 subreddits per scan.
					</p>
				</div>

				<!-- Step 2 -->
				<div
					class="group relative flex flex-col rounded-2xl border border-border bg-card p-7 transition-all hover:border-orange-500/40 hover:shadow-lg hover:shadow-orange-500/5"
				>
					<div
						class="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-pink-500/10 ring-1 ring-pink-500/20"
					>
						<Brain class="h-6 w-6 text-pink-500" />
					</div>
					<div class="mb-2">
						<span class="text-xs font-bold tracking-widest text-pink-500 uppercase">Step 2</span>
					</div>
					<h3 class="mb-2 text-xl font-semibold">AI analyses the comments</h3>
					<p class="text-sm leading-relaxed text-muted-foreground">
						Our AI reads thousands of posts and comments, looking for recurring frustrations,
						feature requests, and hidden opportunities — ranked by relevance.
					</p>
				</div>

				<!-- Step 3 -->
				<div
					class="group relative flex flex-col rounded-2xl border border-border bg-card p-7 transition-all hover:border-orange-500/40 hover:shadow-lg hover:shadow-orange-500/5"
				>
					<div
						class="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500/10 ring-1 ring-indigo-500/20"
					>
						<BarChart2 class="h-6 w-6 text-indigo-500" />
					</div>
					<div class="mb-2">
						<span class="text-xs font-bold tracking-widest text-indigo-500 uppercase">Step 3</span>
					</div>
					<h3 class="mb-2 text-xl font-semibold">Get actionable results</h3>
					<p class="text-sm leading-relaxed text-muted-foreground">
						Review findings with real evidence quotes, relevance scores, and contextual breakdowns.
						Export your findings as CSV or PDF.
					</p>
				</div>
			</div>
		</div>
	</section>

	<!-- ───── DISCOVER NICHES FEATURE ───── -->
	<section class="relative overflow-hidden border-t border-border px-6 py-24 lg:px-12">
		<div
			class="pointer-events-none absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full bg-orange-500/10 blur-[100px]"
		></div>
		<div
			class="pointer-events-none absolute -bottom-40 -left-40 h-[500px] w-[500px] rounded-full bg-pink-500/10 blur-[100px]"
		></div>

		<div class="mx-auto max-w-6xl">
			<div class="grid items-center gap-16 lg:grid-cols-2">
				<div class="order-2 lg:order-1">
					<div
						class="mb-4 inline-flex items-center gap-2 rounded-full border border-orange-500/30 bg-orange-500/10 px-3 py-1 text-xs font-semibold tracking-wide text-orange-500 uppercase"
					>
						<Search class="h-3.5 w-3.5" />
						New Feature
					</div>
					<h2 class="mb-6 text-3xl leading-tight font-bold lg:text-4xl">
						Don't know what to scan? <br /><span
							class="bg-gradient-to-r from-orange-500 to-pink-500 bg-clip-text text-transparent"
							>Discover Niches instantly.</span
						>
					</h2>
					<p class="mb-8 text-lg leading-relaxed text-muted-foreground">
						Stop guessing where your target audience hangs out. Browse our curated database of
						professions and let Taren instantly recommend the most active, relevant subreddits to
						scan for insights.
					</p>

					<ul class="mb-8 space-y-4">
						<li class="flex items-start gap-3 text-muted-foreground">
							<div
								class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-500"
							>
								<svg
									class="h-3 w-3"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="3"
									><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"
									></path></svg
								>
							</div>
							<span>Browse over 100+ highly targeted professions and niches.</span>
						</li>
						<li class="flex items-start gap-3 text-muted-foreground">
							<div
								class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-500"
							>
								<svg
									class="h-3 w-3"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="3"
									><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"
									></path></svg
								>
							</div>
							<span>See subscriber counts and activity levels for every community.</span>
						</li>
						<li class="flex items-start gap-3 text-muted-foreground">
							<div
								class="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-500"
							>
								<svg
									class="h-3 w-3"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="3"
									><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"
									></path></svg
								>
							</div>
							<span>Build a list and launch a targeted scan with one click.</span>
						</li>
					</ul>

					<a
						href="/register"
						class="inline-flex items-center gap-2 rounded-xl border border-border bg-secondary px-6 py-3 font-semibold text-foreground transition-colors hover:bg-secondary/80"
					>
						Try it for free
						<ArrowRight class="h-4 w-4" />
					</a>
				</div>

				<div class="order-1 lg:order-2">
					<div class="relative rounded-2xl border border-border bg-card p-4 shadow-2xl">
						<div
							class="absolute -top-3 -right-3 h-24 w-24 rounded-full bg-orange-500/20 blur-2xl"
						></div>
						<div class="rounded-xl border border-border/50 bg-background/50 p-6 backdrop-blur-sm">
							<div class="mb-4 text-sm font-medium">Profession / Niche</div>
							<div
								class="mb-6 flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3"
							>
								<span class="text-sm">Software Developers</span>
								<svg
									class="h-4 w-4 text-muted-foreground"
									fill="none"
									stroke="currentColor"
									viewBox="0 0 24 24"
									><path
										stroke-linecap="round"
										stroke-linejoin="round"
										stroke-width="2"
										d="M19 9l-7 7-7-7"
									/></svg
								>
							</div>
							<div class="space-y-3">
								<div
									class="flex items-center justify-between rounded-lg border border-orange-500/30 bg-orange-500/10 px-4 py-3"
								>
									<div>
										<div class="text-sm font-semibold text-orange-500">r/learnprogramming</div>
										<div class="text-xs text-orange-500/70">4.1m subscribers</div>
									</div>
									<div
										class="rounded-full bg-orange-500 px-3 py-1 text-xs font-semibold text-white"
									>
										Selected
									</div>
								</div>
								<div
									class="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3"
								>
									<div>
										<div class="text-sm font-semibold">r/webdev</div>
										<div class="text-xs text-muted-foreground">1.8m subscribers</div>
									</div>
									<div class="rounded-full bg-secondary px-3 py-1 text-xs font-semibold">
										Add to list
									</div>
								</div>
								<div
									class="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3"
								>
									<div>
										<div class="text-sm font-semibold">r/reactjs</div>
										<div class="text-xs text-muted-foreground">360k subscribers</div>
									</div>
									<div class="rounded-full bg-secondary px-3 py-1 text-xs font-semibold">
										Add to list
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ───── REAL FINDINGS ───── -->
	<section class="border-t border-border bg-secondary/30 px-6 py-24 lg:px-12">
		<div class="mx-auto max-w-4xl">
			<div class="mb-12 text-center">
				<h2 class="mb-4 text-3xl font-bold lg:text-5xl">Real Findings We've Discovered</h2>
				<p class="mx-auto max-w-2xl text-lg leading-relaxed text-muted-foreground">
					Here's a small sample from the thousands of validated insights in our system. Each was
					discovered by analyzing real Reddit conversations.
				</p>
			</div>

			<div class="space-y-6">
				<!-- Finding 1 -->
				<div class="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
					<div class="px-5 py-4 lg:px-7 lg:py-5">
						<div class="flex items-start justify-between gap-4">
							<div class="min-w-0 flex-1">
								<div class="mb-2 flex flex-wrap items-center gap-2">
									<span
										class="inline-flex items-center rounded-full border border-orange-500/30 bg-orange-500/10 px-2.5 py-0.5 text-xs font-medium text-orange-500"
										>r/ai_agents</span
									>
									<span class="text-xs text-muted-foreground">6 evidences</span>
								</div>
								<h3 class="text-base font-semibold text-foreground lg:text-lg">
									Browser agents waste tokens on DOM/screenshot navigation
								</h3>
							</div>
							<div class="flex shrink-0 flex-col items-end gap-1">
								<span class="text-2xl font-bold text-orange-500">80</span>
								<span class="text-xs font-medium text-orange-500">Very High</span>
							</div>
						</div>
						<div class="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
							<div class="h-full rounded-full bg-red-500" style="width: 80%"></div>
						</div>
					</div>
					<div class="border-t border-border bg-card/50 px-5 py-5 lg:px-7 lg:py-6">
						<div class="mb-6">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Description
							</p>
							<p class="text-sm leading-relaxed text-foreground/90">
								Users repeatedly flag that browser-based agents waste tokens on
								screenshot-per-action loops and DOM navigation instead of using structured APIs or
								cached workflows.
							</p>
						</div>
						<div class="mb-6">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Context
							</p>
							<p class="text-sm leading-relaxed text-foreground/90">
								AI developers and researchers looking to optimize agent efficiency and reduce token
								costs during automated web tasks.
							</p>
						</div>
						<div class="space-y-3">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Evidence Quotes
							</p>
							<div class="rounded-xl border border-border bg-card p-4">
								<p class="text-sm leading-relaxed text-foreground/80 italic">
									"This is like trying to navigate a city by staring at a satellite photo and
									guessing where the doors are. The problem isn't the 'navigation'—it's that we're
									treating the DOM like a visual puzzle instead of a structured API."
								</p>
							</div>
							<div class="rounded-xl border border-border bg-card p-4">
								<p class="text-sm leading-relaxed text-foreground/80 italic">
									"yes, but the biggest cost isn't navigation clicks, it's the screenshot-per-action
									loop... most browser agents default to vision because it's simpler to build, but
									the real move is hybrid."
								</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Finding 2 -->
				<div class="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
					<div class="px-5 py-4 lg:px-7 lg:py-5">
						<div class="flex items-start justify-between gap-4">
							<div class="min-w-0 flex-1">
								<div class="mb-2 flex flex-wrap items-center gap-2">
									<span
										class="inline-flex items-center rounded-full border border-orange-500/30 bg-orange-500/10 px-2.5 py-0.5 text-xs font-medium text-orange-500"
										>r/LocalLLaMA</span
									>
									<span class="text-xs text-muted-foreground">2 evidences</span>
								</div>
								<h3 class="text-base font-semibold text-foreground lg:text-lg">
									Repetitive Reposting and Duplicate Content Clutter
								</h3>
							</div>
							<div class="flex shrink-0 flex-col items-end gap-1">
								<span class="text-2xl font-bold text-orange-400">62</span>
								<span class="text-xs font-medium text-orange-400">High</span>
							</div>
						</div>
						<div class="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
							<div class="h-full rounded-full bg-orange-500" style="width: 62%"></div>
						</div>
					</div>
					<div class="border-t border-border bg-card/50 px-5 py-5 lg:px-7 lg:py-6">
						<div class="mb-6">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Description
							</p>
							<p class="text-sm leading-relaxed text-foreground/90">
								Users are frustrated by the same news and announcements being reposted constantly,
								cluttering the subreddit and drowning out original, substantive discussion.
							</p>
						</div>
						<div class="mb-6">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Context
							</p>
							<p class="text-sm leading-relaxed text-foreground/90">
								Active community members, hobbyists, and developers who value deep discussions and
								curated original content over repetitive announcements.
							</p>
						</div>
						<div class="space-y-3">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Evidence Quotes
							</p>
							<div class="rounded-xl border border-border bg-card p-4">
								<p class="text-sm leading-relaxed text-foreground/80 italic">
									"Can we stop re-posting the same thing 70 times"
								</p>
							</div>
							<div class="rounded-xl border border-border bg-card p-4">
								<p class="text-sm leading-relaxed text-foreground/80 italic">
									"this like the 350017777333444 time this got posted in a day.. jesus christ"
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>

			<div class="mt-20 text-center">
				<h3 class="mb-6 text-3xl font-bold lg:text-4xl">
					Ready to uncover the hidden needs in your niche?
				</h3>
				<p class="mx-auto mb-8 max-w-2xl text-lg text-muted-foreground">
					Stop guessing what your target audience wants. Let Taren's AI find the exact problems they
					are begging you to solve.
				</p>
				<button
					onclick={() => goto('/register')}
					class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 to-pink-500 px-7 py-3.5 text-base font-semibold text-white shadow-lg shadow-orange-500/25 transition-all hover:from-orange-600 hover:to-pink-600 hover:shadow-orange-500/40"
				>
					Scan your first subreddit free
					<ArrowRight class="h-4 w-4" />
				</button>
			</div>
		</div>
	</section>

	<!-- ───── PRICING TEASER ───── -->
	<section class="border-t border-border px-6 py-24 lg:px-12">
		<div class="mx-auto max-w-3xl text-center">
			<h2 class="mb-4 text-4xl font-bold">Start for free, scale when ready</h2>
			<p class="mb-10 text-lg text-muted-foreground">
				Starter at <span class="font-semibold text-foreground">$15/mo</span> beats every competitor.
				Professional at <span class="font-semibold text-foreground">$39/mo</span> gives you unlimited
				scans.
			</p>
			<div class="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
				<a
					href="/register"
					class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-orange-500 to-pink-500 px-7 py-3.5 text-base font-semibold text-white shadow-lg shadow-orange-500/20 transition-all hover:shadow-orange-500/40"
				>
					Start 14-day free trial
					<ArrowRight class="h-4 w-4" />
				</a>
				<a
					href="/pricing"
					class="inline-flex items-center gap-2 rounded-xl border border-border bg-card px-7 py-3.5 text-base font-semibold text-foreground transition-colors hover:bg-secondary"
				>
					See all plans
				</a>
			</div>
		</div>
	</section>

	<!-- ───── FOOTER ───── -->
	<footer class="border-t border-border px-6 py-10 lg:px-12">
		<div class="mx-auto flex max-w-7xl flex-col items-center gap-3 sm:flex-row sm:justify-between">
			<p class="text-sm font-bold">Taren</p>
			<div class="flex gap-6 text-sm text-muted-foreground">
				<a href="/pricing" class="transition-colors hover:text-foreground">Pricing</a>
				<a href="/login" class="transition-colors hover:text-foreground">Sign in</a>
				<a href="/register" class="transition-colors hover:text-foreground">Get started</a>
			</div>
			<p class="text-sm text-muted-foreground">
				&copy; {new Date().getFullYear()} Taren. All rights reserved.
			</p>
		</div>
	</footer>
</div>
