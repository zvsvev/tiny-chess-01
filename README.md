# tiny-chess-01 — fresh rebuild

A 4 KB Python chess engine for make.fun's tiny-chess-01 competition,
rebuilt in-session from the design brief in REBUILD.md (not committed:
it exceeds the snapshot's per-file cap).

- 0x88 board, PVS + 262,144-entry TT + null-move pruning (R=4) + LMR
  + killer/history ordering, PeSTO middlegame evaluation.
- Fixed 60,000-node budget per move; deterministic, no clock.
- `src.py` is the readable source; `main.py` is the packed entrypoint
  (3,734 bytes), produced by the kit's compress command only.
- Perft verified on all 5 standard positions; practice trial-0 Elo
  to be recorded here after the run.
