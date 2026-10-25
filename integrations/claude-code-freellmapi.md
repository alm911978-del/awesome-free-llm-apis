# Claude Code with FreeLLMAPI (multi-provider routing)

This guide documents an optional way to connect Claude Code to a local FreeLLMAPI router. It is an integration guide, not a promise of unlimited or guaranteed free inference.

## What it does

[FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) combines free tiers from multiple providers behind a local API endpoint. Its router can select an eligible model and fail over when a provider hits a rate limit or returns a retryable error. It also documents sticky sessions and an optional context-handoff note.

- Project: https://github.com/tashfeenahmed/freellmapi
- Official model catalog: https://freellmapi.co/models
- Official install and deployment guide: https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/install/01-install.md
- Official Claude Code / agent setup guide: https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/01-clients.md

## Important limits

- The upstream project's headline of roughly 7.4 billion tokens/month is an aggregate estimate across listed free-tier provider capacity. It is **not** a guaranteed personal allowance, and individual quotas, regions, model availability, and provider terms vary.
- You generally need to add your own provider API keys. Free tiers may require registration, phone verification, or other eligibility checks.
- The router is open source, but the upstream project describes its same-day/live model catalog as a paid option; the free catalog may lag behind. Check the upstream pricing/docs before relying on a feature.
- Free models are not necessarily Claude models and may differ in coding quality, context handling, tool use, speed, and reliability. Claude Code compatibility through a third-party router does not guarantee identical behavior to Anthropic's official service.
- Never commit provider keys, the unified router key, local database files, or .env files to Git. Keep secrets in local configuration or environment variables.
- Review the upstream code and security policy before sending private source code or sensitive prompts through any third-party router.

## Setup overview

Use the upstream documentation as the source of truth because commands and supported clients can change.

1. Install and start FreeLLMAPI using its official guide: https://github.com/tashfeenahmed/freellmapi#quick-start
2. Open the local dashboard (the upstream quick start currently documents `http://localhost:3001`).
3. Add provider keys for the free tiers you are eligible to use. Confirm the router reports healthy models before continuing.
4. Copy the unified API key from the dashboard. Do not paste it into a public issue, commit, screenshot, or chat.
5. Follow the official Claude Code setup instructions. The upstream README currently documents a setup command in this form:

   ```bash
   npx freellmapi setup-claude --url http://localhost:3001 --api-key <YOUR_UNIFIED_KEY>
   ```

   Replace the placeholder locally. Check the current upstream docs before running commands, and inspect any configuration changes first.
6. To launch Claude Code through the router, consult the upstream CLI instructions. The project currently documents `npx freellmapi launch` as a launcher option.
7. Send a harmless test prompt, then inspect the router dashboard/logs to confirm which provider/model actually served the request and whether fallback occurred.

## Android / Termux

The upstream project describes Android/Termux support as experimental. Do not assume the desktop one-line installer will work unchanged on Android. Check the official Termux guide and confirm Node.js/Docker/runtime requirements before installing. If you have access to a computer, follow the platform-specific desktop/server instructions instead.

## Troubleshooting checklist

- **No model available:** check that at least one provider key is configured, healthy, eligible in your region, and under its current rate limits.
- **429 / quota errors:** wait for the provider's reset or let the router choose another eligible model; failover only works where a compatible, healthy alternative exists.
- **Claude Code behaves differently:** verify the selected model supports the tools, context length, streaming, and Anthropic-compatible API behavior your task needs.
- **A session changes model:** a context-handoff note can help preserve the task summary, but it cannot guarantee that every hidden/internal detail of the original session is transferred.

## Verification status

This repository adds this guide only. It does not install FreeLLMAPI, create provider accounts or keys, start a local server, or verify live inference. Follow the upstream project and test your own setup before relying on it.
