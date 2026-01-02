from typing import List, Tuple

from pydefect.analysis.calculation.models import CalcResults, CalcSummary, SingleCalcSummary
from pydefect.analysis.defect_structure.defect_structure_info import DefectStructureInfo
from pydefect.analysis.defect_energy.make_defect_energy_info import num_atom_differences
from pydefect.defaults import defaults
from pydefect.makers.defect.defect_entry import DefectEntry


def make_calc_summary(
        calc_set: List[Tuple[CalcResults, DefectEntry, DefectStructureInfo]],
        p_calc_results: CalcResults) -> CalcSummary:
    """Create CalcSummary from a set of defect calculations.

    Args:
        calc_set: List of (CalcResults, DefectEntry, DefectStructureInfo) tuples.
        p_calc_results: Perfect supercell calculation results.

    Returns:
        CalcSummary containing summaries for all defects.

    Example:
        >>> summary = make_calc_summary(calc_set, perfect_results)
        >>> summary.to_json_file()
    """
    summaries = {}
    for calc_results, entry, str_info in calc_set:
        summaries[entry.full_name] = \
            create_single_calc_summary(calc_results, entry, p_calc_results,
                                       str_info)
    return CalcSummary(single_summaries=summaries)


def create_single_calc_summary(calc_results, entry, p_calc_results, str_info):
    """Create SingleCalcSummary for one defect calculation.

    Args:
        calc_results: Defect calculation results.
        entry: DefectEntry specification.
        p_calc_results: Perfect supercell results.
        str_info: DefectStructureInfo analysis.

    Returns:
        SingleCalcSummary with convergence and structural info.
    """
    atom_io = num_atom_differences(calc_results.structure,
                                   p_calc_results.structure)
    relative_energy = calc_results.energy - p_calc_results.energy
    is_energy_strange = abs(relative_energy) > defaults.abs_strange_energy
    return SingleCalcSummary(
        charge=entry.charge,
        atom_io=atom_io,
        electronic_conv=calc_results.electronic_conv,
        ionic_conv=calc_results.ionic_conv,
        is_energy_strange=is_energy_strange,
        same_config_from_init=str_info.same_config_from_init,
        defect_type=str(str_info.defect_type),
        symm_relation=str(str_info.symm_relation))

