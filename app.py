import streamlit as st
import numpy as np
from PIL import Image
import io
import cv2
from streamlit_drawable_canvas import st_canvas

st.set_page_config(layout="wide")
st.title("🔥 AI Object Remover (Draw on Image)")

uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✍️ Draw on Image")

        canvas = st_canvas(
            fill_color="rgba(255, 0, 0, 0.4)",
            stroke_width=20,
            stroke_color="rgba(255,0,0,1)",
            background_image=image,   # ✅ DIRECT DRAW ON IMAGE
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="freedraw",
            key="canvas",
        )

    # =========================
    # APPLY BUTTON
    # =========================
    if st.button("🚀 Apply Remove"):
        if canvas.image_data is not None:

            mask = canvas.image_data[:, :, 3]
            mask = (mask > 0).astype(np.uint8) * 255

            result = cv2.inpaint(img_np, mask, 3, cv2.INPAINT_TELEA)

            with col2:
                st.subheader("✅ Result")
                st.image(result)

            buf = io.BytesIO()
            Image.fromarray(result).save(buf, format="PNG")

            st.download_button("📥 Download", buf.getvalue(), "output.png")

else:
    st.info("Upload image to start")
