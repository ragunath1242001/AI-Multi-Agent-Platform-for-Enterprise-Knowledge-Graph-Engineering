FROM node:22-alpine AS deps
WORKDIR /repo
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY frontend/package.json ./frontend/package.json
RUN corepack enable && corepack prepare pnpm@9.12.0 --activate && pnpm --dir frontend install --frozen-lockfile

FROM node:22-alpine AS builder
WORKDIR /repo
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
COPY --from=deps /repo/node_modules ./node_modules
COPY --from=deps /repo/frontend/node_modules ./frontend/node_modules
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY frontend ./frontend
RUN corepack enable && corepack prepare pnpm@9.12.0 --activate && pnpm --dir frontend build

FROM node:22-alpine AS runner
WORKDIR /repo
ENV NODE_ENV=production
COPY --from=builder /repo/node_modules ./node_modules
COPY --from=builder /repo/frontend/node_modules ./frontend/node_modules
COPY --from=builder /repo/frontend/.next ./frontend/.next
COPY --from=builder /repo/frontend/public ./frontend/public
COPY --from=builder /repo/frontend/package.json ./frontend/package.json
EXPOSE 3000
CMD ["sh", "-c", "corepack enable && corepack prepare pnpm@9.12.0 --activate && pnpm --dir frontend start"]
