import numpy as np
import pandas as pd
import pyfastx as pyfx
import re
import prody as prd
import os, shutil
import urllib.request
from matplotlib import pyplot as plt
import seaborn as sns
from io import BytesIO
import requests
import pathlib


class inputProcessor:
    def __init__(self, filename, database, saving_dir, Residue_Distance_Threshold=25):
        self.filename = filename
        self.database = database
        self.saving_dir = saving_dir
        self.Residue_Distance_Threshold = Residue_Distance_Threshold

    def process_fasta(self):
        uurl = "https://rest.uniprot.org/uniprotkb/stream?"
        output_format = "compressed=false&fields=accession%2Creviewed%2Cid%2Cprotein_name%2Cgene_names%2Corganism_name%2Clength%2Csequence%2Cxref_pdb&format=tsv"
        uurl += output_format
        query = "model_organism%3A9606%20AND%20(reviewed:true)%20AND%20(database:pdb)%20AND%20(database:alphafolddb)"
        uurl += "&query=" + query
        ureq = requests.get(uurl)
        udata = pd.read_csv(BytesIO(ureq.content), delimiter="\t")
        self.fa = pyfx.Fasta(self.database, key_func=lambda x: x.split("|")[1])

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

    def change_row_names(self):

        input = pd.read_csv(self.filename)
        input.rename(
            {
                "Peptide-A": "Peptide A",
                "Link-Site-A": "Residue 1",
                "Peptide-B": "Peptide B",
                "Link-Site-B": "Residue 2",
            },
            axis=1,
            inplace=True,
        )
        # print(input.head())
        x_link_types = list(input["X-link type"].unique())

        # Get the type given by user through command line arguments
        # For now we will work with Intra-Protein-XL
        user_x_link_type_chosen = 0

        self.XLMS_input = input[
            input["X-link type"] == x_link_types[user_x_link_type_chosen]
        ]
        self.XLMS_proteins = self.XLMS_input["uniprotID"].unique()
        self.XLMS_Chain_1 = self.XLMS_input["Peptide A"].unique()
        self.XLMS_Chain_2 = self.XLMS_input["Peptide B"].unique()

    def get_peptide_starts(self, row):
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

        for m in peptide_a.finditer(self.fa[row["uniprotID"]].seq):
            start_list_a.append(m.start())

        for m in peptide_b.finditer(self.fa[row["uniprotID"]].seq):
            start_list_b.append(m.start())

        return [start_list_a, start_list_b]

    def peptide_start_a(self, row):
        """
        This function cleans the list of the start positions of peptides
        args:
            row: row of the dataframe
        return:
            list_str: string of the list of peptide A
        """
        return self.cleanList(row[0])

    def peptide_start_b(self, row):
        """
        This function cleans the list of the start positions of peptides
        args:
            row: row of the dataframe
        return:
            list_str: string of the list of peptide B
        """

        return self.cleanList(row[1])

    def remove_shared_peptides(self, row):
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

    def get_actual_pos_from_residue_pep_a(row):
        """
        This function returns the actual position of the residue in the chain
        args:
            row: row of the dataframe
        return:
            residue_a_loc: actual position of the residue in the chain

        """
        peptide_a_start = int(row["Peptide A-Pos"])
        residue_a = row["Residue 1"]
        residue_a_loc = re.findall(r"\d+", residue_a)
        if len(residue_a_loc) == 1:
            return int(residue_a_loc[0]) + peptide_a_start
        else:
            raise Exception("Residue Location Format Incorrect.")

    def get_actual_pos_from_residue_pep_b(row):
        """
        This function returns the actual position of the residue in the chain
        args:
            row: row of the dataframe
        return:
            residue_b_loc: actual position of the residue in the chain
        """

        peptide_b_start = int(row["Peptide B-Pos"])
        residue_b = row["Residue 2"]
        residue_b_loc = re.findall(r"\d+", residue_b)
        if len(residue_b_loc) == 1:
            return int(residue_b_loc[0]) + peptide_b_start
        else:
            raise Exception("Residue Location Format Incorrect.")

    def convert_to_xlms_format(self):
        print("Here")
        temp = self.XLMS_input.apply(lambda row: self.get_peptide_starts(row), axis=1)
        temp2 = temp.copy()

        self.XLMS_input["Peptide A-Pos"] = temp2.apply(
            lambda row: self.peptide_start_a(row)
        ).copy()
        self.XLMS_input["Peptide B-Pos"] = temp2.apply(
            lambda row: self.peptide_start_b(row)
        ).copy()

        self.XLMS_DF = self.XLMS_input[
            [
                "uniprotID",
                "X-link type",
                "Peptide A",
                "Residue 1",
                "Peptide A-Pos",
                "Peptide B",
                "Residue 2",
                "Peptide B-Pos",
            ]
        ].copy()

        print(self.XLMS_DF.head())

    def remove_shared_peptides(self, row):
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

    def get_actual_pos_from_residue_pep_a(self, row):
        """
        This function returns the actual position of the residue in the chain
        args:
            row: row of the dataframe
        return:
            residue_a_loc: actual position of the residue in the chain

        """
        peptide_a_start = int(row["Peptide A-Pos"])
        residue_a = row["Residue 1"]
        residue_a_loc = re.findall(r"\d+", residue_a)
        if len(residue_a_loc) == 1:
            return int(residue_a_loc[0]) + peptide_a_start
        else:
            raise Exception("Residue Location Format Incorrect.")

    def get_actual_pos_from_residue_pep_b(self, row):
        """
        This function returns the actual position of the residue in the chain
        args:
            row: row of the dataframe
        return:
            residue_b_loc: actual position of the residue in the chain
        """

        peptide_b_start = int(row["Peptide B-Pos"])
        residue_b = row["Residue 2"]
        residue_b_loc = re.findall(r"\d+", residue_b)
        if len(residue_b_loc) == 1:
            return int(residue_b_loc[0]) + peptide_b_start
        else:
            raise Exception("Residue Location Format Incorrect.")

    def calculate_absolute_chain_pos(self):
        XLMS_DF_NO_SHARED = self.XLMS_DF[
            self.XLMS_DF.apply(lambda row: self.remove_shared_peptides(row), axis=1)
        ].copy()
        XLMS_DF_NO_SHARED["Absolute Peptide A-Pos"] = XLMS_DF_NO_SHARED.apply(
            lambda row: self.get_actual_pos_from_residue_pep_a(row), axis=1
        )
        XLMS_DF_NO_SHARED["Absolute Peptide B-Pos"] = XLMS_DF_NO_SHARED.apply(
            lambda row: self.get_actual_pos_from_residue_pep_b(row), axis=1
        )
        self.XLMS_DF_NO_DUPES_NO_SHARED = XLMS_DF_NO_SHARED.drop_duplicates().copy()

        print(self.XLMS_DF_NO_DUPES_NO_SHARED.head())

    def proteins_from_alphafold(self):
        current_working_dir = os.getcwd()
        try:
            os.mkdir(os.path.join(self.saving_dir, "AlphaFold Structures"))
            os.chdir(os.path.join(self.saving_dir, "AlphaFold Structures"))
        except FileExistsError:
            shutil.rmtree(os.path.join(self.saving_dir, "AlphaFold Structures"))
            os.mkdir(os.path.join(self.saving_dir, "AlphaFold Structures"))
            os.chdir(os.path.join(self.saving_dir, "AlphaFold Structures"))
        except Exception as e:
            print(f"An unexpected error occurred while creating the directory: {e}")

        self.XLMS_proteins_without_structure_info = []
        self.XLMS_proteins_with_structure_info = []
        for protein in self.XLMS_proteins:
            os.makedirs(
                os.path.join(self.saving_dir, "AlphaFold Structures"), exist_ok=True
            )
            os.chdir(os.path.join(self.saving_dir, "AlphaFold Structures"))
            os.makedirs(
                os.path.join(self.saving_dir, "AlphaFold Structures", protein),
                exist_ok=True,
            )
            os.chdir(os.path.join(self.saving_dir, "AlphaFold Structures", protein))
            try:
                # Change this URL for updates to AlphaFold Structures
                urllib.request.urlretrieve(
                    f"https://alphafold.ebi.ac.uk/files/AF-{protein}-F1-model_v3.cif",
                    f"{protein}.cif",
                )
                self.XLMS_proteins_with_structure_info.append(protein)
            except urllib.error.HTTPError as e:
                self.XLMS_proteins_without_structure_info.append(protein)
                print(
                    f"AlphaFold Structure not downloaded/found for the following protein: {protein}"
                )
            except Exception as e:
                print(
                    f"An unexpected error occurred while processing protein {protein}: {e}"
                )
        os.chdir(current_working_dir)

    def getResidueDistance(self, row):
        """
        This function returns the distance between the two residues
        args:
            row: row of the dataframe
        return:
            dist: distance between the two residues
        """
        if row["uniprotID"] in self.XLMS_proteins_with_structure_info:
            try:
                protein = row["uniprotID"]
                path = os.path.join(
                    self.saving_dir,
                    "AlphaFold Structures",
                    protein,
                    f"{protein}.cif",
                )
                print(path)
                protein_struct = prd.parseMMCIF(
                    os.path.join(
                        self.saving_dir,
                        "AlphaFold Structures",
                        protein,
                        f"{protein}.cif",
                    )
                )
                pep_a_pos = int(row["Absolute Peptide A-Pos"])
                pep_b_pos = int(row["Absolute Peptide B-Pos"])
                res_1 = protein_struct.select(f"resnum {pep_a_pos} and name CA")
                res_2 = protein_struct.select(f"resnum {pep_b_pos} and name CA")
                dist = prd.calcDistance(res_1, res_2)[0]
                return dist
            except AttributeError:
                print(
                    "Unable to compute distance for the protein: ",
                    row["uniprotID"],
                    ".\nThe structure file is not appropriate.",
                )
                return "N/A"
        else:
            return "N/A"

    def calculateResidueDistance(self):
        self.XLMS_DF_NO_DUPES_NO_SHARED[
            "Residue Distance"
        ] = self.XLMS_DF_NO_DUPES_NO_SHARED.apply(
            lambda row: self.getResidueDistance(row), axis=1
        )

    def getResidueDistanceForDuplicates(self, row):
        """
        This function returns the distance between the two residues
        args:
            row: row of the dataframe
        return:
            dist: distance between the two residues
        """

        if row["uniprotID"] in self.XLMS_proteins_with_structure_info:
            protein = row["uniprotID"]
            row_with_distance = (
                self.XLMS_DF_NO_DUPES_NO_SHARED[
                    self.XLMS_DF_NO_DUPES_NO_SHARED["uniprotID"] == protein
                ]["Residue Distance"]
                .copy()
                .tolist()
            )
            if len(row_with_distance) > 0:
                res_distance = row_with_distance[0]
                return float(res_distance)
            else:
                return "N/A as Shared Peptide"
        else:
            return "N/A"

    def calculateResidueDistanceForDuplicates(self):
        self.XLMS_input["Residue Distance"] = self.XLMS_input.apply(
            lambda row: self.getResidueDistanceForDuplicates(row), axis=1
        )

    # Outputting the distances
    def output_distances(self):
        self.XLMS_input.to_excel(os.path.join(self.saving_dir, "xlms_input.xlsx"))
        path = os.path.join(
            self.saving_dir,
            self.filename.split("/")[-1].split(".")[0] + "_XLMS_Distances_WO_Duplicates.csv",
        )
        print(self.saving_dir)
        print(self.filename)
        print(path)
        self.XLMS_DF_NO_DUPES_NO_SHARED.to_csv(
            os.path.join(
                self.saving_dir,
                self.filename.split("/")[-1].split(".")[0] + "_XLMS_Distances_WO_Duplicates.csv",
            ),
            index=False,
        )

        pd.Series(self.XLMS_proteins_with_structure_info).to_csv(
            os.path.join(self.saving_dir, "xlms_proteins_with_structure_info.csv")
        )
        input_with_distances = pd.read_excel(
            os.path.join(self.saving_dir, "xlms_input.xlsx")
        )
        temp_input = input_with_distances[
            input_with_distances["Residue Distance"] != "N/A as Shared Peptide"
        ]
        processed_input = temp_input[temp_input["Residue Distance"] != "N/A"].copy()
        processed_input.fillna(0, inplace=True)
        processed_input.to_excel(
            os.path.join(
                self.saving_dir, self.filename.split("/")[-1].split(".")[0] + "_XLMS_Output.xlsx"
            ),
            index=False,
        )

        # Define File Name
        self.df_bplt = pd.read_csv(
            os.path.join(
                self.saving_dir,
                self.filename.split("/")[-1].split(".")[0] + "_XLMS_Distances_WO_Duplicates.csv",
            )
        )
        self.df_hplt = pd.read_excel(
            os.path.join(
                self.saving_dir,
                self.filename.split("/")[-1].split(".")[0] + "_XLMS_Output.xlsx"
            )
        )

    def save_barplot(self):
        Barplot = self.df_bplt.plot.bar(y="Residue Distance", rot=0)
        plt.axhline(y=25, color="r", linestyle="dashed")
        Barplot.set_title("Distance_Residue Bar_Plot", fontdict={"fontsize": 12})
        # Barplot.set_xlabel("Score_1",fontdict= { 'fontsize': 10})
        Barplot.axes.get_xaxis().set_visible(False)
        Barplot.set_ylabel("Cα-Cα Distance", fontdict={"fontsize": 10})
        print(
            os.path.join(
                self.saving_dir,
                self.filename.split("/")[-1].split(".")[0] + "XLMS_Distances_Barplot.jpeg",
            )
        )
        plt.savefig(
            os.path.join(
                self.saving_dir,
                self.filename.split("/")[-1].split(".")[0] + "XLMS_Distances_Barplot.jpeg",
            ),
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
        if row["Residue Distance"] <= self.Residue_Distance_Threshold:
            return "Satisfied"
        else:
            return "Violated"

    def save_histplot(self):
        self.df_hplt["Cα-Cα Distance status"] = self.df_hplt.apply(
            lambda row: self.getViolatedCrosslinks(row), axis=1
        )

        # Result = pd.concat([df_hplt, Satisfactory], axis = 1)
        self.df_hplt.to_excel(
            os.path.join(
                self.saving_dir,
                self.filename.split("/")[-1].split(".")[0] + "_XLMS_Final_Output.xlsx",
            )
        )
        df_hisplt = pd.read_excel(
            os.path.join(
                self.saving_dir,
                self.filename.split("/")[-1].split(".")[0] + "_XLMS_Final_Output.xlsx",
            )
        )

        Histplot = sns.histplot(
            df_hisplt,
            x="Residue Distance",
            bins=140,
            stat="probability",
            hue="Cα-Cα Distance status",
            binwidth=3,
        )
        Histplot.set_ylabel("Cross-links", fontdict={"fontsize": 10})
        Histplot.set_xlabel("Cα-Cα Distance", fontdict={"fontsize": 10})
        plt.savefig(
            os.path.join(
                self.saving_dir,
                self.filename.split("/")[-1].split(".")[0] + "XLMS_distances_Histplot.jpeg",
            )
        )
        plt.close()

    def run(self):
        self.process_fasta()
        self.change_row_names()
        self.convert_to_xlms_format()
        self.calculate_absolute_chain_pos()
        self.proteins_from_alphafold()
        self.calculateResidueDistance()
        self.calculateResidueDistanceForDuplicates()
        self.output_distances()
        self.save_barplot()
        self.save_histplot()