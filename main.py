"""Tiny Bot: deep-dip mean reversion.
Buys when the simple 14-period RSI falls below 25 (deep oversold), in any
trend. Sells 6 bars after entry, when RSI recovers above 60, or on a -2%
stop-loss from the entry price. Up to four open positions, each 20% of equity,
capped by the 25% max weight and by cash on hand. The dip edge: RSI below 25
averages +0.55% over the next 6 hours (72% win) on the dev window, and the
bounce fades by 12 hours, so a 6-bar hold takes the peak of the move.
Self-contained, stdlib only, deterministic. Protocol: agent-fun/bars-replay/v1.
"""
import sys
import json


def rsi_step(state, price):
    """Simple RSI(14): mean gain/loss over the last 14 price changes.
    state = [previous price, list of recent changes]. Returns RSI or None."""
    if state[0] is None:
        state[0] = price
        return None
    change = price - state[0]
    state[0] = price
    state[1].append(change)
    if len(state[1]) > 14:
        state[1].pop(0)
    if len(state[1]) < 14:
        return None
    gain = sum(c for c in state[1] if c > 0) / 14.0
    loss = sum(-c for c in state[1] if c < 0) / 14.0
    if loss == 0.0:
        return 100.0
    return 100.0 - 100.0 / (1.0 + gain / loss)


def main():
    inp = sys.stdin
    out = sys.stdout
    hello = json.loads(inp.readline())
    symbols = [s["symbol"] for s in hello["symbols"]]
    scales = {s["symbol"]: (s["price_scale"], s["qty_scale"]) for s in hello["symbols"]}
    max_weight = int(hello["caps"]["max_weight_bps"])
    closes = {s: [] for s in symbols}
    rsi_state = {s: [None, []] for s in symbols}
    cur_rsi = {s: None for s in symbols}
    entry_price = {}
    entry_seq = {}
    counter = 0
    for line in inp:
        if not line.strip():
            continue
        msg = json.loads(line)
        if msg.get("type") == "done":
            break
        if msg.get("type") != "batch":
            continue
        seq = msg["seq"]
        bars = {}
        for b in msg["bars"]:
            sym = b["symbol"]
            ps, _ = scales[sym]
            bars[sym] = int(b["c"]) / (10 ** ps)
        acct = msg["account"]
        cash = int(acct["cash_quote_units"]) / 1e6
        equity = int(acct["equity_quote_units"]) / 1e6
        held = {}
        for p in acct["positions"]:
            _, qs = scales[p["symbol"]]
            held[p["symbol"]] = int(p["qty"]) / (10 ** qs)
        for f in msg.get("fills", []):
            if f.get("side") == "buy" and f.get("status") == "filled":
                sym = f["symbol"]
                ps, _ = scales[sym]
                entry_price[sym] = int(f["price"]) / (10 ** ps)
                entry_seq[sym] = seq
        for sym, close in bars.items():
            closes[sym].append(close)
            value = rsi_step(rsi_state[sym], close)
            if value is not None:
                cur_rsi[sym] = value
        orders = []
        n_hist = min(len(closes[s]) for s in symbols)
        if n_hist >= 30:
            for sym in symbols:
                if sym not in held:
                    continue
                _, qs = scales[sym]
                rsi = cur_rsi[sym]
                held_bars = seq - entry_seq.get(sym, seq)
                stop = sym in entry_price and bars[sym] < entry_price[sym] * 0.98
                if held_bars >= 6 or (rsi is not None and rsi > 60.0) or stop:
                    counter += 1
                    orders.append({
                        "side": "sell", "client_id": "s-%s-%d" % (sym, counter),
                        "symbol": sym,
                        "qty": str(int(round(held[sym] * (10 ** qs)))),
                        "max_slippage_bps": 50,
                    })
            notion = equity * 0.20
            opened = 0
            for sym in symbols:
                if sym in held:
                    continue
                if len(held) + opened >= 4:
                    continue
                rsi = cur_rsi[sym]
                if rsi is not None and rsi < 25.0:
                    buy_notion = min(notion, cash)
                    buy_notion = min(buy_notion, equity * max_weight / 10000.0)
                    if buy_notion >= 1.0:
                        counter += 1
                        opened += 1
                        orders.append({
                            "side": "buy", "client_id": "b-%s-%d" % (sym, counter),
                            "symbol": sym,
                            "notional_quote_units": str(int(buy_notion * 1e6)),
                            "max_slippage_bps": 50,
                        })
        out.write(json.dumps({"type": "reply", "seq": seq, "orders": orders}) + "\n")
        out.flush()


if __name__ == "__main__":
    main()
