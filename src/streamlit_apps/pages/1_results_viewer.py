"""This module creates a streamlit app"""

import streamlit as st

import folium
import xyzservices.providers as xyz
from streamlit_folium import st_folium
import geopandas as gpd

import laptime_sim
from laptime_sim import time_to_str

PATH_LINES = "./simulated/"


def folium_track_map(track: laptime_sim.Track, all_track_racelines: gpd.GeoDataFrame, race_line):

    my_map = None
    my_map = track.divisions.explore(m=my_map, name="divisions", show=False, style_kwds=dict(color="grey"))

    style_kwds = dict(color="black")
    my_map = track.right.explore(m=my_map, name="right", control=False, style_kwds=style_kwds)
    my_map = track.left.explore(m=my_map, name="left", control=False, style_kwds=style_kwds)

    style_kwds = dict(color="black", dashArray="2 5", opacity=0.6)
    my_map = all_track_racelines.explore(m=my_map, name="results", control=False, style_kwds=style_kwds)

    style_kwds = dict(color="blue")
    race_line.explore(m=my_map, name=race_line.car.iloc[0], style_kwds=style_kwds)

    folium.TileLayer(xyz.Esri.WorldImagery).add_to(my_map)
    folium.TileLayer("openstreetmap").add_to(my_map)
    folium.LayerControl().add_to(my_map)
    return my_map


def main() -> None:

    st.header("Race track display")

    sim_results = gpd.read_parquet(PATH_LINES)
    track_name = st.radio("select track", options=sim_results.track_name.unique())
    track = laptime_sim.Track.from_track_name(track_name)

    sim_results: gpd.GeoDataFrame = sim_results[sim_results.track_name == track_name]

    def format_results(x):
        x = sim_results.loc[x]
        return f"{x.car} ({time_to_str(x.best_time)})"

    p = st.radio("select result", options=sim_results.index, format_func=format_results)
    race_line = sim_results[sim_results.index == p]

    track_map = folium_track_map(track, sim_results, race_line)

    st_folium(track_map, returned_objects=[], use_container_width=True)

    with st.expander("track_layout: GeoDataFrame"):
        st.write(track.layout.to_dict(orient="records"))
        st.write(track.layout.is_ring.rename("is_ring"))
        st.write(f"{track.layout.crs=}")


if __name__ == "__main__":
    main()
