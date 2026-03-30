import streamlit as st
import numpy as np
from PIL import Image
import io

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Image Tool", layout="wide")

st.title("✨ AI Image Tool (Stable)")
st.caption("Erase • Enhance (Fast & Deploy Safe)")

# =========================
# UPLOAD
# =========================
uploaded_file = st.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Original")

    tool = st.sidebar.radio("Choose Tool", ["🎯 Erase", "✨ Enhance"])

    # =========================
    # 🎯 ERASE (LAZY LOAD)
    # =========================
    if tool == "🎯 Erase":

        st.sidebar.subheader("Eraser")

        brush = st.sidebar.slider("Brush Size", 5, 50, 20)

        if "mask" not in st.session_state:
            st.session_state.mask = np.zeros((image.height, image.width), dtype=np.uint8)

        x = st.sidebar.number_input("X", 0, image.width - 1, image.width // 2)
        y = st.sidebar.number_input("Y", 0, image.height - 1, image.height // 2)

        if st.sidebar.button("➕ Add Point"):
            import cv2  # ✅ lazy import
            cv2.circle(st.session_state.mask, (x, y), brush, 255, -1)

        if st.sidebar.button("🧹 Reset Mask"):
            st.session_state.mask = np.zeros((image.height, image.width), dtype=np.uint8)

        st.image(st.session_state.mask, caption="Mask Preview")

        if st.button("🚀 Apply AI Erase"):
            import cv2  # ✅ lazy import

            result = cv2.inpaint(
                img_np,
                st.session_state.mask,
                3,
                cv2.INPAINT_TELEA
            )

            with col2:
                st.image(result, caption="Result")

            buf = io.BytesIO()
            Image.fromarray(result).save(buf, format="PNG")

            st.download_button("📥 Download", buf.getvalue(), "erase.png")

    # =========================
    # ✨ ENHANCE
    # =========================
    elif tool == "✨ Enhance":

        strength = st.sidebar.slider("Sharpness", 1, 5, 2)

        if st.button("🚀 Enhance Image"):
            from PIL import ImageFilter  # ✅ lazy import

            result = image

            for _ in range(strength):
                result = result.filter(ImageFilter.SHARPEN)

            with col2:
                st.image(result)

            buf = io.BytesIO()
            result.save(buf, format="PNG")

            st.download_button("📥 Download", buf.getvalue(), "enhanced.png")

else:
    st.info("👈 Upload an image to start")
