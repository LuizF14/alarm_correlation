from src.preprocess.binarize_preprocessor import BinarizeResult
from src.graphing.correlation_strategy import CorrelationStrategy
from tigramite import data_processing as pp
from tigramite.pcmci import PCMCI
from tigramite.independence_tests.cmisymb import CMIsymb

import numpy as np

class PCMCICorrelation:
    name = "PCMCICorrelation"

    def __init__(self, tau_min: int = 1, tau_max: int = 5, pc_alpha: float = 0.05):
        self.tau_min = tau_min
        self.tau_max = tau_max
        self.pc_alpha = pc_alpha

    def correlate(self, binarize_result: BinarizeResult) -> dict:
        data_dict = {i: mat for i, mat in enumerate(binarize_result.matrices)}

        dataframe = pp.DataFrame(
            data_dict,
            var_names=binarize_result.var_names,
            analysis_mode='multiple',
        )

        pcmci = PCMCI(
            dataframe=dataframe,
            cond_ind_test=CMIsymb(),
            verbosity=2,
        )

        return pcmci.run_pcmci(
            tau_min=self.tau_min,
            tau_max=self.tau_max,
            pc_alpha=self.pc_alpha,
        )