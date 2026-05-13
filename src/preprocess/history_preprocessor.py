import polars as pl

class HistoryPreprocessor:
    @staticmethod
    def select_features(query):
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
    
    @staticmethod
    def clean_data(query):
        return query.unique(subset=["Alert ID"], keep='first').drop_nulls()

    @staticmethod
    def select_nodes(query):
        valid_nodes = (
            query.group_by("Node Name")
            .agg(pl.col("Alert ID").n_unique().alias("n_alarmes"))
            .filter(pl.col("n_alarmes") < 20000)
            .select("Node Name")
        )

        return query.join(valid_nodes, on="Node Name", how="inner")