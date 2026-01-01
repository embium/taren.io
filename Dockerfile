# Multi-stage Dockerfile for SvelteKit with adapter-node
FROM node:20-alpine AS builder

# Enable pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Install dependencies
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile

# Copy application source
COPY . .

# Build the application
RUN pnpm run build

# Production stage
FROM node:20-alpine AS runner

# Enable pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# Copy package files for production dependencies
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Install only production dependencies
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --prod --frozen-lockfile

# Copy built application from builder stage
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./package.json

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
