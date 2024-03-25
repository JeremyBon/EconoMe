import numpy as np
from pydantic import BaseModel
import pandas as pd
import warnings
from .sheets import Sheet
from datetime import datetime

warnings.filterwarnings("ignore")


def check_values(
    df, predicted_sheet_value, end_amount_wished, compte, begin, end
):
    try:
        end_amount_predicted = np.round(
            df["CREDIT"].sum() - df["DEBIT"].sum() + predicted_sheet_value, 2
        )
        assert end_amount_predicted == end_amount_wished
    except AssertionError:
        print(
            f"Catégorie:{compte}: La somme des crédits et débits entre {begin} et {end} ne correspond pas à la somme souhaitée"
        )
        print(f"Somme souhaitée: {end_amount_wished}")
        print(f"Somme calculée: {end_amount_predicted}")
        raise


def find_categ_and_undercateg(libelle):
    categ = pd.read_csv("categ.csv", sep=";")
    for _, row in categ.iterrows():
        if row["Description"] in libelle:
            return pd.Series([row["categ"], row["under_categ"]])
    # Retourne NaN si aucun match n'est trouvé
    return pd.Series([pd.NA, pd.NA])


class Transactions(BaseModel):

    def __init__(
        self, df: pd.DataFrame, begin: str, end: str, end_amount_wished: float
    ):
        self.sheet = Sheet()
        self.df = df[(df["Date"] >= begin) & (df["Date"] <= end)]
        predicted_sheet_value = float(
            self.sheet.get_range("Paramètres", "L2")[0][0].replace(",", ".")
        )
        check_values(
            self.df,
            predicted_sheet_value,
            end_amount_wished,
            "LCL",
            begin,
            end,
        )

    def add_period_credit(self):
        last_index = self.sheet.get_last_line_index("DB Bénéfices")
        df = self.df[self.df["CREDIT"] != 0]
        values_date = [
            [datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")]
            for date in df["Date"]
        ]
        values_credit = [[credit] for credit in df["CREDIT"]]
        values_description = [
            [description] for description in df["Description"]
        ]
        values_account = [["Compte Courant"] for _ in range(len(df))]
        values = [
            (values_date, "B"),
            (values_credit, "C"),
            (values_description, "E"),
            (values_account, "F"),
        ]
        for value, col in values:
            self.sheet.add_new_content(
                tab_name="DB Bénéfices",
                initial_case=f"{col}{last_index+1}",
                values=value,
                valueInputOption="USER_ENTERED",
            )

    def add_period_debit(self):
        last_index = self.sheet.get_last_line_index("DB Paiement")
        metadata = self.sheet.get_range(
            "DB Paiement",
            f"K{last_index}:R{last_index+1}",
            valueRenderOption="FORMULA",
        )
        metadata[0].insert(0, "Compte Courant")
        month = self.sheet.get_range(
            "DB Paiement", f"C{last_index}", valueRenderOption="FORMULA"
        )
        df = self.df[self.df["DEBIT"] != 0]  # On garde que les paiements
        df[["categ", "under_categ"]] = df["Description"].apply(
            find_categ_and_undercateg
        )
        values_date = [
            [datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")]
            for date in df["Date"]
        ]
        values_months = [
            [month[0][0].replace(str(last_index), str(last_index + i + 1))]
            for i in range(len(values_date))
        ]
        values_debit = [[debit] for debit in df["DEBIT"]]
        values_description = [
            [description] for description in df["Description"]
        ]
        values_account = [
            [
                (
                    col.replace(str(last_index), str(last_index + i + 1))
                    if type(col) == str
                    else col
                )
                for col in metadata[0]
            ]
            for i in range(len(values_date))
        ]
        values = [
            (values_date, "B"),
            (values_months, "C"),
            (values_debit, "D"),
            (values_description, "G"),
            (values_account, "J"),
        ]

        for value, col in values:
            self.sheet.add_new_content(
                tab_name="DB Paiement",
                initial_case=f"{col}{last_index+1}",
                values=value,
                valueInputOption="USER_ENTERED",
            )

        for index, row in df.reset_index(drop=True).iterrows():
            if type(row["categ"]) == str:
                print(index)
                self.sheet.add_new_content(
                    tab_name="DB Paiement",
                    initial_case=f"H{last_index+1+index}",
                    values=[[row["categ"], row["under_categ"]]],
                )


def add_col(categorie):
    assert len(categorie) == 3
    df = pd.read_csv("categ.csv", sep=";")
    df.loc[len(df)] = categorie
    df.to_csv("categ.csv", sep=";", index=False)
    print("colonne ajoutée avec succès")
    print(df.tail(5))
