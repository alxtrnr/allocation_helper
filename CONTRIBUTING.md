# Contributing to Allocation Helper

## Architecture Overview

- **models.py**
  - Contains staff/patient table class definitions (`StaffTable`, `PatientTable`), SQLAlchemy `Base`, and a DB initialization helper (`init_in_memory_db`).
  - Models are "pure" and decoupled from any UI or business logic. They can be used by tests, service code, and apps.

- **/services/**
  - Service modules (e.g., `staff_service.py`, `patient_service.py`) contain all business logic for CRUD operations (add, update, delete) **with validation and error messages**.
  - All DB writes use try/except with rollbacks for safety.
  - All input/output from these functions is normalized (e.g., name/title case), error-prone conditions are tested first.
  - Services return `{'success': bool, 'object': obj, 'message': str}` or similar result dicts for UI or test to consume.

- **UI code (Streamlit pages, database_utils/database_operations, etc.)**
  - Handles layout, widgets, column editing—but **never manipulates DB rows directly**.
  - All user-triggered data changes call the service functions, check `.success`, and display `.message` or error as feedback.

## Test Philosophy

- All business logic (services) is covered by `pytest` unit tests using in-memory SQLite DBs.
- Use `models.init_in_memory_db()` in your test setup to get `Session, StaffTable, PatientTable` instances that match the production meta-structure.
- Example:

```python
Session, StaffTable, PatientTable = init_in_memory_db()
session = Session()
add_staff_entry(session, name='Jane Smith', role='HCA', gender='F')
assert session.query(StaffTable).filter_by(name='Jane Smith').count() == 1
```

- Tests should cover all CRUD actions, with both successful and expected fail cases.

## How to Extend the Domain or Add Fields

1. **Update models.py:**
   - Add your field to the table class, or define a new entity. E.g.,
     `middle_name = Column(String)` in `StaffTable`.
2. **Update service logic:**
   - Modify the appropriate service function (add, update) to accept and validate the new field if needed.
   - Normalize/validate in service, not UI.
3. **Update UI:**
   - Expose a widget/input to collect the value. Pass it to the service function.
4. **Test:**
   - Write tests with the new field/logic. Test all error paths.

## Golden Rules
- All business logic/validation goes in services. UI *only* interacts with services!
- All DB manipulation must pass through a service layer function.
- Services always handle commit/rollback; tests and UI should never call .commit() except for test setup.

## Example: Adding field 'middle_name' to Staff

1. **models.py:**
   ```python
   class StaffTable(Base):
       ...
       middle_name = Column(String)
   ```
2. **services/staff_service.py:**
   ```python
   def add_staff_entry(..., middle_name=None, ...):
       # Validate/normalize if required, e.g.,
       staff = StaffTable(..., middle_name=middle_name)
   def update_staff_entry(..., middle_name=None, ...):
       if middle_name is not None:
           staff.middle_name = middle_name
   ```
3. **UI:**
   Add a `st.text_input('Middle Name')`, pass to services.
4. **Test:**
   Write cases like:
   ```python
   res = add_staff_entry(session, name='Jane', middle_name='Marie', ...)
   assert res['success']
   s = session.query(StaffTable).filter_by(name='Jane').one()
   assert s.middle_name == 'Marie'
   ```

---

Feel free to contact the maintainers with more architecture or test questions!
