import pandas as pd

from .preprocess_base import PreprocessBase

class SequencePreprocessor2(PreprocessBase):
    def select_features(self, data):
        rename_map = {
            'alhi_cd_alarm_id': 'Alarm ID',
            'alhi_tx_node': 'Node Name',
            'alhi_cd_node_id': 'Node ID',
            'alhi_tx_alert_type': 'Alerty Type',
            'alhi_tx_description': 'Alert Description',
            'alhi_dt_occurrence': 'Alert Occurrence'
        }

        data = (
            data.select(list(rename_map.keys()))
                .rename(rename_map)               
                .drop_nulls()                     
        )
        
        return data
    
    def clean_data(self, data):
        return data.unique(subset=["Alarm ID"], keep='first').drop_nulls()
    
    def group_by(self, query, grouping_attribute='Node ID'):
        query = query.sort([grouping_attribute, "Alert Occurrence"])
        data = query.collect()

        return data.partition_by(grouping_attribute, as_dict=True)
