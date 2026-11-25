# tiny-bot-solana — Tiny momentum bot for Solana hourly bars

[![make.fun](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![rank](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/BrianChen33/tiny-bot-solana/rank.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)
[![reward](https://make.fun/badge/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1/BrianChen33/tiny-bot-solana/reward.svg)](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1)

An entry for the [make.fun](https://make.fun/bounty/u-gorun-gadget-tiny-bot-easy-2-beat-a48f3ce1) bounty
"Tiny Bot, Easy $2: Beat Buy-and-Hold on Solana". A tiny paper-trading bot for
hourly Solana prices: it holds an asset while its trend is up and its RSI says
oversold (buy the dip in an uptrend), and exits to cash when the trend flips
or the RSI says overbought. One program, standard library only, no network.

## Strategy

- Trend: EMA(12) above EMA(26) means uptrend.
- Entry: in an uptrend, buy when RSI(14) falls below 40 (oversold dip).
- Exit: sell when EMA(12) falls below EMA(26), or RSI(14) rises above 70.
- Sizing: an equal share of equity per new position, capped by the harness
  max weight (25%) and by the cash on hand.
- Deterministic: no clock, no environment, no randomness; symbols are
  visited in sorted order, so the two grading runs agree byte for byte.

On the published dev window it scores a small positive net PnL (+$0.56),
12 trades over 5 symbols, max drawdown 0.75% — against buy-and-hold at
-$869 on the same window.

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
