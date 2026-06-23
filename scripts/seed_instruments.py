from src.database import SessionLocal
from src.models import Instrument


def seed_instruments():
    db = SessionLocal()

    instruments = [
        {"ticker": "AAPL", "name": "Apple Inc.", "asset_class": "equity", "exchange": "NASDAQ"},
        {"ticker": "MSFT", "name": "Microsoft Corp.", "asset_class": "equity", "exchange": "NASDAQ"},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "asset_class": "equity", "exchange": "NASDAQ"},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "asset_class": "equity", "exchange": "NASDAQ"},
        {"ticker": "NVDA", "name": "NVIDIA Corp.", "asset_class": "equity", "exchange": "NASDAQ"},
        {"ticker": "TSLA", "name": "Tesla Inc.", "asset_class": "equity", "exchange": "NASDAQ"},
        {"ticker": "META", "name": "Meta Platforms Inc.", "asset_class": "equity", "exchange": "NASDAQ"},
        {"ticker": "JPM", "name": "JPMorgan Chase", "asset_class": "equity", "exchange": "NYSE"},
        {"ticker": "SPY", "name": "SPDR S&P 500 ETF", "asset_class": "etf", "exchange": "NYSE"},
        {"ticker": "QQQ", "name": "Invesco QQQ Trust", "asset_class": "etf", "exchange": "NASDAQ"},
        {"ticker": "GLD", "name": "SPDR Gold Shares", "asset_class": "etf", "exchange": "NYSE"},
        {"ticker": "BTC-USD", "name": "Bitcoin", "asset_class": "crypto", "exchange": "Coinbase"},
    ]

    for i in instruments:
        exists = db.query(Instrument).filter(Instrument.ticker == i["ticker"]).first()
        if exists:
            print(f"Already exists: {i['ticker']}")
            continue

        instrument = Instrument(**i)
        db.add(instrument)
        print(f"Added: {i['ticker']}")

    db.commit()
    db.close()
    print("\nDone.")


if __name__ == "__main__":
    seed_instruments()