---
name: aurellion-provider-adapter
description: Build, configure, test, or replace AURELLION model-provider adapters while keeping endpoints, models, and credentials configurable and secure.
---

# AURELLION Provider Adapter

Use the provider-neutral interface in agents/aurellion/runtime/provider.py.

## Workflow
1. Inspect the current provider contract and tests before editing.
2. Keep provider name, HTTPS endpoint, model identifier, exact allowed hostname list, timeout, and API key configurable.
3. Read secrets only from the approved secret manager or injected environment; never commit, print, log, or include them in errors.
4. Require exact hostname allowlisting; reject wildcard hosts, non-HTTPS endpoints, embedded credentials, and unbounded timeouts.
5. Validate message roles and request limits before making a provider call.
6. Keep provider-specific parsing behind the adapter and return the common ModelResponse shape.
7. Add mock-based tests for success, malformed output, timeout, HTTP failure, invalid endpoint, and secret redaction.
8. Run the focused tests and full foundation suite. Report exact test results.

## Boundaries
- Never make a live provider request unless explicitly authorized for the named environment.
- Never activate production as part of adapter development.
- Never infer a model is connected because a config file or environment variable name exists.
- A successful mock test is not proof of provider authentication or live availability.
