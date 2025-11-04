from pyspark.sql import DataFrame


class SmokeValidationContext:
    def __init__(self, data: DataFrame):
        self.headers = data.columns
        self.rows = [row.asDict() for row in data.collect()]

    def get_smoke_config(self, **kwargs):
        """
        Retrieve configuration row (at qa_config_* file) matching the specified input of keyword arguments.
        
        Returns:
            dict: The matched row (qa_config_* file) that matches all provided key-value pairs.

        Example:
            config = instance.get_smoke_config(env='prod', space='test')
        """
        for row in self.rows:
            if all(row[key] == value for key, value in kwargs.items()):
                return row
        raise KeyError(f'No element with keys: {kwargs}')
    

    def smoke_ranks(self, **filter_keys):
        """
        Retrieve the 'rank' values from rows (qa_config_* file) that match the specified input of filter criteria.

        Returns:
            list: A list of 'rank' values from rows that satisfy the filter conditions.

        Example:
            Assuming rows = [
                 {'id': 1, 'type': 'A', 'rank': 5},
                 {'id': 2, 'type': 'B', 'rank': 3},
                 {'id': 3, 'type': 'A', 'rank': 8}
            ]
            ranks = instance.smoke_ranks(type='A')
            # ranks will be [5, 8]
        """
        rank_values = [
            row['rank'] for row in self.rows
            if all(row[key] == value for key, value in filter_keys.items()) and 'rank' in row
            ]
        return rank_values
        