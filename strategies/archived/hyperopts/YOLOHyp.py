# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# --- Do not remove these libs ---
from functools import reduce
from typing import Any, Callable, Dict, List

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from skopt.space import Categorical, Dimension, Integer, Real  # noqa

from freqtrade.optimize.hyperopt_interface import IHyperOpt

# --------------------------------
# Add your lib to import here
import talib.abstract as ta  # noqa
import freqtrade.vendor.qtpylib.indicators as qtpylib

class YOLOHyp(IHyperOpt):
    
    buy_params = {
		'adx': 34, 
		'aroon-down': 33, 
		'aroon-up': 98
    }

    @staticmethod
    def indicator_space() -> List[Dimension]:
        return [
            Integer(0, 100.0, name='adx'),
            Integer(0, 100.0, name='aroon-up'),
            Integer(0, 100.0, name='aroon-down')
        ]

    @staticmethod
    def sell_indicator_space() -> List[Dimension]:
        return []

    @staticmethod
    def buy_strategy_generator(params: Dict[str, Any]) -> Callable:

        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:

            dataframe.loc[
                ( 
                    (dataframe['adx'] > params['adx']) &
                    (dataframe['aroon-up'] > params['aroon-up']) &
                    (dataframe['aroon-down'] < params['aroon-down']) &
                    (dataframe['volume'] > 0)
                ),
                'buy'
            ] = 1

            return dataframe

        return populate_buy_trend

    @staticmethod
    def sell_strategy_generator(params: Dict[str, Any]) -> Callable:

        def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:

            dataframe['sell'] = 0
            return dataframe

        return populate_sell_trend

    @staticmethod
    def generate_roi_table(params: Dict) -> Dict[int, float]:

        roi_table = {}
        roi_table[0] = params['roi_p1'] + params['roi_p2'] + params['roi_p3'] + params['roi_p4'] + params['roi_p5'] + params['roi_p6']
        roi_table[params['roi_t6']] = params['roi_p1'] + params['roi_p2'] + params['roi_p3'] + params['roi_p4'] + params['roi_p5']
        roi_table[params['roi_t6'] + params['roi_t5']] = params['roi_p1'] + params['roi_p2'] + params['roi_p3'] + params['roi_p4']
        roi_table[params['roi_t6'] + params['roi_t5'] + params['roi_t4']] = params['roi_p1'] + params['roi_p2'] + params['roi_p3']
        roi_table[params['roi_t6'] + params['roi_t5'] + params['roi_t4'] + params['roi_t3']] = params['roi_p1'] + params['roi_p2']
        roi_table[params['roi_t6'] + params['roi_t5'] + params['roi_t4'] + params['roi_t3'] + params['roi_t2']] = params['roi_p1']
        roi_table[params['roi_t6'] + params['roi_t5'] + params['roi_t4'] + params['roi_t3'] + params['roi_t2'] + params['roi_t1']] = 0

        return roi_table

    @staticmethod
    def roi_space() -> List[Dimension]:

        return [
            Integer(1, 15, name='roi_t6'),
            Integer(1, 45, name='roi_t5'),
            Integer(1, 90, name='roi_t4'),
            Integer(45, 120, name='roi_t3'),
            Integer(45, 180, name='roi_t2'),
            Integer(90, 200, name='roi_t1'),

            Real(0.005, 0.10, name='roi_p6'),
            Real(0.005, 0.07, name='roi_p5'),
            Real(0.005, 0.05, name='roi_p4'),
            Real(0.005, 0.025, name='roi_p3'),
            Real(0.005, 0.01, name='roi_p2'),
            Real(0.003, 0.007, name='roi_p1'),
        ]

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        params = self.buy_params

        dataframe.loc[
            ( 
                (dataframe['adx'] > params['adx']) &
                (dataframe['aroon-up'] > params['aroon-up']) &
                (dataframe['aroon-down'] < params['aroon-down']) &
                (dataframe['volume'] > 0)
            ),
            'buy'
        ] = 1

        return dataframe