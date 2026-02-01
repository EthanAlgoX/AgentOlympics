# Root Dockerfile - Builds the Frontend by default
# This allows Railway to deploy the website without changing Root Directory settings.

FROM node:20-alpine AS base

FROM base AS deps
WORKDIR /app
# Copy only frontend package files to install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
# Copy the frontend source code
COPY frontend ./
# Copy public assets if any (though they are inside frontend usually)

ENV NEXT_TELEMETRY_DISABLED 1

# Build the frontend
RUN npm run build

FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built assets from builder
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
