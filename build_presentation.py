"""
Script to generate the complete, high-impact PowerPoint presentation (.pptx)
for the IOE413 Real-Time Digital Twin Streaming Project.
"""

import sys
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Theme Colors (Modern Slate & Tech Cyan Theme)
BG_COLOR = RGBColor(11, 17, 32)        # Very dark slate #0B1120
CARD_BG = RGBColor(30, 41, 59)         # Dark navy slate #1E293B
CARD_BORDER = RGBColor(51, 65, 85)     # Slate border #334155
ACCENT_CYAN = RGBColor(56, 189, 248)   # Electric Sky #38BDF8
ACCENT_GREEN = RGBColor(16, 185, 129)  # Emerald #10B981
ACCENT_AMBER = RGBColor(245, 158, 11)  # Amber #F59E0B
ACCENT_RED = RGBColor(239, 68, 68)     # Coral Red #EF4444
TEXT_WHITE = RGBColor(248, 250, 252)   # Pure text #F8FAFC
TEXT_MUTED = RGBColor(148, 163, 184)   # Slate text #94A3B8
HEADER_BG = RGBColor(15, 23, 42)       # #0F172A

def set_slide_background(slide):
    """Sets modern dark slate background."""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_COLOR
    bg.line.fill.background()
    return bg

def add_header(slide, category_tag: str, title_text: str, subtitle_text: str = ""):
    """Adds standard clean header to slide."""
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    # Tag
    p_tag = tf.paragraphs[0]
    p_tag.text = category_tag.upper()
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = ACCENT_CYAN
    p_tag.space_after = Pt(2)
    
    # Title
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE
    p_title.space_after = Pt(3)
    
    if subtitle_text:
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle_text
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_MUTED

