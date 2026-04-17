# =============================================================================
# Frontend – Dockerfile (Vite, multi-stage)
# =============================================================================

# ── Stage 1: Build ───────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

# Copy Vite config and HTML entry point
COPY vite.config.js ./
COPY index.html ./

# Copy source and static assets
COPY src/ ./src/
# public/ is optional in Vite – copy only if it exists
COPY public* ./public/

RUN npm run build

# ── Stage 2: Serve with vite preview ────────────────────────────────────────
# vite preview correctly handles SPA fallback (returns index.html for 404s)
FROM node:20-alpine AS runner

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
COPY --from=builder /app/vite.config.js ./

EXPOSE 3000

CMD ["npm", "run", "preview"]
