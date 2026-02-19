/* ============================================================
   Global Markets Data
   Comprehensive market/exchange data for all regions
   ============================================================ */

const GLOBAL_MARKETS = {
    "North America": {
        "United States": {
            exchanges: [
                { name: "NYSE", suffix: "", desc: "New York Stock Exchange" },
                { name: "NASDAQ", suffix: "", desc: "Nasdaq Stock Market" },
                { name: "AMEX", suffix: "", desc: "American Stock Exchange" },
            ],
            tickers: [
                { symbol: "AAPL", name: "Apple Inc." },
                { symbol: "MSFT", name: "Microsoft Corp." },
                { symbol: "GOOGL", name: "Alphabet Inc." },
                { symbol: "AMZN", name: "Amazon.com Inc." },
                { symbol: "META", name: "Meta Platforms" },
                { symbol: "TSLA", name: "Tesla Inc." },
                { symbol: "NVDA", name: "NVIDIA Corp." },
                { symbol: "JPM", name: "JPMorgan Chase" },
                { symbol: "SPY", name: "S&P 500 ETF" },
                { symbol: "QQQ", name: "Nasdaq 100 ETF" },
            ],
            currency: "USD",
        },
        "Canada": {
            exchanges: [
                { name: "TSX", suffix: ".TO", desc: "Toronto Stock Exchange" },
                { name: "TSX-V", suffix: ".V", desc: "TSX Venture Exchange" },
            ],
            tickers: [
                { symbol: "RY.TO", name: "Royal Bank of Canada" },
                { symbol: "TD.TO", name: "Toronto-Dominion Bank" },
                { symbol: "ENB.TO", name: "Enbridge Inc." },
                { symbol: "CNR.TO", name: "Canadian National Railway" },
                { symbol: "BNS.TO", name: "Bank of Nova Scotia" },
                { symbol: "SU.TO", name: "Suncor Energy" },
                { symbol: "CP.TO", name: "Canadian Pacific Kansas City" },
                { symbol: "BMO.TO", name: "Bank of Montreal" },
            ],
            currency: "CAD",
        },
        "Mexico": {
            exchanges: [
                { name: "BMV", suffix: ".MX", desc: "Bolsa Mexicana de Valores" },
            ],
            tickers: [
                { symbol: "AMXB.MX", name: "America Movil" },
                { symbol: "WALMEX.MX", name: "Walmart de Mexico" },
                { symbol: "FEMSAUBD.MX", name: "FEMSA" },
                { symbol: "GFNORTEO.MX", name: "Banorte" },
                { symbol: "TLEVISACPO.MX", name: "Televisa" },
                { symbol: "CEMEXCPO.MX", name: "CEMEX" },
            ],
            currency: "MXN",
        },
    },
    "South America": {
        "Brazil": {
            exchanges: [
                { name: "B3 / Bovespa", suffix: ".SA", desc: "Brasil Bolsa Balcao" },
            ],
            tickers: [
                { symbol: "PETR4.SA", name: "Petrobras" },
                { symbol: "VALE3.SA", name: "Vale S.A." },
                { symbol: "ITUB4.SA", name: "Itau Unibanco" },
                { symbol: "BBDC4.SA", name: "Bradesco" },
                { symbol: "ABEV3.SA", name: "Ambev" },
                { symbol: "BBAS3.SA", name: "Banco do Brasil" },
                { symbol: "WEGE3.SA", name: "WEG S.A." },
                { symbol: "RENT3.SA", name: "Localiza" },
            ],
            currency: "BRL",
        },
        "Argentina": {
            exchanges: [
                { name: "BCBA", suffix: ".BA", desc: "Buenos Aires Stock Exchange" },
            ],
            tickers: [
                { symbol: "GGAL.BA", name: "Grupo Financiero Galicia" },
                { symbol: "YPF.BA", name: "YPF S.A." },
                { symbol: "BMA.BA", name: "Banco Macro" },
                { symbol: "PAM.BA", name: "Pampa Energia" },
                { symbol: "CEPU.BA", name: "Central Puerto" },
            ],
            currency: "ARS",
        },
        "Chile": {
            exchanges: [
                { name: "BCS", suffix: ".SN", desc: "Bolsa de Comercio de Santiago" },
            ],
            tickers: [
                { symbol: "SQM-B.SN", name: "SQM" },
                { symbol: "COPEC.SN", name: "Empresas Copec" },
                { symbol: "LTM.SN", name: "LATAM Airlines" },
                { symbol: "BSANTANDER.SN", name: "Banco Santander Chile" },
            ],
            currency: "CLP",
        },
        "Colombia": {
            exchanges: [
                { name: "BVC", suffix: ".CL", desc: "Bolsa de Valores de Colombia" },
            ],
            tickers: [
                { symbol: "ECOPETROL.CL", name: "Ecopetrol" },
                { symbol: "PFBCOLOM.CL", name: "Bancolombia" },
                { symbol: "ISA.CL", name: "ISA S.A." },
            ],
            currency: "COP",
        },
    },
    "Europe": {
        "United Kingdom": {
            exchanges: [
                { name: "LSE", suffix: ".L", desc: "London Stock Exchange" },
            ],
            tickers: [
                { symbol: "SHEL.L", name: "Shell plc" },
                { symbol: "AZN.L", name: "AstraZeneca" },
                { symbol: "HSBA.L", name: "HSBC Holdings" },
                { symbol: "VOD.L", name: "Vodafone Group" },
                { symbol: "ULVR.L", name: "Unilever" },
                { symbol: "BP.L", name: "BP plc" },
                { symbol: "GSK.L", name: "GSK plc" },
                { symbol: "RIO.L", name: "Rio Tinto" },
            ],
            currency: "GBP",
        },
        "Germany": {
            exchanges: [
                { name: "XETRA", suffix: ".DE", desc: "Frankfurt Stock Exchange" },
            ],
            tickers: [
                { symbol: "SAP.DE", name: "SAP SE" },
                { symbol: "SIE.DE", name: "Siemens AG" },
                { symbol: "ALV.DE", name: "Allianz SE" },
                { symbol: "DTE.DE", name: "Deutsche Telekom" },
                { symbol: "BAS.DE", name: "BASF SE" },
                { symbol: "MBG.DE", name: "Mercedes-Benz Group" },
                { symbol: "BMW.DE", name: "BMW AG" },
                { symbol: "VOW3.DE", name: "Volkswagen AG" },
            ],
            currency: "EUR",
        },
        "France": {
            exchanges: [
                { name: "Euronext Paris", suffix: ".PA", desc: "Euronext Paris" },
            ],
            tickers: [
                { symbol: "MC.PA", name: "LVMH" },
                { symbol: "OR.PA", name: "L'Oreal" },
                { symbol: "TTE.PA", name: "TotalEnergies" },
                { symbol: "SAN.PA", name: "Sanofi" },
                { symbol: "AIR.PA", name: "Airbus SE" },
                { symbol: "BNP.PA", name: "BNP Paribas" },
            ],
            currency: "EUR",
        },
        "Switzerland": {
            exchanges: [
                { name: "SIX", suffix: ".SW", desc: "SIX Swiss Exchange" },
            ],
            tickers: [
                { symbol: "NESN.SW", name: "Nestle" },
                { symbol: "NOVN.SW", name: "Novartis" },
                { symbol: "ROG.SW", name: "Roche" },
                { symbol: "UBSG.SW", name: "UBS Group" },
                { symbol: "ZURN.SW", name: "Zurich Insurance" },
            ],
            currency: "CHF",
        },
        "Netherlands": {
            exchanges: [
                { name: "Euronext Amsterdam", suffix: ".AS", desc: "Euronext Amsterdam" },
            ],
            tickers: [
                { symbol: "ASML.AS", name: "ASML Holding" },
                { symbol: "INGA.AS", name: "ING Group" },
                { symbol: "PHIA.AS", name: "Philips" },
                { symbol: "UNA.AS", name: "Unilever (NL)" },
            ],
            currency: "EUR",
        },
        "Spain": {
            exchanges: [
                { name: "BME", suffix: ".MC", desc: "Bolsa de Madrid" },
            ],
            tickers: [
                { symbol: "SAN.MC", name: "Banco Santander" },
                { symbol: "TEF.MC", name: "Telefonica" },
                { symbol: "IBE.MC", name: "Iberdrola" },
                { symbol: "ITX.MC", name: "Inditex" },
                { symbol: "BBVA.MC", name: "BBVA" },
            ],
            currency: "EUR",
        },
        "Italy": {
            exchanges: [
                { name: "Borsa Italiana", suffix: ".MI", desc: "Milan Stock Exchange" },
            ],
            tickers: [
                { symbol: "ENI.MI", name: "ENI S.p.A." },
                { symbol: "ISP.MI", name: "Intesa Sanpaolo" },
                { symbol: "ENEL.MI", name: "Enel S.p.A." },
                { symbol: "UCG.MI", name: "UniCredit" },
                { symbol: "STLAM.MI", name: "Stellantis" },
            ],
            currency: "EUR",
        },
        "Sweden": {
            exchanges: [
                { name: "Nasdaq Stockholm", suffix: ".ST", desc: "Stockholm Stock Exchange" },
            ],
            tickers: [
                { symbol: "ERIC-B.ST", name: "Ericsson" },
                { symbol: "VOLV-B.ST", name: "Volvo" },
                { symbol: "ATCO-A.ST", name: "Atlas Copco" },
                { symbol: "HM-B.ST", name: "H&M" },
            ],
            currency: "SEK",
        },
        "Norway": {
            exchanges: [
                { name: "Oslo Bors", suffix: ".OL", desc: "Oslo Stock Exchange" },
            ],
            tickers: [
                { symbol: "EQNR.OL", name: "Equinor" },
                { symbol: "DNB.OL", name: "DNB Bank" },
                { symbol: "TEL.OL", name: "Telenor" },
            ],
            currency: "NOK",
        },
    },
    "Asia": {
        "India": {
            exchanges: [
                { name: "NSE", suffix: ".NS", desc: "National Stock Exchange of India" },
                { name: "BSE", suffix: ".BO", desc: "Bombay Stock Exchange" },
            ],
            tickers: [
                { symbol: "RELIANCE.NS", name: "Reliance Industries" },
                { symbol: "TCS.NS", name: "Tata Consultancy Services" },
                { symbol: "INFY.NS", name: "Infosys" },
                { symbol: "HDFCBANK.NS", name: "HDFC Bank" },
                { symbol: "ICICIBANK.NS", name: "ICICI Bank" },
                { symbol: "HINDUNILVR.NS", name: "Hindustan Unilever" },
                { symbol: "ITC.NS", name: "ITC Limited" },
                { symbol: "SBIN.NS", name: "State Bank of India" },
                { symbol: "BHARTIARTL.NS", name: "Bharti Airtel" },
                { symbol: "WIPRO.NS", name: "Wipro" },
                { symbol: "LT.NS", name: "Larsen & Toubro" },
                { symbol: "TATAMOTORS.NS", name: "Tata Motors" },
                { symbol: "ADANIENT.NS", name: "Adani Enterprises" },
                { symbol: "HCLTECH.NS", name: "HCL Technologies" },
                { symbol: "RELIANCE.BO", name: "Reliance (BSE)" },
                { symbol: "TCS.BO", name: "TCS (BSE)" },
            ],
            currency: "INR",
        },
        "Japan": {
            exchanges: [
                { name: "TSE", suffix: ".T", desc: "Tokyo Stock Exchange" },
            ],
            tickers: [
                { symbol: "7203.T", name: "Toyota Motor" },
                { symbol: "6758.T", name: "Sony Group" },
                { symbol: "9984.T", name: "SoftBank Group" },
                { symbol: "6861.T", name: "Keyence" },
                { symbol: "8306.T", name: "Mitsubishi UFJ Financial" },
                { symbol: "9432.T", name: "Nippon Telegraph & Telephone" },
                { symbol: "6501.T", name: "Hitachi" },
                { symbol: "4502.T", name: "Takeda Pharmaceutical" },
                { symbol: "7267.T", name: "Honda Motor" },
                { symbol: "8035.T", name: "Tokyo Electron" },
            ],
            currency: "JPY",
        },
        "China": {
            exchanges: [
                { name: "SSE", suffix: ".SS", desc: "Shanghai Stock Exchange" },
                { name: "SZSE", suffix: ".SZ", desc: "Shenzhen Stock Exchange" },
                { name: "HKEX", suffix: ".HK", desc: "Hong Kong Stock Exchange" },
            ],
            tickers: [
                { symbol: "9988.HK", name: "Alibaba Group" },
                { symbol: "0700.HK", name: "Tencent Holdings" },
                { symbol: "3690.HK", name: "Meituan" },
                { symbol: "9618.HK", name: "JD.com" },
                { symbol: "1299.HK", name: "AIA Group" },
                { symbol: "0005.HK", name: "HSBC Holdings (HK)" },
                { symbol: "2318.HK", name: "Ping An Insurance" },
                { symbol: "600519.SS", name: "Kweichow Moutai" },
                { symbol: "601318.SS", name: "Ping An (Shanghai)" },
                { symbol: "000858.SZ", name: "Wuliangye Yibin" },
            ],
            currency: "HKD / CNY",
        },
        "South Korea": {
            exchanges: [
                { name: "KRX", suffix: ".KS", desc: "Korea Exchange" },
                { name: "KOSDAQ", suffix: ".KQ", desc: "KOSDAQ" },
            ],
            tickers: [
                { symbol: "005930.KS", name: "Samsung Electronics" },
                { symbol: "000660.KS", name: "SK Hynix" },
                { symbol: "035420.KS", name: "Naver Corp." },
                { symbol: "035720.KS", name: "Kakao Corp." },
                { symbol: "051910.KS", name: "LG Chem" },
                { symbol: "006400.KS", name: "Samsung SDI" },
                { symbol: "005380.KS", name: "Hyundai Motor" },
                { symbol: "068270.KS", name: "Celltrion" },
            ],
            currency: "KRW",
        },
        "Taiwan": {
            exchanges: [
                { name: "TWSE", suffix: ".TW", desc: "Taiwan Stock Exchange" },
            ],
            tickers: [
                { symbol: "2330.TW", name: "TSMC" },
                { symbol: "2317.TW", name: "Hon Hai Precision (Foxconn)" },
                { symbol: "2454.TW", name: "MediaTek" },
                { symbol: "2382.TW", name: "Quanta Computer" },
                { symbol: "2308.TW", name: "Delta Electronics" },
            ],
            currency: "TWD",
        },
        "Singapore": {
            exchanges: [
                { name: "SGX", suffix: ".SI", desc: "Singapore Exchange" },
            ],
            tickers: [
                { symbol: "D05.SI", name: "DBS Group" },
                { symbol: "O39.SI", name: "OCBC Bank" },
                { symbol: "U11.SI", name: "UOB" },
                { symbol: "Z74.SI", name: "Singtel" },
                { symbol: "C6L.SI", name: "Singapore Airlines" },
            ],
            currency: "SGD",
        },
        "Thailand": {
            exchanges: [
                { name: "SET", suffix: ".BK", desc: "Stock Exchange of Thailand" },
            ],
            tickers: [
                { symbol: "PTT.BK", name: "PTT Public Company" },
                { symbol: "AOT.BK", name: "Airports of Thailand" },
                { symbol: "SCB.BK", name: "Siam Commercial Bank" },
                { symbol: "CPALL.BK", name: "CP ALL" },
            ],
            currency: "THB",
        },
        "Malaysia": {
            exchanges: [
                { name: "Bursa Malaysia", suffix: ".KL", desc: "Bursa Malaysia" },
            ],
            tickers: [
                { symbol: "1155.KL", name: "Maybank" },
                { symbol: "3182.KL", name: "Genting" },
                { symbol: "1295.KL", name: "Public Bank" },
                { symbol: "4863.KL", name: "Telekom Malaysia" },
            ],
            currency: "MYR",
        },
        "Indonesia": {
            exchanges: [
                { name: "IDX", suffix: ".JK", desc: "Indonesia Stock Exchange" },
            ],
            tickers: [
                { symbol: "BBCA.JK", name: "Bank Central Asia" },
                { symbol: "BBRI.JK", name: "Bank Rakyat Indonesia" },
                { symbol: "TLKM.JK", name: "Telkom Indonesia" },
                { symbol: "ASII.JK", name: "Astra International" },
                { symbol: "BMRI.JK", name: "Bank Mandiri" },
            ],
            currency: "IDR",
        },
        "Philippines": {
            exchanges: [
                { name: "PSE", suffix: ".PS", desc: "Philippine Stock Exchange" },
            ],
            tickers: [
                { symbol: "SM.PS", name: "SM Investments" },
                { symbol: "ALI.PS", name: "Ayala Land" },
                { symbol: "BDO.PS", name: "BDO Unibank" },
                { symbol: "TEL.PS", name: "PLDT Inc." },
            ],
            currency: "PHP",
        },
        "Vietnam": {
            exchanges: [
                { name: "HOSE", suffix: ".VN", desc: "Ho Chi Minh Stock Exchange" },
            ],
            tickers: [
                { symbol: "VNM.VN", name: "Vinamilk" },
                { symbol: "VIC.VN", name: "Vingroup" },
                { symbol: "VHM.VN", name: "Vinhomes" },
                { symbol: "FPT.VN", name: "FPT Corporation" },
            ],
            currency: "VND",
        },
        "Israel": {
            exchanges: [
                { name: "TASE", suffix: ".TA", desc: "Tel Aviv Stock Exchange" },
            ],
            tickers: [
                { symbol: "TEVA.TA", name: "Teva Pharmaceutical" },
                { symbol: "LUMI.TA", name: "Bank Leumi" },
                { symbol: "POLI.TA", name: "Bank Hapoalim" },
                { symbol: "ICL.TA", name: "ICL Group" },
            ],
            currency: "ILS",
        },
        "Saudi Arabia": {
            exchanges: [
                { name: "Tadawul", suffix: ".SR", desc: "Saudi Stock Exchange" },
            ],
            tickers: [
                { symbol: "2222.SR", name: "Saudi Aramco" },
                { symbol: "1120.SR", name: "Al Rajhi Bank" },
                { symbol: "2010.SR", name: "SABIC" },
                { symbol: "7010.SR", name: "STC" },
            ],
            currency: "SAR",
        },
    },
    "Africa": {
        "South Africa": {
            exchanges: [
                { name: "JSE", suffix: ".JO", desc: "Johannesburg Stock Exchange" },
            ],
            tickers: [
                { symbol: "NPN.JO", name: "Naspers" },
                { symbol: "SOL.JO", name: "Sasol" },
                { symbol: "SBK.JO", name: "Standard Bank" },
                { symbol: "FSR.JO", name: "FirstRand" },
                { symbol: "AGL.JO", name: "Anglo American" },
                { symbol: "BIL.JO", name: "BHP Group (SA)" },
                { symbol: "MTN.JO", name: "MTN Group" },
                { symbol: "VOD.JO", name: "Vodacom Group" },
            ],
            currency: "ZAR",
        },
        "Nigeria": {
            exchanges: [
                { name: "NGX", suffix: ".LG", desc: "Nigerian Exchange" },
            ],
            tickers: [
                { symbol: "DANGCEM.LG", name: "Dangote Cement" },
                { symbol: "GTCO.LG", name: "Guaranty Trust" },
                { symbol: "ZENITHBANK.LG", name: "Zenith Bank" },
                { symbol: "MTNN.LG", name: "MTN Nigeria" },
                { symbol: "AIRTELAFR.LG", name: "Airtel Africa" },
            ],
            currency: "NGN",
        },
        "Egypt": {
            exchanges: [
                { name: "EGX", suffix: ".CA", desc: "Egyptian Exchange" },
            ],
            tickers: [
                { symbol: "COMI.CA", name: "Commercial International Bank" },
                { symbol: "HRHO.CA", name: "Hermes Holding" },
                { symbol: "TMGH.CA", name: "Talaat Moustafa Group" },
                { symbol: "SWDY.CA", name: "Elsewedy Electric" },
            ],
            currency: "EGP",
        },
        "Kenya": {
            exchanges: [
                { name: "NSE", suffix: ".NR", desc: "Nairobi Securities Exchange" },
            ],
            tickers: [
                { symbol: "SCOM.NR", name: "Safaricom" },
                { symbol: "EQTY.NR", name: "Equity Group" },
                { symbol: "KCB.NR", name: "KCB Group" },
                { symbol: "EABL.NR", name: "East African Breweries" },
            ],
            currency: "KES",
        },
        "Morocco": {
            exchanges: [
                { name: "Casablanca SE", suffix: ".CS", desc: "Casablanca Stock Exchange" },
            ],
            tickers: [
                { symbol: "IAM.CS", name: "Maroc Telecom" },
                { symbol: "ATW.CS", name: "Attijariwafa Bank" },
                { symbol: "BCP.CS", name: "Banque Centrale Populaire" },
            ],
            currency: "MAD",
        },
    },
    "Oceania": {
        "Australia": {
            exchanges: [
                { name: "ASX", suffix: ".AX", desc: "Australian Securities Exchange" },
            ],
            tickers: [
                { symbol: "BHP.AX", name: "BHP Group" },
                { symbol: "CBA.AX", name: "Commonwealth Bank" },
                { symbol: "CSL.AX", name: "CSL Limited" },
                { symbol: "NAB.AX", name: "National Australia Bank" },
                { symbol: "WBC.AX", name: "Westpac Banking" },
                { symbol: "ANZ.AX", name: "ANZ Group" },
                { symbol: "WES.AX", name: "Wesfarmers" },
                { symbol: "FMG.AX", name: "Fortescue" },
                { symbol: "RIO.AX", name: "Rio Tinto (AU)" },
                { symbol: "TLS.AX", name: "Telstra" },
            ],
            currency: "AUD",
        },
        "New Zealand": {
            exchanges: [
                { name: "NZX", suffix: ".NZ", desc: "New Zealand Exchange" },
            ],
            tickers: [
                { symbol: "FPH.NZ", name: "Fisher & Paykel Healthcare" },
                { symbol: "SPK.NZ", name: "Spark New Zealand" },
                { symbol: "AIR.NZ", name: "Air New Zealand" },
                { symbol: "MEL.NZ", name: "Meridian Energy" },
                { symbol: "AIA.NZ", name: "Auckland International Airport" },
            ],
            currency: "NZD",
        },
    },
};
