import pandas as pd

from .preprocess_base import PreprocessBase

class SequencePreprocessor(PreprocessBase):
    def select_features(self, data):
        cols = ['acal_cd_id', 'acal_tx_alert_type', 'acal_nm_severity', 'acal_tx_description', 'acal_cd_node_id', 'acal_tx_node', 'acal_dt_first_occurrence', 'acal_dt_last_occurrence']
        columns_new_names = ['Alert ID', 'Alert Type', 'Alert Severity', 'Alert Description', 'Node ID', 'Node Name', 'First Occurrence', 'Last Occurrence']
        data = data.loc[:, cols]

        data['acal_dt_first_occurrence'] = pd.to_datetime(data['acal_dt_first_occurrence'])
        data['acal_dt_last_occurrence'] = pd.to_datetime(data['acal_dt_last_occurrence'])

        data.columns = columns_new_names

        data = data.dropna()
        return data
    
    def group_by(self, data, grouping_attribute='Node ID'):
        by_node = [group_data.reset_index(drop=True) for group_name, group_data in data.groupby(grouping_attribute)]
        return by_node
