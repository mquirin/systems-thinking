import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st


@dataclass
class Constant:
    level: float

    def value(self, t):
        return self.level


@dataclass
class CosinePos:
    min: float
    max: float

    # t = time between 0 (start) and 1 (end)
    def value(self, t):
        factor = 0.5 + 0.5 * math.cos(math.tau * t)
        return self.min + (self.max - self.min) * factor


# Configuration
temp_goal = 18
temp_outisde_baseline = 10

temp_init = st.number_input("Initial temperature", value=10.0, step=0.5)
max_heat = st.number_input("Max heating output", value=0.7, step=0.05)
heat_per_diff = st.number_input("Heating per difference", value=0.25, step=0.05)
leak_per_diff = st.number_input(
    "Relative leakage to outside temperature", value=0.05, step=0.01
)

periodic_outside_temp = st.toggle("Periodic outside temperature")


def simulation():
    # stock: temperature
    temperature = temp_init

    # input: outside temperature
    if periodic_outside_temp:
        temp_outisde = CosinePos(min=0, max=temp_outisde_baseline)
    else:
        temp_outisde = Constant(level=temp_outisde_baseline)

    # flow: heat from furnace
    # rate is relative to distance to goal temperature (e.g. bimetallic thermostat)
    # only positive, has a max value
    def flow_furnace(t):
        rate = (temp_goal - temperature) * heat_per_diff
        return np.clip(0, rate, max_heat)

    # flow: thermal conduction
    # higher if difference in temperature is higher
    # has only a leakage / isolation factor
    def flow_conduction(t):
        diff_to_outside = temp_outisde.value(t) - temperature
        return diff_to_outside * leak_per_diff

    log = []
    steps = 50
    for step in range(steps):
        t = step / steps
        flow_furnace_ = flow_furnace(t)
        flow_conduction_ = flow_conduction(t)
        log.append(
            {
                "temperature": temperature,
                "outside": temp_outisde.value(t),
                "goal": temp_goal,
                "flow_furnace": flow_furnace_,
                "flow_conduction": flow_conduction_,
            }
        )
        temperature = temperature + flow_furnace_ + flow_conduction_
    df = pd.DataFrame(log)
    return df


df = simulation()

st.line_chart(df[["temperature", "outside", "goal"]])
st.line_chart(df[["flow_furnace", "flow_conduction"]])
df
