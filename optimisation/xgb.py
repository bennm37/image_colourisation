import numpy as np
import xgboost as xgb
from typing import Tuple, Dict, List
from time import time
import argparse
import matplotlib
from matplotlib import pyplot as plt


xgb.train(
    {"tree_method": "hist", "seed": 1994, "disable_default_eval_metric": 1},
    dtrain=dtrain,
    num_boost_round=10,
    obj=squared_log,
    feval=rmsle,
    evals=[(dtrain, "dtrain"), (dtest, "dtest")],
    evals_result=results,
)
