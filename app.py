import streamlit as st
import numpy as np
from PIL import Image
import io
import cv2
from streamlit_drawable_canvas import st_canvas

st.set_page_config(layout="wide")
st.title("🔥 AI Object Remover (Draw & Delete)")

uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Original")

    st.markdown("### ✍️ Draw on the image to remove object")

    # Resize for safe canvas rendering
    display_image = image.copy()
    display_image.thumbnail((700, 700))

    # Canvas (DRAW DIRECTLY ON IMAGE ✅)
    canvas = st_canvas(
        fill_color="rgba(255, 0, 0, 0.4)",
        stroke_width=20,
        stroke_color="rgba(255,0,0,1)",
        background_image=display_image,   # ✅ WORKING HERE
        update_streamlit=True,
        height=display_image.height,
        width=display_image.width,
        drawing_mode="freedraw",          # 🖌️ freehand drawing
        key="canvas",
    )

    # =========================
    # CAPTURE MASK (FIXED)
    # =========================
    if st.button("📸 Capture Selection"):
        if canvas.image_data is not None:

            # extract mask from alpha channel
            mask = canvas.image_data[:, :, 3]

            # convert to binary mask
            mask = (mask > 0).astype(np.uint8) * 255

            # resize mask to original image size
            mask = cv2.resize(mask, (image.width, image.height))

            st.success("Selection captured!")

            # preview mask
            st.image(mask, caption="Mask")

            # =========================
            # APPLY ERASE
            # =========================
            if st.button("🚀 Remove Object"):
                result = cv2.inpaint(
                    img_np,
                    mask,
                    3,
                    cv2.INPAINT_TELEA
                )

                with col2:
                    st.image(result, caption="Result")

                buf = io.BytesIO()
                Image.fromarray(result).save(buf, format="PNG")

                st.download_button("📥 Download", buf.getvalue(), "output.png")

else:
    st.info("Upload image to start")
