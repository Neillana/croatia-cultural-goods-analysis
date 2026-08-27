import geopandas as gpd


def replace_value_in_column(
    gdf: gpd.GeoDataFrame,
    column: str,
    old_value: str,
    new_value: str,
    logger,
) -> gpd.GeoDataFrame:
    """Replaces a specific value in a column and logs the number of changes.

    Args:
        gdf: The input GeoDataFrame.
        column: Name of the target column.
        old_value: The exact string value to be replaced.
        new_value: The new string value to insert.
        logger: Logger instance for tracking the update.

    Returns:
        A new GeoDataFrame with the value replaced.
    """
    gdf = gdf.copy()

    if column in gdf.columns:
        # Maske für den zu ändernden Wert
        mask = gdf[column] == old_value
        num_changed = mask.sum()

        if num_changed > 0:
            gdf.loc[mask, column] = new_value
            logger.info(
                f"Schritt: Wert in '{column}' angepasst. "
                f"'{old_value}' -> '{new_value}' ({num_changed} Feld(er) korrigiert)."
            )
        else:
            logger.info(
                f"Schritt: Keine Anpassung in '{column}'. "
                f"Wert '{old_value}' wurde nicht gefunden."
            )
    else:
        logger.warning(f"Schritt fehlgeschlagen: Spalte '{column}' existiert nicht.")

    return gdf
