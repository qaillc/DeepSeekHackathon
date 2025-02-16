import streamlit as st
import random
import pandas as pd
import altair as alt

# Define the Markov chain states and transitions (same as before)
states = ["S0", "S1", "S2", "S3", "S4", "S5", "S6"]
transitions = {
    "S0": {"S1": 0.8, "S5": 0.2},
    "S1": {"S2": 0.7, "S5": 0.3},
    "S2": {"S3": 0.8, "S5": 0.2},
    "S3": {"S4": 0.7, "S1": 0.1, "S5": 0.2},
    "S4": {"S6": 0.9, "S5": 0.1},
    "S5": {"S0": 0.5, "S1": 0.5},
    "S6": {}  # Absorbing state
}

business_names = [
    "Automated Construction Robots",
    "AI for Simulating Autonomous Vehicle Scenarios",
    "Cybersecurity Defense Solutions",
    "Smart Factory Optimization",
    "AI-based Satellite Image Analysis",
    "Renewable Energy Yield Optimization",
    "AI-Enhanced Open Source Cybersecurity Tools",
    "Spatial Data Analytics for Retail",
    "AI for Real-time Supply Chain Adaptation",
    "AI Code Reviewer",
    "XAI for Healthcare Decision Support",
    "Supply Chain Optimization",
    "AI-Driven Code Generation for Custom Software",
    "Stablecoin-Backed Lending Platforms",
    "AI-Driven Early Detection Systems",
    "AI for Personalized Genomic Medicine",
    "Remote Patient Monitoring Platform",
    "Direct Pharmaceutical Access",
    "Automated Integration Platforms",
    "Efficient Retail Inventory Management"
]

# Business class now tracks completion iteration
class Business:
    def __init__(self, name):
        self.name = name
        self.state = "S0"  # Start at Market Discovery
        self.history = [self.state]
        self.completion_iteration = None  # Record when S6 is reached
    
    def update_state(self, iteration):
        if self.state == "S6":
            return
        options = transitions[self.state]
        next_state = random.choices(list(options.keys()), weights=list(options.values()))[0]
        self.state = next_state
        self.history.append(self.state)
        # Record completion iteration if reaching S6 for the first time
        if self.state == "S6" and self.completion_iteration is None:
            self.completion_iteration = iteration

def run_simulation(num_businesses, max_iterations):
    if num_businesses > len(business_names):
        names = business_names + [f"Business {i}" for i in range(len(business_names)+1, num_businesses+1)]
    else:
        names = business_names[:num_businesses]
    
    businesses = [Business(name) for name in names]
    timeline_data = []
    
    for i in range(max_iterations):
        # Record state distribution at iteration i
        state_counts = {state: 0 for state in states}
        for b in businesses:
            state_counts[b.state] += 1
        state_counts['iteration'] = i
        timeline_data.append(state_counts)
        
        # If all businesses have reached S6, we can exit early
        if all(b.state == "S6" for b in businesses):
            break
        
        # Update each business and record iteration for completion if applicable
        for b in businesses:
            if b.state != "S6":
                b.update_state(i)
    
    return businesses, pd.DataFrame(timeline_data)

# -------------------------------
# Streamlit UI
# -------------------------------
st.title("Business Creation Simulation via Markov Chain")
st.write("This simulation mimics the process of creating businesses. Adjust the parameters below and run the simulation.")

st.sidebar.header("Simulation Parameters")
num_businesses = st.sidebar.number_input("Number of Businesses", min_value=1, max_value=50, value=20)
max_iterations = st.sidebar.number_input("Max Iterations", min_value=10, max_value=500, value=100)

if st.sidebar.button("Run Simulation"):
    with st.spinner("Simulating business creation..."):
        businesses, timeline_df = run_simulation(num_businesses, max_iterations)
    st.success("Simulation Complete!")
    
    # Plot state distribution over iterations
    st.subheader("State Distribution Over Iterations")
    timeline_long = timeline_df.melt(id_vars=["iteration"], value_vars=states, 
                                     var_name="State", value_name="Count")
    chart = alt.Chart(timeline_long).mark_line(point=True).encode(
        x='iteration:Q',
        y='Count:Q',
        color='State:N'
    ).properties(width=700, height=400)
    st.altair_chart(chart, use_container_width=True)
    
    # Determine the order in which businesses reached S6 (if they did)
    completed = [b for b in businesses if b.completion_iteration is not None]
    not_completed = [b for b in businesses if b.completion_iteration is None]
    completed_sorted = sorted(completed, key=lambda b: b.completion_iteration)
    
    st.subheader("Order of Business Creation (Completion Order)")
    for i, b in enumerate(completed_sorted, start=1):
        st.write(f"{i}. {b.name} - Completed at iteration {b.completion_iteration}")
    if not_completed:
        st.write("The following businesses did not reach completion within the simulation:")
        for b in not_completed:
            st.write(f"- {b.name}")
    
    # Final state summary and detailed histories
    st.subheader("Final State of Each Business")
    final_states = {b.name: b.state for b in businesses}
    st.write(final_states)
    
    st.subheader("Detailed Simulation Histories")
    for b in businesses:
        st.write(f"**{b.name}**: {' -> '.join(b.history)}")
