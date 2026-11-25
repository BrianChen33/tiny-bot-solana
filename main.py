"""Tiny momentum bot for make.fun: EMA-crossover paper trading on Solana hourly bars.

Protocol: agent-fun/bars-replay/v1, spoken as newline-delimited JSON on stdin
(hello, batch, done) and stdout (one reply per batch). Standard library only.

Strategy: for each symbol, hold it while its fast EMA sits above its slow EMA
and exit to cash when the fast EMA falls below the slow EMA. New positions are
sized at an equal share of equity, capped by the harness max weight and by the
cash on hand. Deterministic: no clock, no environment, no randomness, and the
symbols are visited in sorted order so the two grading runs agree byte for
byte.
"""

import json
import sys

FAST = 12
SLOW = 26
RSI_LEN = 14
RSI_BUY = 40
RSI_SELL = 70
BPS = 10_000
MIN_NOTIONAL = 1_000_000
MAX_SLIPPAGE_BPS = 100


def ema(values, period):
    """Exponential moving average of a list of closes, seeded on the first."""
    k = 2.0 / (period + 1)
    e = float(values[0])
    for v in values[1:]:
        e = v * k + e * (1.0 - k)
    return e


def rsi(values, period):
    """Relative strength index over the last `period` bars (Wilder smoothing
    approximated by a simple mean of gains and losses)."""
    if len(values) < period + 1:
        return None
    gains = 0.0
    losses = 0.0
    for i in range(len(values) - period, len(values)):
        d = values[i] - values[i - 1]
        if d > 0:
            gains += d
        else:
            losses -= d
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def decide(symbols, capital, caps, warmup_bars, seq, cash, equity, positions, latest, history):
    """Orders for this batch, as wire order dicts."""
    if seq < warmup_bars:
        return []
    orders = []
    spent = 0
    quote_scale = int(capital["quote_scale"])
    max_weight = int(caps["max_weight_bps"])
    for sym in sorted(symbols):
        closes = history.get(sym, [])
        if len(closes) < SLOW + 1:
            continue
        info = symbols[sym]
        price_scale = int(info["price_scale"])
        qty_scale = int(info["qty_scale"])
        fast = ema(closes, FAST)
        slow = ema(closes, SLOW)
        held = positions.get(sym, 0)
        # Trend + oscillator: only enter when the trend is up AND the
        # oscillator says the asset is oversold (buy the dip in an uptrend).
        # Exit when the trend flips or the oscillator says overbought.
        r = rsi(closes, RSI_LEN)
        if r is None:
            continue
        if fast > slow and r < RSI_BUY and held <= 0:
            # Trend up and oversold: buy an equal share of equity.
            held_value = 0
            room = max_weight * equity // BPS - held_value
            spend = min(room, equity // len(symbols), cash - spent)
            if spend >= MIN_NOTIONAL:
                orders.append({
                    "side": "buy",
                    "symbol": sym,
                    "notional_quote_units": spend,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                })
                spent += spend
        elif (fast < slow or r > RSI_SELL) and held > 0:
            # Trend down and long: exit the whole position.
            orders.append({
                "side": "sell",
                "symbol": sym,
                "qty": held,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            })
    return orders


def main():
    symbols = {}
    capital = {}
    caps = {}
    warmup_bars = 0
    cash = 0
    equity = 0
    positions = {}
    latest = {}
    history = {}
    next_cid = 1

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        kind = msg.get("type")
        if kind == "hello":
            symbols = {s["symbol"]: s for s in msg["symbols"]}
            capital = msg["capital"]
            caps = msg["caps"]
            warmup_bars = int(msg.get("warmup_bars", 0))
            cash = int(capital["quote_units"])
            equity = cash
            positions = {}
            latest = {}
            history = {s: [] for s in symbols}
            continue
        if kind == "batch":
            seq = int(msg["seq"])
            for bar in msg["bars"]:
                sym = bar["symbol"]
                latest[sym] = bar
                history.setdefault(sym, []).append(int(bar["c"]))
            acct = msg["account"]
            cash = int(acct["cash_quote_units"])
            equity = int(acct["equity_quote_units"])
            positions = {}
            for p in acct["positions"]:
                positions[p["symbol"]] = int(p["qty"])
            orders = decide(symbols, capital, caps, warmup_bars, seq, cash, equity,
                            positions, latest, history)
            for o in orders:
                if "client_id" not in o:
                    o["client_id"] = "o%d" % next_cid
                    next_cid += 1
                # Wire amounts are u64 decimal strings, not numbers.
                if "notional_quote_units" in o:
                    o["notional_quote_units"] = str(o["notional_quote_units"])
                if "qty" in o:
                    o["qty"] = str(o["qty"])
            reply = {"type": "reply", "seq": seq, "orders": orders}
            sys.stdout.write(json.dumps(reply, separators=(",", ":")) + "\n")
            sys.stdout.flush()
            continue
        if kind == "done":
            return


if __name__ == "__main__":
    main()
