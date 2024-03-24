from scraping.lcl import convert_LCLpdf_to_df
import os

if __name__ == "__main__":
    df = convert_LCLpdf_to_df("EconoMe/Files/LCL")
    filename = "LCL.csv"
    if os.path.exists(filename):
        # Supprimer le fichier CSV existant
        os.remove(filename)
    df.to_csv(filename, index=False)
