import os

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command

from create_dataset.utils import CreateDataset
from public_interface.models import GeneSets
from public_interface.models import TaxonSets


class CreateNexusDatasetTest(TestCase):
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
            'degen_translations': None,
            'number_genes': None,
            'positions': '',
            'partition_by_positions': '',
            'file_format': 'NEXUS',
            'aminoacids': False,
            'outgroup': '',
        }

        self.c = Client()
        self.dataset_creator = CreateDataset(self.cleaned_data)
        self.maxDiff = None

    def test_nexus_all_codons_as_one(self):
        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_nexus_dataset', 'dataset.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['ALL']
        cleaned_data['partition_by_positions'] = 'ONE'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_all_codons_partitioned_as_each(self):
        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_nexus_dataset', 'dataset_partitioned_as_each.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['ALL']
        cleaned_data['partition_by_positions'] = 'EACH'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_with_outgroup(self):
        cleaned_data = self.cleaned_data
        cleaned_data['outgroup'] = 'CP100-10'
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='4genes')
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = """
#NEXUS

BEGIN DATA;
DIMENSIONS NTAX=2 NCHAR=3214;
FORMAT INTERLEAVE DATATYPE=DNA MISSING=? GAP=-;
MATRIX

[16S]
CP100-10_Melitaea_diamina                              ????CGTGGTATCACTATTGATATTGCTSTATGGAAGTTCGAAACGAGCAGATACTATGTCACCATCATTGATGCTCCCGGACACAGAGATTTCATCAAGGACATGATTACTGGGACATCACAAGCCGATTGCGCCGTGCTTATCGTCGCAGCCGGTACTGGTGAGTTCGAAGCTGGTATCTCGGAGGACGGACAAACCCGTGAGCATGCTCTTCTCGCATTCACACTCGGTGTAAAGCAGCTGATAGTGGGTGTCAACAAAATGGACTCTACTGAGCCCCCATACAGCGAGCCACGTTTTGAGGAAATCAAAAAAGAAGTGTCCTCATACATTAAGAAAATTGGTTACAACCCAGCTGCCGTCGCGTTCGTGCCCATTTCTGGCTGGCATGGAGACAACATGCTGGAGCCATCTACCAAGATGCCCTGGTTCAAGGGATGGCAAGTGGATCGCAAAGAAGGCAAGGGTGAAGGTAAATGCCTTATTGAAGCCCTGGACGCCATTCTGCCTCC??
CP100-11_Melitaea_diamina                              ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

[COI]
CP100-10_Melitaea_diamina                              ?????????????????????????TGAGCCGGTATAATTGGTACATCCCTAAGTCTTATTATTCGAACCGAATTAGGAAATCCTAGTTTTTTAATTGGAGATGATCAAATTTATAATACCATTGTAACAGCTCATGCTTTTATTATAATTTTTTTTATAGTTATGCCAATTATAATTGGAGGATTTGGTAATTGACTTGTACCATTAATATTGGGAGCCCCAGATATAGCTTTCCCCCGAATAAATTATATAAGATTTTGATTATTGCCTCCATCCTTAATTCTTTTAATTTCAAGTAGAATTGTAGAAAATGGGGCAGGAACTGGATGAACAGTTTACCCCCCACTTTCATCTAATATTGCCCATAGAGGAGCTTCAGTGGATTTAGCTATTTTTTCTTTACATTTAGCTGGGATTTCCTCTATCTTAGGAGCTATTAATTTTATTACTACAATTATTAATATACGAATTAATAATATATCTTATGATCAAATACCTTTATTTGTATGAGCAGTAGGAATTACAGCATTACTTCTCTTATTATCTTTACCAGTTTTAGCTGGAGCTATTACTATACTTTTAACGGATCGAAATCTTAATACCTCATTTTTTGATTCCTGCGGAGGAGGAGATCC???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
CP100-11_Melitaea_diamina                              ??TGAGCCGGTATAATTGGTACATCCCTAAGTCTTATTATTCGAACCGAATTAGGAAATCCTAGTTTTTTAATTGGAGATGATCAAATTTATAATACCATTGTAACAGCTCATGCTTTTATTATAATTTTTTTTATAGTTATGCCAATTATAATTGGAGGATTTGGTAATTGACTTGTACCATTAATATTGGGAGCCCCAGATATAGCTTTCCCCCGAATAAATTATATAAGATTTTGATTATTGCCTCCATCCTTAATTCTTTTAATTTCAAGTAGAATTGTAGAAAATGGGGCAGGAACTGGATGAACAGTTTACCCCCCACTTTCATCTAATATTGCCCATAGAGGAGCTTCAGTGGATTTAGCTATTTTTTCTTTACATTTAGCTGGGATTTCCTCTATCTTAGGAGCTATTAATTTTATTACTACAATTATTAATATACGAATTAATAATATATCTTATGATCAAATACCTTTATTTGTATGAGCAGTAGGAATTACAGCATTACTTCTCTTATTATCTTTACCAGTTTTAGCTGGAGCTATTACTATACTTTTAACGGATCGAAATCTTAATACCTCATTTTTTGATTCCTGCGGAGGAGGAGATCC??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

[EF1a]
CP100-10_Melitaea_diamina                              ???????????????CAAGTCCACCACCACCGGCCACTTGATTTACAAATGTGGTGGTATCGACAAACGTACCATCGAGAAGTTCGAGAAGGAAGCCCAGGAAATGGGCAAGGGTTCCTTCAAGTACGCTTGGGTGTTGGACAAACTTAAGGCTGAGCGCGAGCGTGGTATCACTATTGATATTGCTCTGTGGAAGTTCGAGACTGCCAAATACTATGTAACCATCATCGATGCTCCCGGACACAGAGATTTCATCAAGAACATGATCACCGGAACATCACAAGCCGATTGCGCCGTACTTATCGTCGCCGCCGGTACTGGTGAGTTCGAAGCCGGTATCTCAAAGAACGGTCAGACCCGTGAGCACGCTCTGCTCGCCTTCACATTAGGTGTAAAGCAGCTGATTGTAGGAGTCAACAAAATGGACTCCACTGAGCCCCCATACAATGAGGGACGTTTCGAGGAAATCAAAAAGGAAGTGTCCTCTTACATCAAGAAGATCGGTTACAACCCAGCTGCCGTCGCTTTCGTACCCATTTCTGGCTGGCACGGAGACAACATGCTGGAGCCATCTACCAAAATGTCCCGGTTCAAGGGATGGCAAGTGGAGCGCAAAGAAGGCAAGG???AAGGTAAATGCCTCATTGAAGCTC???ACGCCATCCTTCCTCCGG?????CCCAC????????????????????????????????????????????????TATTGGTACAGTGCCCGTAGGCAGAGTAGAAACTGGTATCCTCAAACCAGGTACCATTGTTGTTTTCGCTCCCGCCAACATCACCACTGAAGTCAAATCTGTGGAGATGCACCACGAAGCTCTCCAAGAGGCTGTACCTGGAGACAATGTAGGTTTCAACGTCAAGAACGTTTCCGTCAAGGAATTACGTCGTGGTTATGTAGCTGGTGACTCCAAGAACAACCCACCCAAGGGAGCTGCTGACTTCACCGCACAAGTCATTGTGCTCAACCACCCCGGTCAAATCTCCAATGGCTACACACCTGTGCTCGATTGCCACACAGCTCACATTGCCTGCAAATTCGCCGAAATCAAAGAAAAGGTTGACCGTCGTTCCGGTAAATCYACTGAGGACAATCCTAAATCTATCAAATCTGGTGATGCTGCCATTGTGAACTTGGTACCTTCCAAACCCCTCTGTGTGGAGGCCTTCCAAGAATTCCCACCTCTTGGTCG?????????????
CP100-11_Melitaea_diamina                              ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

[wingless]
CP100-10_Melitaea_diamina                              ACACGTCGACTCCGGCAAGTCCACCACCACCGGTCACTTGATTTACAAATGTGGTGGTATCGACAaACGTACCATCGAGAAGTTCGAGAAGGAAGCCCAGGAAATGGGTAAGGGTTCCTTCAAATACGCCTGGGTATTGGACAAACTGAAGGCTGAGCGTGAACGTGGTATCACCATTGACATTGCTCTGTGGAAGTTCGAGACTGCCAAGTACTATGTCACCATCATCGACGCTCCCGGACACAGAGATTTCATCAAGAACATGATCACCGGAACCTCTCAAGCCGATTGCGCTGTGCTCATCGTCGCCGCCGGTACTGGTGAGTTCGAAGCCGGTATCTCAAAGAACGGTCAGACCCGTGAACACGCTCTGCTTGCCTTCACCCTCGGTGTCAAGCAGCTGATTGTAGGT
CP100-11_Melitaea_diamina                              ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
;
END;

begin mrbayes;
    charset 16S = 1-515;
    charset COI = 516-1562;
    charset EF1a = 1563-2802;
    charset wingless = 2803-3214;
partition GENES = 4: 16S, COI, EF1a, wingless;

set partition = GENES;

set autoclose=yes;
outgroup CP100-10_Melitaea_diamina;
prset applyto=(all) ratepr=variable brlensp=unconstrained:Exp(100.0) shapepr=exp(1.0) tratiopr=beta(2.0,1.0);
lset applyto=(all) nst=mixed rates=gamma [invgamma];
unlink statefreq=(all);
unlink shape=(all) revmat=(all) tratio=(all) [pinvar=(all)];
mcmc ngen=10000000 printfreq=1000 samplefreq=1000 nchains=4 nruns=2 savebrlens=yes [temp=0.11];
 sump relburnin=yes [no] burninfrac=0.25 [2500];
 sumt relburnin=yes [no] burninfrac=0.25 [2500] contype=halfcompat [allcompat];
END;
"""
        self.assertEqual(expected.strip(), result)

    def test_nexus_gene_no_reading_frame(self):
        """For this test we will drop 16S"""
        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['1st', '2nd']
        cleaned_data['outgroup'] = ''
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='4genes')
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = """
#NEXUS

BEGIN DATA;
DIMENSIONS NTAX=2 NCHAR=1798;
FORMAT INTERLEAVE DATATYPE=DNA MISSING=? GAP=-;
MATRIX

[COI]
CP100-10_Melitaea_diamina                              ????????????????TGGCGGATATGGACTCCTAGCTATATCGACGATTGGAACCAGTTTTATGGGAGACAATTAAAACATGTACGCCAGCTTATATATTTTTATGTATCCATATATGGGGTTGGAATGCTGTCCTTATTTGGGCCCGAATGCTTCCCGATAATAATAGTTTGTTTTCCCCTCTTATCTTTATTCAGAGATGTGAAAGGGCGGACGGTGACGTTACCCCCTTCTCAAATGCCAAGGGGCTCGTGATTGCATTTTCTTCATTGCGGATTCTCATTTGGGCATAATTATACACATATAAATCGATAAAAATTCTAGACAATCCTTTTGTTGGCGTGGATACGCTTCTCTTTTTTCTTCCGTTTGCGGGCATACATCTTTACGACGAACTAAACTCTTTTGATCTGGGGGGGGACC??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
CP100-11_Melitaea_diamina                              ?TAGCGTAAATGTAATCCAATCTATATCAACGATAGAATCTATTTTAATGAGTGTCAATTTATACATGAAAGTCTGTTTATAAATTTTTAAGTAGCAATAAATGAGATTGTATTACTGACATAAATGGAGCCAGTAAGTTCCCCAAAATTTAAAATTTATATGCTCATCTAATCTTAATTAATAAATGAGAATGGGAGAATGATAAAGTTCCCCACTTATTATATGCCTAAGAGTTAGGGTTAGTATTTTTTACTTAGTGGATTCTTACTAGAGTATATTTATATAAATATATAACAATATATAATTTTGTCAAACTTATTGATAGAGAGAATAAGATACTCCTATATTTACAGTTAGTGAGTATATAACTTAAGGTCAATCTATACTATTTTGTTCTCGAGAGAGTC??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

[EF1a]
CP100-10_Melitaea_diamina                              ??????????AATCACACACGGCATTATTAAATGGGGGATGAAACGACATGAAATTGAAAGAGCCAGAATGGAAGGTCTTAATAGCTGGTTTGAAACTAAGCGACGGACGGGATACATGAATGCCTTGAATTGAACGCAATATAGTACATATGAGCCCGGCAAGGATTATAAAAATATACGGACTCCAGCGATGGCGTCTATGTGCGCGGACGGGATTGAGCGGATTCAAAAGGCAACCGGACAGCCTCTGCTTACTTGGGTAACACTATGTGGGTAAAAATGATCACGACCCCTAAAGAGGCGTTGAGAATAAAAGAGTTCTCTAATAAAAATGGTAAACCGCGCGTGCTTGTCCATTCGGTGCAGGGAAAATCTGACCTCACAAATTCCGTTAAGGTGCAGTGACGAAGAGGAAG??AGGAATGCTATGAGCC??AGCATCTCCCCG???CCAC????????????????????????????????ATGGACGTCCGTGGAGGTGAACGGATCTAACCGGACATGTGTTTGCCCGCAAATACACGAGTAATCGTGAATCACAGAGCCTCAGAGCGTCCGGGAAAGTGGTTAAGTAAAAGTTCGTAAGATTCGCGGGTAGTGCGGGATCAAAAAACCCCAAGGGCGCGATTACGCCAGTATGTCTAACACCGGCAATTCAAGGTAACCCGTCTGATGCAACGCCAATGCTGAATTGCGAATAAGAAAGTGACGCGTCGGAATCACGAGAAACCAATCATAATCGGGAGCGCATGTAATTGTCCTCAACCCTTGGTGAGCTTCAGATTCCCCCTGGCG????????
CP100-11_Melitaea_diamina                              ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

[wingless]
CP100-10_Melitaea_diamina                              CAGTGATCGGAATCACACACGGCATTATTAAATGGGGGATGAAaCGACATGAAATTGAAAGAGCCAGAATGGAAGGTCTTAATAGCTGGTTTGAAACTAAGCGACGGACGGGATACATGAATGCCTTGAATTGAACGCAATATAGTACATATGAGCCCGGCAAGGATTATAAAAATATACGGACTCCAGCGATGGCGTCTATGTGCGCGGACGGGATTGAGCGGATTCAAAAGGCAACCGGACAGCCTCTGCTTACCTGGGTAACACTATGTGG
CP100-11_Melitaea_diamina                              ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
;
END;

begin mrbayes;
    charset COI = 1-698;
    charset EF1a = 699-1524;
    charset wingless = 1525-1798;
partition GENES = 3: COI, EF1a, wingless;

set partition = GENES;

set autoclose=yes;
prset applyto=(all) ratepr=variable brlensp=unconstrained:Exp(100.0) shapepr=exp(1.0) tratiopr=beta(2.0,1.0);
lset applyto=(all) nst=mixed rates=gamma [invgamma];
unlink statefreq=(all);
unlink shape=(all) revmat=(all) tratio=(all) [pinvar=(all)];
mcmc ngen=10000000 printfreq=1000 samplefreq=1000 nchains=4 nruns=2 savebrlens=yes [temp=0.11];
 sump relburnin=yes [no] burninfrac=0.25 [2500];
 sumt relburnin=yes [no] burninfrac=0.25 [2500] contype=halfcompat [allcompat];
END;
"""
        self.assertEqual(expected.strip(), result)

    def test_nexus_gene_excluding_genes_with_less_than_specified_number_of_genes(self):
        """Voucher CP100-11 should be dropped"""
        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['1st', '2nd']
        cleaned_data['outgroup'] = ''
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='4genes')
        cleaned_data['number_genes'] = 2
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = """
#NEXUS

BEGIN DATA;
DIMENSIONS NTAX=1 NCHAR=1798;
FORMAT INTERLEAVE DATATYPE=DNA MISSING=? GAP=-;
MATRIX

[COI]
CP100-10_Melitaea_diamina                              ????????????????TGGCGGATATGGACTCCTAGCTATATCGACGATTGGAACCAGTTTTATGGGAGACAATTAAAACATGTACGCCAGCTTATATATTTTTATGTATCCATATATGGGGTTGGAATGCTGTCCTTATTTGGGCCCGAATGCTTCCCGATAATAATAGTTTGTTTTCCCCTCTTATCTTTATTCAGAGATGTGAAAGGGCGGACGGTGACGTTACCCCCTTCTCAAATGCCAAGGGGCTCGTGATTGCATTTTCTTCATTGCGGATTCTCATTTGGGCATAATTATACACATATAAATCGATAAAAATTCTAGACAATCCTTTTGTTGGCGTGGATACGCTTCTCTTTTTTCTTCCGTTTGCGGGCATACATCTTTACGACGAACTAAACTCTTTTGATCTGGGGGGGGACC??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

[EF1a]
CP100-10_Melitaea_diamina                              ??????????AATCACACACGGCATTATTAAATGGGGGATGAAACGACATGAAATTGAAAGAGCCAGAATGGAAGGTCTTAATAGCTGGTTTGAAACTAAGCGACGGACGGGATACATGAATGCCTTGAATTGAACGCAATATAGTACATATGAGCCCGGCAAGGATTATAAAAATATACGGACTCCAGCGATGGCGTCTATGTGCGCGGACGGGATTGAGCGGATTCAAAAGGCAACCGGACAGCCTCTGCTTACTTGGGTAACACTATGTGGGTAAAAATGATCACGACCCCTAAAGAGGCGTTGAGAATAAAAGAGTTCTCTAATAAAAATGGTAAACCGCGCGTGCTTGTCCATTCGGTGCAGGGAAAATCTGACCTCACAAATTCCGTTAAGGTGCAGTGACGAAGAGGAAG??AGGAATGCTATGAGCC??AGCATCTCCCCG???CCAC????????????????????????????????ATGGACGTCCGTGGAGGTGAACGGATCTAACCGGACATGTGTTTGCCCGCAAATACACGAGTAATCGTGAATCACAGAGCCTCAGAGCGTCCGGGAAAGTGGTTAAGTAAAAGTTCGTAAGATTCGCGGGTAGTGCGGGATCAAAAAACCCCAAGGGCGCGATTACGCCAGTATGTCTAACACCGGCAATTCAAGGTAACCCGTCTGATGCAACGCCAATGCTGAATTGCGAATAAGAAAGTGACGCGTCGGAATCACGAGAAACCAATCATAATCGGGAGCGCATGTAATTGTCCTCAACCCTTGGTGAGCTTCAGATTCCCCCTGGCG????????

[wingless]
CP100-10_Melitaea_diamina                              CAGTGATCGGAATCACACACGGCATTATTAAATGGGGGATGAAaCGACATGAAATTGAAAGAGCCAGAATGGAAGGTCTTAATAGCTGGTTTGAAACTAAGCGACGGACGGGATACATGAATGCCTTGAATTGAACGCAATATAGTACATATGAGCCCGGCAAGGATTATAAAAATATACGGACTCCAGCGATGGCGTCTATGTGCGCGGACGGGATTGAGCGGATTCAAAAGGCAACCGGACAGCCTCTGCTTACCTGGGTAACACTATGTGG
;
END;

begin mrbayes;
    charset COI = 1-698;
    charset EF1a = 699-1524;
    charset wingless = 1525-1798;
partition GENES = 3: COI, EF1a, wingless;

set partition = GENES;

set autoclose=yes;
prset applyto=(all) ratepr=variable brlensp=unconstrained:Exp(100.0) shapepr=exp(1.0) tratiopr=beta(2.0,1.0);
lset applyto=(all) nst=mixed rates=gamma [invgamma];
unlink statefreq=(all);
unlink shape=(all) revmat=(all) tratio=(all) [pinvar=(all)];
mcmc ngen=10000000 printfreq=1000 samplefreq=1000 nchains=4 nruns=2 savebrlens=yes [temp=0.11];
 sump relburnin=yes [no] burninfrac=0.25 [2500];
 sumt relburnin=yes [no] burninfrac=0.25 [2500] contype=halfcompat [allcompat];
END;
"""
        self.assertEqual(expected.strip(), result)

    def test_with_total_char_lengths_aminoacids(self):
        cleaned_data = self.cleaned_data
        cleaned_data['aminoacids'] = True
        cleaned_data['outgroup'] = ''
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='4genes')
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = """
#NEXUS

BEGIN DATA;
DIMENSIONS NTAX=2 NCHAR=899;
"""
        self.assertTrue(expected.strip() in result)

    def test_char_lengths_for_partitions_aminoacids(self):
        cleaned_data = self.cleaned_data
        cleaned_data['aminoacids'] = True
        cleaned_data['outgroup'] = ''
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='4genes')
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = "charset 16S = 1-1"
        self.assertTrue(expected in result)

    def test_order_of_vouchers_is_kept_along_partitions(self):
        cleaned_data = self.cleaned_data
        cleaned_data['voucher_codes'] = 'CP100-09\r\nCP100-10\r\nCP100-11\r\nCP100-12\r\nCP100-13'
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = """
CP100-12_Melitaea_diamina                              ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
CP100-13_Melitaea_diamina                              ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

[EF1a]
CP100-09_Melitaea?_diamina
"""
        self.assertTrue(expected.strip() in result)

    def test_try_dataset_degenerated_in_partitions(self):
        cleaned_data = self.cleaned_data
        cleaned_data['voucher_codes'] = 'CP100-10'
        cleaned_data['degen_translations'] = 'NORMAL'
        cleaned_data['partition_by_positions'] = '1st2nd_3rd'
        cleaned_data['translations'] = True
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = "DIMENSIONS NTAX=1 NCHAR=0;"
        self.assertTrue(expected in result)
