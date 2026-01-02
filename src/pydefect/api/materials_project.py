# -*- coding: utf-8 -*-
#  Copyright (c) 2020 Kumagai group.
"""API for Materials Project integration."""

from itertools import combinations
from pathlib import Path
from shutil import copyfile
from typing import List, Union

import yaml
from mp_api.client import MPRester

from pydefect.data.molecules.molecules import MOLECULE_DATA
from pydefect.defaults import defaults
from pymatgen.core import Composition
from vise.util.logger import get_logger

logger = get_logger(__name__)


class MpQuery:
    """Query Materials Project database for materials.

    Searches for stable materials in a given chemical system.

    Attributes:
        materials: List of MaterialsSummaryDoc from MP.

    Example:
        >>> query = MpQuery(["Mg", "O"])
        >>> for mat in query.materials:
        ...     print(mat.formula_pretty)
    """
    def __init__(self,
                 element_list: List[str],
                 e_above_hull: float = defaults.e_above_hull,
                 properties: List[str] = None):
        # API key is parsed via .pmgrc.yaml
        with MPRester() as m:
            # Due to mp_decode=True by default, class objects are restored.
            logger.info("Note that you're using the newer MPRester.")
            default_fields = ["material_id", "formula_pretty", "structure",
                              "symmetry", "band_gap", "total_magnetization",
                              "types_of_magnetic_species"]
            properties = properties or default_fields
            self.materials = m.materials.summary.search(
                chemsys=chemsys(element_list),
                energy_above_hull=(-1e-5, e_above_hull),
                fields=properties)


def chemsys(element_list: list) -> list:
    """Generate chemical system strings for MP query.

    Args:
        element_list: List of element symbols.

    Returns:
        List of hyphen-separated element combinations.
    """
    result = []
    for num_elements in range(1, len(element_list)+1):
        for comb in combinations(element_list, num_elements):
            result.append('-'.join(comb))

    return result


def make_poscars_from_query(materials_query: List[Union[dict, "SummaryDoc"]],
                            path: Path) -> None:
    """Create POSCAR files from Materials Project query results.

    Args:
        materials_query: List of MP query results.
        path: Directory to create structure files.

    Example:
        >>> query = MpQuery(["Mg", "O"]).materials
        >>> make_poscars_from_query(query, Path("./"))
    """
    mol_dir = Path(__file__).parent.parent / "data" / "molecules"
    
    for query in materials_query:
        try:
            reduced_formula = Composition(query["full_formula"]).reduced_formula
        except (TypeError, AttributeError, KeyError):
            # For new MPRester.
            reduced_formula = query.formula_pretty

        if reduced_formula in MOLECULE_DATA.keys():
            _make_molecular_directory(path, reduced_formula, mol_dir)
        else:
            _make_solid_directory(path, reduced_formula, query)


def _make_solid_directory(path: Path, reduced_formula: str,
                          query: Union[dict, "SummaryDoc"]):
    try:
        task_id = query['task_id']
    except (TypeError, AttributeError, KeyError):
        # For new MPRester.
        task_id = query.material_id

    dirname = path / f"{reduced_formula}_{task_id}"
    logger.info(f"{dirname.name} is being created with a MP structure.")
    dirname.mkdir()

    try:
        query["structure"].to(filename=str(dirname / "POSCAR"))
        d = {"total_magnetization": query["total_magnetization"],
             "band_gap": query["band_gap"],
             "data_source": query["task_id"]}
    except (TypeError, AttributeError, KeyError):
        # For new MPRester.
        query.structure.to(filename=str(dirname / "POSCAR"))
        d = {"total_magnetization": query.total_magnetization,
             "band_gap": query.band_gap,
             "data_source": f"new MPRester {query.material_id}"}

    prior_info = dirname / "prior_info.yaml"
    prior_info.write_text(yaml.dump(d), None)


def _make_molecular_directory(path: Path, reduced_formula: str, mol_dir: Path):
    dirname = path / f"mol_{reduced_formula}"
    logger.info(
        f"{dirname.name} is being created with molecular data in pydefect.")
    if not dirname.exists():
        dirname.mkdir()
        copyfile(mol_dir / reduced_formula / "POSCAR",
                 dirname / "POSCAR")
        copyfile(mol_dir / reduced_formula / "prior_info.yaml",
                 dirname / "prior_info.yaml")
