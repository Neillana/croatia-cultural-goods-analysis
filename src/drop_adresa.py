import geopandas as gpd


def drop_column_adresa(
    gdf: gpd.GeoDataFrame, logger
) -> gpd.GeoDataFrame:
    """Removes the 'adresa' column completely from the GeoDataFrame.

    Args:
        gdf: The input GeoDataFrame.
        logger: A logging.Logger instance to record the removal.

    Returns:
        A new GeoDataFrame without the 'adresa' column.
    """
    logger.info("Schritt 3: Entferne Spalte 'adresa' vollständig...")
    gdf = gdf.copy()

    if "adresa" in gdf.columns:
        gdf = gdf.drop(columns=["adresa"])
        logger.info("Spalte 'adresa' wurde erfolgreich gelöscht.")
    else:
        logger.warning("Spalte 'adresa' existiert bereits nicht mehr.")

    return gdf

