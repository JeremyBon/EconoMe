from pydantic import BaseModel
from typing import List
from googleapiclient.discovery import build
from google.oauth2.service_account import (
    Credentials,
)
import os
from dotenv import load_dotenv

load_dotenv()


class Sheet(BaseModel):
    service: object
    SPREADSHEET_ID: str

    def __init__(self):
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_file(
            filename=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=scope,
        )
        self.service = build("sheets", "v4", credentials=credentials)
        self.SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

    def get_range(self, tab, range, valueRenderOption="FORMATTED_VALUE"):
        result = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.SPREADSHEET_ID,
                range=f"{tab}!{range}",
                valueRenderOption=valueRenderOption,
            )
            .execute()
        )
        return result.get("values", [])

    def get_last_line_index(self, tab):
        values = self.get_range(tab, "B:B")

        # Trouver la dernière ligne complétée
        if not values:
            raise ValueError("La feuille est vide.")
        else:
            last_filled_row = len(values)
            return last_filled_row

    def add_new_content(
        self,
        tab_name: str,
        initial_case: str,
        values: List[List],
        valueInputOption: str = "RAW",
    ):
        """Add new content to the google sheet

        Args:
            tab_name (str): The name of the tab
            initial_case (str): The initial case of the sheet
            values (List[List]): The values to be added
        """
        self.service.spreadsheets().values().update(
            spreadsheetId=self.SPREADSHEET_ID,
            range=f"{tab_name}!{initial_case}",
            valueInputOption=valueInputOption,
            body={"values": values},
        ).execute()
