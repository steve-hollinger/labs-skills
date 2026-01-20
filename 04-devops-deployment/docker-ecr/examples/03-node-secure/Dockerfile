# Example 3: Secure Node.js Production Image
# Demonstrates security hardening and production best practices

# ==============================================================================
# Build Stage
# ==============================================================================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including dev) for build
RUN npm ci

# Copy source code
COPY . .

# Build the application (if using TypeScript or bundler)
# RUN npm run build

# ==============================================================================
# Production Dependencies Stage
# ==============================================================================
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# ==============================================================================
# Runtime Stage
# ==============================================================================
FROM node:20-alpine AS runtime

# Add labels
LABEL maintainer="labs-skills" \
      version="1.0.0" \
      description="Secure Node.js production image"

# Install dumb-init for proper signal handling
# tini is an alternative: apk add --no-cache tini
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -u 1001 -S nodejs -G nodejs

# Set working directory
WORKDIR /app

# Set NODE_ENV
ENV NODE_ENV=production \
    PORT=3000

# Copy production dependencies from deps stage
COPY --from=deps --chown=nodejs:nodejs /app/node_modules ./node_modules

# Copy application code from builder
COPY --from=builder --chown=nodejs:nodejs /app/server.js ./
COPY --from=builder --chown=nodejs:nodejs /app/package.json ./

# Switch to non-root user
USER nodejs

# Document port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Use dumb-init as PID 1 for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Run the application
CMD ["node", "server.js"]
