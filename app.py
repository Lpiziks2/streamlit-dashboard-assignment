# Importing libaries
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import time

@st.cache_data
def load_data():
    # Define file paths
    file_paths = {
        'Kiva Loans': '/Users/laurispiziks/Desktop/VS code/kiva_loans.csv',
        'Kiva MPI Region Locations': '/Users/laurispiziks/Desktop/VS code/kiva_mpi_region_locations.csv',
        'Loan Theme IDs': '/Users/laurispiziks/Desktop/VS code/loan_theme_ids.csv',
        'Loan Themes by Region': '/Users/laurispiziks/Desktop/VS code/loan_themes_by_region.csv'
    }

    df_loans = pd.read_csv(file_paths['Kiva Loans'])
    df_mpi = pd.read_csv(file_paths['Kiva MPI Region Locations'])
    df_theme_ids = pd.read_csv(file_paths['Loan Theme IDs'])
    df_themes_by_region = pd.read_csv(file_paths['Loan Themes by Region'])

    dataframes = {
        'Kiva Loans': df_loans,
        'Kiva MPI Region Locations': df_mpi,
        'Loan Theme IDs': df_theme_ids,
        'Loan Themes by Region': df_themes_by_region
    }

    return dataframes

# Use the cached function to load the data
dataframes = load_data()

# Set the app title and sidebar header
st.title("Kiva Loans Dashboard 📊")
st.sidebar.header("Explore the Kiva Data")

# Sidebar option for selection
option = st.sidebar.selectbox(
    'What would you like to explore? ',
    ['Introduction', 'Borrower Details', 'Kiva Loan Themes', 'Monthly Loan Analysis', 'Average Kiva Customer']
)

# Welcome Page
# Welcome Page
if option == 'Introduction':
    st.markdown("""
        ## Welcome to the Kiva Loans Dashboard
        Kiva is a platform dedicated to helping underserved communities around the world by providing loans to individuals without access to traditional financial services. This dashboard allows you to explore key insights into Kiva's loan data, including loan distribution, repayment patterns, and loan activities.

        Navigate through the sections to analyze borrower details, loan themes, monthly loan trends, and Kiva's target customers.
    """)

    # Expander for the objectives
    with st.expander("🎯  **Objectives of the Dashboard**"):
        st.markdown("""
        The goal of this dashboard is to analyze Kiva's loan data and address the following key questions:

        ### 1. Borrower Details:
        - Where are Kiva's customers located around the world? (Map of the customer distribution)
        - How is gender distributed among borrowers in selected countries?
        - What are the repayment patterns in selected countries?

        ### 2. Kiva Loan Themes:
        - Which loan themes are the most common?
        - What are the top loan activities?

        ### 3. Monthly Loan Analysis:
        - How are loans disbursed on a monthly basis?
        - Use the sidebar to filter the date range and explore trends in monthly loan amounts.

        ### 4. Kiva Target Customer:
        - Who are the primary customers Kiva serves?
        """)


