#!/usr/bin/env python3
"""
Diagnostic and Fix Script for ward_db_alxtrnr.db

This script identifies common issues with staff configuration and offers to fix them.
"""

import sqlite3
import sys

def diagnose_database(db_path):
    """Diagnose issues in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("DATABASE DIAGNOSTIC REPORT")
    print("=" * 60)
    
    # Check staff configuration
    cursor.execute("SELECT COUNT(*) FROM staff_table")
    total_staff = cursor.fetchone()[0]
    print(f"\n📊 Total staff members: {total_staff}")
    
    cursor.execute("SELECT COUNT(*) FROM staff_table WHERE assigned = 1")
    assigned_staff = cursor.fetchone()[0]
    print(f"✅ Staff assigned to allocations: {assigned_staff}")
    print(f"❌ Staff NOT assigned: {total_staff - assigned_staff}")
    
    # Check staff with invalid time ranges
    cursor.execute("SELECT COUNT(*) FROM staff_table WHERE start_time = 0 AND end_time = 0")
    invalid_times = cursor.fetchone()[0]
    if invalid_times > 0:
        print(f"\n⚠️  WARNING: {invalid_times} staff have invalid time range (start=0, end=0)")
        cursor.execute("SELECT id, name FROM staff_table WHERE start_time = 0 AND end_time = 0")
        for row in cursor.fetchall():
            print(f"   - ID {row[0]}: {row[1]}")
    
    cursor.execute("SELECT COUNT(*) FROM staff_table WHERE start_time >= end_time AND end_time != 0")
    backwards_times = cursor.fetchone()[0]
    if backwards_times > 0:
        print(f"\n⚠️  WARNING: {backwards_times} staff have start_time >= end_time")
    
    # Check patients
    cursor.execute("SELECT COUNT(*) FROM patient_table")
    total_patients = cursor.fetchone()[0]
    print(f"\n📊 Total patients: {total_patients}")
    
    cursor.execute("""
        SELECT COUNT(*) FROM patient_table 
        WHERE CAST(observation_level AS INTEGER) > 0
    """)
    patients_needing_obs = cursor.fetchone()[0]
    print(f"🔍 Patients needing observations (level > 0): {patients_needing_obs}")
    
    if patients_needing_obs > 0:
        cursor.execute("""
            SELECT id, name, observation_level, gender_req 
            FROM patient_table 
            WHERE CAST(observation_level AS INTEGER) > 0
        """)
        print("\n   Patients requiring observations:")
        for row in cursor.fetchall():
            gender_note = f" (requires {row[3]} staff)" if row[3] else ""
            print(f"   - ID {row[0]}: {row[1]} (Level {row[2]:1}){gender_note}")
    
    # Calculate if current assignment is feasible
    print("\n" + "=" * 60)
    print("FEASIBILITY CHECK")
    print("=" * 60)
    
    # Count demand per hour
    cursor.execute("SELECT observation_level FROM patient_table")
    demand_per_hour = [0] * 12
    for row in cursor.fetchall():
        try:
            level = int(row[0])
            if level > 0:
                for t in range(12):
                    demand_per_hour[t] += level
        except (ValueError, TypeError):
            pass
    
    # Count supply per hour
    cursor.execute("""
        SELECT start_time, end_time FROM staff_table 
        WHERE assigned = 1
    """)
    supply_per_hour = [0] * 12
    for row in cursor.fetchall():
        start, end = row[0], row[1]
        for t in range(12):
            if start <= t < end:
                supply_per_hour[t] += 1
    
    print("\nHourly Coverage Analysis:")
    print("Hour | Demand | Supply | Status")
    print("-----|--------|--------|--------")
    
    has_shortfall = False
    for t in range(12):
        status = "✅ OK" if supply_per_hour[t] >= demand_per_hour[t] else f"❌ SHORT {demand_per_hour[t] - supply_per_hour[t]}"
        if supply_per_hour[t] < demand_per_hour[t]:
            has_shortfall = True
        print(f"  {t:2d} |   {demand_per_hour[t]:2d}   |   {supply_per_hour[t]:2d}   | {status}")
    
    if has_shortfall:
        print("\n❌ INFEASIBLE: Not enough staff coverage for all hours")
    else:
        print("\n✅ FEASIBLE: Coverage requirements can be met")
    
    conn.close()
    return {
        'total_staff': total_staff,
        'assigned_staff': assigned_staff,
        'invalid_times': invalid_times,
        'patients_needing_obs': patients_needing_obs,
        'has_shortfall': has_shortfall
    }


def fix_database(db_path):
    """Offer to fix common issues."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("SUGGESTED FIXES")
    print("=" * 60)
    
    # Check for unassigned staff with valid times
    cursor.execute("""
        SELECT id, name, start_time, end_time 
        FROM staff_table 
        WHERE assigned = 0 AND start_time < end_time AND end_time > 0
    """)
    unassigned_with_times = cursor.fetchall()
    
    if unassigned_with_times:
        print(f"\n🔧 Found {len(unassigned_with_times)} staff with valid times but not assigned to allocations:")
        for row in unassigned_with_times:
            print(f"   - ID {row[0]}: {row[1]} (hours {row[2]}-{row[3]})")
        
        response = input("\nAssign these staff to allocations? (y/n): ").strip().lower()
        if response == 'y':
            cursor.execute("""
                UPDATE staff_table 
                SET assigned = 1 
                WHERE assigned = 0 AND start_time < end_time AND end_time > 0
            """)
            print(f"✅ Assigned {cursor.rowcount} staff to allocations")
    
    # Check for staff with invalid times
    cursor.execute("""
        SELECT id, name FROM staff_table 
        WHERE start_time = 0 AND end_time = 0
    """)
    invalid_time_staff = cursor.fetchall()
    
    if invalid_time_staff:
        print(f"\n🔧 Found {len(invalid_time_staff)} staff with invalid time range (0-0):")
        for row in invalid_time_staff:
            print(f"   - ID {row[0]}: {row[1]}")
        
        print("\nThese staff need their Start and End times configured in the UI.")
        print("Default day shift: 08:00-19:00 (hours 0-11)")
        print("Default night shift: 20:00-07:00 (hours 0-11)")
        
        response = input("\nSet all to default day shift (08:00-19:00)? (y/n): ").strip().lower()
        if response == 'y':
            cursor.execute("""
                UPDATE staff_table 
                SET start_time = 0, end_time = 12, start = '08:00', end = '19:00'
                WHERE start_time = 0 AND end_time = 0
            """)
            print(f"✅ Set default times for {cursor.rowcount} staff")
    
    conn.commit()
    conn.close()
    print("\n✅ Database updated successfully!")


if __name__ == "__main__":
    db_path = "ward_db_alxtrnr.db"
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"Analyzing database: {db_path}\n")
    
    issues = diagnose_database(db_path)
    
    if issues['assigned_staff'] == 0 or issues['invalid_times'] > 0:
        print("\n" + "=" * 60)
        response = input("\nWould you like to apply suggested fixes? (y/n): ").strip().lower()
        if response == 'y':
            fix_database(db_path)
            print("\n" + "=" * 60)
            print("Re-running diagnostics after fixes...")
            print("=" * 60)
            diagnose_database(db_path)
        else:
            print("\nNo changes made to the database.")
    else:
        print("\n✅ Database configuration looks good!")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("""
1. In the Streamlit UI, go to the Staff page
2. Use the data editor to:
   - Check the 'Assign' checkbox for staff who should work
   - Set 'Start' time (e.g., 08:00 for day shift, 20:00 for night shift)
   - Set 'End' time (e.g., 19:00 for day shift, 07:00 for night shift)
3. Go to the Patients page and ensure observation levels are set correctly
4. Try running the allocations again
""")

