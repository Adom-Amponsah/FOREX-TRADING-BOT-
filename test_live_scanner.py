from live_scanner import LiveScanner

scanner = LiveScanner(timeframe_min=15, scan_interval_sec=60, auto_trade=False)
scanner.run()