# Borrowers Details Page
elif option == 'Borrower Details':
    # Page title
    st.title('Borrower Details')

    # Load the loans data
    df_loans = dataframes['Kiva Loans']

    st.write("In this section, you'll find key insights into borrower demographics and loan distribution patterns across different countries. The map below shows the geographical distribution of loans, and the charts further explore gender distribution and repayment patterns in selected countries. Use the filters in the sidebar to customize your view and explore specific trends.")

    # Map Section
    st.title("Map View")

    # Load the loan themes by region data
    df_themes_by_region = dataframes['Loan Themes by Region']

    # Check if 'lat' and 'lon' columns exist, and clean the data by dropping missing values
    if 'lat' in df_themes_by_region.columns and 'lon' in df_themes_by_region.columns:
        df_themes_by_region_cleaned = df_themes_by_region[['lat', 'lon']].dropna()

        # Display the map with latitude and longitude points
        st.map(df_themes_by_region_cleaned)

    # Insight text under the Map
    st.write("🌍 **Insight**: This map shows the geographical distribution of loans, providing an overview of where the loans are concentrated. You can explore different regions to see the spread of loan activities around the world.")

    # Add space between elements for better layout
    st.write("\n")

    # Sidebar filter for loan distribution
    st.sidebar.header('Filters for Loan Distribution')

    # Clean the gender data to only include 'male' and 'female'
    df_loans_cleaned = df_loans[df_loans['borrower_genders'].isin(['male', 'female'])]

    # Get the list of all countries and allow multiselect for filtering
    all_countries = df_loans_cleaned['country'].unique().tolist()
    selected_countries = st.sidebar.multiselect(
        'Select countries:',
        options=all_countries,
        default=all_countries[:5],  # Default selection of the first 5 countries
        help="Select up to 5 countries."
    )

    # Filter the loan data by the selected countries
    df_filtered = df_loans_cleaned[df_loans_cleaned['country'].isin(selected_countries)]

    # Add space before the next section
    st.write("\n")
    
    # Subheader for gender distribution section
    st.subheader('Gender Distribution in Selected Countries')

    # Group data by gender and country, summing the number of loans (lender_count)
    gender_by_country = df_filtered.groupby(['country', 'borrower_genders'])['lender_count'].sum().reset_index()

    # Create a bar chart to visualize gender distribution across selected countries
    gender_chart = alt.Chart(gender_by_country).mark_bar().encode(
        x=alt.X('country:N', title='Country', axis=alt.Axis(labelAngle=-45),  # Rotate x-axis labels for readability
                sort=alt.EncodingSortField(field='lender_count', op='sum', order='descending')),  # Sort by lender count
        y=alt.Y('lender_count:Q', title='Number of Loans'),
        color=alt.Color('borrower_genders:N', title='Gender'),  # Color by gender
        tooltip=['country', 'lender_count', 'borrower_genders']  # Tooltips showing detailed info
    ).properties(width=700, height=400)

    # Display the gender distribution chart
    st.altair_chart(gender_chart, use_container_width=True)

    # Insight text under the Gender Distribution chart
    st.write("👥 **Insight**: This chart shows how loan distribution varies by gender across the selected countries. You can adjust the country selection using the sidebar filter to explore gender-based lending trends.")

    # Add space before the next section
    st.write("\n")
    
    # Subheader for repayment patterns section
    st.subheader('Repayment Patterns Across Selected Countries')

    # Group data by country and repayment interval, summing the number of loans (lender_count)
    repayment_by_country = df_filtered.groupby(['country', 'repayment_interval'])['lender_count'].sum().reset_index()

    # Create a stacked bar chart for repayment intervals across selected countries
    repayment_chart = alt.Chart(repayment_by_country).mark_bar().encode(
        x=alt.X('country:N', title='Country', axis=alt.Axis(labelAngle=-45),  # Rotate x-axis labels for readability
                sort=alt.EncodingSortField(field='lender_count', op='sum', order='descending')),  # Sort by lender count
        y=alt.Y('lender_count:Q', title='Number of Loans'),
        color=alt.Color('repayment_interval:N', title='Repayment Interval'),  # Color by repayment interval
        tooltip=['country', 'repayment_interval', 'lender_count']  # Tooltips showing detailed info
    ).properties(width=700, height=400)

    # Display the repayment patterns chart
    st.altair_chart(repayment_chart, use_container_width=True)

    # Insight text under the Repayment Patterns chart
    st.write("💰 **Insight**: The repayment patterns shown in this chart give an overview of how borrowers from different countries prefer to structure their loan repayments. You can explore variations in repayment behavior by adjusting the country selection in the sidebar.")


# Themes Page
elif option == "Kiva Loan Themes":
    st.title("Kiva Loan Themes")


    st.markdown("This section displays the most frequent loan themes and activities. Use the sidebar to filter the top items and choose the sorting order.")

    # Add space before the next section
    st.write("\n")

    # Sidebar filter controls
    st.sidebar.header('Filter Loan Themes and Activities')
    top_n = st.sidebar.slider('Select number of top items to display:', 3, 10, 5)
    sort_order = st.sidebar.radio('Select sorting order:', ['Descending', 'Ascending'])
    ascending = sort_order == 'Ascending'

    # Loan Themes Section
    df_theme_ids = dataframes['Loan Theme IDs']
    loan_theme_counts = df_theme_ids['Loan Theme Type'].value_counts().reset_index()
    loan_theme_counts.columns = ['Loan Theme Type', 'Number of Loans']
    loan_theme_counts = loan_theme_counts.sort_values('Number of Loans', ascending=ascending).head(top_n)

    st.subheader("Top Loan Themes")
    theme_chart = alt.Chart(loan_theme_counts).mark_bar().encode(
        x=alt.X('Loan Theme Type:N', sort=alt.EncodingSortField(field='Number of Loans', order=sort_order.lower()), 
                axis=alt.Axis(labelAngle=-45)),  # Rotate labels by 45 degrees
        y='Number of Loans:Q',
        color='Loan Theme Type:N',
        tooltip=['Loan Theme Type', 'Number of Loans']
    ).properties(width=700, height=400)

    st.altair_chart(theme_chart, use_container_width=True)

    st.write("💡 **Insight**: The chart above shows the most frequent loan themes in the Kiva dataset. You can see how the different themes vary in loan count. Use the sidebar to filter and sort the data!")

    # Add space before the next section
    st.write("\n")

    # Loan Activities Section
    df_loans = dataframes['Kiva Loans']
    activity_counts = df_loans['activity'].value_counts().reset_index()
    activity_counts.columns = ['Loan Activity Type', 'Number of Loans']
    activity_counts = activity_counts.sort_values('Number of Loans', ascending=ascending).head(top_n)

    st.subheader("Top Loan Activities")
    activity_chart = alt.Chart(activity_counts).mark_bar().encode(
        x=alt.X('Loan Activity Type:N', sort=alt.EncodingSortField(field='Number of Loans', order=sort_order.lower()), 
                axis=alt.Axis(labelAngle=-45)),  # Rotate labels by 45 degrees
        y='Number of Loans:Q',
        color='Loan Activity Type:N',
        tooltip=['Loan Activity Type', 'Number of Loans']
    ).properties(width=700, height=400)

    st.altair_chart(activity_chart, use_container_width=True)

    st.write("📊 **Insight**: The chart above shows the most common loan activities. See how the activities are distributed across the dataset. Explore the top activities by adjusting the filter in the sidebar.")


