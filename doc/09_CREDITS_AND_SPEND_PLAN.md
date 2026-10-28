# Cloud credits and spend plan

**Balances reported by Krishna on October 28, 2026:** $150 Meta Model API, $100 Baseten, and $100 Modal. These are reported balances, not verified account terms. Before running workloads, check each credit's expiration, eligible product categories, and whether overage can reach a payment method. Credits are a ceiling, not a target to exhaust.

## Give each provider one job

| Provider | WallSense role | Do not use it for |
| --- | --- | --- |
| **Meta — $150** | SensorGPT: tool-calling assistant that answers questions using event results, quality flags, and evaluation limits. This is the product's Meta model integration. | CSI training, every-frame inference, raw CSI uploads, or duplicating a second agent. |
| **Modal — $100** | On-demand API/replay or bounded batch evaluation if local hosting or compute is a bottleneck. Prefer short-lived functions that scale to zero. | Running the same model endpoint already hosted on Baseten, keeping idle compute warm without a demo need, or uploading the full dataset. |
| **Baseten — $100** | Optional hosted CSI-classifier endpoint after robustness review; compare its predictions and latency with local inference. | A duplicate Meta chatbot or an always-on deployment used only to consume credits. |

Meta offers a Responses API with tool calling. As checked October 28, 2026, its published standard Muse Spark rate is $1.25 per million input tokens and $4.25 per million output tokens; account-specific credit and mode terms still govern actual use. Meta's billing interface shown during setup indicated that content may be used for product improvement while free credits are in use. Send only minimal derived event evidence, never raw CSI, private correspondence, API keys, or personal data. Review [API protocols](https://dev.meta.ai/docs/protocols), [tool calling](https://dev.meta.ai/docs/tool-calling), and [pricing and rate limits](https://dev.meta.ai/docs/pricing-rate-limits).

Modal Functions can scale to zero when idle, and Modal bills compute while containers load or process inputs; confirm the credit covers the particular resource before running it. See [Modal pricing](https://modal.com/pricing), [Functions](https://modal.com/docs/guide/functions), and [billing](https://modal.com/docs/guide/billing).

Baseten offers hosted model APIs and custom deployments. Dedicated replicas incur per-minute charges while running; zero replicas avoid GPU charges, though startup time is billable. A Model API budget does not automatically cap dedicated inference or training. Check the live account usage and stop deployments after measurement. See [Baseten overview](https://docs.baseten.co/overview) and [autoscaling](https://docs.baseten.co/deployment/autoscaling/overview).

## Staged usage targets

These are spending limits for experiments, not promises that the credits will be spent. Stop early if a test does not improve a judge-visible part of the demo.

### Meta: target up to $30 before the demo is stable

1. Up to **$1** for one connectivity smoke test; record model ID, latency, token usage, and remaining credit.
2. Up to **$6** for the tool loop: retrieve one event, its model result and signal-quality flags, then explain evidence and limits.
3. Up to **$18** for a fixed evaluation set of 50–100 questions, including uncertain cases and prompts that try to elicit unsupported falls or vital signs.
4. Up to **$5** for final demo rehearsals and retries.
5. Keep **$120** available for later if needed. Do not invoke the model on every replay frame.

### Modal: target up to $30 before the demo is stable

1. Up to **$5** for a small deployment smoke test using synthetic or derived event records.
2. Up to **$15** for a timed replay/API rehearsal and bounded batch evaluation if local compute is a bottleneck.
3. Up to **$10** for final rehearsal only if the Modal service is part of the final demo.
4. Keep **$70** available. Set a shutdown time, inspect usage afterward, and verify the service has scaled to zero.

### Baseten: target up to $25 until model robustness is established

1. **$0 until robustness review.** Wallhack occupancy/motion performance is weak; its model is not ready to represent reliable presence detection.
2. Up to **$5** for a classifier endpoint smoke test if the CSI-Bench model remains promising after additional group/domain checks.
3. Up to **$15** for a measured comparison of cold start, steady-state latency, failures, and prediction agreement with local inference.
4. Up to **$5** for a final rehearsal only if the endpoint improves demo reliability.
5. Keep **$75** available. If it only duplicates the Modal service, skip this deployment.

The current CSI-Bench result is a small, incomplete user-held-out pilot, not a generalization guarantee. Do not deploy it just because its first pilot score is high. The current Wallhack no-presence recall is poor, so do not call that lane reliable occupancy sensing.

## Operating rules

- Keep `MODEL_API_KEY`, `BASETEN_API_KEY`, and Modal credentials in ignored local environment files; never commit credentials or place them in frontend code, screenshots, or the demo video.
- Cache stable evaluation-scope facts locally. Send event IDs, selected feature summaries, scores, quality flags, and limits, not raw time-series arrays.
- Log provider, model ID, request ID, token counts or compute duration, latency, and estimated charge with secrets redacted.
- After each experiment, compare the account balance before and after; stop if free credits are not applied or usage could bill a payment method.
- Record beginning balance, spend, ending balance, and experiment purpose in a private work log. Never commit private account screenshots or correspondence.
- Stop workloads when measurements are complete. Use remaining credits only for a useful evaluation, robust demo run, or measured deployment comparison; leave them unused if no useful experiment remains.
