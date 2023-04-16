# milo_results.py

import pulp
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import csv


def get_staff_assignments(staff, observations, assignments):
    assignments_dict = {}
    for o in observations:
        for t in range(12):
            staff_assigned = [s["name"] for s in staff if assignments[(s["id"], o["id"], t)].value() == 1]
            assignments_dict[(o["name"], t)] = staff_assigned
    return assignments_dict


def export_to_csv(data, headers, filename, index=None, index_label=''):
    with open(filename, "w", newline='') as file:
        writer = csv.writer(file)

        if index is not None:
            # Add the index header as the first column header
            headers = [index_label] + headers

            # Write the headers to the file
            writer.writerow(headers)

            # Write the data to the file
            for i, row in enumerate(data):
                writer.writerow([index[i]] + row)
        else:
            # Write the headers to the file
            writer.writerow(headers)

            # Write the data to the file
            for i, row in enumerate(data):
                writer.writerow([i] + row)


def print_results(staff, observations, assignments, shift):
    # each item (time) in the shift_hours list is used as the label for each respective row in the table
    shift_hours = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00',
                   '19:00'] if shift == 'D' else ['20:00', '21:00', '22:00', '23:00', '00:00', '01:00', '02:00',
                                                  '03:00', '04:00', '05:00', '06:00', '07:00']

    # Table 1: Patient names are the column headers. Rows labels are shift hours. Each cell contains the staff name(s)
    # allocated to the patient at that time.
    ob_names = [o["name"] for o in observations if int(o["observation_level"]) >= 1]
    observations_names = [f"{o['name']} {o['observation_level']}:1 | {o['obs_type']} | rm. {o['room_number']}" for o in
                          observations if int(o["observation_level"]) >= 1]
    assignments_dict = get_staff_assignments(staff, observations, assignments)
    headers = observations_names
    data = [[", ".join(assignments_dict[(o_name, t)]) for o_name in ob_names] for t in range(12)]

    # generate CSV file of table 1 for downloading
    filename = "patient_col.csv"
    export_to_csv(data, headers, filename, index=shift_hours)

    df_t1 = pd.DataFrame(data)
    df_t1.index = shift_hours
    df_t1 = df_t1.rename(columns=dict(zip(df_t1.columns, headers)))
    st.write("##### Table 1: Patient names / observations along the top.")
    st.dataframe(df_t1, width=1200, height=455)

    # Table 2: Staff names are column headers. Rows labels are shift hours. Each cell contains the patient the staff
    # member(s) are allocated to at that time.
    schedule = [["OFF" for _ in staff] for _ in range(12)]
    assignments_count = [0] * len(staff)  # initialize a list to store the number of assignments for each staff member
    for t in range(12):
        for i, s in enumerate(staff):
            for o in observations:
                if assignments[(s["id"], o["id"], t)].value() == 1:
                    schedule[t][i] = o["name"]
                    assignments_count[
                        i] += 1  # increment the assignment count for the staff member whose column the cell is in
    # Add a row at the bottom of the schedule matrix to display the assignment count for each staff member
    assignments_row = [str(count) for count in assignments_count]
    schedule.append(assignments_row)
    shift_hours.append("TOTAL")
    headers = [s["name"] for s in staff]
    df_t2 = pd.DataFrame(schedule)
    df_t2.index = shift_hours
    df_t2 = df_t2.rename(columns=dict(zip(df_t2.columns, headers)))

    # Hide columns where the value in the TOTAL row is less than 1. This omits staff not assigned to any observations.
    total_row = df_t2.loc["TOTAL"]
    total_row_int = total_row.astype(int)
    df_t2 = df_t2.loc[:, total_row_int >= 1]

    st.write("##### Table 2: Staff names along the top")
    st.dataframe(df_t2, width=1200, height=490)

    # add the row index as a column in the DataFrames
    df_t1.insert(0, '', df_t1.index)
    df_t2.insert(0, '', df_t2.index)

    # save both tables to a PDF file
    with PdfPages('tables.pdf') as pdf:
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        ax.table(cellText=df_t2.values, colLabels=df_t2.columns, loc='center')
        pdf.savefig(fig)

        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        ax.table(cellText=df_t1.values, colLabels=df_t1.columns, loc='center')
        pdf.savefig(fig)

        # generate CSV file of table 2 for downloading
        filename = "staff_col.csv"
        export_to_csv(schedule, headers, filename, index=shift_hours)

    st.download_button(label="Download Tables as a PDF", data=open('tables.pdf', 'rb'), mime='pdf/a4')
    st.download_button(label="Download Table 1 as an editable CSV file", data=open('patient_col.csv', 'rb'), mime='text/csv')
    st.download_button(label="Download Table 2 as an editable CSV file", data=open('staff_col.csv', 'rb'), mime='text/csv')
    # st.download_button(
    #     label='Download CSV',
    #     data=csv.encode(),
    #     file_name='my_file.csv',
    #     mime='text/csv'
    # )
    # Display the assignments
    # for s in staff:
    #     st.markdown(f"\n###### Allocations for {s['name']}:")
    #     for o in observations:
    #         for t in range(12):
    #             if assignments[(s["id"], o["id"], t)].value() == 1:
    #                 st.write(f"{s['name']} allocated to {o['name']} at time {t}")
