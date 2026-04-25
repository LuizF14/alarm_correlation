import polars as pl

from .preprocess_base import PreprocessBase

class HistoryPreprocessor(PreprocessBase):
    def select_features(self, query):
        cols_map = {
            'alhi_cd_alarm_id': 'Alert ID',
            'alhi_tx_node': 'Node Name',
            'alhi_cd_node_id': 'Node ID',
            'alhi_tx_alert_type': 'Alerty Type',
            'alhi_tx_description': 'Alert Description',
            'alhi_dt_occurrence': 'Alert Occurrence'
        }

        return (
            query.select(list(cols_map.keys()))
            .rename(cols_map)
            .with_columns([
                pl.col('Alert Occurrence').str.to_datetime(),
            ])
            .drop_nulls()
        )
    
    def clean_data(self, data):
        return data.unique(subset=["Alert ID"], keep='first').drop_nulls()
    
    def group_by(self, query, grouping_attribute='Node ID'):
        query = query.sort([grouping_attribute, "Alert Occurrence"])
        data = query.collect()

        groups = data.partition_by(grouping_attribute, as_dict=True)

        return {
            key[0]: value
            for key, value in groups.items()
        }
