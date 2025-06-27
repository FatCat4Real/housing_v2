import pandas as pd
from test_cal_function import calculate_monthly_payment


class TestCalculateMonthlyPayment:
    
    def test_overpayment_on_final_payment(self):
        """Test that final payment doesn't overpay when remaining balance is small"""
        # Use a very small loan that should be paid off quickly
        result = calculate_monthly_payment(
            loan=10000,
            years=1,
            interest_rates_100=[5.0],
            minimum_monthly_payment=12000,  # Higher than required payment
            additional_payment=0
        )
        
        df = pd.DataFrame(result)
        
        # Check if any payment results in negative remaining balance
        negative_balances = df[df['loan_end'] < 0]
        if not negative_balances.empty:
            print(f"Found negative balances: {negative_balances['loan_end'].values}")
            
        # The last payment should not result in overpayment
        last_row = df.iloc[-1]
        assert last_row['loan_end'] >= -0.01, f"Final balance is negative: {last_row['loan_end']}"
        
        # Principal payment shouldn't exceed loan_start for any payment
        overpayments = df[df['principal'] > df['loan_start']]
        assert overpayments.empty, f"Found overpayments: {overpayments[['loan_start', 'principal']].values}"

    def test_excessive_minimum_payment(self):
        """Test behavior with minimum payment much higher than required"""
        result = calculate_monthly_payment(
            loan=100000,
            years=30,
            interest_rates_100=[3.0],
            minimum_monthly_payment=50000,  # Extremely high minimum payment
            additional_payment=0
        )
        
        df = pd.DataFrame(result)
        
        # Should pay off loan very quickly
        assert len(df) <= 3, f"Loan should be paid off in 3 payments or less, but took {len(df)}"
        
        # Check for negative balances
        negative_balances = df[df['loan_end'] < 0]
        assert negative_balances.empty, f"Found negative balances: {negative_balances['loan_end'].values}"

    def test_interest_on_negative_balance(self):
        """Test that interest calculation doesn't produce weird results on negative balance"""
        result = calculate_monthly_payment(
            loan=5000,
            years=1,
            interest_rates_100=[12.0],
            minimum_monthly_payment=6000,  # Very high payment
            additional_payment=0
        )
        
        df = pd.DataFrame(result)
        
        # All interest payments should be non-negative
        negative_interest = df[df['interest'] < 0]
        assert negative_interest.empty, f"Found negative interest: {negative_interest['interest'].values}"
        
        # Interest should be reasonable (not calculated on negative balance)
        for idx, row in df.iterrows():
            expected_max_interest = row['loan_start'] * (12.0/100/12)  # Monthly rate
            assert row['interest'] <= expected_max_interest + 0.01, \
                f"Interest {row['interest']} exceeds maximum possible {expected_max_interest}"

    def test_data_recording_after_loan_paid(self):
        """Test that no extra data is recorded after loan is fully paid"""
        result = calculate_monthly_payment(
            loan=1000,
            years=5,
            interest_rates_100=[6.0],
            minimum_monthly_payment=5000,  # Very high payment to pay off in 1 payment
            additional_payment=0
        )
        
        df = pd.DataFrame(result)
        
        # Should only have 1 payment record
        assert len(df) == 1, f"Expected 1 payment, but found {len(df)}"
        
        # That payment should result in loan_end <= 0
        assert df.iloc[0]['loan_end'] <= 0.01, f"Loan not fully paid: {df.iloc[0]['loan_end']}"

    def test_consistency_of_totals(self):
        """Test that the sum of principal and interest equals total payments"""
        result = calculate_monthly_payment(
            loan=200000,
            years=15,
            interest_rates_100=[4.0, 4.5, 5.0],
            minimum_monthly_payment=0,
            additional_payment=1000
        )
        
        df = pd.DataFrame(result)
        
        # Sum of principal and interest should equal sum of total payments
        total_principal = df['principal'].sum()
        total_interest = df['interest'].sum()
        total_payments = df['total'].sum()
        
        assert abs(total_principal + total_interest - total_payments) < 0.01, \
            f"Principal ({total_principal}) + Interest ({total_interest}) != Total ({total_payments})"

    def test_principal_reduction_consistency(self):
        """Test that principal_left decreases correctly"""
        result = calculate_monthly_payment(
            loan=50000,
            years=10,
            interest_rates_100=[3.5],
            minimum_monthly_payment=1000,
            additional_payment=0
        )
        
        df = pd.DataFrame(result)
        
        # Check that each payment reduces the balance correctly
        for idx in range(len(df)):
            row = df.iloc[idx]
            expected_end_balance = row['loan_start'] - row['principal']
            
            assert abs(row['loan_end'] - expected_end_balance) < 0.01, \
                f"Row {idx}: Expected balance {expected_end_balance}, got {row['loan_end']}"

    def test_edge_case_zero_payments(self):
        """Test edge case with zero minimum and additional payments"""
        result = calculate_monthly_payment(
            loan=100000,
            years=30,
            interest_rates_100=[4.0],
            minimum_monthly_payment=0,
            additional_payment=0
        )
        
        df = pd.DataFrame(result)
        
        # Should still make required payments
        assert len(df) > 0, "No payments made"
        assert all(df['total'] > 0), "All payments should be positive"

    def test_edge_case_very_short_term(self):
        """Test with very short loan term"""
        result = calculate_monthly_payment(
            loan=12000,
            years=1,
            interest_rates_100=[6.0],
            minimum_monthly_payment=0,
            additional_payment=0
        )
        
        df = pd.DataFrame(result)
        
        # Should complete within 12 months
        assert len(df) <= 12, f"Loan should complete in 12 months, took {len(df)}"
        
        # Final balance should be near zero
        final_balance = df.iloc[-1]['loan_end']
        assert abs(final_balance) < 1.0, f"Final balance should be near zero, got {final_balance}"

    def test_varying_interest_rates(self):
        """Test with multiple interest rate changes"""
        result = calculate_monthly_payment(
            loan=300000,
            years=6,  # 6 rates for 6 years
            interest_rates_100=[2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
            minimum_monthly_payment=0,
            additional_payment=500
        )
        
        df = pd.DataFrame(result)
        
        # Should handle rate changes without issues
        assert len(df) > 0, "No payments generated"
        assert df['total'].sum() > 0, "Total payments should be positive"
        
        # Final balance should be reasonable
        final_balance = df.iloc[-1]['loan_end']
        assert final_balance <= 1.0, f"Final balance too high: {final_balance}"

    def test_mathematical_precision(self):
        """Test for floating point precision issues"""
        result = calculate_monthly_payment(
            loan=999999.99,
            years=30,
            interest_rates_100=[3.33333],
            minimum_monthly_payment=0,
            additional_payment=0.01
        )
        
        df = pd.DataFrame(result)
        
        # Check that calculations maintain reasonable precision
        for idx, row in df.iterrows():
            # Principal + interest should equal total (within precision)
            calculated_total = row['principal'] + row['interest']
            assert abs(calculated_total - row['total']) < 0.01, \
                f"Row {idx}: Precision error in total calculation"


if __name__ == "__main__":
    # Run specific problematic test cases
    test_suite = TestCalculateMonthlyPayment()
    
    print("Testing overpayment on final payment...")
    try:
        test_suite.test_overpayment_on_final_payment()
        print("✓ PASSED")
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
    
    print("\nTesting excessive minimum payment...")
    try:
        test_suite.test_excessive_minimum_payment()
        print("✓ PASSED")
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
    
    print("\nTesting interest on negative balance...")
    try:
        test_suite.test_interest_on_negative_balance()
        print("✓ PASSED")
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
    
    print("\nTesting data recording after loan paid...")
    try:
        test_suite.test_data_recording_after_loan_paid()
        print("✓ PASSED")
    except AssertionError as e:
        print(f"✗ FAILED: {e}") 