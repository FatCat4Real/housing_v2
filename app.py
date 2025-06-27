import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from test_cal_function import calculate_monthly_payment

st.set_page_config(
    page_title="Mortgage Calculator",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Mortgage Payment Calculator")
st.markdown("Adjust the parameters below to see how they affect your mortgage payments")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Parameters")
    
    loan = st.number_input(
        "Loan Amount", 
        min_value=100000.0, 
        max_value=50000000.0, 
        value=4300000.0, 
        step=50000.0,
        format="%.0f"
    )
    
    years = st.slider(
        "Loan Term (Years)", 
        min_value=5, 
        max_value=50, 
        value=40
    )
    
    st.subheader("Interest Rates (%)")
    interest_rates_text = st.text_input(
        "Interest Rates (comma-separated)", 
        value="2.3, 2.9, 3.5, 4.495, 4.495, 5.495"
    )
    
    try:
        interest_rates_100 = [float(x.strip()) for x in interest_rates_text.split(",")]
    except:
        st.error("Please enter valid interest rates separated by commas")
        interest_rates_100 = [4.0]
    
    minimum_monthly_payment = st.number_input(
        "Minimum Monthly Payment", 
        min_value=0.0, 
        value=0.0, 
        step=1000.0,
        format="%.0f"
    )
    
    additional_payment = st.number_input(
        "Additional Monthly Payment", 
        min_value=0.0, 
        value=0.0, 
        step=1000.0,
        format="%.0f"
    )
    
    st.subheader("Refinance Options")
    refinance = st.checkbox("Enable Refinancing", value=False)
    
    if refinance:
        refinance_every_x_years = st.slider(
            "Refinance Every X Years", 
            min_value=1, 
            max_value=10, 
            value=3
        )
        
        refinance_when_principal_hit = st.number_input(
            "Refinance When Principal Hits", 
            min_value=0.0, 
            value=3000000.0, 
            step=100000.0,
            format="%.0f"
        )
        
        refinance_interest_will_increase = st.number_input(
            "Interest Rate Increase After Refinance (%)", 
            min_value=0.0, 
            value=1.0, 
            step=0.1
        )
    else:
        refinance_every_x_years = 3
        refinance_when_principal_hit = 3000000.0
        refinance_interest_will_increase = 1.0

with col2:
    st.header("Mortgage Summary")
    
    try:
        result = calculate_monthly_payment(
            loan=loan,
            years=years,
            interest_rates_100=interest_rates_100,
            minimum_monthly_payment=minimum_monthly_payment,
            additional_payment=additional_payment,
            refinance=refinance,
            refinance_every_x_years=refinance_every_x_years,
            refinance_when_principal_hit=refinance_when_principal_hit,
            refinance_interest_will_increase=refinance_interest_will_increase
        )
        
        df = pd.DataFrame(result)
        
        interest_sum = df['interest'].sum()
        total_sum = df['total'].sum()
        years_taken = int(df.shape[0] / 12)
        months_left = df.shape[0] - (years_taken * 12)
        
        col2_1, col2_2, col2_3, col2_4 = st.columns(4)
        
        with col2_1:
            st.metric("Total Interest", f"฿{interest_sum:,.0f}")
        
        with col2_2:
            st.metric("Total Payments", f"฿{total_sum:,.0f}")
        
        with col2_3:
            st.metric("Years to Pay Off", f"{years_taken}y {months_left}m")
        
        with col2_4:
            st.metric("Principal", f"฿{df['principal'].sum():,.0f}")
        
        st.subheader("Payment Schedule Visualization")
        
        df_monthly = df.copy()
        df_monthly['month'] = range(1, len(df_monthly) + 1)
        df_monthly['year'] = ((df_monthly['month'] - 1) // 12) + 1
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_monthly['month'], 
            y=df_monthly['principal'],
            mode='lines',
            name='Principal Payment',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=df_monthly['month'], 
            y=df_monthly['interest'],
            mode='lines',
            name='Interest Payment',
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title="Monthly Principal vs Interest Payments",
            xaxis_title="Month",
            yaxis_title="Payment Amount (฿)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_monthly['month'], 
            y=df_monthly['loan_end'],
            mode='lines',
            name='Remaining Balance',
            line=dict(color='green'),
            fill='tonexty'
        ))
        
        fig2.update_layout(
            title="Remaining Loan Balance Over Time",
            xaxis_title="Month",
            yaxis_title="Balance (฿)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("Payment Details")
        
        df_display = df_monthly[['month', 'year', 'loan_start', 'total', 'principal', 'interest', 'loan_end']].copy()
        df_display.columns = ['Month', 'Year', 'Starting Balance', 'Total Payment', 'Principal', 'Interest', 'Ending Balance']
        
        for col in ['Starting Balance', 'Total Payment', 'Principal', 'Interest', 'Ending Balance']:
            df_display[col] = df_display[col].apply(lambda x: f"฿{x:,.0f}")
        
        st.dataframe(df_display, use_container_width=True, height=400)
        
    except Exception as e:
        st.error(f"Error calculating mortgage: {str(e)}")
        st.info("Please check your input parameters and try again.")