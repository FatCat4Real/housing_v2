import reflex as rx
import pandas as pd


def calculate_monthly_payment(
    loan: float = 4_300_000,
    years: int = 40,
    interest_rates_100: list[float] = [2.3, 2.9, 3.5, 4.495, 4.495, 5.495],
    minimum_monthly_payment: float = 0,
    additional_payment: float = 0,
    refinance: bool = False,
    refinance_every_x_years: int = 3,
    refinance_when_principal_hit: float = 3_000_000,
    refinance_interest_will_increase: float = 1.0
) -> dict:
    
    assert interest_rates_100 != [], "interest_rates_100 must not be empty"
    assert all([i > 0 for i in interest_rates_100]), "All interest rates must be greater than 0"

    if refinance:
        assert refinance_every_x_years > 0, "refinance cycle must be greater than 0"
        assert len(interest_rates_100) >= refinance_every_x_years, "more rates than refinance cycle is needed"
        
        # extend interest rate list to match loan years
        interest_rates_100 = interest_rates_100[:refinance_every_x_years] * (int(years/refinance_every_x_years) + 1)
        interest_rates_100 = interest_rates_100[:years]

    hist = {
        'loan_start':[], 
        'interest_rate_yearly':[],
        'total':[], 
        'principal':[], 
        'interest':[], 
        'minimum_monthly_payment':[], 
        'additional_payment':[], 
        'loan_end':[]
    }

    months_left = years * 12
    principal_left = loan
    interest_rate_increase = 0

    for i in range(years):
        if i <= len(interest_rates_100) - 1:
            interest_rate = (interest_rates_100[i] + interest_rate_increase) / 100
        else:
            interest_rate = (interest_rates_100[-1] + interest_rate_increase) / 100

        interest_rate_monthly = interest_rate / 12
        
        # Principal * (1 + r)^n = Payment * ((1+r)^n - 1) / r
        # Payment = Principal * (1 + r)^n * r / (1+r)^n - 1
        nomi = (1 + interest_rate_monthly) ** months_left
        denomi = nomi - 1
        required_monthly_payment = (principal_left * interest_rate_monthly * nomi) / denomi

        for j in range(12):
            interest = interest_rate_monthly * principal_left
            interest =  int(interest)
            
            if required_monthly_payment >= principal_left:
                total = int(principal_left)
                minimum_monthly_payment = 0
                additional_payment = 0
            else:
                if minimum_monthly_payment >= principal_left:
                    total = int(principal_left)
                    minimum_monthly_payment = int(principal_left)
                    additional_payment = 0
                else:
                    total = max(required_monthly_payment, minimum_monthly_payment)
                    total = int(total)
                    if total + additional_payment >= principal_left:
                        additional_payment = principal_left - total
                        additional_payment = int(additional_payment)
                    else:
                        total += additional_payment

            principal = total - interest
            
            hist['loan_start'].append(principal_left)
            hist['interest_rate_yearly'].append(interest_rate)
            hist['total'].append(total)
            hist['principal'].append(principal)
            hist['interest'].append(interest)
            hist['minimum_monthly_payment'].append(minimum_monthly_payment)
            hist['additional_payment'].append(additional_payment)
            
            principal_left -= principal
            
            hist['loan_end'].append(principal_left)

            months_left -= 1
            if principal_left <= 0:
                break
        
        if refinance and (i+1) % refinance_every_x_years == 0 and principal_left <= refinance_when_principal_hit:
            interest_rate_increase += refinance_interest_will_increase
            
        if principal_left <= 0:
            break

    return hist


