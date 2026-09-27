"""
Works around a known crewai bug: it tags messages with an internal
'cache_breakpoint' key meant only for providers that support prompt
caching (Anthropic, OpenAI). When a request is routed through LiteLLM to
a provider that doesn't support it (like Groq), that key leaks through
and the provider's API rejects the whole request. This strips it out
right before the call leaves for the provider.
"""

import litellm


def _strip_cache_breakpoint(messages):
    if not messages:
        return messages
    cleaned = []
    for m in messages:
        if isinstance(m, dict) and "cache_breakpoint" in m:
            m = {k: v for k, v in m.items() if k != "cache_breakpoint"}
        cleaned.append(m)
    return cleaned


def apply_patch():
    if getattr(litellm, "_cache_breakpoint_patch_applied", False):
        return

    original_completion = litellm.completion
    original_acompletion = litellm.acompletion

    def patched_completion(*args, **kwargs):
        if "messages" in kwargs:
            kwargs["messages"] = _strip_cache_breakpoint(kwargs["messages"])
        return original_completion(*args, **kwargs)

    async def patched_acompletion(*args, **kwargs):
        if "messages" in kwargs:
            kwargs["messages"] = _strip_cache_breakpoint(kwargs["messages"])
        return await original_acompletion(*args, **kwargs)

    litellm.completion = patched_completion
    litellm.acompletion = patched_acompletion
    litellm._cache_breakpoint_patch_applied = True
