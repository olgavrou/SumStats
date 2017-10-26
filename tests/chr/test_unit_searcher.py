import os
import pytest
import sumstats.chr.loader as loader
import sumstats.chr.searcher as searcher
from sumstats.chr.constants import *
from tests.chr.test_constants import *
from sumstats.utils.interval import *


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq' : frequencyarray}

        load = loader.Loader(None, self.h5file, 'PM001', dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
        load = loader.Loader(None, self.h5file, 'PM002', dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
        load = loader.Loader(None, self.h5file, 'PM003', dict)
        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_for_chromosome(self):
        chr_group = self.f.get("/2")
        name_to_dataset = searcher.query_for_chromosome(chr_group)
        assert len(name_to_dataset[BP_DSET]) == 6
        assert len(name_to_dataset[SNP_DSET]) == 6

    def test_query_for_block_range(self):
        chr_group = self.f.get("/2")
        block_lower_limit = 48480252
        block_upper_limit = 49129966
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        print("bpinterval", bp_interval)
        print("floor", bp_interval.floor())
        print("ceil", bp_interval.ceil())
        name_to_dataset = searcher.query_for_block_range(chr_group, bp_interval)

        assert isinstance(name_to_dataset, dict)

        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 6

        block_lower_limit = 49129966
        block_upper_limit = 48480252
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        with pytest.raises(ValueError):
            searcher.query_for_block_range(chr_group, bp_interval)

        block_lower_limit = 49129966
        block_upper_limit = 49200000
        bp_interval = IntInterval().set_tuple(block_lower_limit, block_upper_limit)
        name_to_dataset = searcher.query_for_block_range(chr_group, bp_interval)

        assert isinstance(name_to_dataset, dict)

        for dset_name in name_to_dataset:
            assert len(name_to_dataset[dset_name]) == 3

