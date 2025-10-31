#!/usr/bin/env python3
"""
Comprehensive test script for data entry functions.
Tests all CRUD operations and verifies persistence.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.staff_service import add_staff_entry, update_staff_entry, delete_staff_entry
from services.patient_service import add_patient_entry, update_patient_entry, delete_patient_entry
from models import StaffTable, PatientTable, Base

# Use a temporary test database
TEST_DB = 'test_data_entry.db'

def setup_test_db():
    """Create a fresh test database."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    engine = create_engine(f'sqlite:///{TEST_DB}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session, engine

def teardown_test_db():
    """Clean up test database."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_staff_crud():
    """Test staff CRUD operations."""
    print("=" * 70)
    print("TEST: STAFF CRUD OPERATIONS")
    print("=" * 70)
    
    Session, engine = setup_test_db()
    session = Session()
    
    try:
        # TEST 1: Create (Add) Staff
        print("\n[TEST 1] Add Staff Members")
        print("-" * 70)
        
        result1 = add_staff_entry(session, name="Alice Johnson", role="RMN", gender="F", 
                                   assigned=True, start_time=0, end_time=12, duration=12)
        print(f"✓ Add Alice: {result1['success']} - {result1['message']}")
        assert result1['success'], "Failed to add Alice"
        
        result2 = add_staff_entry(session, name="Bob Smith", role="HCA", gender="M",
                                   assigned=True, start_time=0, end_time=6, duration=6)
        print(f"✓ Add Bob: {result2['success']} - {result2['message']}")
        assert result2['success'], "Failed to add Bob"
        
        result3 = add_staff_entry(session, name="Carol Davis", role="HCA", gender="F",
                                   assigned=False, start_time=0, end_time=12, duration=12)
        print(f"✓ Add Carol: {result3['success']} - {result3['message']}")
        assert result3['success'], "Failed to add Carol"
        
        # Verify adds
        staff_count = session.query(StaffTable).count()
        print(f"✓ Total staff in DB: {staff_count}")
        assert staff_count == 3, f"Expected 3 staff, got {staff_count}"
        
        # TEST 2: Read (Verify persistence)
        print("\n[TEST 2] Read Staff Data (Verify Persistence)")
        print("-" * 70)
        
        # Close and reopen session to verify persistence
        session.close()
        session = Session()
        
        alice = session.query(StaffTable).filter_by(name="Alice Johnson").first()
        assert alice is not None, "Alice not found after session reopen"
        print(f"✓ Alice found: ID={alice.id}, Role={alice.role}, Gender={alice.gender}, Assigned={alice.assigned}")
        print(f"  Time: {alice.start_time}-{alice.end_time}, Duration={alice.duration}")
        assert alice.role == "RMN"
        assert alice.gender == "F"
        assert alice.assigned == True
        assert alice.start_time == 0
        assert alice.end_time == 12
        
        bob = session.query(StaffTable).filter_by(name="Bob Smith").first()
        assert bob is not None, "Bob not found"
        print(f"✓ Bob found: ID={bob.id}, Role={bob.role}, Duration={bob.duration}")
        assert bob.duration == 6
        
        carol = session.query(StaffTable).filter_by(name="Carol Davis").first()
        assert carol is not None, "Carol not found"
        print(f"✓ Carol found: ID={carol.id}, Assigned={carol.assigned}")
        assert carol.assigned == False
        
        # TEST 3: Update Staff
        print("\n[TEST 3] Update Staff Data")
        print("-" * 70)
        
        # Update Alice's role and assignment
        update1 = update_staff_entry(session, alice.id, role="HCA", assigned=False)
        print(f"✓ Update Alice role to HCA: {update1['success']} - {update1['message']}")
        assert update1['success'], "Failed to update Alice"
        
        # Update Bob's times
        update2 = update_staff_entry(session, bob.id, start_time=2, end_time=8, duration=6)
        print(f"✓ Update Bob times (2-8): {update2['success']} - {update2['message']}")
        assert update2['success'], "Failed to update Bob"
        
        # Verify updates persisted
        session.close()
        session = Session()
        
        alice_updated = session.query(StaffTable).filter_by(name="Alice Johnson").first()
        print(f"✓ Alice updated: Role={alice_updated.role}, Assigned={alice_updated.assigned}")
        assert alice_updated.role == "HCA", f"Role not updated: {alice_updated.role}"
        assert alice_updated.assigned == False, "Assigned not updated"
        
        bob_updated = session.query(StaffTable).filter_by(name="Bob Smith").first()
        print(f"✓ Bob updated: Start={bob_updated.start_time}, End={bob_updated.end_time}")
        assert bob_updated.start_time == 2, "Start time not updated"
        assert bob_updated.end_time == 8, "End time not updated"
        
        # TEST 4: Validation (should fail)
        print("\n[TEST 4] Validation Tests (Should Fail)")
        print("-" * 70)
        
        # Duplicate name
        dup_result = add_staff_entry(session, name="Alice Johnson", role="HCA", gender="F")
        print(f"✓ Duplicate name rejected: {not dup_result['success']} - {dup_result['message']}")
        assert not dup_result['success'], "Duplicate should be rejected"
        
        # Invalid role
        bad_role = add_staff_entry(session, name="Dave", role="DOCTOR", gender="M")
        print(f"✓ Invalid role rejected: {not bad_role['success']} - {bad_role['message']}")
        assert not bad_role['success'], "Invalid role should be rejected"
        
        # Invalid gender
        bad_gender = add_staff_entry(session, name="Eve", role="HCA", gender="X")
        print(f"✓ Invalid gender rejected: {not bad_gender['success']} - {bad_gender['message']}")
        assert not bad_gender['success'], "Invalid gender should be rejected"
        
        # Empty name
        empty_name = add_staff_entry(session, name="", role="HCA", gender="M")
        print(f"✓ Empty name rejected: {not empty_name['success']} - {empty_name['message']}")
        assert not empty_name['success'], "Empty name should be rejected"
        
        # TEST 5: Delete Staff
        print("\n[TEST 5] Delete Staff")
        print("-" * 70)
        
        # Delete Carol
        delete_result = delete_staff_entry(session, "Carol Davis")
        print(f"✓ Delete Carol: {delete_result}")
        assert delete_result == True, "Failed to delete Carol"
        
        # Verify deletion persisted
        session.close()
        session = Session()
        
        carol_deleted = session.query(StaffTable).filter_by(name="Carol Davis").first()
        print(f"✓ Carol deleted (should be None): {carol_deleted}")
        assert carol_deleted is None, "Carol should be deleted"
        
        remaining = session.query(StaffTable).count()
        print(f"✓ Remaining staff: {remaining}")
        assert remaining == 2, f"Expected 2 staff, got {remaining}"
        
        print("\n" + "=" * 70)
        print("✅ ALL STAFF CRUD TESTS PASSED")
        print("=" * 70)
        
    finally:
        session.close()
        engine.dispose()


def test_patient_crud():
    """Test patient CRUD operations."""
    print("\n\n" + "=" * 70)
    print("TEST: PATIENT CRUD OPERATIONS")
    print("=" * 70)
    
    Session, engine = setup_test_db()
    session = Session()
    
    try:
        # TEST 1: Create (Add) Patients
        print("\n[TEST 1] Add Patients")
        print("-" * 70)
        
        result1 = add_patient_entry(session, name="John Doe", observation_level=1, 
                                     obs_type="standard", room_number="01", gender_req="F")
        print(f"✓ Add John Doe: {result1['success']} - {result1['message']}")
        assert result1['success'], "Failed to add John Doe"
        
        result2 = add_patient_entry(session, name="Jane Smith", observation_level=2,
                                     obs_type="arms-length", room_number="02", gender_req="M")
        print(f"✓ Add Jane Smith: {result2['success']} - {result2['message']}")
        assert result2['success'], "Failed to add Jane Smith"
        
        result3 = add_patient_entry(session, name="Mike Wilson", observation_level=0,
                                     room_number="03")
        print(f"✓ Add Mike Wilson: {result3['success']} - {result3['message']}")
        assert result3['success'], "Failed to add Mike Wilson"
        
        # Verify adds
        patient_count = session.query(PatientTable).count()
        print(f"✓ Total patients in DB: {patient_count}")
        assert patient_count == 3, f"Expected 3 patients, got {patient_count}"
        
        # TEST 2: Read (Verify persistence)
        print("\n[TEST 2] Read Patient Data (Verify Persistence)")
        print("-" * 70)
        
        # Close and reopen session
        session.close()
        session = Session()
        
        john = session.query(PatientTable).filter_by(name="John Doe").first()
        assert john is not None, "John not found after session reopen"
        print(f"✓ John found: ID={john.id}, ObsLevel={john.observation_level}, Room={john.room_number}")
        print(f"  ObsType={john.obs_type}, GenderReq={john.gender_req}")
        assert john.observation_level == "1"
        assert john.obs_type == "standard"
        assert john.room_number == "01"
        assert john.gender_req == "F"
        
        jane = session.query(PatientTable).filter_by(name="Jane Smith").first()
        assert jane is not None, "Jane not found"
        print(f"✓ Jane found: ObsLevel={jane.observation_level}, GenderReq={jane.gender_req}")
        assert jane.observation_level == "2"
        assert jane.gender_req == "M"
        
        mike = session.query(PatientTable).filter_by(name="Mike Wilson").first()
        assert mike is not None, "Mike not found"
        print(f"✓ Mike found: ObsLevel={mike.observation_level}")
        assert mike.observation_level == "0"
        
        # TEST 3: Update Patients
        print("\n[TEST 3] Update Patient Data")
        print("-" * 70)
        
        # Update John's observation level and type
        update1 = update_patient_entry(session, john.id, observation_level=3, 
                                       obs_type="eyesight", gender_req="M")
        print(f"✓ Update John obs level to 3: {update1['success']} - {update1['message']}")
        assert update1['success'], "Failed to update John"
        
        # Update Jane's room
        update2 = update_patient_entry(session, jane.id, room_number="05")
        print(f"✓ Update Jane room to 05: {update2['success']} - {update2['message']}")
        assert update2['success'], "Failed to update Jane"
        
        # Verify updates persisted
        session.close()
        session = Session()
        
        john_updated = session.query(PatientTable).filter_by(name="John Doe").first()
        print(f"✓ John updated: ObsLevel={john_updated.observation_level}, Type={john_updated.obs_type}, GenderReq={john_updated.gender_req}")
        assert john_updated.observation_level == "3", "Observation level not updated"
        assert john_updated.obs_type == "eyesight", "Obs type not updated"
        assert john_updated.gender_req == "M", "Gender req not updated"
        
        jane_updated = session.query(PatientTable).filter_by(name="Jane Smith").first()
        print(f"✓ Jane updated: Room={jane_updated.room_number}")
        assert jane_updated.room_number == "05", "Room not updated"
        
        # TEST 4: Validation (should fail)
        print("\n[TEST 4] Validation Tests (Should Fail)")
        print("-" * 70)
        
        # Duplicate name
        dup_result = add_patient_entry(session, name="John Doe", observation_level=1)
        print(f"✓ Duplicate name rejected: {not dup_result['success']} - {dup_result['message']}")
        assert not dup_result['success'], "Duplicate should be rejected"
        
        # Empty name
        empty_name = add_patient_entry(session, name="", observation_level=1)
        print(f"✓ Empty name rejected: {not empty_name['success']} - {empty_name['message']}")
        assert not empty_name['success'], "Empty name should be rejected"
        
        # TEST 5: Delete Patient
        print("\n[TEST 5] Delete Patient")
        print("-" * 70)
        
        # Delete Mike
        delete_result = delete_patient_entry(session, "Mike Wilson")
        print(f"✓ Delete Mike: {delete_result}")
        assert delete_result == True, "Failed to delete Mike"
        
        # Verify deletion persisted
        session.close()
        session = Session()
        
        mike_deleted = session.query(PatientTable).filter_by(name="Mike Wilson").first()
        print(f"✓ Mike deleted (should be None): {mike_deleted}")
        assert mike_deleted is None, "Mike should be deleted"
        
        remaining = session.query(PatientTable).count()
        print(f"✓ Remaining patients: {remaining}")
        assert remaining == 2, f"Expected 2 patients, got {remaining}"
        
        print("\n" + "=" * 70)
        print("✅ ALL PATIENT CRUD TESTS PASSED")
        print("=" * 70)
        
    finally:
        session.close()
        engine.dispose()


def test_patient_staff_exclusions():
    """Test patient-staff exclusion features."""
    print("\n\n" + "=" * 70)
    print("TEST: PATIENT-STAFF EXCLUSIONS")
    print("=" * 70)
    
    Session, engine = setup_test_db()
    session = Session()
    
    try:
        # Add staff
        result_a = add_staff_entry(session, name="Staff A", role="HCA", gender="M")
        result_b = add_staff_entry(session, name="Staff B", role="RMN", gender="F")
        
        # Add patients
        add_patient_entry(session, name="Patient 1", observation_level=1)
        add_patient_entry(session, name="Patient 2", observation_level=2)
        
        print("\n[TEST] Staff Special List Management")
        print("-" * 70)
        
        # Manually set special_list (simulating UI behavior)
        staff_a = session.query(StaffTable).filter_by(name="Staff A").first()
        staff_a.special_list = ["Patient 1", "Patient 2"]
        session.commit()
        
        # Verify special_list persisted
        session.close()
        session = Session()
        
        staff_a = session.query(StaffTable).filter_by(name="Staff A").first()
        print(f"✓ Staff A special_list: {staff_a.special_list}")
        assert "Patient 1" in staff_a.special_list, "Special list not persisted"
        assert "Patient 2" in staff_a.special_list, "Special list incomplete"
        
        print("\n[TEST] Patient Omit Staff Management")
        print("-" * 70)
        
        # Update patient to exclude Staff B
        patient1 = session.query(PatientTable).filter_by(name="Patient 1").first()
        patient1.omit_staff = ["Staff B"]
        session.commit()
        
        # Verify omit_staff persisted
        session.close()
        session = Session()
        
        patient1_updated = session.query(PatientTable).filter_by(name="Patient 1").first()
        print(f"✓ Patient 1 omit_staff: {patient1_updated.omit_staff}")
        assert "Staff B" in patient1_updated.omit_staff, "Omit staff not persisted"
        
        print("\n[TEST] Patient Deletion Cleanup")
        print("-" * 70)
        
        # Test patient deletion removes them from staff special_lists
        delete_patient_entry(session, "Patient 1")
        
        session.close()
        session = Session()
        
        staff_a_after = session.query(StaffTable).filter_by(name="Staff A").first()
        print(f"✓ Staff A special_list after patient deletion: {staff_a_after.special_list}")
        assert "Patient 1" not in staff_a_after.special_list, "Patient not removed from special_list"
        assert "Patient 2" in staff_a_after.special_list, "Patient 2 should still be in list"
        
        print("\n" + "=" * 70)
        print("✅ EXCLUSION TESTS PASSED")
        print("=" * 70)
        
    finally:
        session.close()
        engine.dispose()


def test_real_database():
    """Test operations on the actual ward database."""
    print("\n\n" + "=" * 70)
    print("TEST: REAL DATABASE OPERATIONS")
    print("=" * 70)
    
    real_db = 'ward_db_alxtrnr.db'
    if not os.path.exists(real_db):
        print(f"⚠️  Real database not found: {real_db}")
        print("Skipping real database test")
        return
    
    engine = create_engine(f'sqlite:///{real_db}')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\n[TEST] Read Real Database")
        print("-" * 70)
        
        staff_count = session.query(StaffTable).count()
        patient_count = session.query(PatientTable).count()
        
        print(f"✓ Staff count: {staff_count}")
        print(f"✓ Patient count: {patient_count}")
        
        # Show sample data
        if staff_count > 0:
            staff_sample = session.query(StaffTable).first()
            print(f"\nSample Staff:")
            print(f"  Name: {staff_sample.name}")
            print(f"  Role: {staff_sample.role}")
            print(f"  Gender: {staff_sample.gender}")
            print(f"  Assigned: {staff_sample.assigned}")
            print(f"  Times: {staff_sample.start_time}-{staff_sample.end_time}")
            print(f"  Duration: {staff_sample.duration}")
        
        if patient_count > 0:
            patient_sample = session.query(PatientTable).filter(
                PatientTable.observation_level != "0"
            ).first()
            if patient_sample:
                print(f"\nSample Patient (with observations):")
                print(f"  Name: {patient_sample.name}")
                print(f"  Obs Level: {patient_sample.observation_level}")
                print(f"  Obs Type: {patient_sample.obs_type}")
                print(f"  Room: {patient_sample.room_number}")
                print(f"  Gender Req: {patient_sample.gender_req}")
        
        print("\n" + "=" * 70)
        print("✅ REAL DATABASE READ SUCCESSFUL")
        print("=" * 70)
        
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  COMPREHENSIVE DATA ENTRY TESTING  ".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    
    try:
        # Run all tests
        test_staff_crud()
        test_patient_crud()
        test_patient_staff_exclusions()
        test_real_database()
        
        print("\n\n")
        print("*" * 70)
        print("*" + " " * 68 + "*")
        print("*" + "  🎉 ALL DATA ENTRY TESTS PASSED! 🎉  ".center(68) + "*")
        print("*" + " " * 68 + "*")
        print("*" * 70)
        print("\n✅ Data entry functions are working correctly")
        print("✅ All changes persist across sessions")
        print("✅ Validation is working as expected")
        print("✅ Ready for production use!")
        
    except AssertionError as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        teardown_test_db()

