import os

import h5py
import numpy as np
import pytest
import sumstats.utils.group as gu
import sumstats.utils.utils as utils
from sumstats.utils.dataset import Dataset


class TestUnitGroup(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_group_from_parent(self):
        self.f.create_group("1")
        group = gu.get_group_from_parent(self.f, 1)
        assert group.name == "/1"

        group = gu.get_group_from_parent(self.f, "1")
        assert group.name == "/1"

        with pytest.raises(ValueError):
            gu.get_group_from_parent(self.f, "23")

        group.create_group("subgroup")
        subgroup = gu.get_group_from_parent(group, "subgroup")
        assert subgroup.name == "/1/subgroup"

        with pytest.raises(ValueError):
            gu.get_group_from_parent(group, "subgroup1")

        with pytest.raises(ValueError):
            gu.get_group_from_parent(self.f, "subgroup")

    def test_get_all_groups_from_parent(self):
        self.f.create_group("1")
        self.f.create_group("1/sub1")
        self.f.create_group("1/sub2")
        group1 = gu.get_group_from_parent(self.f, 1)
        groups = gu.get_all_groups_from_parent(group1)
        assert len(groups) == 2
        assert isinstance(groups[0], h5py._hl.group.Group)

    def test_get_dset(self):
        group = self.f.create_group("1")
        data = [1, 2, 3]
        group.create_dataset("dset", data=data)

        dataset = gu.get_dset(group, "dset")
        assert np.array_equal(dataset, data)

        dataset = gu.get_dset(group, "dset1")
        assert dataset is None

    def test_get_dset_from_group(self):
        chr_group_2 = self.f.create_group("/2")
        snp_group = gu._get_dset_from_group('snp', chr_group_2)
        assert utils.empty_array(snp_group)

    def test_create_dset_placeholder(self):
        size = 5
        value = None
        with pytest.raises(AssertionError):
            gu._create_dset_placeholder(size, value)

        value = 1
        placeholder = gu._create_dset_placeholder(size, value)
        assert len(placeholder) == 5
        assert len(set(placeholder)) == 1
        assert isinstance(placeholder, Dataset)

    def test_extend_dsets_for_group(self):
        group = self.f.create_group("1")
        data1 = [1, 2, 3]
        group.create_dataset("dset1", data=data1)
        data2 = [4, 5, 6]
        group.create_dataset("dset2", data=data2)
        TO_QUERY = ['dset1', 'dset2', 'dset3']
        name_to_dset = utils.create_dictionary_of_empty_dsets(TO_QUERY)
        name_to_dset = gu.extend_dsets_for_group_missing(missing_value="group_name", group=group,
                                                         name_to_dataset=name_to_dset,
                                                         missing_dset="dset3",
                                                         existing_dset="dset2")

        data3 = ["group_name", "group_name", "group_name"]
        assert np.array_equal(name_to_dset['dset1'], data1)
        assert np.array_equal(name_to_dset['dset2'], data2)
        assert np.array_equal(name_to_dset['dset3'], data3)
