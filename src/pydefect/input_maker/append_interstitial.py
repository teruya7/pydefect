# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
from typing import List, Union

import numpy as np
from numpy.linalg import inv
from pydefect.input_maker.supercell_info import SupercellInfo, Interstitial
from pydefect.error import NotPrimitiveError
from pymatgen.core import Structure, Element, IStructure
from vise.util.structure_symmetrizer import StructureSymmetrizer
from vise.util.typing import Coords


def append_interstitial(supercell_info: SupercellInfo,
                        unitcell_structure: Union[Structure, IStructure],
                        frac_coords: List[Union[List[float], Coords]],
                        infos: List[str]
                        ) -> SupercellInfo:
    """Append interstitial sites to SupercellInfo.

    Transforms fractional coordinates from unitcell to supercell
    and adds them as interstitial sites with symmetry information.

    Args:
        supercell_info: SupercellInfo to append interstitials to.
        unitcell_structure: Unitcell structure for symmetry analysis.
        frac_coords: Fractional coordinates in unitcell.
        infos: Description strings for each interstitial.

    Returns:
        Updated SupercellInfo with new interstitials.

    Raises:
        NotPrimitiveError: If unitcell doesn't match stored structure.

    Example:
        >>> updated = append_interstitial(
        ...     supercell_info, unitcell, [[0.5, 0.5, 0.5]], ["Td site"]
        ... )
        >>> updated.to_json_file()

    Note:
        inv_trans_mat must be multiplied with coords from the right as the
        trans_mat is multiplied to the unitcell lattice vector from the left.
    """
    if supercell_info.unitcell_structure and \
            supercell_info.unitcell_structure != unitcell_structure:
        print(f"""Unitcell in the supercell_info.json
{supercell_info.unitcell_structure}
"-----------------------------------"
"The given unitcell"
{unitcell_structure}""")
        raise NotPrimitiveError

    if isinstance(frac_coords[0], float):
        frac_coords = [frac_coords]

    for fcoord, info in zip(frac_coords, infos):
        us = Structure.from_dict(unitcell_structure.as_dict())
        us.append(species=Element.H, coords=fcoord)
        symmetrizer = StructureSymmetrizer(us)
        site_symm = symmetrizer.spglib_sym_data.site_symmetry_symbols[-1]

        inv_matrix = inv(np.array(supercell_info.transformation_matrix))
        new_coords = np.dot(fcoord, inv_matrix).tolist()

        supercell_info.interstitials.append(
            Interstitial(frac_coords=new_coords,
                         site_symmetry=site_symm,
                         info=info))
    return supercell_info
