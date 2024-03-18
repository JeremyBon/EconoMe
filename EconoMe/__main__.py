from scraping.lcl import convert_LCLpdf_to_df

if __name__ == "__main__":
    df = convert_LCLpdf_to_df("EconoMe/LCL")
    df.to_csv("LCL.csv", index=False)
