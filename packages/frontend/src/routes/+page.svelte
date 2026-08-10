<script lang="ts">
	import Navigation from '$lib/components/Navigation.svelte';
	import { goto } from '$app/navigation';
	import { Search, Brain, BarChart2, Zap, ArrowRight, CheckCircle2 } from '@lucide/svelte';

	let analysisType = $state<'template' | 'custom'>('template');
	let selectedTemplateId = $state('pain_points');
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

	<!-- ───── AI ANALYSIS MODES ───── -->
	<section class="relative overflow-hidden border-t border-border px-6 py-24 lg:px-12">
		<div
			class="pointer-events-none absolute top-1/2 left-1/2 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-indigo-500/10 blur-[100px]"
		></div>

		<div class="relative z-10 mx-auto max-w-6xl">
			<div class="grid items-center gap-16 lg:grid-cols-2">
				<div class="order-1 lg:order-2">
					<div
						class="mb-4 inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-semibold tracking-wide text-indigo-500 uppercase"
					>
						<Brain class="h-3.5 w-3.5" />
						Precision Control
					</div>
					<h2 class="mb-6 text-3xl leading-tight font-bold lg:text-4xl">
						Tell the AI exactly what <br /><span
							class="bg-gradient-to-r from-indigo-500 to-pink-500 bg-clip-text text-transparent"
							>you are looking for.</span
						>
					</h2>
					<p class="mb-8 text-lg leading-relaxed text-muted-foreground">
						Whether you want a broad overview of pain points or have a highly specific hypothesis to
						validate, Taren's scanning engine adapts to your needs.
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
							<span
								><strong class="text-foreground">Pre-built Templates:</strong> Instantly scan for pain
								points, feature requests, competitor complaints, or buying advice.</span
							>
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
							<span
								><strong class="text-foreground">Custom Instructions:</strong> Write your own prompt to
								uncover highly niche data specific to your product.</span
							>
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
							<span
								><strong class="text-foreground">Contextual Relevance:</strong> The AI ranks findings based
								on how well they match your exact objective.</span
							>
						</li>
					</ul>
				</div>

				<div class="order-2 lg:order-1">
					<div class="relative rounded-2xl border border-border bg-card p-4 shadow-2xl">
						<!-- Subtle background glow behind the interactive card -->
						<div
							class="absolute -bottom-6 -left-6 h-32 w-32 rounded-full bg-indigo-500/20 blur-2xl"
						></div>

						<div
							class="rounded-xl border border-border/50 bg-background/50 pb-2 backdrop-blur-sm"
						>
							<div class="flex items-center justify-between border-b border-border px-5 py-4">
								<p class="text-xs font-bold tracking-wider text-muted-foreground uppercase">
									Analysis Objective
								</p>
								<div class="flex items-center gap-1 rounded-lg bg-secondary p-1">
									<button
										class="rounded-md px-3 py-1 text-xs font-medium transition-colors {analysisType ===
										'template'
											? 'bg-background text-foreground shadow-sm'
											: 'text-muted-foreground hover:text-foreground'}"
										onclick={() => (analysisType = 'template')}
									>
										Template
									</button>
									<button
										class="rounded-md px-3 py-1 text-xs font-medium transition-colors {analysisType ===
										'custom'
											? 'bg-background text-foreground shadow-sm'
											: 'text-muted-foreground hover:text-foreground'}"
										onclick={() => (analysisType = 'custom')}
									>
										Custom
									</button>
								</div>
							</div>

							<div class="min-h-[220px] p-5">
								{#if analysisType === 'template'}
									<div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
										<button
											class="flex flex-col rounded-lg border p-3 text-left transition-colors {selectedTemplateId ===
											'pain_points'
												? 'border-indigo-500 bg-indigo-500/5'
												: 'border-border bg-background hover:border-indigo-500/30'}"
											onclick={() => (selectedTemplateId = 'pain_points')}
										>
											<span
												class="text-sm font-semibold {selectedTemplateId === 'pain_points'
													? 'text-indigo-500'
													: ''}">Pain Points</span
											>
											<span class="mt-1 text-xs text-muted-foreground"
												>Identify recurring frustrations and problems users face.</span
											>
										</button>
										<button
											class="flex flex-col rounded-lg border p-3 text-left transition-colors {selectedTemplateId ===
											'feature_requests'
												? 'border-indigo-500 bg-indigo-500/5'
												: 'border-border bg-background hover:border-indigo-500/30'}"
											onclick={() => (selectedTemplateId = 'feature_requests')}
										>
											<span
												class="text-sm font-semibold {selectedTemplateId === 'feature_requests'
													? 'text-indigo-500'
													: ''}">Feature Requests</span
											>
											<span class="mt-1 text-xs text-muted-foreground"
												>Discover what solutions or tools users are actively asking for.</span
											>
										</button>
										<button
											class="flex flex-col rounded-lg border p-3 text-left transition-colors {selectedTemplateId ===
											'competitor'
												? 'border-indigo-500 bg-indigo-500/5'
												: 'border-border bg-background hover:border-indigo-500/30'}"
											onclick={() => (selectedTemplateId = 'competitor')}
										>
											<span
												class="text-sm font-semibold {selectedTemplateId === 'competitor'
													? 'text-indigo-500'
													: ''}">Competitor Complaints</span
											>
											<span class="mt-1 text-xs text-muted-foreground"
												>Find out what people dislike about existing alternatives.</span
											>
										</button>
										<button
											class="flex flex-col rounded-lg border p-3 text-left transition-colors {selectedTemplateId ===
											'buying'
												? 'border-indigo-500 bg-indigo-500/5'
												: 'border-border bg-background hover:border-indigo-500/30'}"
											onclick={() => (selectedTemplateId = 'buying')}
										>
											<span
												class="text-sm font-semibold {selectedTemplateId === 'buying'
													? 'text-indigo-500'
													: ''}">Buying Advice</span
											>
											<span class="mt-1 text-xs text-muted-foreground"
												>Analyze criteria users consider when purchasing products.</span
											>
										</button>
									</div>
								{:else}
									<div class="flex h-full flex-col">
										<textarea
											placeholder="E.g., Find mentions of what software developers dislike about Jira's ticket management..."
											rows="5"
											class="flex-1 w-full resize-none rounded-lg border border-indigo-500/50 bg-indigo-500/5 px-4 py-3 text-sm text-foreground placeholder-indigo-500/50 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
										></textarea>
										<div class="mt-4 flex items-start gap-2 text-xs text-muted-foreground">
											<Brain class="h-4 w-4 shrink-0 text-indigo-500" />
											<span>The AI will specifically hunt for discussions matching this exact prompt in the selected subreddits.</span>
										</div>
									</div>
								{/if}
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
										>r/ChatGPT</span
									>
									<span class="text-xs text-muted-foreground">6 evidences</span>
								</div>
								<h3 class="text-base font-semibold text-foreground lg:text-lg">
									Climate Crisis Without Effective Action
								</h3>
							</div>
							<div class="flex shrink-0 flex-col items-end gap-1">
								<span class="text-2xl font-bold text-red-500">94</span>
								<span class="text-xs font-medium text-red-500">Very High</span>
							</div>
						</div>
						<div class="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
							<div class="h-full rounded-full bg-red-500" style="width: 94%"></div>
						</div>
					</div>
					<div class="border-t border-border bg-card/50 px-5 py-5 lg:px-7 lg:py-6">
						<div class="mb-6">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Description
							</p>
							<p class="text-sm leading-relaxed text-foreground/90">
								Users describe worsening heat, drought, ocean warming, and ecosystem damage while feeling that governments and institutions are failing to respond at the necessary scale.
							</p>
						</div>
						<div class="mb-6">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Context
							</p>
							<p class="text-sm leading-relaxed text-foreground/90">
								People experiencing visible climate impacts—drought, heat waves, ocean temperatures—feel anger and fatalism over what they perceive as inadequate policy responses focused on individual behavior rather than major emitters.
							</p>
						</div>
						<div class="space-y-3">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Evidence Quotes
							</p>
							<div class="rounded-xl border border-border bg-card p-4">
								<p class="text-sm leading-relaxed text-foreground/80 italic">
									"It hasn't rained since early June where I am and the fields genuinely look like the Savannah. It's awful. Our weather is known as cold, wet and rainy, so where tf is any of that?"
								</p>
							</div>
							<div class="rounded-xl border border-border bg-card p-4">
								<p class="text-sm leading-relaxed text-foreground/80 italic">
									"Yet much of the world isn't treating this as the crisis that it is. Do they think this will clear up by next year? next decade?"
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
										>r/YouTubers</span
									>
									<span class="text-xs text-muted-foreground">2 evidences</span>
								</div>
								<h3 class="text-base font-semibold text-foreground lg:text-lg">
									EU Packaging Rules Feel Punitive to Small Sellers
								</h3>
							</div>
							<div class="flex shrink-0 flex-col items-end gap-1">
								<span class="text-2xl font-bold text-orange-400">79</span>
								<span class="text-xs font-medium text-orange-400">High</span>
							</div>
						</div>
						<div class="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
							<div class="h-full rounded-full bg-orange-500" style="width: 79%"></div>
						</div>
					</div>
					<div class="border-t border-border bg-card/50 px-5 py-5 lg:px-7 lg:py-6">
						<div class="mb-6">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Description
							</p>
							<p class="text-sm leading-relaxed text-foreground/90">
								Small European merchants fear PPWR compliance costs and unclear enforcement disproportionately burden them compared to larger retailers who can absorb expenses.
							</p>
						</div>
						<div class="mb-6">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Context
							</p>
							<p class="text-sm leading-relaxed text-foreground/90">
								Regulatory ambiguity around PPWR obligations is pushing independent EU sellers toward market restrictions or withdrawal, threatening cross-border ecommerce viability and product availability.
							</p>
						</div>
						<div class="space-y-3">
							<p class="mb-2 text-xs font-bold tracking-wide text-muted-foreground uppercase">
								Evidence Quotes
							</p>
							<div class="rounded-xl border border-border bg-card p-4">
								<p class="text-sm leading-relaxed text-foreground/80 italic">
									"Registering in each individual country,paying some fixed fees when we might not even have a single sale feels completely ridiculous for a small independent label with a limited budget."
								</p>
							</div>
							<div class="rounded-xl border border-border bg-card p-4">
								<p class="text-sm leading-relaxed text-foreground/80 italic">
									"Nobody knows, really. It seems they put this regulation out without thinking about small and local businesses."
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
