import CELEnvironment
from cqg_python_api import BarsRequestSample



symbols = ['CLES12Z', 'RBE', 'RBES1', 'HOE', 'HOES1', 'QOS12Z', 'CLES6M', 'EP', 'CLE']
continuation = {'CLES12Z', 'CLES6M', 'QOS12Z'}

param_dict = {'model_file': 'XGB_Model.sav',
              'symbols': symbols,
              'hist_bars_returned':-30,
              'intraday_period': 30,
              'continuation': continuation,
              'target': 'CLE'
              }

CELEnvironment.StartSample(BarsRequestSample, param_dict)

