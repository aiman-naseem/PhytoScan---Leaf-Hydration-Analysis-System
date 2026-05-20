import streamlit as st
import cv2
import numpy as np

# --- STAGE 1: INITIALIZATION (MUST BE FIRST) ---
# This command tells the browser how to draw the window. 
# If any text or style is sent before this, the window is already "drawn" and can't be changed.
st.set_page_config(
    page_title="PhytoScan Diagnostics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STAGE 2: CUSTOM STYLING (CSS) ---
st.markdown("""
    <style>
    /* Professional Sage-Green Gradient Background */
    .stApp {
        background: linear-gradient(180deg, #FFFFFF 0%, #F1F8F1 100%);
    }
    
    /* Typography Styling */
    html, body, [class*="st-"] {
        color: #2E4031;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* Professional Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-left: 5px solid #4A6741;
        border-right: 1px solid #E0E0E0;
        border-top: 1px solid #E0E0E0;
        border-bottom: 1px solid #E0E0E0;
        padding: 20px;
        border-radius: 4px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }

    /* Header Styling */
    h1, h2, h3 {
        color: #1E2F23;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* File Uploader Border */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF;
        border: 2px dashed #A8C69F;
    }
    </style>
    """, unsafe_allow_html=True)

# --- STAGE 3: CORE IMAGE PROCESSING LOGIC ---
def analyze_health(uploaded_file):
    """
    Core CV Pipeline:
    1. Decode Image -> 2. HSV Transform -> 3. Spectral Masking -> 4. Saturation Average
    """
    # Convert uploaded file to OpenCV BGR format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    # 1. BGR to HSV Transformation
    # Decouples Intensity (Value) from Color (Hue/Saturation)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 2. Binary Segmentation
    # Isolating the Green Specturm (Chlorophyll signals)
    lower_green = np.array([35, 30, 30]) 
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Extract only the green pixels from the saturation channel
    green_pixels = hsv[mask > 0]
    
    if len(green_pixels) == 0:
        return None, "Signal Error: No organic pigments detected in frame.", 0, 0
    
    # 3. Feature Extraction (Mean Saturation)
    # Higher saturation = higher water content/turgidity
    avg_sat = np.mean(green_pixels[:, 1])
    health_score = (avg_sat / 255) * 100
    
    # Prepare Mask Visualization (BGR -> RGB for Streamlit)
    res = cv2.bitwise_and(img, img, mask=mask)
    res_rgb = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
    
    return res_rgb, health_score, avg_sat, len(green_pixels)

# --- STAGE 4: USER INTERFACE ---
st.title("PhytoScan: Leaf Hydration Analysis")
st.markdown("##### Professional Diagnostic Interface for Non-Invasive Plant Health Assessment")
st.markdown("---")

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("Input Specimen")
    file = st.file_uploader("Upload leaf sample (JPG/PNG)", type=["jpg", "jpeg", "png"])
    if file:
        st.image(file, caption="Input Specimen Data", use_container_width=True)

with col2:
    st.subheader("Diagnostic Metrics")
    if file:
        # Reset file pointer to ensure analyze_health starts at the beginning of the file
        file.seek(0)
        processed_img, score, raw_val, px_count = analyze_health(file)
        
        if processed_img is not None:
            # Metric Grid
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Hydration Index", f"{score:.2f}%")
            m_col2.metric("Valid Pixel Density", f"{px_count:,}")

            st.markdown("---")
            
            # Clinical Classification Logic
            if score > 45:
                st.info("🟢 **Clinical Status:** Specimen is healthy and well-hydrated.")
            elif score > 30:
                st.warning("🟡 **Clinical Status:** Moderate water stress detected.")
            else:
                st.error("🔴 **Clinical Status:** Critical dehydration deficit observed.")
            
            # Technical Expandable Section
            with st.expander("Technical Segmentation Report"):
                st.image(processed_img, caption="Segmented Chromatic Mask")
                st.caption("Algorithm isolates chlorophyll-active regions and filters out background noise.")
        else:
            # score here contains the error message string
            st.error(score)
    else:
        st.info("System Ready. Please upload a specimen for spectral analysis.")