# Monthly Results Page
elif option == 'Monthly Loan Analysis':
    st.title("Monthly Loan Analysis")

    st.write("This section analyzes the monthly loan disbursements over a selected time period. Use the sidebar to filter the date range and observe trends in loan amounts distributed each month. The chart below updates dynamically as data loads, giving you a clear view of how loan disbursements have evolved over time. Adjust the date range to explore different timeframes and patterns in loan activities.")

    # Data preparation and cleaning
    df_loans = dataframes['Kiva Loans']
    df_loans['date'] = pd.to_datetime(df_loans['date'], errors='coerce')
    df_loans = df_loans.dropna(subset=['date'])  # Remove rows with invalid dates
    df_loans = df_loans[df_loans['loan_amount'] > 0]  # Filter positive loan amounts

    # Filter by date range
    start_date, end_date = st.sidebar.date_input("Select date range:", [df_loans['date'].min(), df_loans['date'].max()])
    df_loans = df_loans[(df_loans['date'] >= pd.Timestamp(start_date)) & (df_loans['date'] <= pd.Timestamp(end_date))]

    # Aggregate monthly loan amounts
    df_loans['year_month'] = df_loans['date'].dt.to_period('M')
    monthly_loan_amount = df_loans.groupby('year_month')['loan_amount'].sum()

    # Remove the last month (July 2017 in this case)
    monthly_loan_amount = monthly_loan_amount[monthly_loan_amount.index != '2017-07']

    st.subheader(f"Monthly Loan Amount Trend ({start_date} to {end_date})")

    # Line chart with progress bar
    progress_bar = st.sidebar.progress(0)
    chart = st.line_chart([])

    for i, (month, amount) in enumerate(monthly_loan_amount.items()):
        chart.add_rows(pd.DataFrame({'Loan Amount': [amount]}, index=[month.to_timestamp()]))
        progress_bar.progress((i + 1) / len(monthly_loan_amount))
        time.sleep(0.1)

    progress_bar.empty()
    st.button("Re-run")

# Our Average Customer Page
elif option == 'Average Kiva Customer':
    st.title(" Kiva Target Customer")

    # Load the loans data
    df_loans = dataframes['Kiva Loans']

    # Clean the gender data
    df_loans_cleaned = df_loans[df_loans['borrower_genders'].isin(['male', 'female'])]

    # Calculate the average loan amount (in USD) and convert to Philippine peso (PHP)
    usd_to_php_rate = 56  # Example conversion rate (1 USD = 56 PHP)
    average_loan_amount_usd = df_loans['loan_amount'].mean()
    average_loan_amount_php = average_loan_amount_usd * usd_to_php_rate

    # Most common gender
    most_common_gender = df_loans_cleaned['borrower_genders'].mode()[0]

    # Most common country
    most_common_country = df_loans['country'].mode()[0]

    # Most common loan purpose (activity)
    most_common_activity = df_loans['activity'].mode()[0]

    # Most common repayment plan
    most_common_repayment_plan = df_loans['repayment_interval'].mode()[0]

    # Display the information
    st.markdown("### The Average Kiva Borrower")
    
    st.write(f"**Gender**: {most_common_gender.capitalize()}")
    st.write(f"**Country**: {most_common_country}")
    
    st.write(f"**Average Loan Amount**: ${average_loan_amount_usd:,.2f} USD (~₱{average_loan_amount_php:,.2f} PHP)")
    st.write(f"**Loan Purpose**: {most_common_activity}")
    st.write(f"**Repayment Plan**: {most_common_repayment_plan.capitalize()}")

    st.image('/Users/laurispiziks/Desktop/VS code/Kiva customer.webp', caption='Image generated using DALL·E.', use_column_width=True)



