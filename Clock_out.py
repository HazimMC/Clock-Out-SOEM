import pytz
import streamlit as st
from datetime import datetime

# --- Logic Functions (Simplified for Streamlit) ---

def check_if_minute_is_over(hour, min):
    while min >= 60:
        min -= 60
        hour += 1
    return f"{str(hour).zfill(2)}:{str(min).zfill(2)}"

def calculate_times(clock_in_str):
    try:
        # Handling different separators (., :)
        clock_in_str = clock_in_str.replace(".", ":")
        if ":" in clock_in_str:
            h, m = map(int, clock_in_str.split(":"))
        else:
            # Handle formats like 0830 or 830
            if len(clock_in_str) == 4:
                h, m = int(clock_in_str[:2]), int(clock_in_str[2:])
            else:
                h, m = int(clock_in_str[:1]), int(clock_in_str[1:])
        
        if m > 59 or h > 23:
            return None, "Invalid time format."

        # Logic for thresholds
        combine_time = int(f"{h}{str(m).zfill(2)}")
        
        # Default flags
        half_day_flag = 1
        adj_h, adj_m = h, m

        if combine_time < 730:
            adj_h, adj_m = 7, 30
        elif 730 <= combine_time <= 930:
            pass 
        elif 930 < combine_time < 1000:
            adj_h, adj_m = 9, 30
        elif combine_time < 1215:
            adj_h, adj_m, half_day_flag = 7, 30, 0
        elif 1215 <= combine_time <= 1415:
            half_day_flag = 0
            # Adjustment logic
            total_min = (h * 60 + m) - 45 - (4 * 60)
            adj_h, adj_m = divmod(total_min, 60)
        elif combine_time > 1415:
            adj_h, adj_m, half_day_flag = 9, 30, 0

        return (adj_h, adj_m, half_day_flag), None
    except Exception:
        return None, "Please enter time in a valid format (e.g., 08:30 or 830)."

# --- Streamlit UI ---

st.set_page_config(page_title="Work Clock Calculator", page_icon="🕒")

st.title("🕒 Work Clock Calculator")
st.markdown("Developed by Hazim (C) 2026")

# Input Section
clock_in = st.text_input("Enter your clock-in time (24H Format, e.g., 08:30 or 830):")

if clock_in:
    result_data, error = calculate_times(clock_in)
    
    if error:
        st.error(error)
    else:
        h, m, half_day_flag = result_data
        
        # Half Day Calculation
        half_out = check_if_minute_is_over(h + 4, m + 45)
        
        # Normal Calculation (9h 30m shift)
        full_out_str = check_if_minute_is_over(h + 9, m + 30)
        
        # --- Display Results ---
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if half_day_flag == 1:
                st.metric("Half Day Clock Out", half_out)
            st.metric("Full Day Clock Out", full_out_str)

        # Time Left Calculation
        tz = pytz.timezone('Asia/Kuala_Lumpur') # Sets the timezone to Malaysia
        now = datetime.now(tz)
        now_total = now.hour * 60 + now.minute
        
        out_h, out_m = map(int, full_out_str.split(":"))
        out_total = out_h * 60 + out_m
        
        if out_total > now_total:
            diff = out_total - now_total
            hrs, mins = divmod(diff, 60)
            st.warning(f"⏳ You have **{hrs}h {mins}m** left for work today.")
        else:
            st.success("🎉 It's time to go home!")

        # OT Section
        st.divider()
        with st.expander("See Overtime (OT) Schedule"):
            base_h, base_m = h + 9, m + 30
            for i in range(1, 4):
                ot_h = base_h + i
                # +10 mins for first OT, then +30 intervals
                ot_full = check_if_minute_is_over(ot_h, base_m + 10)
                ot_half = check_if_minute_is_over(ot_h, base_m + 40)
                
                st.write(f"**OT {i} Hour:** {ot_full} | **OT {i}.5 Hour:** {ot_half}")
