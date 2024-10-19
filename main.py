import math
import streamlit as st
import numpy as np
import pandas as pd

# stock: temperature in a room
# flow in: heat from furnace
#   regulated relative to diff(goal & current temp)
#   only positive, limited by maximum heating capacity
# flow out: heat to outside
#   regulated by difference between inside and outside temperature

temp_goal = 18
temp_outisde_baseline = 10
temp_outisde = temp_outisde_baseline
# temp_init = 10

temp_init = st.number_input("Initial temperature", value=10., step=0.5)
max_heat = st.number_input("Max heating output", value=0.7, step=0.05)
heat_per_diff = st.number_input("Heating per difference", value=0.25, step=0.05)
leak_per_diff = st.number_input("Relative leakage to outside temp", value=0.05, step=0.01)

periodic_outside_temp = st.toggle("Periodic outside temp")

def sim():
    temp = temp_init
    data = []
    temp_outisde = temp_outisde_baseline

    # period
    for t in range(50):
        if periodic_outside_temp:
            factor = .5 + .5 * math.cos(2 * 3.14159 * t/50)
            temp_outisde = temp_outisde_baseline * factor

        def flow_in():
            diff = max(0,temp_goal - temp)
            return min(max_heat,diff * heat_per_diff)
        def flow_out():
            diff = temp_outisde - temp
            return diff * leak_per_diff
        flow_in_ = flow_in()
        flow_out_ = flow_out()
        data.append({'temp':temp, 'outside': temp_outisde, 'goal': temp_goal, 'flow_in': flow_in_,'flow_out':flow_out_ })
        temp = temp + flow_in() + flow_out()
    df = pd.DataFrame(data)
    return df


df = sim()

st.line_chart(df[["temp", "outside","goal"]])
st.line_chart(df[["flow_in", "flow_out"]])
df
