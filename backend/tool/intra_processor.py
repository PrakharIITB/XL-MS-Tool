import numpy as np
import pandas as pd
import pyfastx as pyfx
import os, shutil
import prody as prd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import requests
import pathlib
import re
import urllib


class process_intra:
    def __init__(self, df, fx, threshold, mode="auto"):
        self.df = df
        self.fx = fx
        self.automated = True
        self.threshold = threshold
        if mode == "manual":
            self.automated = False
        self.workdir = os.path.join(os.environ["WORKDIR"], "intra")
        os.makedirs(self.workdir, exist_ok=True)
        self.uniprot_Ids = list(self.df["uniprotID"].unique())

    def _peptide_starts(self, row):
        """
        This function returns the start positions of the peptides in the FASTA file
        args:
            row: row of the dataframe
        return:
            start_list_a: list of start positions of peptide A
            start_list_b: list of start positions of peptide B
        """

        peptide_a = re.compile(row["Peptide A"])
        peptide_b = re.compile(row["Peptide B"])
        start_list_a = []
        start_list_b = []

        for m in peptide_a.finditer(self.fx[row["uniprotID"]].seq):
            start_list_a.append(m.start())

        for m in peptide_b.finditer(self.fx[row["uniprotID"]].seq):
            start_list_b.append(m.start())

        return [start_list_a, start_list_b]

    def cleanList(self, list_var):
        """
        This function cleans the list and returns a string

        args:
            list_var: list of strings
        return:
            list_str: string of the list
        """
        list_str = str(list_var)
        list_str = list_str.replace("[", "")
        list_str = list_str.replace("]", "")
        list_str = list_str.replace("'", "")
        return list_str

    def _peptide_start_a(self, row):
        """
        This function cleans the list of the start positions of peptides
        args:
            row: row of the dataframe
        return:
            list_str: string of the list of peptide A
        """
        return self.cleanList(row[0])

    def _peptide_start_b(self, row):
        """
        This function cleans the list of the start positions of peptides
        args:
            row: row of the dataframe
        return:
            list_str: string of the list of peptide B
        """

        return self.cleanList(row[1])

    def _remove_shared_peptides(self, row):
        """
        This function removes the shared peptides
        args:
            row: row of the dataframe
        return:
            True: if the peptides are not shared
            False: if the peptides are shared
        """

        if len(row["Peptide A-Pos"]) > 0 and len(row["Peptide B-Pos"]) > 0:
            return True
        else:
            return False

    def _get_actual_pos_from_residue_pep(self, row, option=None):
        """
        This function returns the actual position of the residue in the chain
        args:
            row: row of the dataframe
        return:
            residue_a_loc: actual position of the residue in the chain

        """
        if option == "A":
            peptide_start = int(row["Peptide A-Pos"])
            residue = row["Residue 1"]

        elif option == "B":
            peptide_start = int(row["Peptide B-Pos"])
            residue = row["Residue 2"]

        else:
            raise Exception("Option not recognized.")

        residue_loc = re.findall(r"\d+", residue)
        if len(residue_loc) == 1:
            return int(residue_loc[0]) + peptide_start
        else:
            raise Exception("Residue Location Format Incorrect.")

    def _proteins_from_alphafold(self):
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir, exist_ok=True)

        os.chdir(self.workdir)
        self.uniprot_ids_fetched = []
        self.uniprot_ids_not_fetched = []
        for uniprot_Id in self.uniprot_Ids:
            if os.path.exists(f"{uniprot_Id}.cif"):
                self.uniprot_ids_fetched.append(uniprot_Id)
                continue
            else:
                try:
                    urllib.request.urlretrieve(
                        f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_Id}-F1-model_v3.cif",
                        f"{uniprot_Id}.cif",
                    )
                    self.uniprot_ids_fetched.append(uniprot_Id)
                except requests.exceptions.RequestException as e:
                    self.uniprot_ids_not_fetched.append(uniprot_Id)
                    print(f"Error fetching {uniprot_Id}: {e}")

                except Exception as e:
                    self.uniprot_ids_not_fetched.append(uniprot_Id)
                    print(f"Error fetching {uniprot_Id}: {e}")

        print(self.uniprot_ids_not_fetched)

    def _getResidueDistance(self, row):
        protein = row["uniprotID"]
        if protein in self.uniprot_ids_fetched:

            try:
                path = os.path.join(self.workdir, f"{protein}.cif")
                print(os.path.join(os.getcwd(), f"{protein}.cif"))
                path = os.path.join(os.getcwd(), f"{protein}.cif")
                structure = prd.parseMMCIF(path)
                print("structure parsed")
                pep_a_pos = int(row["Absolute Peptide A-Pos"])
                pep_b_pos = int(row["Absolute Peptide B-Pos"])
                res_1 = structure.select(f"resnum {pep_a_pos} and name CA")
                res_2 = structure.select(f"resnum {pep_b_pos} and name CA")
                dist = prd.calcDistance(res_1, res_2)[0]
                return dist

            except AttributeError:
                # TODO: Add logging
                print(
                    "Unable to compute distance for the protein: ",
                    row["uniprotID"],
                    ".\nThe structure file is not appropriate.",
                )
                return pd.NA

        else:
            # TODO: Add logging
            print(f"Protein {protein} not fetched from AlphaFold.")
            return pd.NA

    def df_operations(self):
        """
        This function performs the following operations:
        1. Get the start positions of the peptides

        """

        self.XLMS_DF = self.df[
            [
                "uniprotID",
                "X-link type",
                "Peptide A",
                "Residue 1",
                "Peptide B",
                "Residue 2",
            ]
        ]

        self.XLMS_DF.dropna(subset=["Peptide A", "Peptide B"], inplace=True)

        peptide_starts = self.XLMS_DF.apply(
            lambda row: self._peptide_starts(row), axis=1
        ).copy()

        print(peptide_starts)

        self.XLMS_DF.loc[:, "Peptide A-Pos"] = peptide_starts.apply(
            lambda row: self._peptide_start_a(row)
        )
        self.XLMS_DF.loc[:, "Peptide B-Pos"] = peptide_starts.apply(
            lambda row: self._peptide_start_b(row)
        )

        self.XLMS_DF_NO_SHARED = self.XLMS_DF[
            self.XLMS_DF.apply(lambda row: self._remove_shared_peptides(row), axis=1)
        ]

        self.XLMS_DF_NO_SHARED["Absolute Peptide A-Pos"] = self.XLMS_DF_NO_SHARED.apply(
            lambda row: self._get_actual_pos_from_residue_pep(row, "A"), axis=1
        )

        self.XLMS_DF_NO_SHARED["Absolute Peptide B-Pos"] = self.XLMS_DF_NO_SHARED.apply(
            lambda row: self._get_actual_pos_from_residue_pep(row, "B"), axis=1
        )

        self.XLMS_DF_NO_SHARED["Distance"] = self.XLMS_DF_NO_SHARED.apply(
            lambda row: self._getResidueDistance(row), axis=1
        )

        self.distances = self.XLMS_DF_NO_SHARED["Distance"].to_numpy()
        self.XLMS_DF_NO_SHARED.to_csv("xlms_output.csv", index=False)

    def save_barplot(self):
        self.XLMS_DF_NO_SHARED.dropna()
        Barplot = self.XLMS_DF_NO_SHARED.plot.bar(y="Distance", rot=0)
        plt.axhline(y=self.threshold, color="r", linestyle="dashed")
        Barplot.set_title("Distance_Residue Bar_Plot", fontdict={"fontsize": 12})
        # Barplot.set_xlabel("Score_1",fontdict= { 'fontsize': 10})
        Barplot.axes.get_xaxis().set_visible(False)
        Barplot.set_ylabel("Cα-Cα Distance", fontdict={"fontsize": 10})
        plt.savefig(
            fname="intra_barplot",
            dpi=600,
            bbox_inches="tight",
        )
        plt.close()

    def getViolatedCrosslinks(self, row):
        """
        This function returns the status of the crosslink
        args:
            row: row of the dataframe
        return:
            Satisfied: if the crosslink is satisfied
            Violated: if the crosslink is violated
        """
        if pd.isna(row["Distance"]):
            return "Satisfied"

        elif row["Distance"] <= self.threshold:
            return "Satisfied"
        else:
            return "Violated"

    def save_histplot(self):

        self.XLMS_DF_NO_SHARED["Cα-Cα Distance status"] = self.XLMS_DF_NO_SHARED.apply(
            lambda row: self.getViolatedCrosslinks(row), axis=1
        )

        Histplot = sns.histplot(
            self.XLMS_DF_NO_SHARED,
            x="Distance",
            bins=140,
            stat="probability",
            hue="Cα-Cα Distance status",
            binwidth=3,
        )
        Histplot.set_ylabel("Cross-links", fontdict={"fontsize": 10})
        Histplot.set_xlabel("Cα-Cα Distance", fontdict={"fontsize": 10})
        plt.savefig(
            fname="intra_histogram_plot",
            dpi=600,
            bbox_inches="tight",
        )
        plt.close()

    def run(self):
        if self.automated:
            self._proteins_from_alphafold()
        self.df_operations()
        # self.save_barplot()
        self.save_histplot()


# if __name__ == "__main__":
#     df = pd.read_excel("data/Kamal_Data_Input.xlsx")
#     fx = pyfx.Fasta("data/Human_Database.gz", key_func=lambda x: x.split("|")[1])
#     os.environ["WORKDIR"] = "output/"
#     process = process_intra(df, fx, threshold=30)
#     process.run()
#     print("Intra Proximity Processed.")
