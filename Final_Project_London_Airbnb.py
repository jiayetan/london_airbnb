"""
Name: Jiaye Tan
CS230: Section 6
Data: LondonAirBnBSep2021.csv
URL: https://share.streamlit.io/jiayetan/london_airbnb/main/Final_Project_London_Airbnb.py
Description:
User can use this app to filter, sort, and analysis listings. Some analysis functions include show room
types composition of each neighbourhood with a stacked bar chart and a pie chart; show price distribution
of each room type in each neighbourhood; and show room type and price info with a pivot table.
"""


import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
import webbrowser
import folium
from haversine import haversine


# DATA
# read raw data
data = pd.read_csv("LondonAirBnBSep2021.csv")

# sorted data
data_neighbourhood = sorted(set(data["neighbourhood"].tolist()))
data_room_type = sorted(set(data["room_type"].tolist()))

# attraction info
data_attraction = {
        "Natural History Museum": [51.496165, -0.1791013],
        "British Museum": [51.5194133, -0.1291506],
        "National Gallery": [51.5089712, -0.1312407],
        "Big Ben": [51.5032973, -0.1217477],
        "Tate Modern": [51.5032969, -0.1283406],
        "Tower of London": [51.5045321, -0.1267774],
        "Greenwich Park": [51.4793578, -0.0066917],
        "Buckingham Palace": [51.5060671, -0.1535122],
        "Harrods": [51.4989874, -0.1657343],
        "Hyde Park": [51.5064124, -0.1704307]
}
data_attraction = dict(sorted(data_attraction.items()))


# FUNCTION
def stacked_bar_chart():
    num_apt = []
    num_hotel = []
    num_private = []
    num_shared = []
    num_total_listing = []

    for i in range(len(data_neighbourhood)):
        r1 = len(data.loc[(data["neighbourhood"] == data_neighbourhood[i]) & (data["room_type"] == "Entire home/apt")])
        r2 = len(data.loc[(data["neighbourhood"] == data_neighbourhood[i]) & (data["room_type"] == "Hotel room")])
        r3 = len(data.loc[(data["neighbourhood"] == data_neighbourhood[i]) & (data["room_type"] == "Private room")])
        r4 = len(data.loc[(data["neighbourhood"] == data_neighbourhood[i]) & (data["room_type"] == "Shared room")])
        total = r1 + r2 + r3 + r4
        num_apt.append(r1)
        num_hotel.append(r2)
        num_private.append(r3)
        num_shared.append(r4)
        num_total_listing.append(total)

    # sort with total listing
    list_neighbourhood = [i for _, i in sorted(zip(num_total_listing, data_neighbourhood), reverse=True)]
    num_apt = [i for _, i in sorted(zip(num_total_listing, num_apt), reverse=True)]
    num_hotel = [i for _, i in sorted(zip(num_total_listing, num_hotel), reverse=True)]
    num_private = [i for _, i in sorted(zip(num_total_listing, num_private), reverse=True)]
    num_shared = [i for _, i in sorted(zip(num_total_listing, num_shared), reverse=True)]

    num_apt = np.array(num_apt)
    num_hotel = np.array(num_hotel)
    num_private = np.array(num_private)
    num_shared = np.array(num_shared)

    fig, ax = plt.subplots()
    ax.bar(list_neighbourhood, num_apt, color="r")
    ax.bar(list_neighbourhood, num_hotel, bottom=num_apt, color="b")
    ax.bar(list_neighbourhood, num_private, bottom=num_apt + num_hotel, color="y")
    ax.bar(list_neighbourhood, num_shared, bottom=num_apt + num_hotel + num_private, color="g")
    ax.set_xlabel("Neighbourhood")
    ax.set_ylabel("Number of Listings")
    ax.set_title("Number of Listings in Each Neighbourhood\n", fontsize=15)
    ax.tick_params(axis='x', labelrotation=90)
    ax.legend(labels=data_room_type)

    return fig


def table_group_by_all_listing():
    table = data.rename(columns={"neighbourhood": "Neighbourhood", "id": "Number of Listings"})
    table = table.groupby(by="Neighbourhood").count()["Number of Listings"]
    table = table.reset_index().sort_values("Number of Listings", ascending=False)
    return table


