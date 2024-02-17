import zipfile
import pandas

class Validate:
    def __init__(self, zip, input, choice):
        self.zip = zip
        self.input = input
        self.choice = choice

    def get_unique_proteins(self):
        df = pandas.read_csv(self.input)
        if self.choice == 'intra':
            proteins = df['uniprotID'].unique()
        elif self.choice == 'inter':
            proteins = list(df['uniprotID A'].unique()) + list(df['uniprotID B'].unique())
        # proteins = df['uniprotID'].unique()
        return proteins

    def validate(self):
        with zipfile.ZipFile(self.zip, 'r') as zip_ref:
            file_names = zip_ref.namelist()

        proteins = self.get_unique_proteins()
        uploaded_proteins = [file for file in file_names if file.endswith('.cif')]
        print(uploaded_proteins)
        uploaded_proteins = [file.split('/')[1] for file in uploaded_proteins]
        uploaded_proteins = [file.split('.')[0] for file in uploaded_proteins]

        dict = {}
        for protein in uploaded_proteins:
            if protein not in proteins:
                dict[protein] = False
            else:
                dict[protein] = True

        return dict
    