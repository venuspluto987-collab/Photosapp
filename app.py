import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="AI Image Tool", layout="wide")

st.title("✨ AI Image Tool (Drag Object Delete)")

uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Original")

    tool = st.sidebar.radio("Tool", ["Draw & Delete", "Enhance"])

    # =========================
    # 🎯 DRAW + DELETE
    # =========================
    if tool == "Draw & Delete":

        from streamlit_drawable_canvas import st_canvas
        import cv2

        st.write("✍️ Drag on the image to select object")

        # resize for canvas safety
        display_image = image.copy()
        display_image.thumbnail((600, 600))

        canvas = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=5,
            background_color="white",   # ⚠️ NOT using background_image
            height=display_image.height,
            width=display_image.width,
            drawing_mode="rect",  # drag rectangle
            key="canvas",
        )

        # show image separately
        st.image(display_image, caption="Draw box above this image")

        if canvas.json_data is not None:
            objects = canvas.json_data["objects"]

            if len(objects) > 0:
                obj = objects[-1]

                left = int(obj["left"])
                top = int(obj["top"])
                width = int(obj["width"])
                height = int(obj["height"])

                # scale to original image
                scale_x = image.width / display_image.width
                scale_y = image.height / display_image.height

                x1 = int(left * scale_x)
                y1 = int(top * scale_y)
                x2 = int((left + width) * scale_x)
                y2 = int((top + height) * scale_y)

                # create mask
                mask = np.zeros((image.height, image.width), dtype=np.uint8)
                mask[y1:y2, x1:x2] = 255

                # preview overlay
                overlay = img_np.copy()
                overlay[mask > 0] = (overlay[mask > 0]*0.5 + np.array([255,0,0])*0.5).astype(np.uint8)

                st.image(overlay, caption="Selected Area")

                if st.button("🚀 Delete Object"):
                    result = cv2.inpaint(img_np, mask, 3, cv2.INPAINT_TELEA)

                    with col2:
                        st.image(result, caption="Result")

                    buf = io.BytesIO()
                    Image.fromarray(result).save(buf, format="PNG")

                    st.download_button("Download", buf.getvalue(), "output.png")

    # =========================
    # ✨ ENHANCE
    # =========================
    elif tool == "Enhance":
        from PIL import ImageFilter

        if st.button("Enhance"):
            result = image.filter(ImageFilter.SHARPEN)

            with col2:
                st.image(result)
