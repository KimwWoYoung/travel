import streamlit as st
import pandas as pd
import folium
from folium import Map, Marker, CircleMarker, PolyLine
from folium.plugins import BeautifyIcon
from streamlit_folium import st_folium
import matplotlib.cm as cm
import matplotlib.colors as colors

# CSV 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv("부산여행_여행일수포함_분리추가.csv")
    df["VISIT_ORDER"] = df["VISIT_ORDER"].astype(int)
    return df

df = load_data()

# 드롭다운 옵션 준비
days_options = ["전체"] + sorted(df["여행일수"].dropna().unique())
residence_options = ["전체"] + sorted(df["거주지"].dropna().str.strip().unique())
age_options = ["전체"] + sorted(df["연령대"].dropna().str.strip().unique())
companion_options = ["전체"] + sorted(df["동행유형"].dropna().str.strip().unique())

# 필터 UI
col1, col2, col3, col4 = st.columns(4)
with col1:
    selected_days = st.selectbox("여행일수 선택", days_options)
with col2:
    selected_residence = st.selectbox("거주지 선택", residence_options)
with col3:
    selected_age = st.selectbox("연령대 선택", age_options)
with col4:
    selected_companion = st.selectbox("동행유형 선택", companion_options)

# 필터링
df_filtered = df.copy()

if selected_days != "전체":
    df_filtered = df_filtered[df_filtered["여행일수"] == selected_days]
if selected_residence != "전체":
    df_filtered = df_filtered[df_filtered["거주지"].str.strip() == selected_residence]
if selected_age != "전체":
    df_filtered = df_filtered[df_filtered["연령대"].str.strip() == selected_age]
if selected_companion != "전체":
    df_filtered = df_filtered[df_filtered["동행유형"].str.strip() == selected_companion]

# 유효한 TRAVEL_ID 기반 전체 경로 확보
valid_ids = df_filtered["TRAVEL_ID"].unique()
df_filtered = df[df["TRAVEL_ID"].isin(valid_ids)]

# 색상 맵 설정
norm = colors.Normalize(vmin=df_filtered["VISIT_ORDER"].min(), vmax=df_filtered["VISIT_ORDER"].max())
cmap = cm.get_cmap("Blues")

# 지도 생성
m = Map(location=[35.1796, 129.0756], zoom_start=12)

# 경로 및 마커 표시
for travel_id, group in df_filtered.groupby("TRAVEL_ID"):
    group = group.sort_values("VISIT_ORDER")
    coords = list(zip(group["Y_COORD"], group["X_COORD"]))
    PolyLine(coords, color="blue", weight=2, opacity=0.4).add_to(m)

    for idx, row in group.iterrows():
        location = (row["Y_COORD"], row["X_COORD"])
        order = row["VISIT_ORDER"]
        poi = row["POI_NM"]

        if idx == 0:
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
        elif idx == len(group) - 1:
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

# 지도 출력
st_folium(m, width=1000, height=700)
