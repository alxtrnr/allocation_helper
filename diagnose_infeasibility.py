#!/usr/bin/env python3
"""
Infeasibility Diagnostic Tool

This script analyzes the database and identifies constraint conflicts
that make the allocation problem infeasible.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import StaffTable, PatientTable

def diagnose_infeasibility():
    engine = create_engine('sqlite:///ward_db_alxtrnr.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("=" * 70)
    print("INFEASIBILITY DIAGNOSTIC")
    print("=" * 70)
    
    staff_list = session.query(StaffTable).filter_by(assigned=True).all()
    patient_list = session.query(PatientTable).all()
    
    issues_found = []
    
    # Check 1: Coverage
    print("\n1. CHECKING COVERAGE...")
    min_staff_per_time = [0] * 12
    for p in patient_list:
        level = int(p.observation_level or 0)
        if level > 0:
            for t in range(12):
                min_staff_per_time[t] += level
    
    available_per_time = [0] * 12
    for s in staff_list:
        for t in range(12):
            if s.start_time <= t < s.end_time:
                available_per_time[t] += 1
    
    for t in range(12):
        if available_per_time[t] < min_staff_per_time[t]:
            issues_found.append(f"Hour {t}: Need {min_staff_per_time[t]}, have {available_per_time[t]} (shortfall)")
    
    if not issues_found:
        print("   ✓ Coverage is adequate for all hours")
    
    # Check 2: Special list constraints
    print("\n2. CHECKING SPECIAL LIST CONSTRAINTS...")
    special_list_staff = [s for s in staff_list if s.special_list]
    if special_list_staff:
        for s in special_list_staff:
            print(f"   ℹ {s.name} can only observe: {', '.join(s.special_list)}")
        print("   ✓ Note: Other staff can still observe these patients")
    else:
        print("   ✓ No special list restrictions")
    
    # Check 3: Duration consistency
    print("\n3. CHECKING DURATION CONSISTENCY...")
    for s in staff_list:
        actual_hours = s.end_time - s.start_time
        if s.duration != actual_hours:
            issue = f"{s.name}: duration={s.duration} but works {actual_hours}h (MISMATCH)"
            issues_found.append(issue)
            print(f"   ✗ {issue}")
        else:
            print(f"   ✓ {s.name}: duration matches working hours ({actual_hours}h)")
    
    # Check 4: Break constraints and capacity
    print("\n4. CHECKING BREAK REQUIREMENTS...")
    staff_needing_2h_break = [s for s in staff_list if s.duration >= 12]
    print(f"   {len(staff_needing_2h_break)} staff need 2-hour breaks (slots 5-11)")
    
    # Check break window capacity
    if len(staff_needing_2h_break) > 0:
        print("\n5. CHECKING BREAK WINDOW CAPACITY (SLOTS 5-11)...")
        total_need_per_slot = sum(int(p.observation_level or 0) for p in patient_list)
        capacity_in_window = len(staff_needing_2h_break) * 5  # max 5 of 7 slots
        required_in_window = total_need_per_slot * 7  # 7 slots
        
        print(f"   Staff with 12h shifts: {len(staff_needing_2h_break)}")
        print(f"   Each can work max 5 of 7 slots (due to 2h break)")
        print(f"   Available capacity: {len(staff_needing_2h_break)} × 5 = {capacity_in_window} staff-slots")
        print(f"   Required coverage: {total_need_per_slot} × 7 = {required_in_window} staff-slots")
        
        if capacity_in_window < required_in_window:
            shortage = required_in_window - capacity_in_window
            additional_needed = (shortage + 4) // 5
            issue = (
                f"BREAK WINDOW CAPACITY SHORTAGE:\n"
                f"   - Need {required_in_window} staff-slots but can only provide {capacity_in_window}\n"
                f"   - Shortage: {shortage} staff-slots\n"
                f"   - SOLUTION: Add {additional_needed} more staff working 12h shifts\n"
                f"   - OR change some staff to 11h shifts (only need 1h break)"
            )
            issues_found.append(issue)
            print(f"   ✗ {issue}")
        else:
            print(f"   ✓ Sufficient capacity in break window")
    
    # Summary
    print("\n" + "=" * 70)
    if issues_found:
        print(f"❌ FOUND {len(issues_found)} ISSUE(S) CAUSING INFEASIBILITY")
        print("=" * 70)
        for i, issue in enumerate(issues_found, 1):
            print(f"\nIssue {i}:")
            print(issue)
    else:
        print("✅ NO OBVIOUS ISSUES FOUND")
        print("=" * 70)
        print("\nIf solver still reports infeasible, check:")
        print("1. Consecutive hours constraint (max 2 consecutive per patient)")
        print("2. Gender matching requirements")
        print("3. Omit time constraints")
    
    session.close()
    return issues_found

if __name__ == "__main__":
    diagnose_infeasibility()

