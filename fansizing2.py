import streamlit as st
import math

# -------------------------
# Fan Database (simplified)
# -------------------------
fan_database = [
    {"brand": "ebm-papst", "model": "A2D200-AA02-01", "type": "Axial", "max_flow": 800, "max_pressure": 350, "power": 70, "voltage": 12, "rpm": 2500},
    {"brand": "Sanyo Denki", "model": "9HV1248P1G03", "type": "Centrifugal", "max_flow": 420, "max_pressure": 500, "power": 48, "voltage": 12, "rpm": 3200},
    {"brand": "Delta", "model": "AFB1212GHE", "type": "Axial", "max_flow": 600, "max_pressure": 300, "power": 60, "voltage": 12, "rpm": 4000},
    {"brand": "Nidec", "model": "U76X12MS1A5-57", "type": "Mixed", "max_flow": 500, "max_pressure": 400, "power": 55, "voltage": 12, "rpm": 2800},
    {"brand": "ebm-papst", "model": "R2E220-AA40-17", "type": "Centrifugal", "max_flow": 1000, "max_pressure": 600, "power": 120, "voltage": 12, "rpm": 1800},
    {"brand": "Delta", "model": "BFB1012VH", "type": "Centrifugal", "max_flow": 300, "max_pressure": 450, "power": 40, "voltage": 12, "rpm": 3500},
]

# -------------------------
# Typical region presets
# -------------------------
regions = {
    "Cabin": {"default_flow": 500, "default_pressure": 250, "default_eff": 0.6},
    "Cockpit": {"default_flow": 150, "default_pressure": 200, "default_eff": 0.55},
    "Avionics Bay": {"default_flow": 100, "default_pressure": 350, "default_eff": 0.5},
    "Cargo Hold": {"default_flow": 200, "default_pressure": 300, "default_eff": 0.65},
}

# -------------------------
# UI - Title & Sidebar
# -------------------------
st.set_page_config(page_title="Aircraft Fan Sizing Tool")
st.title("🛫 Aircraft Fan Sizing Tool")
st.write("This tool helps to size fans for aircraft interior ventilation systems.")

region = st.selectbox("Select Aircraft Region", list(regions.keys()))
fan_type = st.selectbox("Select Fan Type", ["Axial", "Centrifugal", "Mixed"])

with st.expander("✏️ Input Parameters"):
    flow_rate = st.number_input("Required Flow Rate (m³/h)", min_value=10, value=regions[region]["default_flow"])
    pressure_drop = st.number_input("Estimated Pressure Drop (Pa)", min_value=10, value=regions[region]["default_pressure"])
    efficiency = st.slider("Fan Efficiency (%)", min_value=30, max_value=90, value=int(regions[region]["default_eff"] * 100))
    num_fans = st.number_input("Number of Fans", min_value=1, value=1)

    # Additional Inputs
    st.markdown("---")
    st.markdown("### 📏 Physical Parameters")
    fan_height = st.number_input("Fan Height (mm)", min_value=10)
    fan_width = st.number_input("Fan Width (mm)", min_value=10)
    fan_depth = st.number_input("Fan Depth (mm)", min_value=10)
    voltage = st.number_input("Operating Voltage (VDC)", value=12)
    rpm = st.number_input("Fan Speed (RPM)", value=2500)

    st.markdown("---")
    st.markdown("### 💨 Airflow Conversion")
    airflow_unit = st.selectbox("Enter Airflow in:", ["m³/min", "CFM", "m³/h"])
    airflow_value = st.number_input("Airflow Value", min_value=0.0, value=round(flow_rate / 60, 2))

    if airflow_unit == "m³/min":
        airflow_cfm = airflow_value * 35.315
        airflow_m3h = airflow_value * 60
    elif airflow_unit == "CFM":
        airflow_m3h = airflow_value / 35.315 * 60
        airflow_cfm = airflow_value
    else:  # m³/h
        airflow_m3h = airflow_value
        airflow_cfm = airflow_value / 60 * 35.315

    st.write(f"**Converted Flow:** {airflow_m3h:.1f} m³/h | {airflow_cfm:.1f} CFM")

# -------------------------
# Calculations
# -------------------------
flow_rate_m3s = airflow_m3h / 3600  # Convert to m³/s
eff_decimal = efficiency / 100

if eff_decimal == 0:
    st.error("Efficiency cannot be zero.")
else:
    power_watt = (flow_rate_m3s * pressure_drop) / eff_decimal
    total_power = power_watt * num_fans

    st.subheader("🔍 Sizing Results")
    st.write(f"Required flow rate per fan: **{airflow_m3h:.1f} m³/h**")
    st.write(f"Required pressure: **{pressure_drop} Pa**")
    st.write(f"Fan efficiency: **{efficiency}%**")
    st.write(f"Calculated power per fan: **{power_watt:.2f} W**")
    st.write(f"Total power for {num_fans} fan(s): **{total_power:.2f} W**")

    # -------------------------
    # Fan suggestion system
    # -------------------------
    st.subheader("🔧 Suggested Fan Models")
    suggested = []
    for fan in fan_database:
        if (fan["type"] == fan_type and
            fan["max_flow"] >= airflow_m3h and
            fan["max_pressure"] >= pressure_drop and
            fan["voltage"] == voltage and
            abs(fan["rpm"] - rpm) <= 1000):
            suggested.append(fan)

    if suggested:
        for fan in suggested:
            st.markdown(f"**{fan['brand']} – {fan['model']}**  ")
            st.write(f"• Type: {fan['type']}  | Max Flow: {fan['max_flow']} m³/h  | Max Pressure: {fan['max_pressure']} Pa  | Power: {fan['power']} W | Voltage: {fan['voltage']} VDC | Speed: {fan['rpm']} RPM")
            st.write("---")
    else:
        st.warning("❌ No suitable fan model found in the database based on your inputs.")

# -------------------------
# Fan Sizing Formulas Info
# -------------------------
st.subheader("📘 Fan Sizing Equations")
st.markdown("""
- **Power (W):** \( P = \frac{Q \cdot \Delta P}{\eta} \)  
- **Q:** Flow rate (m³/s)  
- **ΔP:** Pressure drop (Pa)  
- **η:** Efficiency (decimal)

**Conversions:**
- 1 CFM ≈ 0.0283 m³/min ≈ 1.699 m³/h  
- 1 m³/min ≈ 35.315 CFM  
- 1 m³/h = 0.5886 CFM

**Horsepower (HP) Estimate:**
\( HP = \frac{Q_{cfm} \cdot \Delta P}{6356 \cdot \eta} \)
""")

# -------------------------
# Footer
# -------------------------
st.caption("Developed for aircraft ventilation sizing by Halil İbrahim Aydın ✈️")
