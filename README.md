# The Allocation Helper
Typical Use Case - 
An inpatient mental health ward. The nurse in charge must ensure all general and enhanced observations are allocated to staff correctly for the duration of the shift. 

## Generate allocations that factor in -
* Patient observation level (generals, 1:1, 2:1, 3:1, 4:1)
* Patient/staff matching as needed
* Staff excluded from observations at certain times as needed
* No single allocation any longer than two continuous hours
* Time off for breaks according to hours worked
* Shift patterns - nights/days
* Staff working hours - long day/night or custom hours

  ## Functionality includes -
* Create, update and delete patient and staff details
* View patient and staff details
* Assign staff to complete observations
* Generate and view suggested allocations
* Download suggested allocations. These can be tweaked as needed.

The app is built with and hosted on [Streamlit](https://allocations-and-observations.streamlit.app/) 