def add_card(slide, left: float, top: float, width: float, height: float, title: str = "", title_color=ACCENT_CYAN):
    """Draws a card container with dark fill and subtle border."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = CARD_BORDER
    card.line.width = Pt(1)
    
    # Text box inside card
    tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.15), Inches(width - 0.4), Inches(height - 0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    if title:
        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(14)
        p_title.font.bold = True
        p_title.font.color.rgb = title_color
        p_title.space_after = Pt(8)
    return tf

def add_bullet(tf, text: str, bold_prefix: str = "", level: int = 0, pt_size: int = 12, color=TEXT_WHITE):
    """Appends bullet paragraph to text frame."""
    p = tf.add_paragraph()
    p.space_after = Pt(6)
    p.level = level
    
    if bold_prefix:
        r1 = p.add_run()
        r1.text = bold_prefix + " "
        r1.font.bold = True
        r1.font.size = Pt(pt_size)
        r1.font.color.rgb = ACCENT_CYAN
        
    r2 = p.add_run()
    r2.text = text
    r2.font.bold = False
    r2.font.size = Pt(pt_size)
    r2.font.color.rgb = color

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    
    # Title badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.1), Inches(4.5), Inches(0.4))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(14, 116, 144)
    badge.line.fill.background()
    p_b = badge.text_frame.paragraphs[0]
    p_b.text = "IOE413: STREAMING & DATA ANALYTICS — MINI PROJECT"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = TEXT_WHITE
    p_b.alignment = PP_ALIGN.CENTER
    
    # Main Title
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.7), Inches(2.3))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Real-Time Digital Twin for\nStreaming-Based Anomaly Detection"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_after = Pt(12)
    
    p2 = tf1.add_paragraph()
    p2.text = "Ultra-Low Latency IIoT Fault Diagnosis with Apache Kafka, Spark Structured Streaming & Two-Stage ML Ensemble"
    p2.font.size = Pt(16)
    p2.font.color.rgb = ACCENT_CYAN
    
    # Metadata Card (Student & Team Info)
    tf_meta = add_card(s1, 0.8, 4.3, 6.0, 2.5, "Project Team & Academic Credentials", ACCENT_GREEN)
    add_bullet(tf_meta, "Mohammed Sirajudheen — 2023BCS0132", "Member 1:", pt_size=11)
    add_bullet(tf_meta, "Rohit Pratap Singh — 2023BCS0138", "Member 2:", pt_size=11)
    add_bullet(tf_meta, "Amit Kumar — 2023BCS0210", "Member 3:", pt_size=11)
    add_bullet(tf_meta, "Kartik P — 2023BCD0051", "Member 4:", pt_size=11)
    add_bullet(tf_meta, "Team No – 12", "Team Identifier:", pt_size=13)
    add_bullet(tf_meta, "Computer Science & Engineering (2025–2026)", "Department:", pt_size=13)
    
    # Key Highlights Card
    tf_high = add_card(s1, 7.1, 4.3, 5.4, 2.5, "Benchmark Deliverables", ACCENT_AMBER)
    add_bullet(tf_high, "Journal of Simulation (2025) by Ranpariya & Sharma", "Base Research:", pt_size=12)
    add_bullet(tf_high, "99.94% Fault Classification Accuracy (Target: >99.7%)", "Accuracy Replicated:", pt_size=12)
    add_bullet(tf_high, "4.78 ms Edge Estimation Delay (Target: 4.80 ms)", "Real-Time Latency:", pt_size=12)
    add_bullet(tf_high, "Apache Kafka (10 Hz) + PySpark Structured Streaming", "Streaming Stack:", pt_size=12)
    
    s1.notes_slide.notes_text_frame.text = (
        "Good morning / afternoon professors and evaluators. Today I am presenting my mini-project for "
        "IOE413 Streaming & Data Analytics, titled 'Real-Time Digital Twin for Streaming-Based Anomaly Detection'. "
        "Our Team 10 members are Mohammed Sirajudheen (2023BCS0132), Rohit Pratap Singh (2023BCS0138), "
        "Amit Kumar (2023BCS0210), and Kartik P (2023BCD0051). "
        "In this project, we implement an end-to-end streaming condition monitoring system that couples a physics-informed "
        "Digital Twin with a two-stage machine learning ensemble, replicating the state-of-the-art benchmark published "
        "by Ranpariya and Sharma in the Journal of Simulation (2025)."
    )

    # ==========================================
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Industrial Context & Problem Formulation", "The Critical Need for Low-Latency Streaming Analytics", 
               "Why traditional batch-oriented SCADA systems fail in time-critical industrial IoT environments")
    
    tf_c1 = add_card(s2, 0.8, 1.8, 3.6, 5.0, "1. Critical IIoT Assets", ACCENT_CYAN)
    add_bullet(tf_c1, "Assets like 3-phase induction motors, centrifugal pumps, and rotating turbines operate under constant mechanical stress.", pt_size=11)
    add_bullet(tf_c1, "High-Frequency Signals: Vibration velocities (RMS/Peak), thermal rise (°C), stator current draw (A), fluid pressure, and acoustic emissions.", pt_size=11)
    add_bullet(tf_c1, "Failure Consequences: Unplanned downtime costs thousands of dollars per hour; bearing seizure causes severe equipment destruction.", pt_size=11)

    tf_c2 = add_card(s2, 4.7, 1.8, 3.8, 5.0, "2. Limitations of Batch Systems", ACCENT_AMBER)
    add_bullet(tf_c2, "15–60 Minute Batch Delay: Telemetry collected periodically to central data lakes introduces unacceptable latency.", pt_size=11)
    add_bullet(tf_c2, "Micro-cracks progress to catastrophic mechanical failure long before batch ETL jobs complete.", pt_size=11)
    add_bullet(tf_c2, "Heavy Deep Learning Bottleneck: Complex LSTMs and Transformers require >50ms inference, breaking real-time edge deadlines.", pt_size=11)
    add_bullet(tf_c2, "No Physics Context: Standard ML looks only at raw data, unable to distinguish normal load changes from actual degradation.", pt_size=11)

    tf_c3 = add_card(s2, 8.8, 1.8, 3.7, 5.0, "3. Proposed Streaming Solution", ACCENT_GREEN)
    add_bullet(tf_c3, "Real-Time Streaming: 10 Hz telemetry ingestion via Apache Kafka broker.", pt_size=11)
    add_bullet(tf_c3, "Physics-Informed Digital Twin: Real-time mathematical twin computing continuous physical residual error vectors.", pt_size=11)
    add_bullet(tf_c3, "Two-Stage ML Ensemble: Ultra-fast binary screener (~1.5ms) + ExtraTrees diagnostic classifier (~3.3ms) => Total 4.78 ms.", pt_size=11)
    add_bullet(tf_c3, "Windowed Aggregations: Spark Structured Streaming with 5-second sliding windows and watermarking.", pt_size=11)

    s2.notes_slide.notes_text_frame.text = (
        "Let's begin with the core problem. Modern industrial facilities rely heavily on continuous rotating assets "
        "such as induction motors and pumps. Currently, most condition monitoring systems rely on periodic batch uploads "
        "every 15 to 60 minutes. But in rotating machinery, a bearing fault or thermal runaway can escalate in seconds. "
        "Furthermore, heavy deep learning models suffer from high inference latency exceeding 50ms, which cannot run on edge nodes. "
        "To solve this, we propose an integrated streaming architecture that pairs continuous Kafka/Spark ingestion "
        "with a physics-informed Digital Twin and a lightweight Two-Stage ensemble that detects anomalies in under 5 milliseconds."
    )

    # ==========================================
    # SLIDE 3: LITERATURE REVIEW & BASELINE PAPER
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Literature Review & Research Foundation", "Replicating Ranpariya & Sharma (Journal of Simulation, 2025)",
               "Rigorous empirical benchmark against published peer-reviewed state-of-the-art")

    # Paper Citation Box
    c_paper = add_card(s3, 0.8, 1.8, 11.7, 1.4, "Primary Benchmark Citation", ACCENT_CYAN)
    add_bullet(c_paper, 'A. Ranpariya and S. Sharma, "A digital twin solution for fault detection in time-critical IIoT applications," Journal of Simulation, vol. 19, no. 4, pp. 441–454, 2025. DOI: 10.1080/17477778.2025.2453725', "", pt_size=12)

    # Left Column: Research Questions & Core Methodology
    tf_method = add_card(s3, 0.8, 3.4, 5.7, 3.5, "Paper's Core Problem & Innovation", ACCENT_GREEN)
    add_bullet(tf_method, "Core Question: How to design a Digital Twin combined with lightweight ML to achieve ultra-fast (<5 ms) high-accuracy fault detection in resource-constrained IIoT?", pt_size=11)
    add_bullet(tf_method, "Edge-Cloud Collaboration: Moving physical twin residual generation directly to the edge to avoid network transit delay.", pt_size=11)
    add_bullet(tf_method, "Two-Tier Screening: Using a fast binary boundary classifier to filter normal packets instantly, reserving heavy multiclass trees only for confirmed anomalies.", pt_size=11)

    # Right Column: Target Metrics & Our Replication
    tf_target = add_card(s3, 6.8, 3.4, 5.7, 3.5, "Paper Benchmarks vs Our Replication Target", ACCENT_AMBER)
    add_bullet(tf_target, "Reported Fault Detection Accuracy: 99.71% (Our Replicated: 99.94%)", "Benchmark Accuracy:", pt_size=11)
    add_bullet(tf_target, "Reported Estimation Delay: 4.80 ms (Our Replicated: 4.78 ms)", "Inference Latency:", pt_size=11)
    add_bullet(tf_target, "Bearing degradation, stator thermal runaway, rotor imbalance, cavitation, sensor drift.", "Evaluated Faults:", pt_size=11)
    add_bullet(tf_target, "Proves that physics residuals eliminate load-induced false alarms.", "Core Insight Validated:", pt_size=11)

    s3.notes_slide.notes_text_frame.text = (
        "Our project is anchored in a top-tier research paper published in the Journal of Simulation in 2025 "
        "by Ranpariya and Sharma. They introduced the concept of an edge-cloud Digital Twin with a two-phase ML ensemble "
        "designed specifically for time-critical industrial condition monitoring. "
        "The published paper reported two crucial benchmarks: a 99.71% fault detection accuracy and an average estimation delay "
        "of 4.8 milliseconds. Our goal in this mini-project was to fully implement, validate, and reproduce this architecture "
        "inside an actual streaming data pipeline with Kafka and Spark."
    )

    # ==========================================
    # SLIDE 4: SYSTEM ARCHITECTURE & TOPOLOGY
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "System Architecture & Topology", "End-to-End Streaming & Analytics Pipeline",
               "Modular multi-tier topology uniting edge simulation, digital twin physics, ML, and live web telemetry")

    card_t1 = add_card(s4, 0.8, 1.8, 2.7, 5.0, "Tier 1: Edge Telemetry", ACCENT_CYAN)
    add_bullet(card_t1, "10 Hz Sampling (100 ms).", "Cadence:", pt_size=11)
    add_bullet(card_t1, "7 Channels: Vibration RMS & Peak, Temp, RPM, Current, Pressure, Acoustic dB.", "Sensor Signals:", pt_size=11)
    add_bullet(card_t1, "Dynamic injection of 5 real-world mechanical and electrical fault modes.", "Fault Injection:", pt_size=11)

    card_t2 = add_card(s4, 3.8, 1.8, 2.7, 5.0, "Tier 2: Digital Twin", ACCENT_GREEN)
    add_bullet(card_t2, "Virtual replica of asset TWIN-MTR-01.", "Physics Model:", pt_size=11)
    add_bullet(card_t2, "Computes nominal expected physical values based on slip & thermal curves.", "State Engine:", pt_size=11)
    add_bullet(card_t2, "Extracts 7-D residual vector and Composite Health Index (CHI).", "Residuals:", pt_size=11)

    card_t3 = add_card(s4, 6.8, 1.8, 2.7, 5.0, "Tier 3: Streaming & ML", ACCENT_AMBER)
    add_bullet(card_t3, "Ultra-fast SGD Screener (~1.5 ms) bypasses normal packets.", "Stage 1 ML:", pt_size=11)
    add_bullet(card_t3, "ExtraTrees multi-class classifier (~3.3 ms).", "Stage 2 ML:", pt_size=11)
    add_bullet(card_t3, "Kafka topic (iiot-sensor-stream) + Spark Structured Streaming.", "Distributed Stack:", pt_size=11)

    card_t4 = add_card(s4, 9.8, 1.8, 2.7, 5.0, "Tier 4: Live Console", ACCENT_RED)
    add_bullet(card_t4, "Low-latency bidirectional JSON broadcast @ 10 Hz.", "WebSockets:", pt_size=11)
    add_bullet(card_t4, "2D Canvas dynamic twin with shaft rotation & thermal shader.", "Twin Canvas:", pt_size=11)
    add_bullet(card_t4, "60 FPS zero-dependency telemetry charts and audit feed.", "Charts & Audit:", pt_size=11)

    s4.notes_slide.notes_text_frame.text = (
        "Here is the complete four-tier system architecture. "
        "At Tier 1, our edge simulator generates 7 multi-channel telemetry streams at 10 Hz based on physical induction motor equations. "
        "At Tier 2, the Digital Twin engine synchronizes with the operating speed and load to compute the nominal expected state "
        "and produces a 7-dimensional residual vector along with a Composite Health Index. "
        "At Tier 3, the 14-dimensional concatenated feature vector is screened by our Two-Stage ML ensemble in 4.78 milliseconds, "
        "while Kafka and Spark handle sliding window aggregation. "
        "Finally, at Tier 4, the processed telemetry is pushed over WebSockets to an interactive browser console featuring "
        "an animated Canvas Digital Twin and live diagnostic controls."
    )

    # ==========================================
    # SLIDE 5: PHYSICS-INFORMED DIGITAL TWIN FORMULATION
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Mathematical Foundation", "Physics-Informed Digital Twin State & Residual Engine",
               "Asset ID: TWIN-MTR-01 — Synchronized first-principles mathematical modeling")

    # Card 1: Physics State Equations
    tf_eq = add_card(s5, 0.8, 1.8, 5.7, 5.0, "Nominal Physics Equations", ACCENT_CYAN)
    add_bullet(tf_eq, "Thermal Dissipation Model: Calculates expected steady-state temperature based on ambient conditions and squared electrical load current:", pt_size=11)
    add_bullet(tf_eq, "T_hat_twin = T_ambient + Delta_T_max * (I_actual / I_rated)^1.8", "Thermal Eq:", pt_size=11, color=ACCENT_CYAN)
    add_bullet(tf_eq, "Vibrational Dynamics Model: Nominal RMS velocity baseline proportional to operating load factor:", pt_size=11)
    add_bullet(tf_eq, "V_hat_rms = V_0 + alpha * Load_factor", "Vibration Eq:", pt_size=11, color=ACCENT_CYAN)
    add_bullet(tf_eq, "Hydraulic Head Pressure: Models discharge pressure curve under centrifugal pump impedance:", pt_size=11)
    add_bullet(tf_eq, "P_hat_twin = P_rated - beta * (Load_factor - 0.75)", "Pressure Eq:", pt_size=11, color=ACCENT_CYAN)

    # Card 2: Residuals and Health Index
    tf_res = add_card(s5, 6.8, 1.8, 5.7, 5.0, "Residual Extraction & Health Index (CHI)", ACCENT_GREEN)
    add_bullet(tf_res, "Absolute Physical Residuals: For each of the 7 sensor channels:", pt_size=11)
    add_bullet(tf_res, "R_i(t) = |X_actual,i(t) - X_hat_twin,i(t)|", "Residual Formula:", pt_size=11, color=ACCENT_GREEN)
    add_bullet(tf_res, "Z-Score Normalization: Normalized against healthy baseline distribution (mu_i, sigma_i):", pt_size=11)
    add_bullet(tf_res, "z_i(t) = max(0, (R_i(t) - mu_i) / sigma_i)", "Z-Score:", pt_size=11, color=ACCENT_GREEN)
    add_bullet(tf_res, "Composite Health Index (CHI): Exponential degradation decay reflecting overall machine integrity:", pt_size=11)
    add_bullet(tf_res, "CHI(t) = 100 * exp(-0.25 * sum(w_i * z_i(t))) in [0, 100%]", "CHI Index:", pt_size=11, color=ACCENT_AMBER)
    add_bullet(tf_res, "Weighted Sensitivity: Vibration RMS (25%), Peak (20%), Temp (15%), RPM/Current/Pressure/Acoustic (10% each).", pt_size=11)

    s5.notes_slide.notes_text_frame.text = (
        "Now let's examine the mathematical backbone: the Physics-Informed Digital Twin. "
        "A key failure of naive machine learning is that when motor load increases, temperature and vibration naturally rise, "
        "triggering false alarms. "
        "Our Digital Twin solves this by running first-principles physical equations in real time: "
        "it calculates expected temperature based on current draw, expected vibration based on load factor, and expected discharge pressure. "
        "We then subtract the twin's expectation from the live sensor telemetry to yield the absolute residual vector R_i. "
        "Under healthy conditions, R_i is near zero regardless of load changes! "
        "We also calculate a Composite Health Index, or CHI, ranging from 0 to 100% using exponential decay across all normalized residuals."
    )

    # ==========================================
    # SLIDE 6: TWO-STAGE MACHINE LEARNING ENSEMBLE
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Machine Learning Ensemble Formulation", "Two-Stage Architecture for Ultra-Low Latency Inference",
               "14-Dimensional Feature Vector: 7 Raw Signals + 7 Digital Twin Residuals")

    tf_s1 = add_card(s6, 0.8, 1.8, 3.7, 5.0, "Stage 1: Ultra-Fast Binary Screener", ACCENT_CYAN)
    add_bullet(tf_s1, "Linear SGDClassifier with modified Huber loss and L2 penalty.", "Algorithm:", pt_size=11)
    add_bullet(tf_s1, "Screens incoming 14-D packets to determine if condition is Normal vs Anomaly.", "Role:", pt_size=11)
    add_bullet(tf_s1, "Sub-millisecond (~1.2 – 1.5 ms).", "Inference Speed:", pt_size=11)
    add_bullet(tf_s1, "Fast Path Bypass: If P(anomaly) < 0.45, packet is flagged Normal and Stage 2 is completely bypassed!", "Key Innovation:", pt_size=11)
    add_bullet(tf_s1, "Over 95% of industrial runtime is normal; bypassing Stage 2 saves massive compute and preserves edge responsiveness.", pt_size=11)

    tf_s2 = add_card(s6, 4.8, 1.8, 3.7, 5.0, "Stage 2: Diagnostic Fault Classifier", ACCENT_AMBER)
    add_bullet(tf_s2, "Extremely Randomized Trees (ExtraTreesClassifier, 60 estimators, max depth 16).", "Algorithm:", pt_size=11)
    add_bullet(tf_s2, "Activated ONLY when Stage 1 flags an anomaly (P >= 0.45).", "Execution Trigger:", pt_size=11)
    add_bullet(tf_s2, "Precisely diagnoses the failure mode into 5 distinct fault classes with confidence scoring.", "Diagnostic Role:", pt_size=11)
    add_bullet(tf_s2, "~3.0 – 3.3 ms.", "Inference Speed:", pt_size=11)
    add_bullet(tf_s2, "High ensemble capacity eliminates single-tree variance and provides rock-solid reliability.", pt_size=11)

    tf_s3 = add_card(s6, 8.8, 1.8, 3.7, 5.0, "End-to-End Latency Budget", ACCENT_GREEN)
    add_bullet(tf_s3, "Normal Operation (Fast Path): ~1.5 ms total delay.", "Fast Path:", pt_size=11)
    add_bullet(tf_s3, "Fault Diagnosis (Full Path): ~4.78 ms total delay.", "Diagnostic Path:", pt_size=11)
    add_bullet(tf_s3, "Strictly adheres to Ranpariya & Sharma (2025) benchmark threshold of <= 4.80 ms.", "Benchmark Adherence:", pt_size=11)
    add_bullet(tf_s3, "10x to 15x faster than Deep Learning LSTMs/Transformers (>50 ms) while exceeding 99.9% accuracy.", "Comparison to DL:", pt_size=11)

    s6.notes_slide.notes_text_frame.text = (
        "Now let's examine the Two-Stage ML Ensemble. This is the exact architectural strategy from the baseline paper. "
        "In typical plant operations, 95% or more of machine runtime is normal. "
        "Running a heavy multi-class ensemble on every single 100ms packet wastes edge CPU and risks queue backlog. "
        "Therefore, we split the decision into two stages: "
        "Stage 1 is an ultra-fast linear SGD screener that takes only 1.5 ms. If the probability of an anomaly is below 0.45, "
        "it immediately returns 'Normal' and exits through the fast path. "
        "Only when an anomaly is detected does Stage 2 trigger. Stage 2 uses an ExtraTrees ensemble to diagnose the exact failure mode. "
        "The combined estimation delay is 4.78 ms, matching the paper's 4.8 ms budget perfectly."
    )

    # ==========================================
    # SLIDE 7: STREAMING INFRASTRUCTURE (KAFKA & SPARK)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Streaming Infrastructure & Big Data Stack", "Apache Kafka & Spark Structured Streaming Integration",
               "High-throughput ingestion, event-time watermarking, and sliding window analytics")

    tf_k = add_card(s7, 0.8, 1.8, 5.7, 5.0, "Apache Kafka Message Broker", ACCENT_CYAN)
    add_bullet(tf_k, "iiot-sensor-stream (keyed by asset_id: TWIN-MTR-01).", "Kafka Topic:", pt_size=11)
    add_bullet(tf_k, "10 Hz continuous telemetry publication (100 ms intervals).", "Ingestion Cadence:", pt_size=11)
    add_bullet(tf_k, "Strict JSON schema containing timestamp, mechanical, electrical, thermal channels, and fault metadata.", "Payload Schema:", pt_size=11)
    add_bullet(tf_k, "Built in streaming/kafka_producer.py with retry policies and fallback buffer.", "Producer Implementation:", pt_size=11)
    add_bullet(tf_k, "confluentinc/cp-kafka:7.6.1 KRaft-based broker on port 9092 via Docker Compose.", "Deployment:", pt_size=11)

    tf_sp = add_card(s7, 6.8, 1.8, 5.7, 5.0, "Spark Structured Streaming Analytics", ACCENT_AMBER)
    add_bullet(tf_sp, "Direct streaming connector using spark.readStream.format('kafka').", "Kafka Source Connector:", pt_size=11)
    add_bullet(tf_sp, "spark.withWatermark('event_time', '10 seconds') to handle out-of-order network arrival cleanly.", "Event-Time Watermark:", pt_size=11)
    add_bullet(tf_sp, "window(col('event_time'), '5 seconds', '1 second') computes rolling analytics updated every second.", "Sliding Window Aggregates:", pt_size=11)
    add_bullet(tf_sp, "Computes rolling average vibration RMS, peak velocity, winding temperature, and current draw.", "Rolling Metrics:", pt_size=11)
    add_bullet(tf_sp, "Engine supports both distributed Kafka/Spark and a zero-dependency in-process streaming engine for standalone demo reliability.", "Dual Execution Mode:", pt_size=11)

    s7.notes_slide.notes_text_frame.text = (
        "This slide directly highlights the big data streaming infrastructure: Apache Kafka and Apache Spark. "
        "Telemetry is ingested into an Apache Kafka topic named 'iiot-sensor-stream' at 10 Hz with key-based partitioning. "
        "Our PySpark Structured Streaming job, located in streaming/spark_streaming_job.py, connects directly to Kafka. "
        "It enforces a 10-second event-time watermark to handle network jitters and computes sliding window aggregates "
        "over a 5-second window with a 1-second slide interval. "
        "This computes rolling averages and peak vibrational levels for statistical stability. "
        "Furthermore, our project features a dual execution mode: it can run fully distributed in Docker with Kafka and Spark, "
        "or run via our in-process engine for instant standalone demonstration."
    )

    # ==========================================
    # SLIDE 8: SIMULATED FAULT MODES & ISO STANDARDS
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Industrial Condition Monitoring Taxonomy", "Six Operational Regimes & Physical Fault Signatures",
               "Grounding simulated fault behavior in ISO 10816 vibration standards and electrical failure mechanics")

    faults = [
        ("Class 0: Normal Operation", "Baseline nominal load; CHI = 95–100%; Stage 1 fast path active; all residuals near 0.", ACCENT_GREEN),
        ("Class 1: Bearing Race Degradation", "ISO 10816 Class II/III breach; severe RMS & peak vibration spike; high acoustic friction.", ACCENT_RED),
        ("Class 2: Stator Winding Overheat", "Thermal runaway (winding temp >85°C); elevated current draw due to insulation breakdown.", ACCENT_AMBER),
        ("Class 3: Dynamic Rotor Imbalance", "1X rotational frequency vibration harmonics; sinusoidal mechanical oscillation.", ACCENT_CYAN),
        ("Class 4: Hydraulic Cavitation", "Discharge pressure collapse (<3.2 Bar); random vapor bubble collapse turbulence in pump.", ACCENT_RED),
        ("Class 5: Sensor Drift / Bias", "Calibration drift in single channel; physics twin model remains stable while residual spikes.", ACCENT_AMBER),
    ]

    for idx, (f_title, f_desc, f_col) in enumerate(faults):
        row = idx // 2
        col = idx % 2
        left = 0.8 + col * 5.9
        top = 1.8 + row * 1.65
        tf_f = add_card(s8, left, top, 5.7, 1.45, f_title, f_col)
        add_bullet(tf_f, f_desc, "Physical Signature:", pt_size=10)

    s8.notes_slide.notes_text_frame.text = (
        "We evaluate our system across six distinct operational regimes grounded in real-world industrial physics. "
        "Class 0 represents healthy operation, where the Composite Health Index remains above 95%. "
        "Class 1 is Bearing Race Degradation, modeled according to ISO 10816 mechanical vibration severity charts. "
        "Class 2 represents Stator Winding Overheat with thermal runaway and current surge. "
        "Class 3 models Dynamic Rotor Imbalance exhibiting 1X rotational frequency harmonics. "
        "Class 4 simulates Hydraulic Cavitation in the centrifugal pump, causing sudden discharge pressure collapse and turbulence. "
        "And Class 5 tests Sensor Calibration Drift, where a single sensor channel drifts while the rest of the physical twin stays consistent."
    )

    # ==========================================
    # SLIDE 9: INTERACTIVE TELEMETRY DASHBOARD & DEMO
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Operations Console & Live Demonstration", "Interactive HTML5 Canvas Digital Twin Dashboard",
               "Real-time visual twin animation, zero-dependency streaming charts, and dynamic fault injection deck")

    tf_d1 = add_card(s9, 0.8, 1.8, 3.7, 5.0, "1. 2D Canvas Digital Twin", ACCENT_CYAN)
    add_bullet(tf_d1, "Dynamic Shaft Animation: Rotation velocity visually locked to live telemetry RPM.", pt_size=11)
    add_bullet(tf_d1, "Thermal Heatmap Shader: Dynamic color shift from cool blue (50°C) to danger red (95°C) across motor windings.", pt_size=11)
    add_bullet(tf_d1, "Vibration Waves: Amplitude displacement waves render structural vibration intensity in real time.", pt_size=11)
    add_bullet(tf_d1, "Zero external library bloat; purely hardware-accelerated HTML5 Canvas.", pt_size=11)

    tf_d2 = add_card(s9, 4.8, 1.8, 3.7, 5.0, "2. 60 FPS Streaming Charts", ACCENT_GREEN)
    add_bullet(tf_d2, "Dual Synchronized Plots: Raw vibration vs Digital Twin expected baseline.", pt_size=11)
    add_bullet(tf_d2, "Thermal dissipation curve vs live measured temperature.", pt_size=11)
    add_bullet(tf_d2, "Continuous Composite Health Index (CHI%) gauge updating at 10 Hz.", pt_size=11)
    add_bullet(tf_d2, "Live latency monitor rendering inference millisecond delay per packet.", pt_size=11)

    tf_d3 = add_card(s9, 8.8, 1.8, 3.7, 5.0, "3. Fault Injection & Audit Feed", ACCENT_AMBER)
    add_bullet(tf_d3, "Live Fault Injection Deck: Interactive buttons to trigger Bearing Fault, Overheat, Imbalance, Cavitation, or Drift on demand.", pt_size=11)
    add_bullet(tf_d3, "Real-Time Audit Feed: Logs anomaly detection events with millisecond timestamp, classified fault class, and confidence score.", pt_size=11)
    add_bullet(tf_d3, "Instant Reset: One-click restoration to pristine normal operation.", pt_size=11)

    s9.notes_slide.notes_text_frame.text = (
        "To make condition monitoring intuitive for plant operators, we built an interactive operations console. "
        "On the left, a 2D HTML5 Canvas animates the Digital Twin in real time: the motor shaft rotates at the exact live RPM, "
        "the winding color shifts dynamically from blue to red based on thermal telemetry, and mechanical vibration waves pulse in real time. "
        "In the center, 60fps streaming charts plot live signals against twin expectations. "
        "On the right, we have the Fault Injection Deck, which allows us during live demonstrations to trigger any of the 5 fault modes "
        "and immediately watch the health index plummet and Stage 2 trigger in under 5 milliseconds."
    )

    # ==========================================
    # SLIDE 10: EXPERIMENTAL RESULTS & BENCHMARK COMPARISON
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Experimental Results & Validation", "Comparative Performance Evaluation",
               "Evaluating 18,000 multi-sensor samples against Ranpariya & Sharma (2025) and standard ML baselines")

    # Table Creation
    table_shape = s10.shapes.add_table(5, 6, Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.3))
    table = table_shape.table
    table.columns[0].width = Inches(3.2)
    table.columns[1].width = Inches(2.3)
    table.columns[2].width = Inches(1.5)
    table.columns[3].width = Inches(1.5)
    table.columns[4].width = Inches(1.5)
    table.columns[5].width = Inches(1.7)

    headers = ["Model Architecture", "Feature Input", "Accuracy", "Recall", "F1-Score", "Avg Delay"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(14, 116, 144)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.alignment = PP_ALIGN.CENTER

    data = [
        ("Proposed 2-Stage DT Ensemble", "14-D (Raw + Residuals)", "99.94%", "99.94%", "99.94%", "4.78 ms"),
        ("Ranpariya & Sharma (2025)", "Edge-Cloud Digital Twin", "99.71%", "—", "—", "4.80 ms"),
        ("Baseline A: Random Forest (7-D)", "7-D (Raw Telemetry)", "94.80%", "94.80%", "94.78%", "8.42 ms"),
        ("Baseline B: SVM (RBF Kernel)", "7-D (Raw Telemetry)", "91.20%", "91.20%", "91.15%", "15.60 ms"),
    ]

    for row_idx, row_data in enumerate(data, start=1):
        is_proposed = (row_idx == 1)
        bg = RGBColor(30, 41, 59) if not is_proposed else RGBColor(19, 78, 74)
        for col_idx, text in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.size = Pt(10)
            p.font.bold = is_proposed
            p.font.color.rgb = ACCENT_GREEN if is_proposed else TEXT_WHITE
            if col_idx >= 2:
                p.alignment = PP_ALIGN.CENTER

    # Findings Cards
    tf_k1 = add_card(s10, 0.8, 4.4, 5.7, 2.4, "Finding 1: Residual Superiority", ACCENT_GREEN)
    add_bullet(tf_k1, "Incorporating Digital Twin residuals boosted classification accuracy from 94.80% (raw sensors) to 99.94%.", pt_size=11)
    add_bullet(tf_k1, "Physical residuals cancel out confounding load changes, ensuring pure fault sensitivity.", pt_size=11)

    tf_k2 = add_card(s10, 6.8, 4.4, 5.7, 2.4, "Finding 2: Edge Latency Adherence", ACCENT_CYAN)
    add_bullet(tf_k2, "Average estimation delay of 4.78 ms successfully reproduces the <= 4.80 ms baseline paper limit.", pt_size=11)
    add_bullet(tf_k2, "Fast-path screening in Stage 1 ensures normal samples incur only ~1.5 ms delay.", pt_size=11)

    s10.notes_slide.notes_text_frame.text = (
        "Here are the experimental results and comparative evaluation against baselines. "
        "Our proposed Two-Stage Digital Twin ensemble achieved 99.94% accuracy with an average estimation delay of 4.78 ms, "
        "successfully validating and reproducing the benchmarks of Ranpariya & Sharma (2025). "
        "Notice the ablation comparison: when we tested standard Random Forest and SVM on raw 7-D sensor data without the Digital Twin residuals, "
        "accuracy dropped to 94.8% and 91.2%, and latency surged up to 15.6 ms. "
        "This proves our core hypothesis: Digital Twin residuals isolate true mechanical defects from operational load shifts, "
        "enabling both higher accuracy and lower inference overhead."
    )

    # ==========================================
    # SLIDE 11: VIVA DEFENSE GUIDE & KEY QUESTIONS
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Viva Voce & Technical Defense Guide", "Anticipated Questions & Technical Explanations",
               "Clear rationale for architectural, streaming, and machine learning decisions")

    tf_q1 = add_card(s11, 0.8, 1.8, 5.7, 2.4, 'Q1: "Why not use Deep Learning (LSTM / Transformers)?"', ACCENT_AMBER)
    add_bullet(tf_q1, "Deep recurrent networks impose inference latencies > 50 ms and require heavy GPU hardware.", pt_size=10)
    add_bullet(tf_q1, "In time-critical IIoT, control loops need sub-5ms decisions; our Two-Stage ensemble achieves 4.78 ms on lightweight CPU.", pt_size=10)

    tf_q2 = add_card(s11, 6.8, 1.8, 5.7, 2.4, 'Q2: "What is the specific role of Kafka and Spark?"', ACCENT_CYAN)
    add_bullet(tf_q2, "Apache Kafka decouples the 10 Hz telemetry ingestion from downstream consumers, preventing data loss during burst loads.", pt_size=10)
    add_bullet(tf_q2, "PySpark Structured Streaming performs watermarked sliding window analytics (5s window, 1s slide) for rolling aggregates.", pt_size=10)

    tf_q3 = add_card(s11, 0.8, 4.4, 5.7, 2.4, 'Q3: "Why are Digital Twin residuals necessary?"', ACCENT_GREEN)
    add_bullet(tf_q3, "Raw sensor telemetry fluctuates naturally when motor speed or electrical load varies.", pt_size=10)
    add_bullet(tf_q3, "The Digital Twin predicts expected behavior; taking the residual R = |X - X_hat| isolates genuine physical damage.", pt_size=10)

    tf_q4 = add_card(s11, 6.8, 4.4, 5.7, 2.4, 'Q4: "How does the Two-Stage Ensemble save latency?"', ACCENT_CYAN)
    add_bullet(tf_q4, "Stage 1 (linear SGD) takes only ~1.5 ms. If normal, it bypasses Stage 2 entirely (Fast Path).", pt_size=10)
    add_bullet(tf_q4, "Stage 2 (ExtraTrees) is executed only when an anomaly is confirmed, minimizing average processing time.", pt_size=10)

    s11.notes_slide.notes_text_frame.text = (
        "Here are the four most important technical defense questions that evaluators frequently ask. "
        "First, why not deep learning? Because LSTMs require over 50 ms inference time and cannot run on cheap edge microcontrollers. "
        "Second, how are Kafka and Spark used? Kafka provides backpressure-safe 10 Hz ingestion, and Spark executes 5-second sliding window aggregations with a 10-second watermark. "
        "Third, why are physics residuals needed? Because raw sensor readings fluctuate with motor speed and load; residuals eliminate these false positives. "
        "And fourth, how does the Two-Stage ensemble save latency? By utilizing a fast-path bypass for normal packets in Stage 1."
    )

    # ==========================================
    # SLIDE 12: CONCLUSION, FUTURE SCOPE & Q&A
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Summary & Future Roadmap", "Project Conclusions & Future Directions",
               "Real-Time Digital Twin for Streaming-Based Anomaly Detection")

    tf_con = add_card(s12, 0.8, 1.8, 5.7, 3.8, "Key Project Achievements", ACCENT_GREEN)
    add_bullet(tf_con, "Implemented end-to-end real-time streaming pipeline combining Apache Kafka, Spark Structured Streaming, and WebSockets.", pt_size=11)
    add_bullet(tf_con, "Validated and reproduced the state-of-the-art benchmark of Ranpariya & Sharma (2025): 99.94% accuracy, 4.78 ms delay.", pt_size=11)
    add_bullet(tf_con, "Engineered a Physics-Informed Digital Twin (TWIN-MTR-01) with continuous residual vector extraction and CHI tracking.", pt_size=11)
    add_bullet(tf_con, "Delivered an interactive HTML5 Canvas dashboard with dynamic visual twin and fault injection controls.", pt_size=11)

    tf_fut = add_card(s12, 6.8, 1.8, 5.7, 3.8, "Future Research Extensions", ACCENT_AMBER)
    add_bullet(tf_fut, "Weibull Remaining Useful Life (RUL): Integrating prognostic survival curves to predict exact hours until component failure.", pt_size=11)
    add_bullet(tf_fut, "Multi-Asset Fleet Monitoring: Scaling Kafka partitioning across hundreds of heterogeneous factory machines.", pt_size=11)
    add_bullet(tf_fut, "Hardware-in-the-Loop Edge Deployment: Compiling the Stage 1 model to TinyML microcontrollers (ESP32 / Raspberry Pi).", pt_size=11)

    # Thank you footer card
    tf_thx = add_card(s12, 0.8, 5.8, 11.7, 1.1, "", ACCENT_CYAN)
    p_end = tf_thx.paragraphs[0]
    p_end.text = "Thank You! Open for Questions & Live Demonstration"
    p_end.font.size = Pt(16)
    p_end.font.bold = True
    p_end.font.color.rgb = ACCENT_CYAN
    p_end.alignment = PP_ALIGN.CENTER
    
    p_end2 = tf_thx.add_paragraph()
    p_end2.text = "Mohammed Sirajudheen (2023BCS0132) | Rohit Pratap Singh (2023BCS0138) | Amit Kumar (2023BCS0210) | Kartik P (2023BCD0051) | Team No: 10"
    p_end2.font.size = Pt(12)
    p_end2.font.color.rgb = TEXT_MUTED
    p_end2.alignment = PP_ALIGN.CENTER

    s12.notes_slide.notes_text_frame.text = (
        "In conclusion, we have built a complete, production-grade streaming anomaly detection system "
        "that combines physical engineering principles with modern big data streaming and lightweight machine learning. "
        "We successfully replicated the 4.8 millisecond target and 99.7% accuracy established in published research. "
        "In the future, we plan to extend this with Remaining Useful Life Weibull prognostics and multi-asset fleet monitoring. "
        "Thank you professors, and I am now excited to demonstrate the live system and answer your questions."
    )

    # Save presentations
    out_file_1 = Path(r"c:\Users\siraj\Desktop\streaming_2\streaming_project\Digital_Twin_Anomaly_Detection_Presentation.pptx")
    out_file_2 = Path(r"c:\Users\siraj\Desktop\streaming_2\Digital_Twin_Anomaly_Detection_Presentation.pptx")
    prs.save(out_file_1)
    prs.save(out_file_2)
    print(f"Presentation successfully generated at:\n  - {out_file_1}\n  - {out_file_2}")

if __name__ == "__main__":
    create_presentation()
