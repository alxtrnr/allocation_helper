#!/usr/bin/env python3
"""
Database Migration Script: Fix Invalid Staff Duration Values

This script automatically corrects any staff records where the 'duration' field
does not match the actual working hours (end_time - start_time).

This ensures data consistency and prevents solver infeasibility issues caused by
mismatched duration values that affect break constraint calculations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import StaffTable

def fix_staff_durations():
    """Fix all staff records with inconsistent duration values."""
    engine = create_engine('sqlite:///ward_db_alxtrnr.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("=" * 70)
    print("DATABASE MIGRATION: Fixing Staff Duration Values")
    print("=" * 70)
    
    staff_list = session.query(StaffTable).all()
    fixed_count = 0
    
    for staff in staff_list:
        actual_hours = staff.end_time - staff.start_time
        
        if staff.duration != actual_hours:
            old_duration = staff.duration
            staff.duration = actual_hours
            fixed_count += 1
            print(f"\n✓ Fixed {staff.name}:")
            print(f"  Working hours: {staff.start_time} to {staff.end_time} ({actual_hours} hours)")
            print(f"  Duration: {old_duration} → {actual_hours}")
    
    if fixed_count > 0:
        session.commit()
        print("\n" + "=" * 70)
        print(f"✅ Successfully fixed {fixed_count} staff record(s)")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✅ All staff records are already correct - no changes needed")
        print("=" * 70)
    
    session.close()
    return fixed_count

if __name__ == "__main__":
    fix_staff_durations()

