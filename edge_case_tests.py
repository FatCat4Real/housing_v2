import pandas as pd
from test_cal_function import calculate_monthly_payment

def test_division_by_zero_edge_case():
    """Test potential division by zero when months_left becomes 0"""
    print("=== TESTING DIVISION BY ZERO EDGE CASE ===")
    print()
    
    try:
        # Very short term that might cause months_left to reach 0 during calculation
        result = calculate_monthly_payment(
            loan=1000,
            years=1,
            interest_rates_100=[0.0],  # Zero interest to isolate the issue
            minimum_monthly_payment=0,
            additional_payment=0
        )
        print("✓ No division by zero error occurred")
    except ZeroDivisionError as e:
        print(f"✗ Division by zero error: {e}")
    except Exception as e:
        print(f"✗ Other error: {e}")

def test_zero_interest_rate():
    """Test behavior with zero interest rate"""
    print("\n=== TESTING ZERO INTEREST RATE ===")
    print()
    
    result = calculate_monthly_payment(
        loan=12000,
        years=1,
        interest_rates_100=[0.0],  # Zero interest
        minimum_monthly_payment=0,
        additional_payment=0
    )
    
    df = pd.DataFrame(result)
    print(f"With zero interest rate:")
    print(f"  Total interest paid: ${df['interest'].sum():,.2f}")
    print(f"  Should be zero: {df['interest'].sum() == 0}")
    print(f"  Loan paid off in: {len(df)} payments")
    print(f"  Each payment should be: ${12000/12:,.2f}")
    print(f"  Average payment: ${df['total'].mean():,.2f}")

def test_very_high_interest_rate():
    """Test behavior with extremely high interest rate"""
    print("\n=== TESTING VERY HIGH INTEREST RATE ===")
    print()
    
    result = calculate_monthly_payment(
        loan=100000,
        years=30,
        interest_rates_100=[50.0],  # 50% annual interest
        minimum_monthly_payment=0,
        additional_payment=0
    )
    
    df = pd.DataFrame(result)
    print(f"With 50% interest rate:")
    print(f"  Required monthly payment: ${df.iloc[0]['total']:,.2f}")
    print(f"  First month interest: ${df.iloc[0]['interest']:,.2f}")
    print(f"  Principal in first payment: ${df.iloc[0]['principal']:,.2f}")
    
    # Check if loan grows instead of shrinking
    if df.iloc[0]['principal'] < 0:
        print("⚠️  BUG: Negative principal payment - loan is growing!")

def test_negative_payment_amounts():
    """Test what happens with negative additional payments (not realistic but edge case)"""
    print("\n=== TESTING EDGE CASE SCENARIOS ===")
    print()
    
    # Test very small loan
    result = calculate_monthly_payment(
        loan=1,  # $1 loan
        years=1,
        interest_rates_100=[5.0],
        minimum_monthly_payment=0,
        additional_payment=0
    )
    
    df = pd.DataFrame(result)
    print(f"$1 loan results:")
    print(f"  Payment required: ${df.iloc[0]['total']:,.4f}")
    print(f"  Interest: ${df.iloc[0]['interest']:,.4f}")
    print(f"  Principal: ${df.iloc[0]['principal']:,.4f}")

def test_months_left_consistency():
    """Test that months_left is calculated correctly throughout"""
    print("\n=== TESTING MONTHS_LEFT CALCULATION ===")
    print()
    
    # This test checks if the function properly tracks months_left
    # The bug might be in how months_left is used in the annuity formula
    
    result = calculate_monthly_payment(
        loan=100000,
        years=2,  # 24 months
        interest_rates_100=[6.0],
        minimum_monthly_payment=0,
        additional_payment=0
    )
    
    df = pd.DataFrame(result)
    print(f"2-year loan analysis:")
    print(f"  Total payments made: {len(df)}")
    print(f"  Should be close to 24 months")
    
    # The issue might be that months_left is calculated based on total term
    # but should be recalculated based on remaining balance after each payment
    print(f"  Final balance: ${df.iloc[-1]['loan_end']:,.2f}")
    print(f"  Total paid: ${df['total'].sum():,.2f}")

def test_interest_rate_array_bounds():
    """Test what happens when we run out of interest rates in the array"""
    print("\n=== TESTING INTEREST RATE ARRAY BOUNDS ===")
    print()
    
    result = calculate_monthly_payment(
        loan=100000,
        years=10,  # 10 years
        interest_rates_100=[3.0, 4.0],  # Only 2 rates for 10 years
        minimum_monthly_payment=0,
        additional_payment=0
    )
    
    df = pd.DataFrame(result)
    
    # Check if the function properly uses the last rate for remaining years
    print(f"10-year loan with only 2 interest rates:")
    print(f"  Should use 4.0% for years 3-10")
    print(f"  Total payments: {len(df)}")
    print(f"  Final balance: ${df.iloc[-1]['loan_end']:,.2f}")

if __name__ == "__main__":
    test_division_by_zero_edge_case()
    test_zero_interest_rate()
    test_very_high_interest_rate()
    test_negative_payment_amounts()
    test_months_left_consistency()
    test_interest_rate_array_bounds() 