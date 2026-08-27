from collections import defaultdict

import geopandas as gpd
import numpy as np


def clean_text_columns(gdf: gpd.GeoDataFrame, logger) -> gpd.GeoDataFrame:
    """Cleans text columns within a GeoDataFrame and logs detailed modifications.

    Iterates through all columns of type 'object' or 'string', fixes linebreaks,
    excel artifacts, whitespaces, and converts specific empty or placeholder values 
    into Python None (np.nan) objects. Each modification is tracked and 
    summarized statistically per column and globally using the provided logger.
    """
    logger.info("Schritt 1: Detaillierter Text-Clean gestartet...")
    gdf = gdf.copy()
    text_columns = gdf.select_dtypes(include=["object", "string"]).columns

    col_stats = defaultdict(lambda: {
        "linebreaks": 0,
        "excel_artifacts": 0,
        "whitespaces": 0,
        "placeholders": 0,
        "invalid_to_nan": 0
    })
    
    global_stats = {
        "linebreaks": 0,
        "excel_artifacts": 0,
        "whitespaces": 0,
        "placeholders": 0,
        "invalid_to_nan": 0
    }

    for col in text_columns:
        s = gdf[col]
        
        is_original_na = s.isna()
        s_str = s.astype(str)
        s_str[is_original_na] = np.nan 
        
        mask_linebreaks = s_str.str.contains(r'[\r\n]', regex=True, na=False)
        cnt_linebreaks = mask_linebreaks.sum()
        col_stats[col]["linebreaks"] += cnt_linebreaks
        global_stats["linebreaks"] += cnt_linebreaks
        s_str = s_str.str.replace(r'[\r\n]+', ' ', regex=True)
        
        mask_artifacts = s_str.str.contains(r'\xa0|_x[0-9A-Fa-f]{4}_', regex=True, na=False)
        cnt_artifacts = mask_artifacts.sum()
        col_stats[col]["excel_artifacts"] += cnt_artifacts
        global_stats["excel_artifacts"] += cnt_artifacts
        s_str = s_str.str.replace(r'\xa0|_x[0-9A-Fa-f]{4}_', ' ', regex=True)
        
        mask_whitespaces = s_str.str.contains(r'^\s+|\s+$|\s{2,}', regex=True, na=False)
        cnt_whitespaces = mask_whitespaces.sum()
        col_stats[col]["whitespaces"] += cnt_whitespaces
        global_stats["whitespaces"] += cnt_whitespaces
        s_str = s_str.str.replace(r'\s+', ' ', regex=True).str.strip()
        
        mask_placeholders = s_str.str.match(r'^-$', na=False)
        cnt_placeholders = mask_placeholders.sum()
        col_stats[col]["placeholders"] += cnt_placeholders
        global_stats["placeholders"] += cnt_placeholders
        s_str = s_str.str.replace(r'^-$', '', regex=True)
        
        invalid_texts = ["", "nan", "NaN", "None", "null", "<NA>"]
        mask_invalid = s_str.isin(invalid_texts) & ~is_original_na
        cnt_invalid = mask_invalid.sum()
        col_stats[col]["invalid_to_nan"] += cnt_invalid
        global_stats["invalid_to_nan"] += cnt_invalid
        s_str = s_str.replace(invalid_texts, np.nan)
        
        gdf[col] = s_str

    logger.info("--- Fehlerstatistik pro Spalte ---")
    for col, stats in col_stats.items():
        col_total = sum(stats.values())
        if col_total > 0:
            details = ", ".join([f"{k}: {v}" for k, v in stats.items() if v > 0])
            logger.info(f"> Spalte '{col}': {col_total} Änderungen ({details})")
            
    logger.info("--- Globale Fehlerzusammenfassung ---")
    logger.info(f"> Zeilenumbrüche entfernt: {global_stats['linebreaks']}")
    logger.info(f"> Excel-Artefakte entfernt: {global_stats['excel_artifacts']}")
    logger.info(f"> Whitespace-Korrekturen: {global_stats['whitespaces']}")
    logger.info(f"> Platzhalter entfernt: {global_stats['placeholders']}")
    logger.info(f"> Ungültige Texte zu NaN konvertiert: {global_stats['invalid_to_nan']}")
    
    total_updates = sum(global_stats.values())
    logger.info(f"Gesamtanzahl behobener Anomalien über alle Spalten: {total_updates}")
    
    gdf.attrs["global_stats"] = global_stats
    gdf.attrs["col_stats"] = col_stats

    return gdf
