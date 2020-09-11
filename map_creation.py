"""
This program creates a map of points in the map with different colours according to the elevation
"""
import folium
import pandas


def elev_color(elevation):
    """
    Point will have colour according to its elevation
    """
    if elevation < 1000:
        return 'green'
    elif 1000 <= elevation < 3000:
        return 'orange'
    else:
        return 'red'


if __name__ == "main":
    data = pandas.read_csv("Volcanoes.txt")
    lan = list(data["LAT"])
    lon = list(data["LON"])
    elev = list(data["ELEV"])
    new_map = folium.Map(location=[38.58, -99], zoom_start=13, tiles="Stamen Terrain")
    feat_groupv = folium.FeatureGroup(name="Volcanoes")
    for lt, lon, el in zip(lan, lon, elev):
        feat_groupv.add_child(
            folium.CircleMarker(location=[lt, lon], radius=6, popup=str(el) + " m",
                                fill_color=elev_color(el),
                                color=elev_color(el), fill=True, fillOpacity=0.7))

    feat_groupw = folium.FeatureGroup(name="Population")
    feat_groupw.add_child(folium.GeoJson(data=open('world.json', 'r',
                                                   encoding='utf-8-sig').read(),
                                         style_function=lambda x: {'fillColor': 'yellow'}))
    new_map.add_child(feat_groupv)
    new_map.add_child(feat_groupw)
    new_map.add_child(folium.LayerControl())
    new_map.save("Map1.html")
