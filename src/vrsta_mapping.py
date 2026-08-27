import geopandas as gpd


def rename_vrsta_categories(
    gdf: gpd.GeoDataFrame, logger
) -> gpd.GeoDataFrame:
    """Translates 'vrsta' column values to match the official ministry register.

    Applies a fixed mapping to standardize all four unique categories in the
    'vrsta' column to their official terms from the Ministry of Culture.

    Args:
        gdf: The input GeoDataFrame containing the 'vrsta' column.
        logger: A logging.Logger instance to record processing changes.

    Returns:
        A new GeoDataFrame with updated 'vrsta' category names.
    """
    logger.info(
        "Schritt: Passe Spalte 'vrsta' an das offizielle Webregister an..."
    )
    gdf = gdf.copy()

    if "vrsta" in gdf.columns:
        vrsta_mapping = {
            "Pojedinačna kulturna dobra": "Nepokretna pojedinačna",
            "Kulturnopovijesne cjeline": "Kulturnopovijesna cjelina",
            "Kulturni krajolici": "Kulturni krajolik",
            "Arheološka kulturna dobra": "Arheologija",
        }

        orig_series = gdf["vrsta"].astype(str)
        cleaned_series = orig_series.map(vrsta_mapping).fillna(orig_series)

        changed_mask = orig_series != cleaned_series
        num_changed = changed_mask.sum()

        gdf["vrsta"] = cleaned_series

        logger.info(
            f"Spalte 'vrsta': {num_changed} Datensätze auf Register-Namen aktualisiert."
        )
    else:
        logger.warning("Spalte 'vrsta' nicht im GeoDataFrame gefunden!")

    return gdf
