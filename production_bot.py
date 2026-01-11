from live_scanner import LiveScanner
import argparse

def main():
    parser = argparse.ArgumentParser(description='Gold Trading Bot')
    parser.add_argument('--auto', action='store_true', help='Enable auto-trading (DEMO ONLY)')
    parser.add_argument('--timeframe', type=int, default=15, help='Timeframe in minutes')
    parser.add_argument('--interval', type=int, default=60, help='Scan interval in seconds')
    
    args = parser.parse_args()
    
    if args.auto:
        print("⚠️  WARNING: Auto-trading enabled")
        print("⚠️  Ensure you're using a DEMO account")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted")
            return
    
    scanner = LiveScanner(
        timeframe_min=args.timeframe,
        scan_interval_sec=args.interval,
        auto_trade=args.auto
    )
    
    scanner.run()

if __name__ == "__main__":
    main()
