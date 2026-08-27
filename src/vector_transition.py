import geopandas as gpd


def extract_centroid_coordinates(gdf: gpd.GeoDataFrame, logger) -> gpd.GeoDataFrame:
    logger.info("Schritt 4: Extrahieren der Mittelpunkt-Koordinaten aus 'geometry'...")
    gdf = gdf.copy()

    if "geometry" not in gdf.columns:
        logger.error("Spalte 'geometry' wurde im GeoDataFrame nicht gefunden!")
        return gdf

    original_crs = gdf.crs
    if original_crs is None:
        logger.warning("Kein CRS (Koordinatensystem) im GeoDataFrame definiert! Gehe standardmäßig von EPSG:4326 (WGS84) aus.")
        gdf.set_crs(epsg=4326, inplace=True)
        original_crs = gdf.crs

    try:
        gdf_metric = gdf.to_crs(epsg=3857)
        centroids_metric = gdf_metric.geometry.centroid

        centroids_wgs84 = centroids_metric.to_crs(epsg=4326)

        gdf["longitude"] = centroids_wgs84.x
        gdf["latitude"] = centroids_wgs84.y
        
        logger.info(f"Mittelpunkte für {len(gdf)} Geometrien erfolgreich berechnet.")
        logger.info("Neue Spalten 'longitude' und 'latitude' (in WGS84) wurden hinzugefügt.")

    except (ValueError, TypeError) as e:
        logger.error(f"Fehler bei der Koordinatenberechnung: {e}")

    return gdf