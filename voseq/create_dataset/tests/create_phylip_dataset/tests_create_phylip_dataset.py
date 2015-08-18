import os

from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth.models import User

from create_dataset.utils import CreateDataset
from public_interface.models import GeneSets
from public_interface.models import Sequences
from public_interface.models import TaxonSets
from public_interface.models import Vouchers


class CreatePhylipDatasetTest(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump2.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        gene_set = GeneSets.objects.get(geneset_name='all_genes')
        taxon_set = TaxonSets.objects.get(taxonset_name='all_taxa')
        self.cleaned_data = {
            'gene_codes': '',
            'taxonset': taxon_set,
            'voucher_codes': '',
            'geneset': gene_set,
            'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
            'number_genes': None,
            'degen_translations': None,
            'positions': ['ALL'],
            'partition_by_positions': 'ONE',
            'file_format': 'PHY',
            'aminoacids': False,
            'outgroup': '',
        }
        self.dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                         'tests', 'create_phylip_dataset', 'dataset.phy')
        self.aa_dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                            'tests', 'create_phylip_dataset', 'aa_dataset.phy')

        self.user = User.objects.get(username='admin')
        self.user.set_password('pass')
        self.user.save()

        self.c = Client()
        self.dataset_creator = CreateDataset(self.cleaned_data)
        self.maxDiff = None

    def test_create_simple_dataset(self):
        with open(self.dataset_file, "r") as handle:
            expected = handle.read()
        result = self.dataset_creator.dataset_str
        self.assertEqual(expected, result)

    def test_charset_block_file_of_simple_dataset(self):
        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        result = self.dataset_creator.charset_block
        self.assertEqual(expected, result)

    def test_create_aa_dataset(self):
        with open(self.aa_dataset_file, "r") as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['aminoacids'] = True
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected, result)

    def test_stop_codon_warning(self):
        voucher = Vouchers.objects.get(code='CP100-10')
        sequence_with_stop_codon = 'NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNtaaTCTGTAGGCGATGCCTTGAAGGACGGCTTCGACGGAGCGTCGCGGGTCATGATGCCCAATACGGAGTTAGAAGCGCCTGCTCAGCGAAACGACGCCGCCCCGCACAGAGTCCCGCGACGAGACCGATACAGATTTCAACTTCGGCCGCACAATCCTGACCACAAAACACCCGGANTCAAGGACCTAGTGTACTTGGAATCATCGCCGGGTTTCTGCGAAAAGAACCCGCGGCTGGGCATTCCCGGCACGCACGGGCGTGCCTGCAACGACACGAGTATCGGCGTCGACGGCTGCGACCTCATGTGCTGCGGCCGTGGCTACCGGACCGAGACAATGTTCGTCGTGGAGCGATGCAAC'
        seq = Sequences.objects.get(code=voucher, gene_code='wingless')
        seq.sequences = sequence_with_stop_codon
        seq.save()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['aminoacids'] = True
        dataset_creator = CreateDataset(cleaned_data)

        expected = 'Gene wingless, sequence CP100-10_Aus_aus contains stop codons "*"'
        result = dataset_creator.warnings
        self.assertTrue(expected in result)

    def test_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st2nd_3rd'
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        with open(self.dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)