def table_group_by_neighbourhood():
    data_n = data.loc[data["neighbourhood"] == opt_chart_neighbourhood]
    table = data_n.rename(columns={"room_type": "Room Type", "id": "Listings"})
    table = table.groupby(by="Room Type").count()["Listings"]
    table = table.reset_index().sort_values("Listings", ascending=False)
    return table


def pie_chart(neighbourhood):
    r1 = len(data.loc[(data["neighbourhood"] == neighbourhood) & (data["room_type"] == "Entire home/apt")])
    r2 = len(data.loc[(data["neighbourhood"] == neighbourhood) & (data["room_type"] == "Hotel room")])
    r3 = len(data.loc[(data["neighbourhood"] == neighbourhood) & (data["room_type"] == "Private room")])
    r4 = len(data.loc[(data["neighbourhood"] == neighbourhood) & (data["room_type"] == "Shared room")])
    num_room = [r1, r2, r3, r4]

    fig, ax = plt.subplots()
    ax.pie(num_room, labels=data_room_type, autopct="%.1f%%")

    ax.set_title(f"Room Type Composition of {opt_chart_neighbourhood}\n", fontsize=15)

    return fig


def histogram_chart(neighbourhood, room_type):
    price = data.loc[(data["neighbourhood"] == neighbourhood) & (data["room_type"] == room_type)]["price"].tolist()

    fig, ax = plt.subplots()
    ax.hist(price, bins="auto", range=[0, 800], color="y")

    ax.set_title(f"Price Distribution of all {opt_chart_room_type} in {opt_chart_neighbourhood}\n", fontsize=15)
    ax.set_xlabel("Price (didn't include price over 800)")
    ax.set_ylabel("Number of Listings")

    return fig


def pivot_table():
    table = pd.pivot_table(data, values=["price", "id"], index=["neighbourhood", "room_type"], aggfunc={"id": np.count_nonzero, "price": [np.mean, min, max]})
    return table


# DEFAULT PAGE
st.header("London Airbnb Search and Analysis System")
st.write("---")

# SIDEBAR
# Filters and Sorts
st.sidebar.header("Filters")
# select by neighbourhood or by attraction
opt_filter_type = st.sidebar.radio("Select areas:", ("By Neighbourhood", "By Attraction"))
if opt_filter_type == "By Neighbourhood":
    opt_neighborhood = st.sidebar.multiselect("Select neighbourhoods you want to stay:", data_neighbourhood)
else:
    opt_attraction = st.sidebar.selectbox("Select an attraction you want to stay nearby:", data_attraction)
    opt_len_unit = st.sidebar.radio("Select length unit:", ("mi", "km"))
    opt_radius = st.sidebar.slider(f"Distance to the attraction within: ({opt_len_unit})", 0.5, 3.0, step=0.1)

# select room type
opt_room_type = st.sidebar.multiselect("Select room types:", data_room_type)

# select price range
price_str = ["<50", "100", "150", "200", "300", "500", "1000", "2000", "5000+"]
price_int = [0, 100, 150, 200, 300, 500, 1000, 2000, 99999]
price_int_exception = [50, 5000]
opt_price_min, opt_price_max = st.sidebar.select_slider("Set the price range per night: (GBP)", options=price_str, value=[price_str[0], price_str[8]])

for i in range(len(price_str)):
    if price_str[i] == opt_price_min:
        if i == 8:
            opt_price_min = price_int_exception[1]
        else:
            opt_price_min = price_int[i]
    if price_str[i] == opt_price_max:
        if i == 0:
            opt_price_max = price_int_exception[0]
        else:
            opt_price_max = price_int[i]

# more filters
more_filters = st.sidebar.expander("More Filters")
opt_zero_review = more_filters.checkbox("At least one review")
opt_availability = more_filters.checkbox("Availability in one year > 70%")

# sorts
st.sidebar.header("Sorts")
opt_sort = st.sidebar.selectbox("Sort listings by:", ["Listing ID Asc.", "Price Lowest to Highest", "Price Highest to Lowest"])

# show results
st.sidebar.write("")
opt_display = st.sidebar.button("Show Listings with Table and Map")
st.sidebar.write("---")

