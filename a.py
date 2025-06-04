import streamlit as st
import pandas as pd
import folium
from folium import Map, Marker, CircleMarker, PolyLine
from folium.plugins import BeautifyIcon
from streamlit_folium import st_folium
import matplotlib.cm as cm
import matplotlib.colors as colors
import os

# ---- 데이터 로딩 함수 ----
@st.cache_data
def load_data():
    if os.path.exists("부산여행.pkl"):
        df = pd.read_pickle("부산여행.pkl")
    else:
        df = pd.read_csv("부산여행_여행일수포함_분리추가.csv")
        df["VISIT_ORDER"] = df["VISIT_ORDER"].astype(int)
        df.to_pickle("부산여행.pkl")  # 최초 1회만 저장
    return df

# ---- 데이터 로딩 ----
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# ---- 드롭다운 필터 ----
days_options = ["전체"] + sorted(df["여행일수"].dropna().unique())
residence_options = ["전체"] + sorted(df["거주지"].dropna().str.strip().unique())
age_options = ["전체"] + sorted(df["연령대"].dropna().str.strip().unique())
companion_options = ["전체"] + sorted(df["동행유형"].dropna().str.strip().unique())

col1, col2, col3, col4 = st.columns(4)
with col1:
    selected_days = st.selectbox("여행일수 선택", days_options)
with col2:
    selected_residence = st.selectbox("거주지 선택", residence_options)
with col3:
    selected_age = st.selectbox("연령대 선택", age_options)
with col4:
    selected_companion = st.selectbox("동행유형 선택", companion_options)

# ---- 필터링 ----
df_filtered = df.copy()
if selected_days != "전체":
    df_filtered = df_filtered[df_filtered["여행일수"] == selected_days]
if selected_residence != "전체":
    df_filtered = df_filtered[df_filtered["거주지"].str.strip() == selected_residence]
if selected_age != "전체":
    df_filtered = df_filtered[df_filtered["연령대"].str.strip() == selected_age]
if selected_companion != "전체":
    df_filtered = df_filtered[df_filtered["동행유형"].str.strip() == selected_companion]

# ---- 유효 ID 기준 필터링 ----
valid_ids = df_filtered["TRAVEL_ID"].unique()
if len(valid_ids) > 30:
    st.warning("TRAVEL_ID가 너무 많습니다. 필터를 더 좁혀주세요. (현재: %d개)" % len(valid_ids))
    st.stop()

df_filtered = df[df["TRAVEL_ID"].isin(valid_ids)]

# ---- 지도 보기 버튼 ----
if st.button("지도 보기"):
    norm = colors.Normalize(vmin=df_filtered["VISIT_ORDER"].min(), vmax=df_filtered["VISIT_ORDER"].max())
    cmap = cm.get_cmap("Blues")
    m = Map(location=[35.1796, 129.0756], zoom_start=12)

    for travel_id, group in df_filtered.groupby("TRAVEL_ID"):
        group = group.sort_values("VISIT_ORDER")
        coords = list(zip(group["Y_COORD"], group["X_COORD"]))
        PolyLine(coords, color="blue", weight=2, opacity=0.4).add_to(m)

        for i, row in group.iterrows():
            location = (row["Y_COORD"], row["X_COORD"])
            order = row["VISIT_ORDER"]
            poi = row["POI_NM"]

            if i == group.index[0]:
                Marker(
                    location=location,
                    icon=BeautifyIcon(
                        icon_shape='rectangle',
                        border_color='red',
                        border_width=2,
                        text_color='white',
                        background_color='red',
                        number=order
                    ),
                    popup=f"[출발] {poi}",
                    tooltip=f"{order}번 - {poi}"
                ).add_to(m)
            elif i == group.index[-1]:
                Marker(
                    location=location,
                    icon=BeautifyIcon(
                        icon_shape='arrow-down',
                        border_color='red',
                        border_width=2,
                        text_color='white',
                        background_color='red',
                        number=order
                    ),
                    popup=f"[도착] {poi}",
                    tooltip=f"{order}번 - {poi}"
                ).add_to(m)
            else:
                CircleMarker(
                    location=location,
                    radius=6,
                    fill=True,
                    fill_color=colors.to_hex(cmap(norm(order))),
                    fill_opacity=0.8,
                    color='gray',
                    popup=f"{order}번 방문지: {poi}",
                    tooltip=f"{order}번 - {poi}"
                ).add_to(m)

    st_folium(m, width=1000, height=700)
