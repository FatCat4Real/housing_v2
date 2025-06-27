import pandas as pd
from test_cal_function import calculate_monthly_payment

def demonstrate_overpayment_bug():
    """Demonstrate the overpayment bug with a simple example"""
    print("=== DEMONSTRATING OVERPAYMENT BUG ===")
    print()
    
    # Small loan with high minimum payment to trigger the bug quickly
    result = calculate_monthly_payment(
        loan=10000,
        years=1,
        interest_rates_100=[5.0],
        minimum_monthly_payment=12000,  # Much higher than required
        additional_payment=0
    )
    
    df = pd.DataFrame(result)
    
    print("Loan Parameters:")
    print(f"  Initial loan: $10,000")
    print(f"  Interest rate: 5.0%")
    print(f"  Minimum payment: $12,000")
    print()
    
    print("Payment Details:")
    for i, row in df.iterrows():
        print(f"Payment {i+1}:")
        print(f"  Starting balance: ${row['loan_start']:,.2f}")
        print(f"  Interest:         ${row['interest']:,.2f}")
        print(f"  Principal:        ${row['principal']:,.2f}")
        print(f"  Total payment:    ${row['total']:,.2f}")
        print(f"  Ending balance:   ${row['loan_end']:,.2f}")
        
        # Highlight the bug
        if row['principal'] > row['loan_start']:
            print(f"  ⚠️  BUG: Principal payment (${row['principal']:,.2f}) exceeds starting balance (${row['loan_start']:,.2f})")
        
        if row['loan_end'] < 0:
            print(f"  ⚠️  BUG: Negative ending balance: ${row['loan_end']:,.2f}")
        
        print()

def demonstrate_consistency_bug():
    """Demonstrate mathematical inconsistency"""
    print("=== DEMONSTRATING MATHEMATICAL INCONSISTENCY ===")
    print()
    
    result = calculate_monthly_payment(
        loan=50000,
        years=2,
        interest_rates_100=[6.0],
        minimum_monthly_payment=30000,  # High payment
        additional_payment=0
    )
    
    df = pd.DataFrame(result)
    
    print("Checking mathematical consistency:")
    print()
    
    for i, row in df.iterrows():
        calculated_principal = row['total'] - row['interest']
        recorded_principal = row['principal']
        
        print(f"Payment {i+1}:")
        print(f"  Starting balance: ${row['loan_start']:,.2f}")
        print(f"  Total payment:    ${row['total']:,.2f}")
        print(f"  Interest:         ${row['interest']:,.2f}")
        print(f"  Calculated principal: ${calculated_principal:,.2f}")
        print(f"  Recorded principal:   ${recorded_principal:,.2f}")
        
        if abs(calculated_principal - recorded_principal) > 0.01:
            print(f"  ⚠️  BUG: Principal calculation inconsistency!")
        
        # Check if principal exceeds starting balance
        if recorded_principal > row['loan_start']:
            print(f"  ⚠️  BUG: Principal (${recorded_principal:,.2f}) > Starting balance (${row['loan_start']:,.2f})")
            print(f"       This means we're paying more principal than we owe!")
        
        print(f"  Ending balance:   ${row['loan_end']:,.2f}")
        print()

if __name__ == "__main__":
    demonstrate_overpayment_bug()
    demonstrate_consistency_bug() 