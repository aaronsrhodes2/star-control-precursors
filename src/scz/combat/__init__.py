"""Combat module — 1v1 ship melee + super-melee picker.

Slice scope: each side fields one ship. Both sides can be AI-driven (the
canonical auto-fight default) or player-driven. The static decision
function in `combat/ai.py` flies any ship; per-personality variation is
deferred per the variation-architecture commitment. Stat blocks in
`combat/ships.py` mirror the canon stat tables in
[ship-roster.md](../../../references/lore/ship-roster.md).
"""
