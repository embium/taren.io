<script lang="ts">
	import Navigation from '$lib/components/Navigation.svelte';
	import { goto } from '$app/navigation';
	import { Search, Brain, BarChart2, Zap, ArrowRight, CheckCircle2 } from '@lucide/svelte';
</script>

<svelte:head>
	<title>Taren — Discover What People Really Want</title>
	<meta name="description" content="Taren scrapes Reddit and uses AI to surface hidden pain points in any community. Find your next product idea in minutes, not months." />
</svelte:head>

<div class="min-h-screen bg-background text-foreground">
	<Navigation />

	<!-- ───── HERO ───── -->
	<section class="relative overflow-hidden px-6 pb-24 pt-24 lg:px-12 lg:pb-36 lg:pt-32">
		<!-- Subtle radial glow — adapts to dark/light via opacity -->
		<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
			<div class="h-[600px] w-[600px] rounded-full bg-orange-500/10 blur-3xl dark:bg-orange-500/5"></div>
		</div>

		<div class="relative mx-auto max-w-4xl text-center">
			<p class="mb-5 inline-flex items-center gap-2 rounded-full border border-orange-500/30 bg-orange-500/10 px-4 py-1.5 text-sm font-medium text-orange-500">
				<Zap class="h-3.5 w-3.5" />
				AI-powered Reddit market research
			</p>

			<h1 class="mb-6 text-5xl font-bold tracking-tight text-foreground lg:text-7xl">
				Discover what people
				<span class="bg-gradient-to-r from-orange-500 to-pink-500 bg-clip-text text-transparent">
					actually struggle with
				</span>
			</h1>

			<p class="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-muted-foreground lg:text-xl">
				Taren scrapes Reddit communities and applies AI analysis to surface real, validated pain points — so you can build products people are already asking for.
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

			<p class="mt-5 text-sm text-muted-foreground">14-day free trial · No card charged until trial ends</p>
		</div>
	</section>

	<!-- ───── HOW IT WORKS ───── -->
	<section class="border-t border-border px-6 py-24 lg:px-12">
		<div class="mx-auto max-w-5xl">
			<div class="mb-16 text-center">
				<h2 class="mb-4 text-4xl font-bold lg:text-5xl">How it works</h2>
				<p class="mx-auto max-w-xl text-lg text-muted-foreground">Three steps from subreddit to insight</p>
			</div>

			<div class="grid gap-8 md:grid-cols-3">
				<!-- Step 1 -->
				<div class="group relative flex flex-col rounded-2xl border border-border bg-card p-7 transition-all hover:border-orange-500/40 hover:shadow-lg hover:shadow-orange-500/5">
					<div class="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-orange-500/10 ring-1 ring-orange-500/20">
						<Search class="h-6 w-6 text-orange-500" />
					</div>
					<div class="mb-2 flex items-center gap-3">
						<span class="text-xs font-bold text-orange-500 uppercase tracking-widest">Step 1</span>
					</div>
					<h3 class="mb-2 text-xl font-semibold">Pick your subreddits</h3>
					<p class="text-sm leading-relaxed text-muted-foreground">
						Enter any subreddit name — a niche community, a competitor's audience, or a broad topic. Taren handles up to 10 subreddits per scan.
					</p>
				</div>

				<!-- Step 2 -->
				<div class="group relative flex flex-col rounded-2xl border border-border bg-card p-7 transition-all hover:border-orange-500/40 hover:shadow-lg hover:shadow-orange-500/5">
					<div class="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-pink-500/10 ring-1 ring-pink-500/20">
						<Brain class="h-6 w-6 text-pink-500" />
					</div>
					<div class="mb-2">
						<span class="text-xs font-bold text-pink-500 uppercase tracking-widest">Step 2</span>
					</div>
					<h3 class="mb-2 text-xl font-semibold">AI analyses the comments</h3>
					<p class="text-sm leading-relaxed text-muted-foreground">
						Our AI reads thousands of posts and comments, looking for recurring frustrations, unmet needs, and hidden opportunities — ranked by severity.
					</p>
				</div>

				<!-- Step 3 -->
				<div class="group relative flex flex-col rounded-2xl border border-border bg-card p-7 transition-all hover:border-orange-500/40 hover:shadow-lg hover:shadow-orange-500/5">
					<div class="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500/10 ring-1 ring-indigo-500/20">
						<BarChart2 class="h-6 w-6 text-indigo-500" />
					</div>
					<div class="mb-2">
						<span class="text-xs font-bold text-indigo-500 uppercase tracking-widest">Step 3</span>
					</div>
					<h3 class="mb-2 text-xl font-semibold">Get actionable results</h3>
					<p class="text-sm leading-relaxed text-muted-foreground">
						Review pain points with real evidence quotes, severity scores, and target audience breakdowns. Export your findings as CSV or PDF.
					</p>
				</div>
			</div>
		</div>
	</section>

	<!-- ───── SOCIAL PROOF / PAIN POINTS PREVIEW ───── -->
	<section class="border-t border-border bg-secondary/30 px-6 py-24 lg:px-12">
		<div class="mx-auto max-w-5xl">
			<div class="grid items-center gap-12 lg:grid-cols-2">
				<div>
					<p class="mb-3 text-sm font-semibold uppercase tracking-widest text-orange-500">Real results</p>
					<h2 class="mb-5 text-4xl font-bold leading-tight">Stop guessing what to build next</h2>
					<p class="mb-8 text-lg text-muted-foreground leading-relaxed">
						Founders and product teams use Taren to validate ideas before writing a single line of code.
						Instead of months of interviews, get evidence-backed pain points in minutes.
					</p>
					<ul class="space-y-3">
						{#each [
							'Validated pain points with real comment evidence',
							'Severity scores so you prioritize the right problems',
							'Target audience breakdown per pain point',
							'Export results to share with your team',
						] as point}
							<li class="flex items-start gap-3">
								<CheckCircle2 class="mt-0.5 h-5 w-5 shrink-0 text-orange-500" />
								<span class="text-muted-foreground">{point}</span>
							</li>
						{/each}
					</ul>
					<button
						onclick={() => goto('/register')}
						class="mt-8 inline-flex items-center gap-2 rounded-xl bg-foreground px-6 py-3 text-sm font-semibold text-background transition-opacity hover:opacity-80"
					>
						Try it free
						<ArrowRight class="h-4 w-4" />
					</button>
				</div>

				<!-- Mock results card -->
				<div class="rounded-2xl border border-border bg-card p-6 shadow-xl shadow-foreground/5">
					<p class="mb-4 text-xs font-semibold uppercase tracking-widest text-muted-foreground">Example pain point</p>
					<div class="mb-4 flex items-center justify-between">
						<h4 class="font-semibold text-foreground">No affordable automation tools for solopreneurs</h4>
						<span class="ml-3 shrink-0 rounded-full bg-red-500/10 px-2.5 py-0.5 text-xs font-bold text-red-400">Severity 87</span>
					</div>
					<p class="mb-5 text-sm text-muted-foreground leading-relaxed">
						Users in r/Entrepreneur frequently express frustration that existing automation platforms are priced for enterprises, leaving solo operators unable to afford them.
					</p>
					<div class="space-y-2">
						<p class="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Evidence</p>
						{#each [
							'"I tried Zapier but $50/month is ridiculous for 5 zaps…"',
							'"Why is there nothing in the $5–15/month range that actually works?"',
						] as quote}
							<div class="rounded-lg border border-border bg-secondary/50 px-3 py-2">
								<p class="text-xs italic text-muted-foreground">{quote}</p>
							</div>
						{/each}
					</div>
					<div class="mt-4 flex items-center gap-2">
						<span class="rounded-full border border-orange-500/30 bg-orange-500/10 px-2.5 py-0.5 text-xs font-medium text-orange-500">r/Entrepreneur</span>
						<span class="text-xs text-muted-foreground">· Target: Solo founders</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ───── PRICING TEASER ───── -->
	<section class="border-t border-border px-6 py-24 lg:px-12">
		<div class="mx-auto max-w-3xl text-center">
			<h2 class="mb-4 text-4xl font-bold">Start for free, scale when ready</h2>
			<p class="mb-10 text-lg text-muted-foreground">
				Starter at <span class="font-semibold text-foreground">$15/mo</span> beats every competitor.
				Professional at <span class="font-semibold text-foreground">$39/mo</span> gives you unlimited scans.
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
		<div class="mx-auto max-w-7xl flex flex-col items-center gap-3 sm:flex-row sm:justify-between">
			<p class="text-sm font-bold">Taren</p>
			<div class="flex gap-6 text-sm text-muted-foreground">
				<a href="/pricing" class="hover:text-foreground transition-colors">Pricing</a>
				<a href="/login" class="hover:text-foreground transition-colors">Sign in</a>
				<a href="/register" class="hover:text-foreground transition-colors">Get started</a>
			</div>
			<p class="text-sm text-muted-foreground">&copy; {new Date().getFullYear()} Taren. All rights reserved.</p>
		</div>
	</footer>
</div>
