import pandas as pd
from .inter_proccesor import process_inter
from .intra_processor import process_intra
import pyfastx as pyfx
import os


class mainApp:
    def __init__(self, threshold, data, fasta, option=None, mode="auto"): 
        # df = pd.read_excel("data/Kamal_Data_Input.xlsx")
        # fx = pyfx.Fasta("data/Human_Database.gz", key_func=lambda x: x.split("|")[1])
        print('in mainApp')
        df = pd.read_csv(data)
        fx = pyfx.Fasta(fasta, key_func=lambda x: x.split("|")[1])
        os.environ["WORKDIR"] = "/Users/prakhar/Files/Work/DH307/Tool/backend/output"

        if option == "intra" or option == "loop":
            print('Intra Proximity Started.')
            process = process_intra(df, fx, threshold, mode)
            process.run()
            print("Intra Proximity Processed.")

        if option == "inter":
            print('Inter Proximity Started.')
            process = process_inter(df, fx, threshold, mode)
            process.run()
            print("Inter Proximity Processed.")

        if option == "mixed":
            # TODO: Add the code for mixed part.
            pass
