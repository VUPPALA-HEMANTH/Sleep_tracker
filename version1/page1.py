import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, time, timedelta

SLEEP_FILE = "sleep.json"

# --- Load & Save Functions ---
def load_data():
    try:
        with open(SLEEP_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(SLEEP_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Backend Helper ---
def time_to_minutes_sleep(t: time) -> int:
    """Convert time to minutes since previous day midnight for sleep comparison."""
    mins = t.hour*60 + t.minute
    # If hour < 12, treat as next day (24+ scale)
    if mins < 12*60:
        mins += 24*60
    return mins

def time_to_minutes_wake(t: time) -> int:
    """Convert time to minutes for wake comparison (literal)."""
    return t.hour*60 + t.minute

# --- Page 1 Function ---
def page1():
    st.header("Add Sleep Record")
    data = load_data()
    
    # --- Date Selection ---
    record_date = st.date_input("Select Date", value=date.today())
    
    # --- Time Selection (exact) ---
    st.subheader("Sleep Times")
    expected_sleep = st.time_input("Expected Sleep Time (HH:MM)", value=time(23,0))
    actual_sleep   = st.time_input("Actual Sleep Time (HH:MM)", value=time(23,0))
    
    st.subheader("Wake Times")
    expected_wake = st.time_input("Expected Wake Up Time (HH:MM)", value=time(7,0))
    actual_wake   = st.time_input("Actual Wake Up Time (HH:MM)", value=time(7,0))
    
    # --- Conditional Reason Fields ---
    reason_sleep = ""
    reason_wake  = ""
    
    if time_to_minutes_sleep(actual_sleep) > time_to_minutes_sleep(expected_sleep):
        reason_sleep = st.text_input("Reason for sleeping later than expected")
    
    if time_to_minutes_wake(actual_wake) > time_to_minutes_wake(expected_wake):
        reason_wake = st.text_input("Reason for waking up later than expected")
    
    # --- Add Record Button ---
    if st.button("Add Record"):
        new_record = {
            "date": record_date.isoformat(),
            "expected_sleep": expected_sleep.strftime("%H:%M"),
            "actual_sleep": actual_sleep.strftime("%H:%M"),
            "expected_wake": expected_wake.strftime("%H:%M"),
            "actual_wake": actual_wake.strftime("%H:%M"),
            "reason_sleep": reason_sleep,
            "reason_wake": reason_wake
        }
        data.append(new_record)
        save_data(data)
        st.success("Record added successfully!")
    
    action = st.radio("Choose an action", options=["None", "Edit Record", "Delete Record"])

    if action in ["Edit Record", "Delete Record"]:
        # Ask for date only after choosing action
        selected_date = st.date_input(
            "Select Date", 
            value=date.today(), 
            key=f"{action}_date"
        )
        records_for_date = [rec for rec in data if rec['date'] == selected_date.isoformat()]

        if records_for_date:
            for i, rec in enumerate(records_for_date):
                st.markdown(f"**Record {i+1}**")
                st.write(f"Expected Sleep: {rec['expected_sleep']}, Actual Sleep: {rec['actual_sleep']}")
                st.write(f"Expected Wake: {rec['expected_wake']}, Actual Wake: {rec['actual_wake']}")
                st.write(f"Reason Sleep: {rec.get('reason_sleep', '')}, Reason Wake: {rec.get('reason_wake', '')}")

                if action == "Edit Record":
                    # Editable fields
                    new_expected_sleep = st.time_input(
                        "Expected Sleep", 
                        value=datetime.strptime(rec['expected_sleep'], "%H:%M").time(),
                        key=f"exp_sleep_{i}"
                    )
                    new_actual_sleep = st.time_input(
                        "Actual Sleep", 
                        value=datetime.strptime(rec['actual_sleep'], "%H:%M").time(),
                        key=f"act_sleep_{i}"
                    )
                    new_expected_wake = st.time_input(
                        "Expected Wake", 
                        value=datetime.strptime(rec['expected_wake'], "%H:%M").time(),
                        key=f"exp_wake_{i}"
                    )
                    new_actual_wake = st.time_input(
                        "Actual Wake", 
                        value=datetime.strptime(rec['actual_wake'], "%H:%M").time(),
                        key=f"act_wake_{i}"
                    )

                    if st.button(f"Confirm Update Record {i+1}", key=f"update_{i}"):
                        rec['expected_sleep'] = new_expected_sleep.strftime("%H:%M")
                        rec['actual_sleep'] = new_actual_sleep.strftime("%H:%M")
                        rec['expected_wake'] = new_expected_wake.strftime("%H:%M")
                        rec['actual_wake'] = new_actual_wake.strftime("%H:%M")
                        save_data(data)
                        st.success("Record updated!")

                elif action == "Delete Record":
                    if st.button(f"Confirm Delete Record {i+1}", key=f"delete_{i}"):
                        data.remove(rec)
                        save_data(data)
                        st.warning("Record deleted!")
        else:
            st.info("No records found for this date.")


    # --- Display All Records ---
    if data:
        df = pd.DataFrame(data)
        st.subheader("All Sleep Records")
        st.dataframe(df)
