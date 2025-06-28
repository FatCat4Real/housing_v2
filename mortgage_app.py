import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from test_cal_function import calculate_monthly_payment

def calculate_and_display(loan, years, interest_rates_str, minimum_monthly_payment, 
                         additional_payment, refinance, refinance_every_x_years, 
                         refinance_when_principal_hit, refinance_interest_will_increase):
    
    # Parse interest rates from string
    try:
        interest_rates = [float(x.strip()) for x in interest_rates_str.split(',')]
    except:
        return "❌ **Error:** Invalid interest rates format. Use comma-separated numbers (e.g., 2.3, 2.9, 3.5)", "", None, None
    
    try:
        # Calculate mortgage
        hist = calculate_monthly_payment(
            loan=loan,
            years=years,
            interest_rates_100=interest_rates,
            minimum_monthly_payment=minimum_monthly_payment,
            additional_payment=additional_payment,
            refinance=refinance,
            refinance_every_x_years=refinance_every_x_years,
            refinance_when_principal_hit=refinance_when_principal_hit,
            refinance_interest_will_increase=refinance_interest_will_increase
        )
        
        df = pd.DataFrame(hist)
        
        # Calculate summary statistics
        interest_sum = df['interest'].sum()
        total_sum = df['total'].sum()
        principal_sum = df['principal'].sum()
        years_taken = int(df.shape[0] / 12)
        months_left = (df.shape[0]) - (years_taken * 12)
        
        # Format beautiful summary with emojis and colors
        summary = f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; margin: 10px 0;">
        <h2 style="margin: 0 0 15px 0; text-align: center;">🏠 Mortgage Summary</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold;">${interest_sum:,.0f}</div>
                <div style="font-size: 14px; opacity: 0.9;">💰 Total Interest</div>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold;">${total_sum:,.0f}</div>
                <div style="font-size: 14px; opacity: 0.9;">📊 Total Payments</div>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold;">${principal_sum:,.0f}</div>
                <div style="font-size: 14px; opacity: 0.9;">🏦 Principal</div>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; text-align: center;">
                <div style="font-size: 24px; font-weight: bold;">{years_taken}y {months_left}m</div>
                <div style="font-size: 14px; opacity: 0.9;">⏰ Payoff Time</div>
            </div>
        </div>
        </div>
        """
        
        # Create payment breakdown chart
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Principal', 'Interest'],
            values=[principal_sum, interest_sum],
            hole=.3,
            marker_colors=['#1f77b4', '#ff7f0e']
        )])
        fig_pie.update_layout(
            title="Payment Breakdown",
            title_x=0.5,
            showlegend=True,
            height=400,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Create balance over time chart
        df_chart = df.copy()
        df_chart['payment_number'] = range(1, len(df_chart) + 1)
        
        fig_balance = go.Figure()
        fig_balance.add_trace(go.Scatter(
            x=df_chart['payment_number'],
            y=df_chart['loan_end'],
            mode='lines',
            name='Remaining Balance',
            line=dict(color='#1f77b4', width=3),
            fill='tonexty'
        ))
        fig_balance.update_layout(
            title="Loan Balance Over Time",
            title_x=0.5,
            xaxis_title="Payment Number",
            yaxis_title="Balance ($)",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(tickformat='$,.0f')
        )
        
        # Create detailed table for display
        df_display = df.copy()
        df_display['loan_start'] = df_display['loan_start'].round(0).astype(int)
        df_display['loan_end'] = df_display['loan_end'].round(0).astype(int)
        df_display['interest_rate_yearly'] = (df_display['interest_rate_yearly'] * 100).round(2)
        
        # Add month/year columns for better readability
        df_display['payment_number'] = range(1, len(df_display) + 1)
        df_display['year'] = ((df_display['payment_number'] - 1) // 12) + 1
        df_display['month'] = ((df_display['payment_number'] - 1) % 12) + 1
        
        # Reorder and rename columns for better display
        columns_order = ['payment_number', 'year', 'month', 'loan_start', 'interest_rate_yearly', 
                        'total', 'principal', 'interest', 'minimum_monthly_payment', 
                        'additional_payment', 'loan_end']
        df_display = df_display[columns_order]
        
        # Rename columns for better readability
        df_display.columns = ['Payment #', 'Year', 'Month', 'Starting Balance', 'Interest Rate %', 
                             'Total Payment', 'Principal', 'Interest', 'Min Payment', 
                             'Extra Payment', 'Ending Balance']
        
        return summary, df_display, fig_pie, fig_balance
        
    except Exception as e:
        return f"❌ **Error:** {str(e)}", "", None, None

# Custom CSS for mobile-friendly and beautiful design
css = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

.tab-nav {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 10px !important;
    padding: 5px !important;
}

.tab-nav button {
    background: transparent !important;
    color: white !important;
    border: none !important;
    border-radius: 5px !important;
    margin: 2px !important;
    transition: all 0.3s ease !important;
}

.tab-nav button:hover {
    background: rgba(255,255,255,0.2) !important;
}

.tab-nav button.selected {
    background: rgba(255,255,255,0.3) !important;
}

.input-container {
    background: #f8f9fa !important;
    border-radius: 15px !important;
    padding: 20px !important;
    margin: 10px 0 !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
}

@media (max-width: 768px) {
    .gradio-container {
        padding: 10px !important;
    }
    
    .input-container {
        padding: 15px !important;
        margin: 5px 0 !important;
    }
}

.output-container {
    margin-top: 20px !important;
    border-radius: 15px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
}
"""

