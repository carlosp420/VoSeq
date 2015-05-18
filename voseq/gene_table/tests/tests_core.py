from django.test import TestCase
from django.core.management import call_command
from django.test import Client

from Bio.Seq import Seq
from Bio.Alphabet import generic_dna

from core import utils
from public_interface.models import Genes
from public_interface.models import Sequences


class TestGeneTable(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)
        self.client = Client()

    def test_view_index(self):
        response = self.client.get('/create_gene_table/')
        self.assertEqual(200, response.status_code)
