# Bug Report: calculate_monthly_payment Function

## Summary
The `calculate_monthly_payment` function in `test_cal_function.py` contains several critical bugs and issues that cause incorrect calculations and potential crashes.

## Critical Bugs

### 1. **CRITICAL: Overpayment on Final Payment**
**Location**: Lines 43-51
**Issue**: When the remaining principal is less than the calculated payment amount, the function allows overpayment.
**Impact**: Results in negative loan balances and incorrect total interest calculations.

**Example**:
- $10,000 loan with $12,000 minimum payment
- Function pays $11,958.33 in principal when only $10,000 is owed
- Results in -$1,958.33 ending balance

**Code causing issue**:
```python
principal = total - interest
principal_left -= total - interest  # Can make principal_left negative
```

### 2. **CRITICAL: Division by Zero with 0% Interest Rate**
**Location**: Line 37
**Issue**: When interest rate is 0%, `denomi` becomes 0, causing a division by zero error.
**Impact**: Function crashes with ZeroDivisionError.

**Code causing issue**:
```python
nomi = (1 + interest_rate_monthly) ** months_left  # becomes 1 when rate is 0
denomi = nomi - 1  # becomes 0 when rate is 0
required_monthly_payment = (principal_left * interest_rate_monthly * nomi) / denomi  # Division by zero!
```

### 3. **MAJOR: Mathematical Inconsistency in Principal Payments**
**Issue**: Principal payments can exceed the starting balance of the loan.
**Impact**: Loan calculations become mathematically impossible.

**Example**:
- Starting balance: $20,250
- Total payment: $30,000
- Interest: $101.25
- Principal: $29,898.75 (exceeds starting balance!)

## Logical Issues

### 4. **Improper Handling of Excessive Payments**
**Issue**: No validation when minimum_payment + additional_payment exceeds reasonable amounts.
**Impact**: Can pay off loans unrealistically fast with overpayment.

### 5. **Interest Calculated on Negative Balances**
**Issue**: When principal_left goes negative, interest is still calculated on the negative amount.
**Impact**: Can result in negative interest payments in subsequent iterations.

### 6. **Data Recording After Loan is Paid**
**Issue**: Function continues to record payment data even after loan balance reaches zero.
**Impact**: Skews statistics and creates confusing payment histories.

## Minor Issues

### 7. **Unused Variable**
**Issue**: `year_left` is decremented but never used.
**Impact**: Dead code, potential confusion.

### 8. **Months Left Calculation**
**Issue**: `months_left` is decremented linearly but should be recalculated based on remaining balance and payment amounts.
**Impact**: Incorrect payment calculations in scenarios with additional payments.

## Test Results

### Tests That Failed:
- ✗ `test_overpayment_on_final_payment`: Found negative balances: -$1,958.33
- ✗ `test_excessive_minimum_payment`: Found negative balances: -$49,623.44
- ✗ `test_division_by_zero_edge_case`: ZeroDivisionError with 0% interest
- ✗ `test_zero_interest_rate`: ZeroDivisionError

### Tests That Passed:
- ✓ `test_interest_on_negative_balance`: Function handles this case
- ✓ `test_data_recording_after_loan_paid`: Stops recording when balance ≤ 0

## Recommended Fixes

### Fix 1: Prevent Overpayment
```python
# Instead of:
principal = total - interest
principal_left -= total - interest

# Use:
max_principal = min(total - interest, principal_left)
actual_total = max_principal + interest
principal_left -= max_principal
```

### Fix 2: Handle Zero Interest Rate
```python
if interest_rate_monthly == 0:
    required_monthly_payment = principal_left / months_left
else:
    nomi = (1 + interest_rate_monthly) ** months_left
    denomi = nomi - 1
    required_monthly_payment = (principal_left * interest_rate_monthly * nomi) / denomi
```

### Fix 3: Add Input Validation
```python
# Validate inputs
if loan <= 0:
    raise ValueError("Loan amount must be positive")
if years <= 0:
    raise ValueError("Years must be positive")
if any(rate < 0 for rate in interest_rates_100):
    raise ValueError("Interest rates cannot be negative")
```

### Fix 4: Proper Final Payment Handling
```python
# Check if this is the final payment
if principal_left <= total:
    # Final payment - only pay what's owed
    final_payment = principal_left + interest
    # Record the actual payment made, not the calculated payment
```

## Impact Assessment
- **High**: Functions using this code for real financial calculations will produce incorrect results
- **Medium**: Any automated systems relying on this could make wrong financial decisions  
- **Low**: Test/demonstration code may mislead users about actual loan calculations

## Files Affected
- `test_cal_function.py` - Contains the buggy function
- Any code importing and using `calculate_monthly_payment` 