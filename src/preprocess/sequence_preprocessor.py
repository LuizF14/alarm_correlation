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
    
    def clean_data(self, data):
        smart_oss_id_pattern = r"\s*-\s*SmartOSS Id:.*$"
        data["Alert Description"] = data['Alert Description'].str.replace(smart_oss_id_pattern, "", regex=True).str.strip()
        relevant_columns = [
            'Alert Type', 
            # 'Alert Description', 
            'Node ID'
        ]

        data = data.sort_values(by=relevant_columns + ['First Occurrence'])
    
        grouped_rows = []

        for _, group in data.groupby(relevant_columns):
            group = group.sort_values('First Occurrence')

            current_start = None
            current_end = None
            base_row = None

            for _, row in group.iterrows():
                start = row['First Occurrence']
                end = row['Last Occurrence']

                if current_start is None or current_end is None or base_row is None:
                    current_start = start
                    current_end = end
                    base_row = row.copy()
                    continue

                # verifica interseção
                if start <= current_end:
                    # merge do intervalo
                    current_end = max(current_end, end)
                else:
                    new_row = base_row.copy()
                    new_row['First Occurrence'] = current_start
                    new_row['Last Occurrence'] = current_end
                    grouped_rows.append(new_row)

                    current_start = start
                    current_end = end
                    base_row = row.copy()

            if current_start is not None and base_row is not None:
                new_row = base_row.copy()
                new_row['First Occurrence'] = current_start
                new_row['Last Occurrence'] = current_end
                grouped_rows.append(new_row)

        return pd.DataFrame(grouped_rows)
    

    def group_by(self, data, grouping_attribute='Node ID'):
        by_node = {group_name: group_data.reset_index(drop=True) for group_name, group_data in data.groupby(grouping_attribute)}
        return by_node
