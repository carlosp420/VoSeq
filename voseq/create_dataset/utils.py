from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from core.utils import get_voucher_codes
from core.utils import get_gene_codes
from core.utils import flatten_taxon_names_dict
from core.utils import chain_and_flatten
from public_interface.models import Genes
from public_interface.models import Sequences
from public_interface.models import Vouchers


class CreateDataset(object):
    """
    Accept form input to create a dataset in several formats, codon positions,
    for list of codes and genes. Also takes into account the vouchers passed as
    taxonset.

    Attributes:
        ``dataset_str``: output dataset to pass to users.

    """
    def __init__(self, cleaned_data):
        print(">>>>>>_init", cleaned_data)
        self.errors = []
        self.seq_objs = dict()
        self.cleaned_data = cleaned_data
        self.voucher_codes = get_voucher_codes(cleaned_data)
        self.gene_codes = get_gene_codes(cleaned_data)
        self.taxon_names = cleaned_data['taxon_names']
        self.dataset_str = self.create_dataset()
        self.codon_positions = cleaned_data['positions']
        self.reading_frames = self.get_reading_frames()

    def create_dataset(self):
        self.voucher_codes = get_voucher_codes(self.cleaned_data)
        self.gene_codes = get_gene_codes(self.cleaned_data)
        self.create_seq_objs()
        return self.from_seq_objs_to_fasta()

    def create_seq_objs(self):
        """Generate a list of sequence objects. Also takes into account the
        genes passed as geneset.

        Returns:
            list of sequence objects as produced by BioPython.

        """
        our_taxon_names = self.get_taxon_names_for_taxa()

        all_seqs = Sequences.objects.all().values('code_id', 'gene_code', 'sequences').order_by('code_id')
        for s in all_seqs:
            code = s['code_id'].lower()
            gene_code = s['gene_code'].lower()
            if code in self.voucher_codes and gene_code in self.gene_codes:
                seq = Seq(s['sequences'])
                seq_obj = SeqRecord(seq)
                seq_obj.id = flatten_taxon_names_dict(our_taxon_names[code])
                if 'GENECODE' in self.taxon_names:
                    seq_obj.id += '_' + gene_code
                seq_obj.name = gene_code

                if gene_code not in self.seq_objs:
                    self.seq_objs[gene_code] = []
                self.seq_objs[gene_code].append(seq_obj)

    def from_seq_objs_to_fasta(self):
        """Take a list of BioPython's sequence objects and return a FASTA string

        Returns:
            The FASTA string will contain the gene_code at the top as if it were
            another FASTA gene sequence.

        """
        fasta_str = []
        append = fasta_str.append

        for gene_code in self.seq_objs:
            this_gene = None
            for seq_record in self.seq_objs[gene_code]:
                if this_gene is None:
                    this_gene = seq_record.name
                    seq_str = '>' + this_gene + '\n' + '--------------------'
                    append(seq_str)
                if this_gene != seq_record.name:
                    this_gene = seq_record.name
                    seq_str = '>' + this_gene + '\n' + '--------------------'
                    append(seq_str)
                seq_str = '>' + seq_record.id + '\n' + str(seq_record.seq)
                append(seq_str)

        return '\n'.join(fasta_str)

    def get_taxon_names_for_taxa(self):
        """Returns dict: {'CP100-10': {'taxon': 'name'}}

        Takes list of voucher_codes and list of taxon_names from cleaned form.

        Returns:
            Dictionar with data, also as dicts.

        """
        vouchers_with_taxon_names = {}

        all_vouchers = Vouchers.objects.all().order_by('code').values('code', 'orden', 'superfamily',
                                                                      'family', 'subfamily', 'tribe',
                                                                      'subtribe', 'genus', 'species',
                                                                      'subspecies', 'auctor', 'hostorg',)
        for voucher in all_vouchers:
            code = voucher['code'].lower()
            if code in self.voucher_codes:
                obj = dict()
                for taxon_name in self.taxon_names:
                    if taxon_name != 'GENECODE':
                        taxon_name = taxon_name.lower()
                        obj[taxon_name] = voucher[taxon_name]
                vouchers_with_taxon_names[code] = obj

        return vouchers_with_taxon_names

    def get_reading_frames(self):
        """

        :return: dict of gene_code: reading_frame. If not found, flag warning.
        """
        reading_frames = dict()
        genes = Genes.objects.all().values('gene_code', 'reading_frame')
        for gene in genes:
            gene_code = gene['gene_code'].lower()
            if gene_code in self.gene_codes:
                reading_frames[gene_code] = gene['reading_frame']
        return reading_frames

    def get_sequence_based_on_codon_positions(self, gene_code, seq):
        """Puts the sequence in frame, by deleting base pairs at the begining
        of the sequence if the reading frame is not 1:

        :param gene_code: as lower case
        :param seq: as BioPython seq object.
        :return: sequence as string with codon positions removed, if needed.

        Example:
            If reading frame is 2: ATGGGG becomes TGGGG. Then the sequence is
            processed to extract the codon positions requested by the user.

        """
        if 'ALL' in self.codon_positions:
            return seq

        reading_frame = int(self.reading_frames[gene_code.lower()]) - 1
        seq = seq[reading_frame:]

        # This is the BioPython way to get codon positions
        # http://biopython.org/DIST/docs/tutorial/Tutorial.html#htoc19
        first_position = seq[0::3]
        second_position = seq[1::3]
        third_position = seq[2::3]

        if '1st' in self.codon_positions \
                and '2nd' not in self.codon_positions \
                and '3rd' not in self.codon_positions:
            return first_position

        if '2nd' in self.codon_positions \
                and '1st' not in self.codon_positions \
                and '3rd' not in self.codon_positions:
            return second_position

        if '3rd' in self.codon_positions \
                and '1st' not in self.codon_positions \
                and '2nd' not in self.codon_positions:
            return third_position

        if '1st' in self.codon_positions and '2nd' in self.codon_positions \
                and '3rd' not in self.codon_positions:
            return chain_and_flatten(first_position, second_position)

        if '1st' in self.codon_positions and '3rd' in self.codon_positions \
                and '2nd' not in self.codon_positions:
            return chain_and_flatten(first_position, third_position)

        if '2nd' in self.codon_positions and '3rd' in self.codon_positions \
                and '1st' not in self.codon_positions:
            return chain_and_flatten(second_position, third_position)
