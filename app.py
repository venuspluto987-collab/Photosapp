import streamlit as st
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="AI Image Tool", layout="wide")

st.title("✨ AI Image Tool (Pro)")
st.caption("Erase • Draw Delete • Enhance")

uploaded_file = st.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="📸 Original")

    tool = st.sidebar.radio("Choose Tool", ["🎯 Brush Erase", "📦 Object Delete", "✨ Enhance"])

    # =========================
    # 🎯 BRUSH ERASE
    # =========================
    if tool == "🎯 Brush Erase":
        import cv2

        brush = st.sidebar.slider("Brush Size", 5, 50, 20)

        if "mask" not in st.session_state:
            st.session_state.mask = np.zeros((image.height, image.width), dtype=np.uint8)

        x = st.sidebar.number_input("X", 0, image.width - 1, image.width // 2)
        y = st.sidebar.number_input("Y", 0, image.height - 1, image.height // 2)

        if st.sidebar.button("➕ Add Point"):
            cv2.circle(st.session_state.mask, (x, y), brush, 255, -1)

        if st.sidebar.button("🧹 Reset Mask"):
            st.session_state.mask = np.zeros((image.height, image.width), dtype=np.uint8)

        # overlay preview
        overlay = img_np.copy()
        mask = st.session_state.mask > 0
        overlay[mask] = (overlay[mask]*0.5 + np.array([255,0,0])*0.5).astype(np.uint8)

        st.image(overlay, caption="🔴 Brush Area")

        if st.button("🚀 Apply Erase"):
            result = cv2.inpaint(img_np, st.session_state.mask, 3, cv2.INPAINT_TELEA)

            with col2:
                st.image(result, caption="✅ Result")

    # =========================
    # 📦 OBJECT DELETE (NEW)
    # =========================
    elif tool == "📦 Object Delete":
        import cv2

        st.sidebar.subheader("Draw Object Box")

        x1 = st.sidebar.number_input("Start X", 0, image.width-1, 50)
        y1 = st.sidebar.number_input("Start Y", 0, image.height-1, 50)
        x2 = st.sidebar.number_input("End X", 0, image.width-1, 200)
        y2 = st.sidebar.number_input("End Y", 0, image.height-1, 200)

        # create mask
        mask = np.zeros((image.height, image.width), dtype=np.uint8)
        mask[y1:y2, x1:x2] = 255

        # overlay preview
        overlay = img_np.copy()
        overlay[mask > 0] = (overlay[mask > 0]*0.5 + np.array([255,0,0])*0.5).astype(np.uint8)

        st.image(overlay, caption="🔴 Selected Object Area")

        if st.button("🚀 Delete Object"):
            result = cv2.inpaint(img_np, mask, 3, cv2.INPAINT_TELEA)

            with col2:
                st.image(result, caption="✅ Object Removed")

            buf = io.BytesIO()
            Image.fromarray(result).save(buf, format="PNG")

            st.download_button("📥 Download", buf.getvalue(), "object_removed.png")

    # =========================
    # ✨ ENHANCE
    # =========================
    elif tool == "✨ Enhance":
        strength = st.sidebar.slider("Sharpness", 1, 5, 2)

        if st.button("🚀 Enhance"):
            from PIL import ImageFilter

            result = image
            for _ in range(strength):
                result = result.filter(ImageFilter.SHARPEN)

            with col2:
                st.image(result, caption="✨ Enhanced")

else:
    st.info("👈 Upload an image to start")

       