# Analysis
# all listings
st.sidebar.header("Room and Price Analysis")
opt_stacked_bar_chart = st.sidebar.button("Room Types of All Listings")
opt_pivot_table = st.sidebar.button("Show Price Analysis")
st.sidebar.write("")
opt_chart_neighbourhood = st.sidebar.selectbox("Select a neighbourhood:", data_neighbourhood)
opt_chart_room_type = st.sidebar.selectbox("Select a room type:", data_room_type)
opt_pie_chart = st.sidebar.button("Show Room Type Composition")
opt_histogram = st.sidebar.button("Show Price Distribution")

# Credit
st.sidebar.write("---")
st.sidebar.success("This site was made by Jiaye Tan for CS230 course.")

# MAIN PAGE
# show all listing with table and map
if opt_display:
    if opt_filter_type == "By Neighbourhood":
        filtered_data = data.loc[data["neighbourhood"].isin(opt_neighborhood) & data["room_type"].isin(opt_room_type) & (data["price"] >= opt_price_min) & (data["price"] <= opt_price_max)]
    else:
        loc_lat = []
        loc_lon = []
        for i in range(len(data)):
            distance = haversine(data_attraction[opt_attraction], [data["latitude"][i], data["longitude"][i]], unit=opt_len_unit)
            if distance <= opt_radius:
                loc_lat.append(data["latitude"][i])
                loc_lon.append(data["longitude"][i])
        filtered_data = data.loc[data["latitude"].isin(loc_lat) & data["longitude"].isin(loc_lon) & data["room_type"].isin(opt_room_type) & (data["price"] >= opt_price_min) & (data["price"] <= opt_price_max)]
    if opt_zero_review:
        filtered_data = filtered_data.loc[filtered_data["number_of_reviews"] > 0]
    if opt_availability:
        filtered_data = filtered_data.loc[filtered_data["availability_365"] / 365 > 0.7]
    if opt_sort == "Price Lowest to Highest":
        filtered_data = filtered_data.sort_values(by=["price"])
    if opt_sort == "Price Highest to Lowest":
        filtered_data = filtered_data.sort_values(by=["price"], ascending=False)

    # show metrics
    host_id = filtered_data["host_id"].tolist()
    host_id_list = []
    for i in host_id:
        if i not in host_id_list:
            host_id_list.append(i)
    col_1, col_2, col_3 = st.columns(3)
    col_1.metric(label="Total Listings", value=len(filtered_data), delta=None)
    if len(filtered_data) > 0:
        col_2.metric(label="Average Price (GBP)", value=int(filtered_data["price"].mean()), delta=None)
    else:
        col_2.metric(label="Average Price (GBP)", value="", delta=None)
    col_3.metric(label="Number of Hosts", value=len(host_id_list), delta=None)

    # show table
    show_table_listing = pd.DataFrame({
        "ID": filtered_data["id"],
        "Room Name": filtered_data["name"],
        "Neighbourhood": filtered_data["neighbourhood"],
        "Room Type": filtered_data["room_type"],
        "Price": filtered_data["price"]
    })
    st.table(show_table_listing)

    # show on map
    center = [51.509865, -0.118092]
    london_map = folium.Map(location=center, zoom_start=11)

    for i in filtered_data.itertuples():
        icon = folium.Icon(icon="home", prefix="fa", color="red")
        folium.Marker(location=[i[7], i[8]], popup=f"Price: {i[10]}", tooltip=i[2], icon=icon).add_to(london_map)

    if opt_filter_type == "By Attraction":
        icon_a = folium.Icon(icon="flag", prefix="fa", color="blue")
        folium.Marker(location=data_attraction[opt_attraction], popup=None, tooltip=opt_attraction, icon=icon_a).add_to(london_map)

    file_path = os.getcwd() + "\\london_map.html"
    london_map.save(file_path)
    webbrowser.open('file://' + file_path)

# show all listing with stacked bar chart
if opt_stacked_bar_chart:
    st.pyplot(stacked_bar_chart())
    st.table(table_group_by_all_listing())

# show pivot table
if opt_pivot_table:
    st.table(pivot_table())

# show room type composition of neighbourhood with pie chart
if opt_pie_chart:
    col_1, col_2 = st.columns([4, 2])
    col_1.pyplot(pie_chart(opt_chart_neighbourhood))
    col_2.table(table_group_by_neighbourhood())

# show price distribution
if opt_histogram:
    st.pyplot(histogram_chart(opt_chart_neighbourhood, opt_chart_room_type))
