import os

import pytest

import sumstats.trait.loader as loader
from sumstats.trait.constants import TO_STORE_DSETS
from sumstats.trait.search.access.service import Service
from tests.prep_tests import *
import tests.test_constants as search_arrays

trait1 = "t1"
trait2 = "t2"
trait3 = "t3"
study1 = "s1"
study2 = "s2"
study3 = "s3"


class TestUnitSearcher(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self):
        search_arrays.chrarray = [10, 10, 10, 10]

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study=study1, loader=loader, trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study=study2, loader=loader, trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study=study3, loader=loader, trait=trait2,
                                                        test_arrays=search_arrays)
        load.load()

        self.start = 0
        self.size = 20

        self.query = Service(self.h5file)

    def teardown_method(self):
        os.remove(self.h5file)

    def test_query_for_all_assocs(self):
        self.query.query_for_all_associations(self.start, self.size)
        datasets = self.query.get_result()
        study_set = set(datasets[STUDY_DSET])

        assert study_set.__len__() == 3

    def test_query_for_trait(self):
        self.query.query_for_trait(trait1, self.start, self.size)
        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 8

        study_set = set(datasets[STUDY_DSET])

        assert study_set.__len__() == 2

        self.query.query_for_trait(trait2, self.start, self.size)
        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 4

        study_set = set(datasets[STUDY_DSET])

        assert study_set.__len__() == 1

    def test_query_for_study(self):
        self.query.query_for_study(trait1, study1, self.start, self.size)

        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 4

        study_set = set(datasets[STUDY_DSET])

        assert study_set.__len__() == 1
        assert study1 in study_set.pop()

        self.query.query_for_study(trait1, study1, self.start, self.size)
        datasets = self.query.get_result()

        for dset_name in TO_STORE_DSETS:
            assert len(datasets[dset_name]) == 4

    def test_non_existing_trait(self):
        with pytest.raises(ValueError):
            self.query.query_for_trait(trait3, self.start, self.size)

    def test_non_existing_trait_study_combination(self):
        with pytest.raises(ValueError):
            self.query.query_for_study(trait3, study2, self.start, self.size)

