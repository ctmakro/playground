wg = '''<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container">
  <div class="asdf">{}</div>
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
  {{
  "symbol": "{}",
  "width": "280",
  "height": "280",
  "locale": "en",
  "dateRange": "{}",
  "colorTheme": "light",
  "trendLineColor": "#37a6ef",
  "underLineColor": "#e3f2fd",
  "isTransparent": false,
  "autosize": false,
  "largeChartUrl": ""
}}
  </script>
</div>
<!-- TradingView Widget END -->'''


print('''
<style>
.tradingview-widget-container{
    display:inline-block;
    margin:5px;
}
.asdf { text-align:center;}
</style>''')

items = '1/FX_IDC:CNYUSD,FOREXCOM:XAUUSD/31.1034807/FX_IDC:CNYUSD,INDEX:HSI,GOOGL,AAPL'.split(',')
names = 'USD/CNY,CNY/g,HSI,Google,Apple'.split(',')
dataranges = '12m,1m'.split(',')

for n,i in zip(names,items):
    for d in dataranges:
        print(wg.format(n+(' ({})'.format(d)), i, d))
