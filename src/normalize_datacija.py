import re

import geopandas as gpd
import pandas as pd


def _parse_datacija_logic(text):
    if pd.isna(text) or not isinstance(text, str) or text.strip() == "":
        return pd.Series([pd.NA, pd.NA])

    text_lower = text.lower()

    text_lower = re.sub(r'1\.\s*pol', 'prva_pol', text_lower)
    text_lower = re.sub(r'2\.\s*pol', 'druga_pol', text_lower)

    is_bc = bool(re.search(r'p\.?\s*n\.?\s*e|pr\.|p\.?\s*kr', text_lower))
    multiplier = -1 if is_bc else 1

    is_century = "st" in text_lower

    offset_start, offset_end = 1, 100
    if "poč" in text_lower:
        offset_start, offset_end = 1, 30
    elif "sred" in text_lower:
        offset_start, offset_end = 31, 70
    elif "kraj" in text_lower:
        offset_start, offset_end = 71, 100
    elif "prva_pol" in text_lower:
        offset_start, offset_end = 1, 50
    elif "druga_pol" in text_lower:
        offset_start, offset_end = 51, 100

    numbers = [int(num) for num in re.findall(r'\d+', text_lower)]

    if not numbers:
        return pd.Series([pd.NA, pd.NA])

    start_num = numbers[0]
    end_num = numbers[-1] if len(numbers) > 1 else start_num

    if is_century:
        if is_bc:
            start_year = (start_num * 100 * -1) + offset_start - 1
            end_year = (end_num * 100 * -1) + offset_end - 1
        else:
            start_year = (start_num - 1) * 100 + offset_start
            end_year = (end_num - 1) * 100 + offset_end
    else:
        start_year = start_num * multiplier
        end_year = end_num * multiplier

    if start_year > end_year:
        start_year, end_year = end_year, start_year

    return pd.Series([start_year, end_year])

def parse_datacija_columns(gdf: gpd.GeoDataFrame, logger) -> gpd.GeoDataFrame:
    """Parses the 'datacija' column into numerical 'year_start' and 'year_end' columns.

    Extracts centuries (st.) and negative years for B.C. (p.n.e.).
    Uses Pandas Nullable Integer (Int64) to support missing values.
    """
    logger.info("Schritt 3: Parsing von 'datacija' in numerische Jahreszahlen...")
    gdf = gdf.copy()

    gdf["year_start"] = pd.NA
    gdf["year_end"] = pd.NA

    if "datacija" not in gdf.columns:
        logger.error("Spalte 'datacija' wurde im GeoDataFrame nicht gefunden!")
        return gdf

    if gdf["datacija"].isna().all():
        logger.warning("Spalte 'datacija' enthält nur Nullwerte. Kein Parsing notwendig.")
    
        gdf["year_start"] = gdf["year_start"].astype("Int64")
        gdf["year_end"] = gdf["year_end"].astype("Int64")
        return gdf

    parsed_df = gdf["datacija"].apply(_parse_datacija_logic)
    parsed_df.columns = ["parsed_start", "parsed_end"]

    has_value_mask = gdf["datacija"].notna() & (gdf["datacija"].astype(str).str.strip() != "")

    valid_pattern_mask = has_value_mask & parsed_df["parsed_start"].notna()
    num_changed = valid_pattern_mask.sum()

    failed_pattern_mask = has_value_mask & ~valid_pattern_mask
    num_failed = failed_pattern_mask.sum()

    gdf.loc[valid_pattern_mask, "year_start"] = parsed_df.loc[valid_pattern_mask, "parsed_start"]
    gdf.loc[valid_pattern_mask, "year_end"] = parsed_df.loc[valid_pattern_mask, "parsed_end"]

    gdf["year_start"] = gdf["year_start"].astype("Int64")
    gdf["year_end"] = gdf["year_end"].astype("Int64")

    if num_changed > 0:
        logger.info(f"Spalte 'datacija': {num_changed} Werte erfolgreich in 'year_start' und 'year_end' (als Integer) umgewandelt.")

    if num_failed > 0:
        invalid_values = gdf.loc[failed_pattern_mask, "datacija"].unique().tolist()
        logger.warning(
            f"Spalte 'datacija': {num_failed} Zeilen konnten nicht als "
            f"gültige Jahreszahl/Jahrhundert interpretiert werden (keine Zahlen gefunden). "
            f"Betroffene Werte: {invalid_values}"
        )

    logger.info("Parsing von 'datacija' beendet.")
    return gdf