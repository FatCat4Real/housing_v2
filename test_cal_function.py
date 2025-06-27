import pandas as pd

def calculate_monthly_payment(
    loan: float = 4_300_000,
    years: int = 40,
    interest_rates_100: list[float] = [2.3, 2.9, 3.5, 4.495, 4.495, 5.495],
    minimum_monthly_payment: float = 0,
    additional_payment: float = 0
) -> dict:

    hist = {
        'loan_start':[], 
        'total':[], 
        'principal':[], 
        'interest':[], 
        'minimum_monthly_payment':[], 
        'additional_payment':[], 
        'loan_end':[]
    }

    year_left = years
    months_left = years * 12
    principal_left = loan

    for i in range(years):
        if i <= len(interest_rates_100) - 1:
            interest_rate = interest_rates_100[i] / 100
        else:
            interest_rate = interest_rates_100[-1] / 100

        interest_rate_monthly = interest_rate / 12
        
        # Principal * (1 + r)^n = Payment * ((1+r)^n - 1) / r
        # Payment = Principal * (1 + r)^n * r / (1+r)^n - 1
        nomi = (1 + interest_rate_monthly) ** months_left
        denomi = nomi - 1
        required_monthly_payment = (principal_left * interest_rate_monthly * nomi) / denomi

        for j in range(12):
            total = max(required_monthly_payment, minimum_monthly_payment)
            total += additional_payment

            interest = interest_rate_monthly * principal_left
            principal = total - interest
            
            hist['loan_start'].append(principal_left)
            hist['total'].append(total)
            hist['principal'].append(principal)
            hist['interest'].append(interest)
            hist['minimum_monthly_payment'].append(minimum_monthly_payment)
            hist['additional_payment'].append(additional_payment)
            
            principal_left -= total - interest
            
            hist['loan_end'].append(principal_left)

            months_left -= 1
            if principal_left <= 0:
                break
    
        year_left -= 1
        if principal_left <= 0:
            break

    return hist


df = pd.DataFrame(
    calculate_monthly_payment(
        # minimum_monthly_payment=15_000, additional_payment=5_000
        minimum_monthly_payment=20_000, additional_payment=0
    )
)

print(df['interest'].sum())
print(df['interest'].sum() + df['principal'].sum())
print(df['total'].sum())
years_taken = int(df.shape[0] / 12)
months_left = (df.shape[0]) - (years_taken * 12)
print(f'{years_taken}y {months_left}m')