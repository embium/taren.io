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

# Build the frontend package
RUN pnpm --filter=frontend build

# Production stage
FROM node:20-alpine AS runner

# Enable pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# Copy workspace files
COPY pnpm-workspace.yaml pnpm-lock.yaml package.json ./

# Copy only frontend package.json
COPY --from=builder /workspace/packages/frontend/package.json ./packages/frontend/package.json

# Install only production dependencies for frontend
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --prod --frozen-lockfile --filter=frontend

# Copy built application from builder
COPY --from=builder /workspace/packages/frontend/build ./build

# Copy static assets and other necessary files
COPY --from=builder /workspace/packages/frontend/package.json ./package.json

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
