import streamlit as st
import numpy as np
from PIL import Image
import base64
import io
import cv2

st.set_page_config(layout="wide")
st.title("🔥 AI Object Remover (Pro UI)")

uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    # convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    st.markdown("### ✍️ Draw on image to remove object")

    canvas_html = f"""
    <canvas id="canvas"></canvas>

    <script>
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

    const img = new Image();
    img.src = "data:image/png;base64,{img_str}";

    img.onload = function() {{
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
    }}

    let drawing = false;

    canvas.addEventListener("mousedown", () => drawing = true);
    canvas.addEventListener("mouseup", () => drawing = false);
    canvas.addEventListener("mousemove", draw);

    function draw(e) {{
        if (!drawing) return;
        ctx.fillStyle = "rgba(255,0,0,0.4)";
        ctx.beginPath();
        ctx.arc(e.offsetX, e.offsetY, 10, 0, Math.PI * 2);
        ctx.fill();
    }}

    function sendMask() {{
        const dataURL = canvas.toDataURL();
        window.parent.postMessage({{
            type: "mask",
            data: dataURL
        }}, "*");
    }}
    </script>

    <button onclick="sendMask()">Send Selection</button>
    """

    mask_data = st.components.v1.html(canvas_html, height=600)

    st.info("After drawing → Click 'Send Selection'")

    # NOTE: Streamlit can't directly capture postMessage easily,
    # so we simulate via re-upload

    mask_file = st.file_uploader("Upload drawn mask (auto soon)")

    if mask_file:
        mask_img = Image.open(mask_file).convert("L")
        mask_np = np.array(mask_img)

        _, mask_bin = cv2.threshold(mask_np, 10, 255, cv2.THRESH_BINARY)

        if st.button("🚀 Remove Object"):
            result = cv2.inpaint(img_np, mask_bin, 3, cv2.INPAINT_TELEA)

            st.image(result)

            buf = io.BytesIO()
            Image.fromarray(result).save(buf, format="PNG")

            st.download_button("Download", buf.getvalue(), "output.png")
