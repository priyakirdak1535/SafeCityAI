
import streamlit as st
import torch
from PIL import Image, ImageDraw
import numpy as np
import pandas as pd
import cv2
import tempfile
import os
import io
from datetime import datetime

st.set_page_config(page_title="SafeCityAI", page_icon="S", layout="wide")

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #f8f9fb; }
  [data-testid="stSidebar"] { background: #ffffff; border-right: 0.5px solid #e2e4e8; }
  .block-container { padding: 1.5rem 2rem 3rem; }

  .app-header {
    background: white; border: 0.5px solid #e2e4e8; border-radius: 12px;
    padding: 16px 20px; margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 14px;
  }
  .logo {
    width: 40px; height: 40px; background: #185FA5; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 20px; font-weight: 700; flex-shrink: 0;
  }
  .stat-card {
    background: white; border: 0.5px solid #e2e4e8; border-radius: 10px;
    padding: 16px; text-align: center;
  }
  .stat-number { font-size: 30px; font-weight: 600; margin: 0; line-height: 1.1; }
  .stat-label  { font-size: 12px; color: #888; margin: 4px 0 0; }
  .section-label {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.06em; color: #888; margin-bottom: 8px;
  }
  .card {
    background: white; border: 0.5px solid #e2e4e8;
    border-radius: 12px; padding: 18px;
  }
  .violation-banner {
    background: #FCEBEB; border: 0.5px solid #F09595;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 1rem;
  }
  .safe-banner {
    background: #EAF3DE; border: 0.5px solid #97C459;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 1rem;
  }
  .det-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .det-table th {
    background: #f8f9fb; color: #555; font-weight: 500;
    padding: 9px 12px; text-align: left; border-bottom: 0.5px solid #e2e4e8;
    position: sticky; top: 0;
  }
  .det-table td { padding: 9px 12px; border-bottom: 0.5px solid #f0f1f3; color: #333; }
  .det-table tr:last-child td { border-bottom: none; }
  .det-table tr:hover td { background: #fafbfc; }
  .pill-green {
    background: #EAF3DE; color: #27500A; padding: 3px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 500;
  }
  .pill-red {
    background: #FCEBEB; color: #791F1F; padding: 3px 10px;
    border-radius: 20px; font-size: 11px; font-weight: 500;
  }
  .tab-btn {
    padding: 8px 20px; border-radius: 8px; font-size: 13px;
    cursor: pointer; border: 0.5px solid #e2e4e8;
    background: white; color: #555; font-weight: 500;
  }
  .tab-active { background: #185FA5 !important; color: white !important; border-color: #185FA5 !important; }
  .stTabs [data-baseweb="tab-list"] {
    background: white; border-radius: 10px; padding: 4px;
    border: 0.5px solid #e2e4e8; gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px; font-size: 13px; padding: 6px 18px;
    color: #555;
  }
  .stTabs [aria-selected="true"] { background: #185FA5; color: white; }
  div[data-testid="stFileUploader"] {
    background: white; border: 1.5px dashed #d0d3d9;
    border-radius: 12px; padding: 8px;
  }
  .stButton > button {
    background: #185FA5; color: white; border: none;
    border-radius: 8px; padding: 8px 20px; font-size: 13px;
  }
  .stButton > button:hover { background: #0C447C; }
  .stSlider [data-testid="stThumbValue"] { font-size: 12px; }
  .video-progress {
    background: white; border: 0.5px solid #e2e4e8;
    border-radius: 10px; padding: 14px 18px; margin-bottom: 1rem;
  }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    m = torch.hub.load("/content/yolov5", "custom",
                       path="/content/best.pt", source="local",
                       force_reload=False, verbose=False)
    return m

with st.spinner("Loading model..."):
    model = load_model()


def draw_boxes_pil(image, detections):
    img = image.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    for _, row in detections.iterrows():
        label = row["name"]
        conf  = float(row["confidence"])
        x1, y1, x2, y2 = int(row["xmin"]), int(row["ymin"]), int(row["xmax"]), int(row["ymax"])
        color = "#22c55e" if label == "with_helmet" else "#ef4444"
        for t in range(3):
            draw.rectangle([x1-t, y1-t, x2+t, y2+t], outline=color)
        text = f"{label}  {conf:.2f}"
        tw = len(text) * 7 + 8
        draw.rectangle([x1, y1-22, x1+tw, y1], fill=color)
        draw.text((x1+4, y1-19), text, fill="white")
    return img


def draw_boxes_cv2(frame, detections):
    for _, row in detections.iterrows():
        label = row["name"]
        conf  = float(row["confidence"])
        x1, y1, x2, y2 = int(row["xmin"]), int(row["ymin"]), int(row["xmax"]), int(row["ymax"])
        color = (34, 197, 94) if label == "with_helmet" else (239, 68, 68)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        text = f"{label} {conf:.2f}"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(frame, (x1, y1-th-10), (x1+tw+8, y1), color, -1)
        cv2.putText(frame, text, (x1+4, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 1)
    return frame


def build_table_html(df):
    if df.empty:
        return "<p style='color:#aaa;text-align:center;padding:20px'>No detections</p>"
    rows = ""
    for i, row in df.iterrows():
        label = row["name"]
        conf  = float(row["confidence"])
        pill  = f'<span class="pill-green">{label}</span>' if label == "with_helmet" \
                else f'<span class="pill-red">{label}</span>'
        bc    = "#22c55e" if label == "with_helmet" else "#ef4444"
        conf_html = f"""
          <div style="font-weight:500">{conf:.2f}</div>
          <div style="height:4px;background:#e2e4e8;border-radius:3px;margin-top:3px;width:80px">
            <div style="width:{int(conf*100)}%;height:4px;background:{bc};border-radius:3px"></div>
          </div>"""
        rows += f"""<tr>
          <td style="color:#bbb;width:32px">{i+1}</td>
          <td>{pill}</td>
          <td>{conf_html}</td>
          <td style="font-family:monospace">{int(row['xmin'])}</td>
          <td style="font-family:monospace">{int(row['ymin'])}</td>
          <td style="font-family:monospace">{int(row['xmax'])}</td>
          <td style="font-family:monospace">{int(row['ymax'])}</td>
        </tr>"""
    return f"""
    <div style="overflow-x:auto;max-height:320px;overflow-y:auto">
    <table class="det-table">
      <thead><tr>
        <th>#</th><th>Class</th><th>Confidence</th>
        <th>xmin</th><th>ymin</th><th>xmax</th><th>ymax</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table></div>"""


def show_stats(detections):
    total     = len(detections)
    helmets   = len(detections[detections["name"] == "with_helmet"])
    no_helmet = len(detections[detections["name"] == "without_helmet"])
    avg_conf  = round(float(detections["confidence"].mean()), 2) if total > 0 else 0.0
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-card"><p class="stat-number">{total}</p><p class="stat-label">Total detected</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card"><p class="stat-number" style="color:#3B6D11">{helmets}</p><p class="stat-label">With helmet</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card"><p class="stat-number" style="color:#A32D2D">{no_helmet}</p><p class="stat-label">Without helmet</p></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><p class="stat-number">{avg_conf}</p><p class="stat-label">Avg confidence</p></div>', unsafe_allow_html=True)
    return no_helmet


def show_banner(no_helmet):
    ts = datetime.now().strftime("%H:%M:%S")
    if no_helmet > 0:
        st.markdown(f"""
        <div class="violation-banner">
          <div style="font-size:14px;font-weight:600;color:#A32D2D">
            Violation detected — {no_helmet} person(s) without helmet
          </div>
          <div style="font-size:12px;color:#c0392b;margin-top:3px">
            Timestamp: {ts}
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="safe-banner">
          <div style="font-size:14px;font-weight:600;color:#27500A">
            No violations — all riders wearing helmets
          </div>
        </div>""", unsafe_allow_html=True)


# ── HEADER ───────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="logo">S</div>
  <div>
    <div style="font-size:17px;font-weight:600;color:#1a1a1a">
      SafeCityAI — Helmet violation detection
    </div>
    <div style="font-size:12px;color:#888">
      YOLOv5s · mAP@0.5: 0.754 · Classes: with_helmet / without_helmet
    </div>
  </div>
  <div style="margin-left:auto">
    <span style="background:#EAF3DE;color:#27500A;font-size:11px;
                 padding:4px 12px;border-radius:20px;font-weight:500">
      Model ready
    </span>
  </div>
</div>""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Settings")
    conf_thresh = st.slider("Confidence threshold", 0.1, 1.0, 0.5, 0.05)
    model.conf  = conf_thresh
    st.markdown("---")
    skip_frames = st.slider("Video: process every N frames", 1, 10, 3, 1)
    st.caption("Higher = faster processing, lower accuracy")
    st.markdown("---")
    st.markdown("**Model info**")
    st.markdown("Trained on 3,341 images  \nmAP@0.5: **0.754**  \nPrecision: **0.709**  \nRecall: **0.746**")

# ── TABS ──────────────────────────────────────────────────────────────
tab_img, tab_vid, tab_cam = st.tabs(["  Image detection  ",
                                      "  Video detection  ",
                                      "  Webcam (live)  "])


# ════════════════════════════════════════════════════════════════
# TAB 1 — IMAGE
# ════════════════════════════════════════════════════════════════
with tab_img:
    st.markdown('<div class="section-label">Upload image</div>', unsafe_allow_html=True)
    uploaded_img = st.file_uploader("", type=["jpg","jpeg","png"],
                                     key="img_upload", label_visibility="collapsed")
    if uploaded_img:
        img = Image.open(uploaded_img).convert("RGB")

        with st.spinner("Running detection..."):
            results    = model(img)
            detections = results.pandas().xyxy[0]
            result_img = draw_boxes_pil(img, detections)

        no_helmet = show_stats(detections)
        st.markdown("<br>", unsafe_allow_html=True)
        show_banner(no_helmet)

        left, right = st.columns(2)
        with left:
            st.markdown('<div class="section-label">Original</div>', unsafe_allow_html=True)
            st.image(img, use_column_width=True)
        with right:
            st.markdown('<div class="section-label">Detections</div>', unsafe_allow_html=True)
            st.image(result_img, use_column_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Analysis table</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card">{build_table_html(detections)}</div>',
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        buf = io.BytesIO()
        result_img.save(buf, format="PNG")
        st.download_button("Download result image", buf.getvalue(),
                           f"detection_{datetime.now().strftime('%H%M%S')}.png",
                           "image/png")
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:48px;color:#aaa">
          <div style="font-size:36px;margin-bottom:12px;color:#e2e4e8">S</div>
          <div style="font-size:14px;color:#aaa">Upload an image to begin detection</div>
          <div style="font-size:12px;color:#bbb;margin-top:6px">Supports JPG, JPEG, PNG</div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TAB 2 — VIDEO
# ════════════════════════════════════════════════════════════════
with tab_vid:
    st.markdown('<div class="section-label">Upload video</div>', unsafe_allow_html=True)
    uploaded_vid = st.file_uploader("", type=["mp4","avi","mov","mkv"],
                                     key="vid_upload", label_visibility="collapsed")
    if uploaded_vid:
        # Save to temp file
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        tfile.write(uploaded_vid.read())
        tfile.flush()

        cap = cv2.VideoCapture(tfile.name)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps          = cap.get(cv2.CAP_PROP_FPS)
        w            = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h            = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration     = round(total_frames / fps, 1) if fps > 0 else 0

        st.markdown(f"""
        <div class="video-progress">
          <div style="display:flex;gap:24px;font-size:13px;color:#555">
            <span>Duration: <b>{duration}s</b></span>
            <span>Frames: <b>{total_frames}</b></span>
            <span>FPS: <b>{round(fps,1)}</b></span>
            <span>Resolution: <b>{w}x{h}</b></span>
          </div>
        </div>""", unsafe_allow_html=True)

        process_btn = st.button("Process video")

        if process_btn:
            out_path = tempfile.mktemp(suffix="_out.mp4")
            fourcc   = cv2.VideoWriter_fourcc(*"mp4v")
            out      = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

            progress_bar  = st.progress(0)
            status_text   = st.empty()
            preview_slot  = st.empty()

            all_detections = []
            frame_idx = 0
            processed = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % skip_frames == 0:
                    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil   = Image.fromarray(rgb)
                    res   = model(pil)
                    dets  = res.pandas().xyxy[0]

                    if not dets.empty:
                        dets["frame"] = frame_idx
                        all_detections.append(dets)

                    frame = draw_boxes_cv2(frame, dets)
                    processed += 1

                    # Show preview every 30 processed frames
                    if processed % 30 == 0:
                        preview_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        preview_slot.image(preview_rgb, caption=f"Frame {frame_idx}",
                                           use_column_width=True)

                out.write(frame)
                frame_idx += 1
                pct = int(frame_idx / total_frames * 100)
                progress_bar.progress(min(pct, 100))
                status_text.markdown(
                    f'<p style="font-size:12px;color:#888">Processing frame {frame_idx} / {total_frames}</p>',
                    unsafe_allow_html=True
                )

            cap.release()
            out.release()

            progress_bar.progress(100)
            status_text.markdown('<p style="font-size:12px;color:#3B6D11">Processing complete</p>',
                                  unsafe_allow_html=True)

            # Combine all detections
            if all_detections:
                combined = pd.concat(all_detections, ignore_index=True)
                total_v     = len(combined)
                helmet_v    = len(combined[combined["name"] == "with_helmet"])
                no_helmet_v = len(combined[combined["name"] == "without_helmet"])
                avg_conf_v  = round(float(combined["confidence"].mean()), 2)

                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                c1.markdown(f'<div class="stat-card"><p class="stat-number">{total_v}</p><p class="stat-label">Total detections</p></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="stat-card"><p class="stat-number" style="color:#3B6D11">{helmet_v}</p><p class="stat-label">With helmet</p></div>', unsafe_allow_html=True)
                c3.markdown(f'<div class="stat-card"><p class="stat-number" style="color:#A32D2D">{no_helmet_v}</p><p class="stat-label">Without helmet</p></div>', unsafe_allow_html=True)
                c4.markdown(f'<div class="stat-card"><p class="stat-number">{avg_conf_v}</p><p class="stat-label">Avg confidence</p></div>', unsafe_allow_html=True)

                if no_helmet_v > 0:
                    st.markdown(f"""
                    <br><div class="violation-banner">
                      <div style="font-size:14px;font-weight:600;color:#A32D2D">
                        {no_helmet_v} violation frame(s) detected in video
                      </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-label">Analysis table (all frames)</div>',
                            unsafe_allow_html=True)

                show_cols = ["frame","name","confidence","xmin","ymin","xmax","ymax"]
                combined_show = combined[show_cols].copy()
                combined_show.columns = ["Frame","Class","Confidence","xmin","ymin","xmax","ymax"]
                combined_show["Confidence"] = combined_show["Confidence"].round(2)
                st.markdown(
                    f'<div class="card">{build_table_html(combined[["name","confidence","xmin","ymin","xmax","ymax"]].head(100))}</div>',
                    unsafe_allow_html=True
                )

            # Download processed video
            st.markdown("<br>", unsafe_allow_html=True)
            with open(out_path, "rb") as vf:
                st.download_button(
                    "Download processed video",
                    vf.read(),
                    f"processed_{datetime.now().strftime('%H%M%S')}.mp4",
                    "video/mp4"
                )

            os.unlink(tfile.name)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:48px;color:#aaa">
          <div style="font-size:14px;color:#aaa">Upload a video to begin detection</div>
          <div style="font-size:12px;color:#bbb;margin-top:6px">Supports MP4, AVI, MOV, MKV</div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TAB 3 — WEBCAM
# ════════════════════════════════════════════════════════════════
with tab_cam:
    st.markdown("""
    <div class="card" style="margin-bottom:1rem">
      <div style="font-size:14px;font-weight:500;color:#1a1a1a;margin-bottom:6px">
        Live webcam detection
      </div>
      <div style="font-size:13px;color:#888">
        Colab does not support direct webcam access. Use one of these options:
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Option 1 — upload a webcam snapshot</div>',
                unsafe_allow_html=True)
    cam_img = st.camera_input("")

    if cam_img:
        img = Image.open(cam_img).convert("RGB")
        with st.spinner("Detecting..."):
            results    = model(img)
            detections = results.pandas().xyxy[0]
            result_img = draw_boxes_pil(img, detections)

        no_helmet = show_stats(detections)
        st.markdown("<br>", unsafe_allow_html=True)
        show_banner(no_helmet)

        left, right = st.columns(2)
        with left:
            st.markdown('<div class="section-label">Captured frame</div>',
                        unsafe_allow_html=True)
            st.image(img, use_column_width=True)
        with right:
            st.markdown('<div class="section-label">Detections</div>',
                        unsafe_allow_html=True)
            st.image(result_img, use_column_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Analysis table</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<div class="card">{build_table_html(detections)}</div>',
            unsafe_allow_html=True
        )
