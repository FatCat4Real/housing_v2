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
            principal = required_monthly_payment - interest
            minimum_added = max(required_monthly_payment - minimum_monthly_payment, 0)
            addition_added = additional_payment

            if principal >= principal_left:
                principal = principal_left
                minimum_added = 0
                addition_added = 0
            elif principal + minimum_added >= principal_left:
                minimum_added = principal_left - principal
                addition_added = 0
            elif principal + minimum_added + addition_added >= principal_left:
                addition_added = additional_payment - (principal + minimum_added)

            # total = max(required_monthly_payment, minimum_monthly_payment) + additional_payment
            # principal = principal + minimum_added - interest
            
            hist['loan_start'].append(principal_left)
            hist['interest_rate_yearly'].append(interest_rate)
            # hist['total'].append(total)
            hist['total'].append(principal + minimum_added + addition_added + interest)
            hist['principal'].append(principal)
            hist['interest'].append(interest)
            # hist['minimum_monthly_payment'].append(minimum_monthly_payment)
            hist['minimum_monthly_payment'].append(minimum_added)
            hist['additional_payment'].append(addition_added)
            
            principal_left -= (principal + minimum_added + addition_added)
            
            hist['loan_end'].append(principal_left)

            months_left -= 1
            if principal_left <= 0:
                break
        
        if refinance and (i+1) % refinance_every_x_years == 0 and principal_left <= refinance_when_principal_hit:
            interest_rate_increase += refinance_interest_will_increase
            
        if principal_left <= 0:
            break

    return hist

if __name__ == '__main__':
    df = pd.DataFrame(
        # calculate_monthly_payment(
        #     interest_rates_100=[4],
        #     minimum_monthly_payment=15_000, 
        #     additional_payment=5_000, 
        #     refinance=False,
        #     refinance_every_x_years=3,
        #     refinance_when_principal_hit=3_000_000,
        #     refinance_interest_will_increase=0.5
            
            
        #     # minimum_monthly_payment=20_000, additional_payment=0, refinance=True, 
        # )
        # calculate_monthly_payment(minimum_monthly_payment=20_000,additional_payment=0)
        calculate_monthly_payment(minimum_monthly_payment=15_000,additional_payment=5_000)
    )

    print(df['interest'].sum())
    print(df['interest'].sum() + df['principal'].sum())
    print(df['total'].sum())
    years_taken = int(df.shape[0] / 12)
    months_left = (df.shape[0]) - (years_taken * 12)
    print(f'{years_taken}y {months_left}m')
    df.to_csv('data.csv')