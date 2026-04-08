# streamlit run Clock_out.py
import pytz
import time
import streamlit as st
from datetime import datetime

# --- Logic Functions (Simplified for Streamlit) ---

st.set_page_config(
    page_title="Clock Out", 
    page_icon="🕒",
    layout="centered"
)

def check_if_minute_is_over(hour, min):
    while min >= 60:
        min -= 60
        hour += 1
    return f"{str(hour).zfill(2)}:{str(min).zfill(2)}"

def extract_time(time):
    # Handling different separators (., :)
    time = time.replace(".", ":")
    if ":" in time:
        h, m = map(int, time.split(":"))
    else:
        # Handle formats like 0830 or 830
        if len(time) == 4:
            h, m = int(time[:2]), int(time[2:])
        else:
            h, m = int(time[:1]), int(time[1:])
    
    if m > 59 or h > 23:
        return None, "Invalid time format."
    else:
        return (h, m), None

def check_ot_time_left(ot_time):

    result_data, error = extract_time(ot_time)

    if error:
        st.error(error)
        
    h, m = result_data

    tz = pytz.timezone('Asia/Kuala_Lumpur') # Sets the timezone to Malaysia
    now = datetime.now(tz)

    now_total = now.hour * 60 + now.minute
        
    ot_total = h * 60 + m
    
    if ot_total > now_total:
        diff = ot_total - now_total
        if diff > 60:
            return f"🔴"
        else:
            return f"🟡"
    else:
        return f"🟢"


def calculate_times(clock_in_str):
    is_late =  False
    try:
        result_data, error = extract_time(clock_in_str)
        if error:
            st.error(error)
            
        h, m = result_data

        # Logic for thresholds
        combine_time = int(f"{h}{str(m).zfill(2)}")
        
        # Default flags
        half_day_flag = 1
        adj_h, adj_m = h, m

        if combine_time < 730:
            adj_h, adj_m = 7, 30
        elif 730 <= combine_time <= 930:
            pass 
        elif 930 < combine_time < 1130:
            adj_h, adj_m = 9, 30
            is_late = True
        elif combine_time < 1215:
            adj_h, adj_m, half_day_flag = 7, 30, 0
        elif 1215 <= combine_time <= 1415:
            half_day_flag = 0
            # Adjustment logic
            total_min = (h * 60 + m) - 45 - (4 * 60)
            adj_h, adj_m = divmod(total_min, 60)
        elif combine_time > 1415:
            adj_h, adj_m, half_day_flag = 9, 30, 0

        return (adj_h, adj_m, half_day_flag, is_late), None
    except Exception:
        return None, "Please enter time in a valid format (e.g., 08:30 or 830)."

# --- Streamlit UI ---

st.title("🕒 Clock Out (SOEM)")
# st.markdown("Developed by Hazim (C) 2026")

# Input Section
clock_in = st.text_input("Enter your clock-in time (24H Format, e.g., 08:30 or 830):")

if clock_in:
    result_data, error = calculate_times(clock_in)
    
    if error:
        st.error(error)
    else:
        h, m, half_day_flag, is_late = result_data

        if is_late:
            st.warning("⚠️ LATE!  \nYour clock-in has been adjusted to 09:30")
        
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
        # Run the countdown loop
        st.divider()
        countdown_placeholder = st.empty()

        # OT Section
        st.divider()
        with st.expander("See Overtime (OT) Schedule"):
            base_h, base_m = h + 9, m + 30
            for i in range(1, 4):
                ot_h = base_h + i
                # +10 mins for first OT, then +30 intervals
                ot_full = check_if_minute_is_over(ot_h, base_m + 10)
                ot_half = check_if_minute_is_over(ot_h, base_m + 40)
                
                st.write(f"**OT {i} Hour:** {ot_full} " + check_ot_time_left(ot_full) + f" | **OT {i}.5 Hour:** {ot_half} "  + check_ot_time_left(ot_half))

        while True:
            now = datetime.now(tz)
            now_total = now.hour * 60 * 60 + now.minute * 60 + now.second
            
            out_h, out_m = map(int, full_out_str.split(":"))
            out_total = out_h * 60 * 60 + out_m * 60 # Convert target to seconds
            
            if out_total > now_total:
                seconds_left = out_total - now_total
                hrs, remainder = divmod(seconds_left, 3600)
                mins, secs = divmod(remainder, 60)
                
                # This overwrites the placeholder every second
                countdown_placeholder.warning(f"⏳ Time until freedom: **{hrs}h {mins}m {secs}s**")
                time.sleep(1) # Wait 1 second before looping
            else:
                countdown_placeholder.success("🎉 It's time to go home!")
                break # Stop the loop once you reach the time
