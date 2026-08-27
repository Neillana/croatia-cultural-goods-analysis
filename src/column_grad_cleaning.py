import geopandas as gpd


def clean_column_grad(gdf: gpd.GeoDataFrame, logger) -> gpd.GeoDataFrame:
    """Standardizes the 'grad' column to Title Case and splits by delimiter."""
    logger.info("Schritt 2: Bereinige Spalte 'grad'...")
    gdf = gdf.copy()
    
    orig_series = gdf["grad"].astype(str)
    
    cleaned_series = orig_series.str.title().str.split(" - ").str[0].str.strip()
    
    changed_mask = orig_series != cleaned_series
    num_changed = changed_mask.sum()
    
    gdf["grad"] = cleaned_series
    logger.info(f"Spalte 'grad': {num_changed} Werte erfolgreich standardisiert.")
    
    return gdf
