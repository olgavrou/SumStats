import numpy as np
from functools import reduce


def get_group_from_parent(parent_group, child_group):
    group = parent_group.get(str(child_group))
    if group is None:
        raise ValueError("Group: %s does not exist in: %s" % (child_group, parent_group))
    return group


def get_dset(group, dset_name):
    dset = group.get(dset_name)
    if dset is not None:
        dset = dset[:]
    return dset


def get_upper_limit_mask(upper_limit, vector):
    _check_type_compatibility(upper_limit, vector)
    mask = None
    if upper_limit is not None:
        mask = vector <= upper_limit
    return mask


def get_lower_limit_mask(lower_limit, vector):
    _check_type_compatibility(lower_limit, vector)
    mask = None
    if lower_limit is not None:
        mask = vector >= lower_limit
    return mask


def combine_list_of_masks(list_of_masks):
    not_none_masks = [mask for mask in list_of_masks if mask is not None]

    if len(not_none_masks) == 0:
        return None
    if len(not_none_masks) == 1:
        return not_none_masks[0]
    return reduce(lambda mask1, mask2: [all(tup) for tup in zip(mask1, mask2)], not_none_masks)


def interval_mask(lower_limit, upper_limit, vector):
    _check_type_compatibility(upper_limit, vector)
    _check_type_compatibility(lower_limit, vector)
    mask_u = get_upper_limit_mask(upper_limit, vector)
    mask_l = get_lower_limit_mask(lower_limit, vector)
    list_of_masks = [mask_l, mask_u]
    return combine_list_of_masks(list_of_masks)


def equality_mask(value, vector):
    _check_type_compatibility(value, vector)
    mask = None
    if value is not None:
        mask = vector == value

    return mask


# This needs to be tested for performance issues
def filter_by_mask(vector, mask):
    if not_boolean_mask(mask):
        raise TypeError("Trying to filter vector using non boolean mask")
    filtered_vector = vector[mask]
    return filtered_vector


def not_boolean_mask(mask):
    return not all(type(x) == bool or type(x) == np.bool_ for x in mask)


def filter_dictionary_by_mask(dictionary, mask):
    return {dset : filter_by_mask(dataset, mask) for dset, dataset in dictionary.items()}


def filter_dsets_with_restrictions(name_to_dataset, dset_name_to_restriction):
    list_of_masks = []
    for dset_name in dset_name_to_restriction:
        argument = dset_name_to_restriction[dset_name]
        if isinstance(argument, tuple):
            lower_limit = argument[0]
            upper_limit = argument[1]
            dataset_to_filter_on = name_to_dataset[dset_name]
            list_of_masks.append(interval_mask(lower_limit, upper_limit, dataset_to_filter_on))
        else:
            value = argument
            dataset_to_filter_on = name_to_dataset[dset_name]
            list_of_masks.append(equality_mask(value, dataset_to_filter_on))

    filtering_mask = combine_list_of_masks(list_of_masks)
    if filtering_mask is not None:
        return filter_dictionary_by_mask(name_to_dataset, filtering_mask)

    return name_to_dataset


def convert_lists_to_np_arrays(dictionary, dset_types):
    return {dset_name: np.array(dataset, dtype=dset_types[dset_name]) for dset_name, dataset in dictionary.items()}


def remove_headers(name_to_dataset, column_headers):
    for column in column_headers:
        if column == name_to_dataset[column][0]:
            name_to_dataset[column] = name_to_dataset[column][1:]
        else:
            raise ValueError("Headers in file to not match defined column names: " + str(column_headers))
    return name_to_dataset


def assert_np_datasets_not_empty(name_to_dataset):
    for dset_name, dataset in name_to_dataset.items():
        if empty_np_array(dataset):
            raise ValueError("Array is None or empty: " + dset_name)


def empty_np_array(array):
    if array.tolist() is None:
        return True
    if len(array) == 0:
        return True
    return False


def _check_type_compatibility(value, vector):
    if value is None:
        return
    if np.issubdtype(vector.dtype, str) and np.issubdtype(np.array([value]).dtype, str):
        return

    if np.array([value]).dtype != vector.dtype:
        raise TypeError("Failed to create boolean mask of array of type "
                        "" + str(vector.dtype) + ' using value of type ' + str(np.array([value]).dtype))
