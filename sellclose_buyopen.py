from System import *
from QuantConnect import *
from QuantConnect.Data import *
from QuantConnect.Algorithm import *
from QuantConnect.Indicators import *

### <summary>
### Demonstration algorthm for the Warm Up feature with basic indicators.
### </summary>
### <meta name="tag" content="indicators" />
### <meta name="tag" content="warm up" />
### <meta name="tag" content="history and warm up" />
### <meta name="tag" content="using data" />
class WarmupAlgorithm(QCAlgorithm):

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2015,10,8)   #Set Start Date
        self.SetEndDate(2015,11,11)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        self.resolution=Resolution.Minute
        
        # Find more symbols here: http://quantconnect.com/data
        
        symbols = [ ]
        z=['AAPL', 'AXP', 'BA', 'CAT', 'CSCO', 'CVX', 'DD',
                           'DIS', 'GE', 'GS', 'HD', 'IBM', 'INTC', 'JPM',
                           'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'PFE',
                           'PG', 'TRV', 'UNH', 'UTX', 'V', 'VZ', 'WMT', 'XOM']
        for b in z:
            r=self.AddEquity(b)
            symbols.append(r)
        self.symbolData = {}
        
        
        for added in symbols:
            self.symbolData[added] = SymbolData(self, added,  self.resolution)
        

        self.SetWarmup(6000)
        self.first = True
        for key,value in self.symbolData.items():
            self.Log(str(key.Symbol)+"\n")

    def summer(self,k,key):
        tt=float(0)
        for i in range(0,k):
            tt+=self.symbolData[key].windowSMA[i]
            
            return tt
            
    def OnData(self, data):
        if self.Time.hour==9:
            for key, sd in self.symbolData.items():
                if sd.Stoc.Current.Value>sd.hsf:
                    self.symbolData[key].hsf=sd.Stoc.Current.Value
                if sd.Stoc.Current.Value<sd.lsf:
                    self.symbolData[key].lsf=sd.Stoc.Current.Value
                if self.Portfolio[key.Symbol].Invested:
                    
                    if sd.r==1:
                        if sd.Stoc.Current.Value>sd.target:
                            self.Liquidate(key.Symbol)
                    elif sd.r==2:
                        if  sd.Stoc.Current.Value<sd.target:
                            self.Liquidate(key.Symbol)
                        
                            
        elif self.Time.hour==10 and self.Time.minute==45:
            for key, sd in self.symbolData.items():
                if self.Portfolio[key.Symbol].Invested:
                    self.Liquidate(key.Symbol)
                    
            
                #self.Log(str(sd.lsf)+str(sd.hsf)+"ggggggggggggggg")
                self.symbolData[key].windowSMA.Add((sd.hsf-sd.lsf)/sd.Stoc.Current.Value)
                
                
                
                if not self.IsWarmingUp:
                    self.symbolData[key].window.Add(self.summer(5,key))
                    #self.Log(str(key.Symbol)+str(self.symbolData[key].window[0])+"lf")
        elif self.Time.hour==15 and self.Time.minute==45 and not self.IsWarmingUp:
            alphas = dict()
            #sort stocks by their current stochastic
            for key, sd in self.symbolData.items():
                if sd.Security.Price == 0:
                    continue
                
                alphas[key]=sd.window[0]
                #self.Log(str(sd.Stoc.Current.Value)+str(key))
            selected = sorted(alphas.items(), key=lambda x: x[1], reverse=True)
            
            if  self.symbolData[selected[0][0]].Stoc.Current.Value<self.symbolData[selected[0][0]].hsf \
            and self.symbolData[selected[0][0]].Stoc.Current.Value>self.symbolData[selected[0][0]].lsf:
                if  self.symbolData[selected[0][0]].Stoc.Current.Value<(self.symbolData[selected[0][0]].lsf+self.symbolData[selected[0][0]].hsf)/2:
                    
                
                    self.SetHoldings(selected[0][0].Symbol,0.25)
                    self.symbolData[selected[0][0]].r=1
                    self.symbolData[selected[0][0]].target=self.symbolData[selected[0][0]].Stoc.Current.Value+ \
                    (self.symbolData[selected[0][0]].hsf-self.symbolData[selected[0][0]].lsf)/3
                    
                    
                else:
                    self.SetHoldings(selected[0][0].Symbol,-0.25)
                    self.symbolData[selected[0][0]].r=2
                    self.symbolData[selected[0][0]].target=self.symbolData[selected[0][0]].Stoc.Current.Value- \
                    (self.symbolData[selected[0][0]].hsf-self.symbolData[selected[0][0]].lsf)/3
            for key, sd in self.symbolData.items():
                self.symbolData[key].hsf=0
                self.symbolData[key].lsf=999999
                    
            
            
                    
                
                
                
                
                    
                    
            
            
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.'''
        
        
            
        
            
            
class SymbolData:
    def __init__(self, algorithm, security, resolution):
        self.Security = security
        self.Stoc= Identity(algorithm.CreateIndicatorName(security.Symbol, "STO" , Resolution.Minute))
        self.Consolidator = algorithm.ResolveConsolidator(security.Symbol, timedelta(minutes=1))
        algorithm.RegisterIndicator(security.Symbol, self.Stoc, self.Consolidator)
        self.window = RollingWindow[float](100)
        self.hsf=0
        self.lsf=999999
        self.windowSMA=RollingWindow[float](100)
        self.isinv=False
        self.r=0
        self.target=None
