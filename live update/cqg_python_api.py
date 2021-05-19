# The sample makes Timed Bar request and waits for response and updates for 20 sec

import threading
import CELEnvironment
from CELEnvironment import Trace
import win32com.client
from collections import OrderedDict
from HandleNewData import HandleData


class BarsRequestSample(CELEnvironment.CELSinkBase):
    def __init__(self):
        self.eventDone = threading.Event()
        self.id_dict = {}
        self.closes = {}


    def Init(self, celEnvironment):
        self.celEnvironment = celEnvironment

    def Start(self, param_dict):
        self.symbols = param_dict['symbols']

        self.handle_new_bars = HandleData(param_dict)

        for symbol in self.symbols:
            Trace("Create timed bars request")
            request = win32com.client.Dispatch(self.celEnvironment.cqgCEL.CreateTimedBarsRequest())
            request.Symbol = symbol
            request.RangeStart = 0
            request.RangeEnd = param_dict['hist_bars_returned']
            request.IntradayPeriod = param_dict['intraday_period']
            request.Continuation = 4 if symbol in param_dict['continuation'] else 3
            request.UpdatesEnabled = True
            request.EqualizeCloses = True
            request.SessionsFilter = 31

            Trace("Starting the request...")

            bars = self.celEnvironment.cqgCEL.RequestTimedBars(request)
            self.id_dict[bars.Id] = symbol
            self.eventDone.wait(5)

            Trace("Done!")

    def OnDataError(self, cqgError, errorDescription):
        if (cqgError is not None):
            error = win32com.client.Dispatch(cqgError)
            Trace("OnDataError: Code: {} Description: {}".format(error.Code, error.Description))
        self.eventDone.set()

    def OnTimedBarsResolved(self, cqgTimedBars, cqgError):
        if (cqgError is not None):
            error = win32com.client.Dispatch(cqgError)
            Trace("OnTimedBarsResolved: Code: {} Description: {}".format(error.Code,
                                                                         error.Description))
            self.eventDone.set()
        else:
            bars = win32com.client.Dispatch(cqgTimedBars)
            Trace("OnTimedBarsResolved: Bars count: {} Bars:".format(bars.Count))
            for i in range(0, bars.Count):
                self.dumpBar(win32com.client.Dispatch(bars.Item(i)), i)

    def OnTimedBarsAdded(self, cqgTimedBars):
        bars = win32com.client.Dispatch(cqgTimedBars)
        id = self.id_dict[bars.Id]
        global last_good_close

        for i in range(0, bars.Count):
            if bars.Item(i).Close > -2000000000:
                last_good_close = bars.Item(i).Close

        last_close_final = last_good_close
        self.append(win32com.client.Dispatch(bars.Item(bars.Count - 2)), id, last_close_final)

    def dumpBar(self, bar, index):
        Trace("   Bar index: {} Timestamp {} Open {} High {} Low {} Close {} "
              "ActualVolume {} CommodityVolume {} ContractVolume {} TickVolume {}".format(
            index, bar.Timestamp, bar.Open, bar.High, bar.Low, bar.Close,
            bar.ActualVolume, bar.CommodityVolume, bar.ContractVolume, bar.TickVolume))

    def append(self, bar, id, last_close):
        timestamp = str(bar.Timestamp)
        self.closes['Timestamp'] = timestamp
        if bar.Close < -2000000000:
            self.closes[id] = last_close
        else:
            self.closes[id] = bar.Close


        if len(self.closes) == len(self.symbols)+1:
            key_list = self.symbols.copy()
            key_list.insert(0, 'Timestamp')

            sorted_closes = OrderedDict((k, self.closes[k]) for k in key_list)
            print(self.closes)
            self.handle_new_bars.data_triage(sorted_closes)
            sorted_closes.clear()
            self.closes = {}




