import polars as pl

class ActivePreprocessor:
    @staticmethod
    def select_features(query):
        cols_map = {
            'acal_cd_alarm_id': 'Alert ID',
            'acal_tx_alert_type': 'Alert Type',
            'acal_nm_severity': 'Alert Severity',
            'acal_tx_description': 'Alert Description',
            'acal_cd_node_id': 'Node ID',
            'acal_tx_node': 'Node Name',
            'acal_dt_first_occurrence': 'First Occurrence',
            'acal_dt_last_occurrence': 'Last Occurrence'
        }

        return (
            query.select(list(cols_map.keys()))
            .rename(cols_map)
            .with_columns([
                pl.col('First Occurrence').str.to_datetime(),
                pl.col('Last Occurrence').str.to_datetime(),
            ])
            .drop_nulls()
        )
    
    @staticmethod
    def clean_data(data):
        return data.unique(subset=["Alert ID"], keep='first').drop_nulls()
