import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime, date, time
from page1 import page1
from page2 import page2


st.title("My Sleep Tracker")

page = st.sidebar.selectbox("Select Page", ["Table / Input", "Analysis / Stats"])

if page == "Table / Input":
    page1()
elif page == "Analysis / Stats":
    page2()



# if __name__ == "__main__":
#     main()

