# Multi-stage Dockerfile for SvelteKit with adapter-node (Monorepo)
# Build from workspace root: docker build -f packages/frontend/Dockerfile -t taren-frontend .

FROM node:20-alpine AS builder

# Enable pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# Set working directory
WORKDIR /app

# Copy workspace files
COPY pnpm-workspace.yaml ./
COPY pnpm-lock.yaml ./
COPY package.json ./

# Copy frontend package.json
COPY packages/frontend/package.json ./packages/frontend/

# Install dependencies (entire workspace to resolve internal dependencies)
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

# Copy frontend source
COPY packages/frontend ./packages/frontend

# Build the application
WORKDIR /app/packages/frontend
RUN pnpm run build

# Production stage
FROM node:20-alpine AS runner

# Enable pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# Copy workspace files for production install
COPY pnpm-workspace.yaml ./
COPY pnpm-lock.yaml ./
COPY package.json ./
COPY packages/frontend/package.json ./packages/frontend/

# Install only production dependencies
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --prod --frozen-lockfile --filter=frontend

# Copy built application from builder stage
COPY --from=builder /app/packages/frontend/build ./build
COPY --from=builder /app/packages/frontend/package.json ./package.json

# Create a non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S sveltekit -u 1001

# Change ownership of the app directory  
RUN chown -R sveltekit:nodejs /app

# Switch to non-root user
USER sveltekit

# Expose the port the app runs on
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Start the application
CMD ["node", "build"]
