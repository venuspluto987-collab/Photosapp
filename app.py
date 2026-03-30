import streamlit as st
import numpy as np
from PIL import Image
import io
import cv2

st.set_page_config(layout="wide")
st.title("🔥 Click to Remove Object")

uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Click positions below")

    st.markdown("### 👉 Click on image to mark object")

    # store clicks
    if "points" not in st.session_state:
        st.session_state.points = []

    # simulate click input
    x = st.number_input("X position", 0, image.width-1)
    y = st.number_input("Y position", 0, image.height-1)

    if st.button("➕ Add Click"):
        st.session_state.points.append((x, y))

    if st.button("🧹 Reset"):
        st.session_state.points = []

    # create mask
    mask = np.zeros((image.height, image.width), dtype=np.uint8)

    for (px, py) in st.session_state.points:
        cv2.circle(mask, (px, py), 25, 255, -1)

    # overlay preview
    overlay = img_np.copy()
    overlay[mask > 0] = (overlay[mask > 0]*0.5 + np.array([255,0,0])*0.5).astype(np.uint8)

    st.image(overlay, caption="Selected Area")

    if st.button("🚀 Remove Object"):
        result = cv2.inpaint(img_np, mask, 3, cv2.INPAINT_TELEA)

        with col2:
            st.image(result, caption="Result")

        buf = io.BytesIO()
        Image.fromarray(result).save(buf, format="PNG")

        st.download_button("Download", buf.getvalue(), "output.png")
