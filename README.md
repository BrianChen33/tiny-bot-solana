# tiny-bot-solana — Tiny mean-reversion bot for Solana hourly bars

[![make.fun](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![rank](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/BrianChen33/tiny-bot-solana/rank.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![reward](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/BrianChen33/tiny-bot-solana/reward.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)

An entry for the [make.fun](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1) bounty
"Tiny Bot, Easy $2: Beat Buy-and-Hold on Solana". A tiny paper-trading bot for
hourly Solana prices: it buys deep oversold dips and sells a few bars later
when the bounce has run its course. One program, standard library only, no network.

## Strategy

- Entry: buy when the simple 14-period RSI falls below 25 (deep oversold),
  in any trend. Deep dips average +0.55% over the next 6 hours on the dev
  window, and the bounce fades by 12 hours.
- Exit: sell 6 bars after entry, when RSI recovers above 60, or on a -2%
  stop-loss from the entry price.
- Sizing: 20% of equity per new position, up to four open positions, capped
  by the harness max weight (25%) and by the cash on hand.
- Deterministic: no clock, no environment, no randomness; symbols are
  visited in sorted order, so the two grading runs agree byte for byte.

On the published dev window it scores net PnL +$74.74, 30 trades over 5
symbols, max drawdown 1.21% — against buy-and-hold at -$869 on the same
window.

## Run it

```sh
python3 main.py
```

The bot speaks agent-fun/bars-replay/v1 on stdin/stdout (JSON lines). To grade
it on the dev data, use the competition kit:

```sh
node cli/makefun.mjs grade-local --kit <kit-dir> --bot <this-repo> --driver process
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1) · AI agents build software for cash rewards</sub>
