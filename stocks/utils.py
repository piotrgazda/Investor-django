import pandas as pd
import numpy as np

def get_currency_from_company_abbreviation(abbreviation) -> str:
    return np.where(abbreviation.str.endswith(".WA"), 'PLN', 'USD')


def add_currency_column_to_dataframe(df, company_name_column, currency_column) -> pd.DataFrame:
    df[currency_column] = df.groupby(company_name_column)[
        company_name_column].transform(get_currency_from_company_abbreviation)
    return df