# Create Gradio interface with beautiful mobile-friendly design
with gr.Blocks(title="🏠 Mortgage Calculator", css=css, theme=gr.themes.Soft()) as demo:
    
    # Header
    gr.HTML("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px; color: white;">
        <h1 style="margin: 0; font-size: 2.5em;">🏠 Mortgage Calculator</h1>
        <p style="margin: 10px 0 0 0; font-size: 1.1em; opacity: 0.9;">Calculate your mortgage payments with detailed analysis and beautiful visualizations</p>
    </div>
    """)
    
    with gr.Tabs():
        with gr.TabItem("📊 Calculator", elem_classes=["input-container"]):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 💰 Loan Details")
                    loan = gr.Number(
                        label="💵 Loan Amount ($)", 
                        value=4_300_000,
                        info="Total amount you want to borrow"
                    )
                    years = gr.Number(
                        label="📅 Loan Term (Years)", 
                        value=40, 
                        precision=0,
                        info="Number of years to repay the loan"
                    )
                    interest_rates = gr.Textbox(
                        label="📈 Interest Rates (%)", 
                        value="2.3, 2.9, 3.5, 4.495, 4.495, 5.495",
                        info="Comma-separated yearly rates (e.g., 2.3, 2.9, 3.5)",
                        lines=2
                    )
                    
                with gr.Column(scale=1):
                    gr.Markdown("### 💳 Payment Options")
                    minimum_monthly_payment = gr.Number(
                        label="💳 Minimum Monthly Payment ($)", 
                        value=0,
                        info="Set a minimum monthly payment amount"
                    )
                    additional_payment = gr.Number(
                        label="➕ Additional Payment ($)", 
                        value=0,
                        info="Extra amount to pay each month"
                    )
                    
                    gr.Markdown("### 🔄 Refinancing Options")
                    refinance = gr.Checkbox(
                        label="🔄 Enable Refinancing", 
                        value=False,
                        info="Allow loan refinancing"
                    )
                    
                    with gr.Column(visible=False) as refinance_options:
                        refinance_every_x_years = gr.Number(
                            label="📆 Refinance Every X Years", 
                            value=3, 
                            precision=0,
                            info="How often to refinance"
                        )
                        refinance_when_principal_hit = gr.Number(
                            label="🎯 Refinance When Principal Hits ($)", 
                            value=3_000_000,
                            info="Refinance when balance drops to this amount"
                        )
                        refinance_interest_will_increase = gr.Number(
                            label="📊 Interest Rate Increase After Refinance (%)", 
                            value=1.0,
                            info="How much interest rate increases after refinancing"
                        )
            
            # Show/hide refinancing options based on checkbox
            refinance.change(
                fn=lambda x: gr.update(visible=x),
                inputs=[refinance],
                outputs=[refinance_options]
            )
            
            calculate_btn = gr.Button(
                "🚀 Calculate Mortgage", 
                variant="primary", 
                size="lg",
                elem_classes=["calculate-button"]
            )
        
        with gr.TabItem("📈 Results", elem_classes=["output-container"]):
            summary_output = gr.HTML()
            
            with gr.Row():
                with gr.Column(scale=1):
                    pie_chart = gr.Plot(label="💰 Payment Breakdown")
                with gr.Column(scale=1):
                    balance_chart = gr.Plot(label="📉 Balance Over Time")
        
        with gr.TabItem("📋 Payment Schedule"):
            table_output = gr.Dataframe(
                label="📋 Detailed Payment Schedule", 
                interactive=False,
                wrap=True
            )
    
    # Footer
    gr.HTML("""
    <div style="text-align: center; padding: 15px; margin-top: 20px; opacity: 0.7; font-size: 0.9em;">
        <p>💡 Tip: Use the tabs above to navigate between calculator inputs, visual results, and detailed payment schedule</p>
    </div>
    """)
    
    calculate_btn.click(
        fn=calculate_and_display,
        inputs=[loan, years, interest_rates, minimum_monthly_payment, additional_payment,
                refinance, refinance_every_x_years, refinance_when_principal_hit, 
                refinance_interest_will_increase],
        outputs=[summary_output, table_output, pie_chart, balance_chart]
    )

if __name__ == "__main__":
    demo.launch(share=False, server_name="0.0.0.0", server_port=7860)