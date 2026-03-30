import streamlit as st
import numpy as np
from PIL import Image
import base64
import io
import cv2

st.set_page_config(layout="wide")
st.title("🔥 AI Object Remover (Working Draw + Apply)")

uploaded_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)

    # convert image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    st.markdown("### ✍️ Draw on image → Click Apply")

    # =========================
    # HTML WITH RETURN VALUE
    # =========================
    canvas_html = f"""
    <canvas id="canvas"></canvas>
    <br><br>
    <button onclick="sendData()">Apply</button>

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
        ctx.fillStyle = "rgba(255,0,0,0.5)";
        ctx.beginPath();
        ctx.arc(e.offsetX, e.offsetY, 15, 0, Math.PI * 2);
        ctx.fill();
    }}

    function sendData() {{
        const dataURL = canvas.toDataURL("image/png");
        window.parent.postMessage({{
            isStreamlitMessage: true,
            type: "streamlit:setComponentValue",
            value: dataURL
        }}, "*");
    }}
    </script>
    """

    # ✅ THIS RETURNS VALUE
    mask_data = st.components.v1.html(canvas_html, height=600)

    # =========================
    # PROCESS MASK
    # =========================
    if mask_data:
        st.success("✅ Selection received!")

        # decode base64
        mask_base64 = mask_data.split(",")[1]
        mask_bytes = base64.b64decode(mask_base64)
        mask_img = Image.open(io.BytesIO(mask_bytes)).convert("L")

        mask_np = np.array(mask_img)

        _, mask_bin = cv2.threshold(mask_np, 10, 255, cv2.THRESH_BINARY)

        # =========================
        # APPLY REMOVE
        # =========================
        result = cv2.inpaint(img_np, mask_bin, 3, cv2.INPAINT_TELEA)

        st.image(result, caption="✅ Result")

        buf = io.BytesIO()
        Image.fromarray(result).save(buf, format="PNG")

        st.download_button("📥 Download", buf.getvalue(), "output.png")
