"""Dialog system: LLM-rendered surface text over a deterministic FSM.

The runtime FSM and character data live here; LLM integration will be
added in a later commit to render the canned `npc_text` and choice
labels with per-species voice. For now we use the canned text as the
final output — the framework is correct and the LLM is just the
final render-layer to swap in.
"""
