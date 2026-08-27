import geopandas as gpd


def clean_text_columns(gdf: gpd.GeoDataFrame, logger) -> gpd.GeoDataFrame:
    """Cleans text columns within a GeoDataFrame and logs the modifications.

    Iterates through all columns of type 'object' or 'string', removes carriage
    returns, strips leading/trailing whitespaces, and converts specific empty 
    or placeholder values into Python None objects. Each modification is 
    tracked and summarized using the provided logger instance.

    Args:
        gdf: The input GeoDataFrame containing spatial and attribute data.
        logger: A logging.Logger instance configured to record the cleaning 
            process details and summary statistics.

    Returns:
        A new GeoDataFrame instance containing the cleaned and normalized 
        text fields, while maintaining the original geometry and CRS.
    """
    logger.info("Schritt 1: Allgemeiner Text-Clean (Strip, Linebreaks, Platzhalter)...")
    gdf = gdf.copy()
    text_columns = gdf.select_dtypes(include=["object", "string"]).columns
    total_updates = 0

    for col in text_columns:
        orig_series = gdf[col].astype(str)
        cleaned_series = (
            orig_series.str.replace(r"\n\r", " ", regex=True)
            .str.strip()
            .str.replace(r"^-$", "", regex=True)
            .replace(["", "nan", "None"], None)
        )
        changed_mask = orig_series != cleaned_series.astype(str)
        num_changed = changed_mask.sum()

        if num_changed > 0:
            gdf[col] = cleaned_series
            logger.info(f"Spalte '{col}': {num_changed}")
            total_updates += num_changed

    logger.info(f"Allgemeiner Text-Clean beendet. {total_updates} Änderungen.")
    return gdf