class State(rx.State):
    # Input parameters
    loan: str = "4300000"
    years: str = "40"
    interest_rates_str: str = "2.3,2.9,3.5,4.495,4.495,5.495"
    minimum_monthly_payment: str = "0"
    additional_payment: str = "0"
    refinance: bool = False
    refinance_every_x_years: str = "3"
    refinance_when_principal_hit: str = "3000000"
    refinance_interest_will_increase: str = "1.0"
    
    # Results
    total_interest: float = 0
    total_payment: float = 0
    loan_duration_years: int = 0
    loan_duration_months: int = 0
    
    def calculate(self):
        try:
            # Parse interest rates
            interest_rates = [float(rate.strip()) for rate in self.interest_rates_str.split(',') if rate.strip()]
            
            # Calculate mortgage
            result = calculate_monthly_payment(
                loan=float(self.loan),
                years=int(self.years),
                interest_rates_100=interest_rates,
                minimum_monthly_payment=float(self.minimum_monthly_payment),
                additional_payment=float(self.additional_payment),
                refinance=self.refinance,
                refinance_every_x_years=int(self.refinance_every_x_years),
                refinance_when_principal_hit=float(self.refinance_when_principal_hit),
                refinance_interest_will_increase=float(self.refinance_interest_will_increase)
            )
            
            # Calculate summary statistics
            df = pd.DataFrame(result)
            self.total_interest = float(df['interest'].sum())
            self.total_payment = float(df['total'].sum())
            
            # Calculate loan duration
            total_months = len(df)
            self.loan_duration_years = total_months // 12
            self.loan_duration_months = total_months % 12
            
        except Exception as e:
            print(f"Calculation error: {e}")


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Mortgage Calculator", size="9", margin_bottom="2rem"),
            
            # Input Parameters
            rx.hstack(
                rx.vstack(
                    rx.heading("Loan Parameters", size="6"),
                    rx.hstack(
                        rx.text("Loan Amount:"),
                        rx.input(
                            value=State.loan,
                            on_change=State.set_loan,
                            type="number"
                        ),
                        align="center"
                    ),
                    rx.hstack(
                        rx.text("Loan Term (years):"),
                        rx.input(
                            value=State.years,
                            on_change=State.set_years,
                            type="number"
                        ),
                        align="center"
                    ),
                    rx.hstack(
                        rx.text("Interest Rates (%):"),
                        rx.input(
                            value=State.interest_rates_str,
                            on_change=State.set_interest_rates_str,
                            placeholder="2.3,2.9,3.5,4.495"
                        ),
                        align="center"
                    ),
                    spacing="4",
                    align="start",
                    width="50%"
                ),
                
                rx.vstack(
                    rx.heading("Payment Parameters", size="6"),
                    rx.hstack(
                        rx.text("Min Monthly Payment:"),
                        rx.input(
                            value=State.minimum_monthly_payment,
                            on_change=State.set_minimum_monthly_payment,
                            type="number"
                        ),
                        align="center"
                    ),
                    rx.hstack(
                        rx.text("Additional Payment:"),
                        rx.input(
                            value=State.additional_payment,
                            on_change=State.set_additional_payment,
                            type="number"
                        ),
                        align="center"
                    ),
                    spacing="4",
                    align="start",
                    width="50%"
                ),
                spacing="8",
                align="start"
            ),
            
            # Refinance Parameters
            rx.vstack(
                rx.heading("Refinance Options", size="6"),
                rx.hstack(
                    rx.checkbox(
                        "Enable Refinancing",
                        checked=State.refinance,
                        on_change=State.set_refinance
                    ),
                    align="center"
                ),
                rx.cond(
                    State.refinance,
                    rx.hstack(
                        rx.vstack(
                            rx.hstack(
                                rx.text("Refinance Every (years):"),
                                rx.input(
                                    value=State.refinance_every_x_years,
                                    on_change=State.set_refinance_every_x_years,
                                    type="number"
                                ),
                                align="center"
                            ),
                            rx.hstack(
                                rx.text("Refinance When Principal Hits:"),
                                rx.input(
                                    value=State.refinance_when_principal_hit,
                                    on_change=State.set_refinance_when_principal_hit,
                                    type="number"
                                ),
                                align="center"
                            ),
                            spacing="4"
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Interest Rate Increase (%):"),
                                rx.input(
                                    value=State.refinance_interest_will_increase,
                                    on_change=State.set_refinance_interest_will_increase,
                                    type="number"
                                ),
                                align="center"
                            ),
                            spacing="4"
                        ),
                        spacing="8"
                    )
                ),
                spacing="4",
                align="start"
            ),
            
            # Calculate Button
            rx.button(
                "Calculate Mortgage",
                on_click=State.calculate,
                size="4",
                margin="2rem 0"
            ),
            
            # Results Summary
            rx.cond(
                State.total_payment > 0,
                rx.vstack(
                    rx.heading("Mortgage Summary", size="7"),
                    rx.hstack(
                        rx.card(
                            rx.vstack(
                                rx.text("Total Interest", weight="bold"),
                                rx.text(f"${State.total_interest:,.0f}", size="8", color="red")
                            ),
                            padding="4"
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("Total Payment", weight="bold"),
                                rx.text(f"${State.total_payment:,.0f}", size="8", color="blue")
                            ),
                            padding="4"
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("Loan Duration", weight="bold"),
                                rx.text(f"{State.loan_duration_years}y {State.loan_duration_months}m", size="8", color="green")
                            ),
                            padding="4"
                        ),
                        spacing="4"
                    ),
                    spacing="4",
                    margin="2rem 0"
                )
            ),
            
            spacing="8",
            align="center",
            min_height="100vh",
            padding="8"
        ),
        max_width="1200px",
        margin="0 auto"
    )


app = rx.App()
app.add_page(index)
