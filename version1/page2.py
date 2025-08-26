import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

SLEEP_FILE = "sleep.json"

def load_data():
    try:
        with open(SLEEP_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def page2():
    st.header("Sleep Tracker Analysis")
    data = load_data()
    if not data:
        st.info("No data to show yet.")
        return

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    # --- Convert sleep/wake times to minutes for backend comparison ---
    def sleep_to_minutes(t_str):
        t = datetime.strptime(t_str, "%H:%M").time()
        mins = t.hour*60 + t.minute
        # For sleep times between 0:00-4:30, map to 24+ scale
        if mins < 5*60:
            mins += 24*60
        return mins

    def wake_to_minutes(t_str):
        t = datetime.strptime(t_str, "%H:%M").time()
        return t.hour*60 + t.minute

    df['expected_sleep_min'] = df['expected_sleep'].apply(sleep_to_minutes)
    df['actual_sleep_min']   = df['actual_sleep'].apply(sleep_to_minutes)
    df['expected_wake_min']  = df['expected_wake'].apply(wake_to_minutes)
    df['actual_wake_min']    = df['actual_wake'].apply(wake_to_minutes)

    # Highlight too late days
    st.sidebar.header("Thresholds for Highlighting")
    sleep_late_time = st.sidebar.time_input("Sleep Too Late Threshold", value=datetime.strptime("00:30", "%H:%M").time())
    wake_late_time = st.sidebar.time_input("Wake Too Late Threshold", value=datetime.strptime("08:30", "%H:%M").time())
    sleep_late_min = sleep_late_time.hour*60 + sleep_late_time.minute
    if sleep_late_min < 5*60:
        sleep_late_min += 24*60
    wake_late_min = wake_late_time.hour*60 + wake_late_time.minute
    df['sleep_late'] = df['actual_sleep_min'] > sleep_late_min
    df['wake_late'] = df['actual_wake_min'] > wake_late_min

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["Sleep Analysis", "Wake Analysis", "Averages"])

    # ------------------- Sleep Analysis -------------------
    with tab1:
        st.subheader("Sleep Times")
        # Convert minutes to hours for plotting
        df['expected_sleep_hours'] = df['expected_sleep_min'] / 60
        df['actual_sleep_hours']   = df['actual_sleep_min'] / 60

        # Create interactive Plotly figure
        fig_sleep = go.Figure()
        fig_sleep.add_trace(go.Scatter(
            x=df['date'],
            y=df['expected_sleep_hours'],
            mode='lines+markers',
            name='Expected Sleep'
        ))
        fig_sleep.add_trace(go.Scatter(
            x=df['date'],
            y=df['actual_sleep_hours'],
            mode='lines+markers',
            name='Actual Sleep',
            marker=dict(color=['red' if late else 'green' for late in df['sleep_late']])
        ))

        # Update hovertext to show HH:MM
        hover_expected_sleep = [
            f"{d.date().strftime('%d-%m-%Y')}: {int(h)//1:02d}:{int((h%1*60)):02d}"
            for d, h in zip(df['date'], df['expected_sleep_hours'])
        ]
        hover_actual_sleep = [
            f"{d.date().strftime('%d-%m-%Y')}: {int(h)//1:02d}:{int((h%1*60)):02d}"
            for d, h in zip(df['date'], df['actual_sleep_hours'])
        ]
        fig_sleep.data[0].hovertext = hover_expected_sleep
        fig_sleep.data[0].hoverinfo = "text"
        fig_sleep.data[1].hovertext = hover_actual_sleep
        fig_sleep.data[1].hoverinfo = "text"

        # Y-axis custom tick labels HH:MM from 21:00 → 28:30
        tick_vals = list(range(21, 29))  # 21 → 28
        tick_text = [f"{h%24:02d}:00" for h in tick_vals]
        fig_sleep.update_layout(
            xaxis_title="Date",
            yaxis=dict(title="Sleep Time (HH:MM)", tickvals=tick_vals, ticktext=tick_text),
            title="Sleep Times (Interactive)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_sleep, use_container_width=True)

    # ------------------- Wake Analysis -------------------
    with tab2:
        st.subheader("Wake Times")
        df['expected_wake_hours'] = df['expected_wake_min'] / 60
        df['actual_wake_hours']   = df['actual_wake_min'] / 60

        fig_wake = go.Figure()
        fig_wake.add_trace(go.Scatter(
            x=df['date'],
            y=df['expected_wake_hours'],
            mode='lines+markers',
            name='Expected Wake'
        ))
        fig_wake.add_trace(go.Scatter(
            x=df['date'],
            y=df['actual_wake_hours'],
            mode='lines+markers',
            name='Actual Wake',
            marker=dict(color=['red' if late else 'green' for late in df['wake_late']])
        ))

        # Update hovertext to show HH:MM
        hover_expected_wake = [
            f"{d.date().strftime('%d-%m-%Y')}: {int(h)//1:02d}:{int((h%1*60)):02d}"
            for d, h in zip(df['date'], df['expected_wake_hours'])
        ]
        hover_actual_wake = [
            f"{d.date().strftime('%d-%m-%Y')}: {int(h)//1:02d}:{int((h%1*60)):02d}"
            for d, h in zip(df['date'], df['actual_wake_hours'])
        ]
        fig_wake.data[0].hovertext = hover_expected_wake
        fig_wake.data[0].hoverinfo = "text"
        fig_wake.data[1].hovertext = hover_actual_wake
        fig_wake.data[1].hoverinfo = "text"

        fig_wake.update_layout(
            xaxis_title="Date",
            yaxis_title="Wake Hour (HH:MM)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_wake, use_container_width=True)


    # ------------------- Averages -------------------
    with tab3:
        st.subheader("Average Sleep & Wake Times")
        avg_sleep_min = df['actual_sleep_min'].mean() % (24*60)
        avg_wake_min  = df['actual_wake_min'].mean() % (24*60)
        avg_expected_sleep_min = df['expected_sleep_min'].mean() % (24*60)
        avg_expected_wake_min = df['expected_wake_min'].mean() % (24*60)

        avg_sleep_hh = int(avg_sleep_min // 60)
        avg_sleep_mm = int(avg_sleep_min % 60)
        avg_wake_hh = int(avg_wake_min // 60)
        avg_wake_mm = int(avg_wake_min % 60)
        avg_expected_sleep_hh = int(avg_expected_sleep_min // 60)
        avg_expected_sleep_mm = int(avg_expected_sleep_min % 60)
        avg_expected_wake_hh = int(avg_expected_wake_min // 60)
        avg_expected_wake_mm = int(avg_expected_wake_min % 60)

        st.write(f"Average Expected Sleep Time: {avg_expected_sleep_hh:02d}:{avg_expected_sleep_mm:02d}")
        st.write(f"Average Sleep Time: {avg_sleep_hh:02d}:{avg_sleep_mm:02d}")
        
        st.write(f"Average Expected Wake Time: {avg_expected_wake_hh:02d}:{avg_expected_wake_mm:02d}")
        st.write(f"Average Wake Time: {avg_wake_hh:02d}:{avg_wake_mm:02d}")

        # Difference metrics
        df['sleep_diff_min'] = df['actual_sleep_min'] - df['expected_sleep_min']
        df['wake_diff_min'] = df['actual_wake_min'] - df['expected_wake_min']
        avg_sleep_diff_h = int(df['sleep_diff_min'].mean()//60)
        avg_sleep_diff_m = int(df['sleep_diff_min'].mean()%60)
        avg_wake_diff_h = int(df['wake_diff_min'].mean()//60)
        avg_wake_diff_m = int(df['wake_diff_min'].mean()%60)
        st.write(f"Average Sleep Difference (Actual - Expected): {avg_sleep_diff_h}h {avg_sleep_diff_m}m")
        st.write(f"Average Wake Difference (Actual - Expected): {avg_wake_diff_h}h {avg_wake_diff_m}m")
