# Multi-stage Dockerfile for SvelteKit with adapter-node (Monorepo)
# Build from workspace root: docker build -f packages/frontend/Dockerfile -t taren-frontend .

FROM node:20-alpine AS builder

# Enable pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# Set working directory to workspace root
WORKDIR /workspace

# Copy workspace configuration files
COPY pnpm-workspace.yaml pnpm-lock.yaml package.json ./

# Copy all packages (needed for monorepo dependency resolution)
COPY packages ./packages

# Install all dependencies
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

# Build the frontend package (use path-based filter since package name is "taren.io")
RUN pnpm --filter=./packages/frontend run build

# Production stage
FROM node:20-alpine AS runner

# Enable pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# Copy package.json from frontend
COPY --from=builder /workspace/packages/frontend/package.json ./package.json

# Copy workspace node_modules (pnpm hoists dependencies here)
COPY --from=builder /workspace/node_modules ./node_modules

# Copy frontend's node_modules (may contain package-specific dependencies)
COPY --from=builder /workspace/packages/frontend/node_modules ./node_modules/.pnpm/node_modules

# Copy built application from builder
COPY --from=builder /workspace/packages/frontend/build ./build

# Create a non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S sveltekit -u 1001

# Change ownership
RUN chown -R sveltekit:nodejs /app

# Switch to non-root user
USER sveltekit

# Expose the port
EXPOSE 3000

# Environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Start the application
CMD ["node", "build"]
