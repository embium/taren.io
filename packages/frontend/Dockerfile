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

# Copy entire workspace structure to preserve pnpm symlinks
WORKDIR /workspace
COPY --from=builder /workspace ./

# Set working directory to frontend package
WORKDIR /workspace/packages/frontend

# Create a non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S sveltekit -u 1001

# Change ownership
RUN chown -R sveltekit:nodejs /workspace

# Switch to non-root user
USER sveltekit

# Expose the port
EXPOSE 3000

# Environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Start the application from the frontend directory
CMD ["node", "build"]
