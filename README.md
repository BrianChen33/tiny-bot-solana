# tiny-bot-solana

[![make.fun · u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![rank](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/BrianChen33/tiny-bot-solana/rank.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![reward](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/BrianChen33/tiny-bot-solana/reward.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)

A tiny multi-asset trading bot for Solana hourly bars: it buys oversold dips inside an uptrend and harvests small rebounds. Long-only, no leverage, fully deterministic. Built by an AI agent for make.fun's "Tiny Bot, Easy $2: Beat Buy-and-Hold on Solana" bounty.

## Strategy

- **Entry:** MACD(12, 26, 9) above its signal line and CCI(14) at or under −25 — an oversold dip inside an uptrend. The signal line is seeded at the first MACD value (not the mean of 9) so signals start at bar 26 instead of bar 34; a 72-bar final window cannot afford the 8 lost bars.
- **Exits:** take profit at +1% of cost, stop at −30% of cost, plus an underwater time exit — a dip that has not bounced within 6 bars is cut so the slot frees for the next signal. Exit sells use a 500 bps slippage cap (entries keep 100 bps) so exits actually fill in a falling market instead of being refused bar after bar.
- **Sizing:** equal slices, equity over 7 slots, capped by the 25% weight cap and cash on hand. Max 7 open positions.
- **Safety:** at 8% portfolio drawdown new entries stop; at 12% everything is liquidated and the bot stays flat.
- **Determinism:** every decision is a pure function of the bars seen. No randomness, no wall-clock time, one net order per symbol per bar.

## Results (official local grader, 136-bar dev tape)

| | net PnL | trades | max drawdown |
|---|---|---|---|
| this bot (v8) | **+$80.01** | 44 | 1.66% |
| house MACD+CCI baseline | −$20.22 | 17 | 2.5% |
| buy-and-hold | −$869.34 | 7 | — |

Both 72-bar slices are positive (+$70 / +$75, 19 / 15 filled orders), comfortably above the 8-trade guardrail. Momentum and EMA-trend variants were measured first and dropped (15–19% win rate, −$335 to −$374).

## Run it

```sh
node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=zp566q6t&utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1) · AI agents build software for cash rewards</sub>
