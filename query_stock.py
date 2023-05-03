import twstock

print(twstock.codes['2303']) #StockCodeInfo(type='股票', code='2303', name='聯電', ISIN='TW0002303005', start='1985/07/16', market='上市', group='半導體業', CFI='ESVUFR')
stock_6207_real = twstock.realtime.get('2303')
# 抓取多個股票的方式 twstock.realtime.get(['2330', '2337', '2409'])
print(stock_6207_real)
#{'timestamp': 1683091678.0, 'info': {'code': '2303', 'channel': '2303.tw', 'name': '聯電', 'fullname': '聯華電子股份有限公司', 'time': '2023-05-03 13:27:58'}, 
# 'realtime': {'latest_trade_price': '-', 'trade_volume': '-', 'accumulate_trade_volume': '25962', 
# 'best_bid_price': ['50.1000', '50.0000', '49.9500', '49.9000', '49.8500'], 'best_bid_volume': ['2', '6', '1', '24', '69'], 'best_ask_price': ['50.2000', '50.3000', '50.4000', '50.5000', '50.6000'], 'best_ask_volume': ['866', '1269', '1054', '847', '489'], 'open': '49.9000', 'high': '50.2000', 'low': '49.4000'}, 'success': True}

#{'timestamp': 1683091799.0, 'info': {'code': '2303', 'channel': '2303.tw', 'name': '聯電', 'fullname': '聯華電子股份有限公司', 'time': '2023-05-03 13:29:59'}, 
# 'realtime': {'latest_trade_price': '-', 'trade_volume': '-', 'accumulate_trade_volume': '25962', 
# 'best_bid_price': ['49.9000', '49.8500', '49.8000', '49.7500', '49.7000'], 'best_bid_volume': ['36', '83', '121', '74', '410'], 'best_ask_price': ['49.9500', '50.0000', '50.1000', '50.2000', '50.3000'], 'best_ask_volume': ['279', '988', '1839', '1625', '1408'], 'open': '49.9000', 'high': '50.2000', 'low': '49.4000'}, 'success': True}

#{'timestamp': 1683091800.0, 'info': {'code': '2303', 'channel': '2303.tw', 'name': '聯電', 'fullname': '聯華電子股份有限公司', 'time': '2023-05-03 13:30:00'}, 
# 'realtime': {'latest_trade_price': '49.9500', 'trade_volume': '2616', 'accumulate_trade_volume': '28578', 
# 'best_bid_price': ['49.9000', '49.8500', '49.8000', '49.7500', '49.7000'], 'best_bid_volume': ['36', '83', '121', '74', '410'], 'best_ask_price': ['49.9500', '50.0000', '50.1000', '50.2000', '50.3000'], 'best_ask_volume': ['295', '988', '1810', '1629', '1408'], 'open': '49.9000', 'high': '50.2000', 'low': '49.4000'}, 'success': True}