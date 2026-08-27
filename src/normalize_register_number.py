import geopandas as gpd
import numpy as np


def extract_register_artefacts(gdf: gpd.GeoDataFrame, logger) -> gpd.GeoDataFrame:
    """Splits 'registarski_broj' into a clean identifier and moves any trailing 
    characters into a new column 'register_artefacts', with additional cleaning.

    Validates that extracted artefacts contain exactly a 4-digit number.
    """
    logger.info("Schritt 2: Extraktion von 'register_artefacts' aus 'registarski_broj'...")
    gdf = gdf.copy()
    
    gdf["register_artefacts"] = np.nan

    if "registarski_broj" not in gdf.columns:
        logger.error("Spalte 'registarski_broj' wurde im GeoDataFrame nicht gefunden!")
        return gdf

    if gdf["registarski_broj"].isna().all():
        logger.warning("Spalte 'registarski_broj' enthält nur Nullwerte. Keine Aufteilung notwendig.")
        return gdf

    regex_pattern = r"^(?P<clean_id>[A-Z]+-\d+)(?P<artefacts>.*)$"
    extracted = gdf["registarski_broj"].str.extract(regex_pattern)
    
    if "clean_id" not in extracted.columns:
        extracted["clean_id"] = np.nan
    if "artefacts" not in extracted.columns:
        extracted["artefacts"] = np.nan

    valid_pattern_mask = extracted["clean_id"].notna() & gdf["registarski_broj"].notna()
    has_artefacts_mask = valid_pattern_mask & (extracted["artefacts"].str.strip().fillna("") != "")
    num_changed = has_artefacts_mask.sum()
    
    failed_pattern_mask = gdf["registarski_broj"].notna() & ~valid_pattern_mask
    num_failed = failed_pattern_mask.sum()

    gdf["registarski_broj"] = np.where(valid_pattern_mask, extracted["clean_id"], gdf["registarski_broj"])
    
    cleaned_artefacts = (
        extracted["artefacts"]
        .str.strip()
        .str.lstrip("-")
        .str.rstrip(".")
        .str.strip()
    )
    
    gdf["register_artefacts"] = cleaned_artefacts.replace("", np.nan)
    
    has_value_mask = gdf["register_artefacts"].notna()
    
    is_four_digits_mask = gdf["register_artefacts"].str.match(r"^\d{4}$", na=False)
    
    invalid_artefacts_mask = has_value_mask & ~is_four_digits_mask
    num_invalid_artefacts = invalid_artefacts_mask.sum()
    
    if num_changed > 0:
        logger.info(f"Spalte 'registarski_broj': {num_changed} Werte aufgeteilt und Reste nach 'register_artefacts' verschoben.")
        
    if num_failed > 0:
        invalid_values = gdf.loc[failed_pattern_mask, "registarski_broj"].unique().tolist()
        logger.warning(
            f"Spalte 'registarski_broj': {num_failed} Zeilen entsprachen nicht dem "
            f"erwarteten Format (Buchstaben-Zahlen) und wurden übersprungen. "
            f"Betroffene Werte: {invalid_values}"
        )

    if num_invalid_artefacts > 0:
        invalid_orig_values = gdf.loc[invalid_artefacts_mask, "registarski_broj"].unique().tolist()
        invalid_clean_values = gdf.loc[invalid_artefacts_mask, "register_artefacts"].unique().tolist()
        
        logger.warning(
            f"Spalte 'register_artefacts': {num_invalid_artefacts} extrahierte Artefakte "
            f"sind KEINE exakt 4-stellige Zahl (Jahresangabe). "
            f"Bereinigte Fehlerwerte: {invalid_clean_values} | "
            f"Aus Originaleinträgen: {invalid_orig_values}"
        )

    logger.info("Extraktion von 'register_artefacts' beendet.")
    return gdf
