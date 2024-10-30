#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import pyreadstat
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="L2Geo Baseline 2024: Daily Data Quality Check Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Define the correct password
def check_password():
    def password_entered():
        if st.session_state["password"] == "hi":  # Replace 'your_password' with your desired password
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password in session state after check
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect password")
        return False
    else:
        # Password correct
        return True

# Only show the main app if the password is correct
if check_password():
    # Your main Streamlit app code goes here
    st.write("")
    # Your app's content can be added below...


    st.title("Listening to South Caucasus ") 

    # Enable Altair dark theme for charts
    alt.themes.enable("dark")

    # Custom CSS to make the radio buttons horizontal
    st.markdown("""
        <style>
        .stRadio > div {
            flex-direction: row;
        }
        </style>
    """, unsafe_allow_html=True)



    # Horizontal navigation bar using st.radio
    selected_page = st.radio("", ["Home", "L2Geo", "L2Arm"])
    if selected_page == "Home":
        st.title("Data Quality Dashboard")

    # Page 1: Data Quality
    if selected_page == "L2Geo":
        # st.title("Data Quality Dashboard")

        # Create the tabs for Page 1
        tabs = st.tabs(["Passport", "Roster", "Migration", "Education", "ICT", "Employment", "Social Benefits", "Nonwage Revenue", "Food", "Nonfood", "Dwelling", "Durables",  "Agriculture", "Perception"])

        with tabs[0]:
            st.header("Passport Module")
            st.write("This is the Passport Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)          
            file_path = "./data/geo0pass_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path) 
            missing_symbols = ["."]
            # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Data Filter')

                # Convert date columns to datetime if not already done
                df0['start_date'] = pd.to_datetime(df0['start_date'], errors='coerce')
                df0['end_date'] = pd.to_datetime(df0['end_date'], errors='coerce')

                # Date filter (single date or range)
                start_date_filter = st.date_input("Start Date", pd.to_datetime(df0['start_date'].min()))
                end_date_filter = st.date_input("End Date", pd.to_datetime(df0['end_date'].max()))

                # Filter by icode, psu, region, urban
                selected_agree = st.multiselect("Filter by Agreement", df0['agreement'].unique())
                selected_region = st.multiselect("Filter by Region", df0['region'].unique())
                selected_urban = st.multiselect("Filter by Urban/Rural", df0['urban'].unique())
                selected_psu = st.multiselect("Filter by PSU", df0['psu'].unique())
                selected_icode = st.multiselect("Filter by Enumerator", df0['icode'].unique())

                # Apply date filters
                filtered_data = df0[
                    (df0['start_date'] >= pd.to_datetime(start_date_filter)) &
                    (df0['end_date'] <= pd.to_datetime(end_date_filter))
                ]

                # Apply filters for other selections if any
                if selected_agree:
                    filtered_data = filtered_data[filtered_data['agreement'].isin(selected_agree)]

                if selected_icode:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode)]
                
                if selected_psu:
                    filtered_data = filtered_data[filtered_data['psu'].isin(selected_psu)]
                
                if selected_region:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region)]
                
                if selected_urban:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban)]

            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
            daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')

            # Plot the line graph using Altair with dynamic width and custom styling
            line_chart = alt.Chart(daily_submissions).mark_line(
                color='red',  # Red line color
                strokeWidth=2  # Thickness of the line
            ).encode(
                x=alt.X('start_date:T',
                        axis=alt.Axis(
                            format='%Y-%m-%d',  # Adjust the date format (Year/Month/Day)
                            labelAngle=-45,  # Angle the labels for better readability
                            labelOverlap=False,
                            title='Submission Date'
                        )),
                y=alt.Y('total_submissions:Q', title='Total Submissions'),
                tooltip=[alt.Tooltip('start_date:T', title='Date'), alt.Tooltip('total_submissions', title='Total Submissions')]
            ).properties(
                # title='Daily Total Submissions (Agreement == 1)',
                width='container',  # Dynamically adjust width based on the container size
                height=400
            ).interactive()

            # Add points to the line graph with custom styling
            points = alt.Chart(daily_submissions).mark_point(
                filled=True,  # Filled dots
                color='white',  # White dot color
                size=100,  # Size of the points
                stroke='red',  # Red circle around the dots
                strokeWidth=2  # Thickness of the red circle
            ).encode(
                x='start_date:T',
                y='total_submissions:Q'
            )

            # Combine the line and points together
            combined_chart = line_chart + points

            # Display the chart in Streamlit
            st.subheader("Daily Total Submissions")
            st.altair_chart(combined_chart, use_container_width=True)  # Use container width to make it responsive

            # # Display the chart in Streamlit
            # st.subheader("Line Graph: Daily Total Submissions (Agreement == 1)")
            # st.altair_chart(line_chart)   
            # 

            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=['dur_total',"dur_food"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")

            st.subheader("Correlation Matrix")

            corr_vars = st.multiselect("Select variables to correlate", numeric_cols)  # Show only numeric variables
            corr = filtered_data[corr_vars].corr()

        
            
            # If variables are selected
            if corr_vars:
                # Calculate the correlation matrix for the selected variables
                corr = filtered_data[corr_vars].corr()

                # Plot the correlation matrix
                fig, ax = plt.subplots(figsize=(10, 8))  # Adjust the figure size as needed
                # Create the heatmap with formatting adjustments
                sns.heatmap(
                    corr, 
                    annot=True, 
                    cmap='coolwarm', 
                    fmt='.2f',  # 2 decimal places
                    annot_kws={"size": 8},  # Adjust the size of the values inside the cells
                    cbar_kws={'shrink': 0.8, 'ticks': [0.2, 0.4, 0.6, 0.8, 1.0]},  # Adjust the size of the color bar (legend)
                    ax=ax
                )

                # Customize the x and y axis labels
                plt.xticks(rotation=45, ha='right', fontsize=8)  # Rotate x-axis labels, set font size
                plt.yticks(fontsize=8)  # Set y-axis label font size

                # Customize the colorbar (legend) label size
                cbar = ax.collections[0].colorbar
                cbar.ax.tick_params(labelsize=8)  # Set the size of the colorbar (legend) values

                # Display the heatmap in Streamlit
                st.pyplot(fig)  
            else:
                st.write("Please select variables to correlate")

            # Allow users to select two variables for scatter plot
            st.subheader("Scatter Plot between Two Variables")

            # Allow users to select two variables for scatter plot, with default variables pre-selected
            default_vars = ['corrected_dur_total', 'corrected_dur_food']
            scatter_vars = st.multiselect("Select two variables for scatter plot", filtered_data.columns, default=default_vars)


            # Ensure exactly two variables are selected
            if len(scatter_vars) == 2:
                # Create a scatter plot between the selected two variables
                fig, ax = plt.subplots()
                sns.scatterplot(x=filtered_data[scatter_vars[0]], y=filtered_data[scatter_vars[1]], ax=ax)
                
                # Set axis labels
                ax.set_xlabel(scatter_vars[0])
                ax.set_ylabel(scatter_vars[1])
                ax.set_title(f"Scatter Plot: {scatter_vars[0]} vs {scatter_vars[1]}")

                # Display the scatter plot in Streamlit
                st.pyplot(fig)
            else:
                st.write("Please select exactly two variables to create a scatter plot")


            # Heatmap
            def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
                heatmap = alt.Chart(input_df).mark_rect().encode(
                    y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="icode", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
                    x=alt.X(f'{input_x}:O', axis=alt.Axis(title="date", titleFontSize=18, titlePadding=15, titleFontWeight=900)), 
                    color=alt.Color(f'max({input_color}):Q',
                                    legend=alt.Legend(title="", labelFontSize=12, titleFontSize=14),  # Enable the legend with formatting
                                    scale=alt.Scale(scheme=input_color_theme)),
                    stroke=alt.value('black'),
                    strokeWidth=alt.value(0.25),
                ).properties(
                    width=900
                ).configure_axis(
                    labelFontSize=12,
                    titleFontSize=12
                )
                return heatmap        
            

            st.subheader("Daily Interviews by Enumerators")
            # Group by 'start_date' and 'icode' and calculate the total submissions
            tot_subm = agreed.groupby(['start_date', 'icode']).size().reset_index(name='nsubm')

            # List of color themes for the heatmap
            color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
            selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

            # Create the heatmap using the grouped DataFrame `tot_subm`
            heatmap = make_heatmap(tot_subm, 'icode', 'start_date', 'nsubm', selected_color_theme)

            # Display the heatmap
            st.altair_chart(heatmap, use_container_width=True)


        with tabs[1]:
            st.header("Roster Module - Data Quality")
            st.write("This is the Roster Module for Data Quality.")

            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/roster_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path) 
            missing_symbols = ["."]
            # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            with st.sidebar:
                st.title('Roster Filter')

                # Convert date columns to datetime if not already done
                df0['start_date'] = pd.to_datetime(df0['start_date'], errors='coerce')
                df0['end_date'] = pd.to_datetime(df0['end_date'], errors='coerce')

                # Date filter (single date or range)
 
                # Filter by icode, psu, region, urban
                selected_agree = st.multiselect("Filter by Agreement", df0['agreement'].unique())
                selected_region = st.multiselect("Filter by Region", df0['region'].unique())
                selected_urban = st.multiselect("Filter by Urban/Rural", df0['urban'].unique())
                selected_psu = st.multiselect("Filter by PSU", df0['psu'].unique())
                selected_icode = st.multiselect("Filter by Enumerator", df0['icode'].unique())
                selected_gender = st.multiselect("Filter by Gender", df0['gender'].unique())
                # Apply date filters
               
                filtered_data = df0.copy()

                if selected_icode:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode)]

                if selected_region:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region)]
                
                if selected_urban:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban)]

                if selected_gender:
                    filtered_data = filtered_data[filtered_data['gender'].isin(selected_gender)]            
                    



            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_roster"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")


            # Allow users to select two variables for scatter plot
            st.subheader("Scatter Plot between Two Variables")

            # Allow users to select two variables for scatter plot, with default variables pre-selected
            default_vars = ['hhsize', 'corrected_dur_roster']
            scatter_vars = st.multiselect("Select two variables for scatter plot", filtered_data.columns, default=default_vars)


            # Ensure exactly two variables are selected
            if len(scatter_vars) == 2:
                # Create a scatter plot between the selected two variables
                fig, ax = plt.subplots()
                sns.scatterplot(x=filtered_data[scatter_vars[0]], y=filtered_data[scatter_vars[1]], ax=ax)
                
                # Set axis labels
                ax.set_xlabel(scatter_vars[0])
                ax.set_ylabel(scatter_vars[1])
                ax.set_title(f"Scatter Plot: {scatter_vars[0]} vs {scatter_vars[1]}")

                # Display the scatter plot in Streamlit
                st.pyplot(fig)
            else:
                st.write("Please select exactly two variables to create a scatter plot")

            st.title("Histogram of Selected Variable")

# Dropdown to select a numeric column in the dataframe
 
            selected_numeric_column = st.selectbox("Select a numeric variable for histogram:", numeric_cols, index=numeric_cols.get_loc("age"))

            # Dropdown to select a categorical column for grouping
            categorical_columns = filtered_data.select_dtypes(include=['int64']).columns
            selected_category_column = st.selectbox("Select a category to separate by:", categorical_columns, index=categorical_columns.get_loc("gender"))

# Plot separate histograms based on the selected category
            if selected_numeric_column and selected_category_column:
                st.write(f"Separate Histograms of '{selected_numeric_column}' for each '{selected_category_column}'")
            
                # Set aesthetic parameters
                sns.set_style("whitegrid")
            
                # Create the faceted histogram
                g = sns.FacetGrid(filtered_data, col=selected_category_column, height=4, aspect=1.2, palette="Set2")
                g.map(sns.histplot, selected_numeric_column, kde=False, color="skyblue", alpha=0.7)
            
                # Customize each plot
                g.set_titles(col_template="{col_name}")
                g.set_axis_labels(selected_numeric_column, "Frequency")
                
                # Display the plot in Streamlit
                st.pyplot(g.fig)

        with tabs[2]:
            st.header("Migration Module")
            st.write("This is the Migration Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/migration_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Migration Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_m = st.multiselect("Filter by Region", df0['region'].unique(), key="region_filter")
                selected_urban_m = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="urban_filter")
                selected_icode_m = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="icode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_m:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_m)]
            
                if selected_urban_m:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_m)]
            
                if selected_icode_m:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_m)]
            

            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_mig"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")


        with tabs[3]:
            st.header("Education Module")
            st.write("This is the Education Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/educ_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Education Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="edregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="edurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="edicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
 


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_edu"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")



        with tabs[4]:
            st.header("ICT Module")
            st.write("This is the ICT Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/ict_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
             # Sidebar
            with st.sidebar:
                st.title('ICT Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="ictregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="icturban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="icticode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
 


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_ict"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")

        with tabs[5]:
            st.header("Employment Module")
            st.write("This is the Employment Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/emp_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            with st.sidebar:
                st.title('Employment Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="empregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="empurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="empicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
 

            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_emp"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")


        with tabs[6]:
            st.header("Social Benefits Module")
            st.write("This is the Social Benefits Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/soc_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            with st.sidebar:
                st.title('Social Benefits Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="socregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="socurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="socicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_soc"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")
                
        with tabs[7]:
            st.header("Non-Wage Income Module")
            st.write("This is the Non-Wage Income Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/nonwage_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Non-Wage Income Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="nwregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="nwurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="nwicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_nonwage"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")


        with tabs[8]:
            st.header("Food Module")
            st.write("This is the Food Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)

           # @st.cache_data

            def load_data():
                url = "https://www.dropbox.com/scl/fi/1gnzhj243mtsu6axsyr9d/food_geo.dta?rlkey=f84yoglmiq915kart9tmooz0w&st=jm56o5rr&dl=1"  # Replace with your actual link
                try:
         # Step 1: Download the .dta file
                    response = requests.get(url)
                    response.raise_for_status()
        
        # Step 2: Save the file locally
                    with open("data.dta", "wb") as file:
                          file.write(response.content)
        
        # Step 3: Read the .dta file with pandas
                    df = pd.read_stata("data.dta")
                    return df
    
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading data: {e}")
                    return None
                except Exception as e:
                    print(f"Error loading data: {e}")
                    return None
            
            df0 = load_data()            
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Food Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="foodregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="foodurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="foodicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')
            daily_food = filtered_data.groupby('start_date')['food_num'].mean().reset_index()

            # Display the chart in Streamlit
            line_chart = alt.Chart(daily_food).mark_line(
                color='red',  # Red line color
                strokeWidth=2  # Thickness of the line
            ).encode(
                x=alt.X('start_date:T',
                        axis=alt.Axis(
                            format='%Y-%m-%d',  # Adjust the date format (Year/Month/Day)
                            labelAngle=-45,  # Angle the labels for better readability
                            labelOverlap=False,
                            title='Submission Date'
                        )),
                y=alt.Y('food_num:Q', title='Selected food count'),
                tooltip=[alt.Tooltip('start_date:T', title='Date'), alt.Tooltip('food_num', title='Selected food count')]
            ).properties(
                # title='Daily Total Submissions (Agreement == 1)',
                width='container',  # Dynamically adjust width based on the container size
                height=400
            ).interactive()

            # Add points to the line graph with custom styling
            points = alt.Chart(daily_food).mark_point(
                filled=True,  # Filled dots
                color='white',  # White dot color
                size=100,  # Size of the points
                stroke='red',  # Red circle around the dots
                strokeWidth=2  # Thickness of the red circle
            ).encode(
                x='start_date:T',
                y='food_num:Q'
            )

            # Combine the line and points together
            combined_chart = line_chart + points

            # Display the chart in Streamlit
            st.subheader("Daily Selected food count")
            st.altair_chart(combined_chart, use_container_width=True)  # Use container width to make it responsive

            
            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_food", "dur_food"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")    

        with tabs[9]:
            st.header("Non-Food Module")
            st.write("This is the Non-Food Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            def load_data():
                url = "https://www.dropbox.com/scl/fi/seu41v8w0oco9r37zb6qm/nonfood_geo.dta?rlkey=0izk4bhnpw38m6bxhnkfwmaql&st=08r6pa4n&dl=1"  # Replace with your actual link
                try:
         # Step 1: Download the .dta file
                    response = requests.get(url)
                    response.raise_for_status()
        
        # Step 2: Save the file locally
                    with open("data.dta", "wb") as file:
                          file.write(response.content)
        
        # Step 3: Read the .dta file with pandas
                    df = pd.read_stata("data.dta")
                    return df
    
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading data: {e}")
                    return None
                except Exception as e:
                    print(f"Error loading data: {e}")
                    return None
            
            df0 = load_data()                        
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Non-Food Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="nfregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="nfurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="nficode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_nfa", "dur_nfa"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")    

        with tabs[10]:
            st.header("Dwelling Module")
            st.write("This is the Dwelling Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/dwelling_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Dwelling Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="dwregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="dwurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="dwicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
             


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_dwa", "dur_dwa"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")    

        with tabs[11]:
            st.header("Durable Goods Module")
            st.write("This is the Durable Goods Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/durables_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Durables Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="drregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="drurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="dricode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_dwd", "dur_dwd"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")    


        with tabs[12]:
            st.header("Agriculture Module")
            st.write("This is the Agriculture Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/agr_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Agriculture Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="agregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="agurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="agicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            

            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_agriculture", "dur_agriculture"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")    

        with tabs[13]:
            st.header("Perception Module")
            st.write("This is the Perception Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/perc_geo.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Perception Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="prregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="prurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="pricode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            

            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_perc", "dur_perc"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")  
                
    
    # Page 2: Fieldwork Monitoring
    elif selected_page == "L2Arm":
        st.title("Fieldwork Monitoring Dashboard")

        # Create the tabs for Page 2
        tabs = st.tabs(["Passport", "Roster", "Migration", "Education", "ICT", "Employment", "Social Benefits", "Nonwage Revenue", "Food", "Nonfood", "Dwelling", "Durables",  "Agriculture", "Perception"])

        with tabs[0]:
            st.header("Passport Module")
            st.write("This is the Passport Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/geo0pass_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
            # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Data Filter')

                # Convert date columns to datetime if not already done
                df0['start_date'] = pd.to_datetime(df0['start_date'], errors='coerce')
                df0['end_date'] = pd.to_datetime(df0['end_date'], errors='coerce')

                # Date filter (single date or range)
                start_date_filter = st.date_input("Start Date", pd.to_datetime(df0['start_date'].min()))
                end_date_filter = st.date_input("End Date", pd.to_datetime(df0['end_date'].max()))

                # Filter by icode, psu, region, urban
                selected_agree = st.multiselect("Filter by Agreement", df0['agreement'].unique())
                selected_region = st.multiselect("Filter by Region", df0['region'].unique())
                selected_urban = st.multiselect("Filter by Urban/Rural", df0['urban'].unique())
                selected_psu = st.multiselect("Filter by PSU", df0['psu'].unique())
                selected_icode = st.multiselect("Filter by Enumerator", df0['icode'].unique())

                # Apply date filters
                filtered_data = df0[
                    (df0['start_date'] >= pd.to_datetime(start_date_filter)) &
                    (df0['end_date'] <= pd.to_datetime(end_date_filter))
                ]

                # Apply filters for other selections if any
                if selected_agree:
                    filtered_data = filtered_data[filtered_data['agreement'].isin(selected_agree)]

                if selected_icode:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode)]
                
                if selected_psu:
                    filtered_data = filtered_data[filtered_data['psu'].isin(selected_psu)]
                
                if selected_region:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region)]
                
                if selected_urban:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban)]

            # Donut chart
            def make_donut(input_response, input_text, input_color):
                if input_color == 'blue':
                    chart_color = ['#29b5e8', '#155F7A']
                if input_color == 'green':
                    chart_color = ['#27AE60', '#12783D']
                if input_color == 'orange':
                    chart_color = ['#F39C12', '#875A12']
                if input_color == 'red':
                    chart_color = ['#E74C3C', '#781F16']
                    
                source = pd.DataFrame({
                    "Topic": ['', input_text],
                    "% value": [100-input_response, input_response]
                })
                source_bg = pd.DataFrame({
                    "Topic": ['', input_text],
                    "% value": [100, 0]
                })
                    
                plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
                    theta="% value",
                    color= alt.Color("Topic:N",
                                    scale=alt.Scale(
                                        #domain=['A', 'B'],
                                        domain=[input_text, ''],
                                        # range=['#29b5e8', '#155F7A']),  # 31333F
                                        range=chart_color),
                                    legend=None),
                ).properties(width=130, height=130)
                    
                text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
                plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
                    theta="% value",
                    color= alt.Color("Topic:N",
                                    scale=alt.Scale(
                                        # domain=['A', 'B'],
                                        domain=[input_text, ''],
                                        range=chart_color),  # 31333F
                                    legend=None),
                ).properties(width=130, height=130)
                return plot_bg + plot + text

            # Convert population to text 
            def format_number(num):
                if num > 1000000:
                    if not num % 1000000:
                        return f'{num // 1000000} M'
                    return f'{round(num / 1000000, 1)} M'
                return f'{num // 1000} K'
            

            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
            daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')

            # Plot the line graph using Altair with dynamic width and custom styling
            line_chart = alt.Chart(daily_submissions).mark_line(
                color='red',  # Red line color
                strokeWidth=2  # Thickness of the line
            ).encode(
                x=alt.X('start_date:T',
                        axis=alt.Axis(
                            format='%Y-%m-%d',  # Adjust the date format (Year/Month/Day)
                            labelAngle=-45,  # Angle the labels for better readability
                            labelOverlap=False,
                            title='Submission Date'
                        )),
                y=alt.Y('total_submissions:Q', title='Total Submissions'),
                tooltip=[alt.Tooltip('start_date:T', title='Date'), alt.Tooltip('total_submissions', title='Total Submissions')]
            ).properties(
                # title='Daily Total Submissions (Agreement == 1)',
                width='container',  # Dynamically adjust width based on the container size
                height=400
            ).interactive()

            # Add points to the line graph with custom styling
            points = alt.Chart(daily_submissions).mark_point(
                filled=True,  # Filled dots
                color='white',  # White dot color
                size=100,  # Size of the points
                stroke='red',  # Red circle around the dots
                strokeWidth=2  # Thickness of the red circle
            ).encode(
                x='start_date:T',
                y='total_submissions:Q'
            )

            # Combine the line and points together
            combined_chart = line_chart + points

            # Display the chart in Streamlit
            st.subheader("Daily Total Submissions")
            st.altair_chart(combined_chart, use_container_width=True)  # Use container width to make it responsive

            # # Display the chart in Streamlit
            # st.subheader("Line Graph: Daily Total Submissions (Agreement == 1)")
            # st.altair_chart(line_chart)   
            # 

            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=['dur_total',"dur_food"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")

            st.subheader("Correlation Matrix")

            corr_vars = st.multiselect("Select variables to correlate", numeric_cols)  # Show only numeric variables
            corr = filtered_data[corr_vars].corr()

        
            
            # If variables are selected
            if corr_vars:
                # Calculate the correlation matrix for the selected variables
                corr = filtered_data[corr_vars].corr()

                # Plot the correlation matrix
                fig, ax = plt.subplots(figsize=(10, 8))  # Adjust the figure size as needed
                # Create the heatmap with formatting adjustments
                sns.heatmap(
                    corr, 
                    annot=True, 
                    cmap='coolwarm', 
                    fmt='.2f',  # 2 decimal places
                    annot_kws={"size": 8},  # Adjust the size of the values inside the cells
                    cbar_kws={'shrink': 0.8, 'ticks': [0.2, 0.4, 0.6, 0.8, 1.0]},  # Adjust the size of the color bar (legend)
                    ax=ax
                )

                # Customize the x and y axis labels
                plt.xticks(rotation=45, ha='right', fontsize=8)  # Rotate x-axis labels, set font size
                plt.yticks(fontsize=8)  # Set y-axis label font size

                # Customize the colorbar (legend) label size
                cbar = ax.collections[0].colorbar
                cbar.ax.tick_params(labelsize=8)  # Set the size of the colorbar (legend) values

                # Display the heatmap in Streamlit
                st.pyplot(fig)  
            else:
                st.write("Please select variables to correlate")

            # Allow users to select two variables for scatter plot
            st.subheader("Scatter Plot between Two Variables")

            # Allow users to select two variables for scatter plot, with default variables pre-selected
            default_vars = ['corrected_dur_total', 'corrected_dur_food',]
            scatter_vars = st.multiselect("Select two variables for scatter plot", filtered_data.columns, default=default_vars)


            # Ensure exactly two variables are selected
            if len(scatter_vars) == 2:
                # Create a scatter plot between the selected two variables
                fig, ax = plt.subplots()
                sns.scatterplot(x=filtered_data[scatter_vars[0]], y=filtered_data[scatter_vars[1]], ax=ax)
                
                # Set axis labels
                ax.set_xlabel(scatter_vars[0])
                ax.set_ylabel(scatter_vars[1])
                ax.set_title(f"Scatter Plot: {scatter_vars[0]} vs {scatter_vars[1]}")

                # Display the scatter plot in Streamlit
                st.pyplot(fig)
            else:
                st.write("Please select exactly two variables to create a scatter plot")


            # Heatmap
            def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
                heatmap = alt.Chart(input_df).mark_rect().encode(
                    y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="icode", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
                    x=alt.X(f'{input_x}:O', axis=alt.Axis(title="date", titleFontSize=18, titlePadding=15, titleFontWeight=900)), 
                    color=alt.Color(f'max({input_color}):Q',
                                    legend=alt.Legend(title="", labelFontSize=12, titleFontSize=14),  # Enable the legend with formatting
                                    scale=alt.Scale(scheme=input_color_theme)),
                    stroke=alt.value('black'),
                    strokeWidth=alt.value(0.25),
                ).properties(
                    width=900
                ).configure_axis(
                    labelFontSize=12,
                    titleFontSize=12
                )
                return heatmap        
            

            st.subheader("Daily Interviews by Enumerators")
            # Group by 'start_date' and 'icode' and calculate the total submissions
            tot_subm = agreed.groupby(['start_date', 'icode']).size().reset_index(name='nsubm')

            # List of color themes for the heatmap
            color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
            selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

            # Create the heatmap using the grouped DataFrame `tot_subm`
            heatmap = make_heatmap(tot_subm, 'icode', 'start_date', 'nsubm', selected_color_theme)

            # Display the heatmap
            st.altair_chart(heatmap, use_container_width=True)


        with tabs[1]:
            st.header("Roster Module - Data Quality")
            st.write("This is the Roster Module for Data Quality.")

            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/roster_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
            # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            with st.sidebar:
                st.title('Roster Filter')

                # Convert date columns to datetime if not already done
                df0['start_date'] = pd.to_datetime(df0['start_date'], errors='coerce')
                df0['end_date'] = pd.to_datetime(df0['end_date'], errors='coerce')

                # Date filter (single date or range)
               # start_date_filter = st.date_input("Start Date", pd.to_datetime(df0['start_date'].min()))
               # end_date_filter = st.date_input("End Date", pd.to_datetime(df0['end_date'].max()))

                # Filter by icode, psu, region, urban
                selected_agree = st.multiselect("Filter by Agreement", df0['agreement'].unique())
                selected_region = st.multiselect("Filter by Region", df0['region'].unique())
                selected_urban = st.multiselect("Filter by Urban/Rural", df0['urban'].unique())
                selected_psu = st.multiselect("Filter by PSU", df0['psu'].unique())
                selected_icode = st.multiselect("Filter by Enumerator", df0['icode'].unique())
                selected_gender = st.multiselect("Filter by Gender", df0['gender'].unique())
                # Apply date filters
                #filtered_data = df0[
                 #   (df0['start_date'] >= pd.to_datetime(start_date_filter)) &
                 #   (df0['end_date'] <= pd.to_datetime(end_date_filter))
                #]
                filtered_data = df0.copy()

                # Apply filters for other selections if any
              #  if selected_agree:
               #     filtered_data = filtered_data[filtered_data['agreement'].isin(selected_agree)]

                if selected_icode:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode)]
                
               # if selected_psu:
                #    filtered_data = filtered_data[filtered_data['psu'].isin(selected_psu)]
                
                if selected_region:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region)]
                
                if selected_urban:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban)]

                if selected_gender:
                    filtered_data = filtered_data[filtered_data['gender'].isin(selected_gender)]            
                    



            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_roster"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")


            # Allow users to select two variables for scatter plot
            st.subheader("Scatter Plot between Two Variables")

            # Allow users to select two variables for scatter plot, with default variables pre-selected
            default_vars = ['hhsize', 'corrected_dur_roster']
            scatter_vars = st.multiselect("Select two variables for scatter plot", filtered_data.columns, default=default_vars)


            # Ensure exactly two variables are selected
            if len(scatter_vars) == 2:
                # Create a scatter plot between the selected two variables
                fig, ax = plt.subplots()
                sns.scatterplot(x=filtered_data[scatter_vars[0]], y=filtered_data[scatter_vars[1]], ax=ax)
                
                # Set axis labels
                ax.set_xlabel(scatter_vars[0])
                ax.set_ylabel(scatter_vars[1])
                ax.set_title(f"Scatter Plot: {scatter_vars[0]} vs {scatter_vars[1]}")

                # Display the scatter plot in Streamlit
                st.pyplot(fig)
            else:
                st.write("Please select exactly two variables to create a scatter plot")

            st.title("Histogram of Selected Variable")

# Dropdown to select a numeric column in the dataframe
 
            selected_numeric_column = st.selectbox("Select a numeric variable for histogram:", numeric_cols, index=numeric_cols.get_loc("age"))

            # Dropdown to select a categorical column for grouping
            categorical_columns = filtered_data.select_dtypes(include=['int64']).columns
            selected_category_column = st.selectbox("Select a category to separate by:", categorical_columns, index=categorical_columns.get_loc("gender"))

# Plot separate histograms based on the selected category
            if selected_numeric_column and selected_category_column:
                st.write(f"Separate Histograms of '{selected_numeric_column}' for each '{selected_category_column}'")
            
                # Set aesthetic parameters
                sns.set_style("whitegrid")
            
                # Create the faceted histogram
                g = sns.FacetGrid(filtered_data, col=selected_category_column, height=4, aspect=1.2, palette="Set2")
                g.map(sns.histplot, selected_numeric_column, kde=False, color="skyblue", alpha=0.7)
            
                # Customize each plot
                g.set_titles(col_template="{col_name}")
                g.set_axis_labels(selected_numeric_column, "Frequency")
                
                # Display the plot in Streamlit
                st.pyplot(g.fig)


        with tabs[2]:
            st.header("Migration Module")
            st.write("This is the Migration Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/migration_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Migration Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="mgregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="mgurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="mgicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_mig"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")


        with tabs[3]:
            st.header("Education Module")
            st.write("This is the Education Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/educ_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Education Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="edregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="edurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="edicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
                   


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_edu"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")


        with tabs[4]:
            st.header("ICT Module")
            st.write("This is the ICT Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/ict_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('ICT Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="ictregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="icturban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="icticode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_ict"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")

        with tabs[5]:
            st.header("Employment Module")
            st.write("This is the Employment Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/emp_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Employment Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="empregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="empurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="empicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
                  


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_emp"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")


        with tabs[6]:
            st.header("Social Benefits Module")
            st.write("This is the Social Benefits Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/soc_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Social Benefits Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="scregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="scurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="scicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_soc"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")
                
        with tabs[7]:
            st.header("Non-Wage Income Module")
            st.write("This is the Non-Wage Income Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/nonwage_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Non-Wage Income Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="nwregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="nwurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="nwicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            



            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["dur_nonwage"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")


        with tabs[8]:
            st.header("Food Module")
            st.write("This is the Food Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            def load_data():
                url = "https://www.dropbox.com/scl/fi/g3kasbxsoc0qwlx31tru9/food_arm.dta?rlkey=4mfa0qf1sw0tnfd49c2ggvvm4&st=5q8bia6u&dl=1"  # Replace with your actual link
                try:
         # Step 1: Download the .dta file
                    response = requests.get(url)
                    response.raise_for_status()
        
        # Step 2: Save the file locally
                    with open("data.dta", "wb") as file:
                          file.write(response.content)
        
        # Step 3: Read the .dta file with pandas
                    df = pd.read_stata("data.dta")
                    return df
    
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading data: {e}")
                    return None
                except Exception as e:
                    print(f"Error loading data: {e}")
                    return None
            
            df0 = load_data()     
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Food Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="fdregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="fdurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="fdicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            

            
            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')

            daily_food = filtered_data.groupby('start_date')['food_num'].mean().reset_index()

            # Display the chart in Streamlit
            line_chart = alt.Chart(daily_food).mark_line(
                color='red',  # Red line color
                strokeWidth=2  # Thickness of the line
            ).encode(
                x=alt.X('start_date:T',
                        axis=alt.Axis(
                            format='%Y-%m-%d',  # Adjust the date format (Year/Month/Day)
                            labelAngle=-45,  # Angle the labels for better readability
                            labelOverlap=False,
                            title='Submission Date'
                        )),
                y=alt.Y('food_num:Q', title='Selected food count'),
                tooltip=[alt.Tooltip('start_date:T', title='Date'), alt.Tooltip('food_num', title='Selected food count')]
            ).properties(
                # title='Daily Total Submissions (Agreement == 1)',
                width='container',  # Dynamically adjust width based on the container size
                height=400
            ).interactive()

            # Add points to the line graph with custom styling
            points = alt.Chart(daily_food).mark_point(
                filled=True,  # Filled dots
                color='white',  # White dot color
                size=100,  # Size of the points
                stroke='red',  # Red circle around the dots
                strokeWidth=2  # Thickness of the red circle
            ).encode(
                x='start_date:T',
                y='food_num:Q'
            )

            # Combine the line and points together
            combined_chart = line_chart + points

            # Display the chart in Streamlit
            st.subheader("Daily Selected food count")
            st.altair_chart(combined_chart, use_container_width=True)  # Use container width to make it responsive



            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_food", "dur_food"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")    

        with tabs[9]:
            st.header("Non-Food Module")
            st.write("This is the Non-Food Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            def load_data():
                url = "https://www.dropbox.com/scl/fi/qltaucdatbyiwj2t1g0w5/nonfood_arm.dta?rlkey=gg6v28zi19fwkygh5gfmztq60&st=37mocb28&dl=1"  # Replace with your actual link
                try:
         # Step 1: Download the .dta file
                    response = requests.get(url)
                    response.raise_for_status()
        
        # Step 2: Save the file locally
                    with open("data.dta", "wb") as file:
                          file.write(response.content)
        
        # Step 3: Read the .dta file with pandas
                    df = pd.read_stata("data.dta")
                    return df
    
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading data: {e}")
                    return None
                except Exception as e:
                    print(f"Error loading data: {e}")
                    return None
            
            df0 = load_data()                 
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Non-Food Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="nfregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="nfurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="nficode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            

            
            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_nfa", "dur_nfa"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")   
                        

        with tabs[10]:
            st.header("Dwelling Module")
            st.write("This is the Dwelling Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/dwelling_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Dwelling Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="dwregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="dwurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="dwicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
                   


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_dwa", "dur_dwa"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")    

        with tabs[11]:
            st.header("Durable Goods Module")
            st.write("This is the Durable Goods Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/durables_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Durables Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="drregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="drurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="dricode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_dwd", "dur_dwd"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")    


        with tabs[12]:
            st.header("Agriculture Module")
            st.write("This is the Agriculture Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/agr_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Agriculture Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="agregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="agurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="agicode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            
            

            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_agriculture", "dur_agriculture"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")    

        with tabs[13]:
            st.header("Perception Module")
            st.write("This is the Perception Module for Daily Data Quality Check.")
            # Add your content for the Passport module here
            #######################
            # Load data
            # df_reshaped = pd.read_csv('us-population-2010-2019-reshaped.csv')
            # Load the Stata file (replace with your file path)
            file_path = "./data/perc_arm.dta"  # If located in a subfolder named 'data'
            df0, meta = pyreadstat.read_dta(file_path)
            missing_symbols = ["."]
           # Replace these symbols with `NaN` in object columns
            df0.replace(missing_symbols, pd.NA, inplace=True)
            # st.write(df0.dtypes)

            # Assume there's a date column named 'start_date' in your data
            # Ensure the date column is in datetime format
            datevars = ['start_date', 'end_date', 'date']
            timevars = ['start_time', 'end_time', 'time']
    
            # Ensure each date column is in datetime format
            for col in datevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d')


            # Format each time column to the 'CCYY/NN/DD_HH' format
            for col in timevars:
                df0[col] = pd.to_datetime(df0[col], errors='coerce')  # 'errors=coerce' will handle any non-date values
                df0[col] = df0[col].dt.strftime('%Y/%m/%d %H:%M:%S')
            
            # st.write(df0.dtypes)
            # st.dataframe(df0.head())


            #######################
            # Sidebar
            with st.sidebar:
                st.title('Perception Filter')
            
                # Filter by Region, Urban/Rural, and Enumerator
                selected_region_e = st.multiselect("Filter by Region", df0['region'].unique(), key="prregion_filter")
                selected_urban_e = st.multiselect("Filter by Urban/Rural", df0['urban'].unique(), key="prurban_filter")
                selected_icode_e = st.multiselect("Filter by Enumerator", df0['icode'].unique(), key="pricode_filter")
            
                # Create a copy of the DataFrame to apply filters on
                filtered_data = df0.copy()
            
                # Apply filters if selections are made
                if selected_region_e:
                    filtered_data = filtered_data[filtered_data['region'].isin(selected_region_e)]
            
                if selected_urban_e:
                    filtered_data = filtered_data[filtered_data['urban'].isin(selected_urban_e)]
            
                if selected_icode_e:
                    filtered_data = filtered_data[filtered_data['icode'].isin(selected_icode_e)]
            


            # Filters
            st.subheader("Data Tables")
            selected_vars = st.multiselect("Select variables to view", filtered_data.columns)
            filtered_data = filtered_data.sort_values(by="date", ascending=True)

            if selected_vars:
                st.write(f"Displaying {len(filtered_data)} rows after filtering:")
                st.dataframe(filtered_data[selected_vars])
            else:
                st.write("Please select variables to view")


            # Filter data where 'agreement' is 1
            #agreed = filtered_data[filtered_data['agreement'] == 1]

            # Group by date and count the number of submissions where agreement == 1
           # daily_submissions = agreed.groupby('start_date').size().reset_index(name='total_submissions')




            st.subheader("Summary Statistics")

            # Ensure that only integer and float columns are available for selection (excluding string/object columns)
            numeric_cols = filtered_data.select_dtypes(include=['int64', 'float64', 'object']).columns

            # Filters
            # st.subheader("Select numeric variables")
            sum_vars = st.multiselect("Select variables to summarize", numeric_cols, default=["corrected_dur_perc", "dur_perc"])  # Show only numeric variables

            # If variables are selected
            if sum_vars:
                # Get summary statistics for the selected numeric variables, ignoring missing values
                summary = filtered_data[sum_vars].describe()

                # Apply different formatting for each statistic, ignoring missing values
                formatted_summary = summary.copy()

                # Custom formatting for each statistic
                formatted_summary.loc['count'] = summary.loc['count'].map('{:.0f}'.format)  # No decimals for count
                formatted_summary.loc['mean'] = summary.loc['mean'].map('{:.2f}'.format)  # 2 decimals for mean
                formatted_summary.loc['std'] = summary.loc['std'].map('{:.3f}'.format)  # 3 decimals for standard deviation
                formatted_summary.loc['min'] = summary.loc['min'].map('{:.2f}'.format)  # 2 decimals for min
                formatted_summary.loc['25%'] = summary.loc['25%'].map('{:.2f}'.format)  # 2 decimals for 25th percentile
                formatted_summary.loc['50%'] = summary.loc['50%'].map('{:.2f}'.format)  # 2 decimals for median (50th percentile)
                formatted_summary.loc['75%'] = summary.loc['75%'].map('{:.2f}'.format)  # 2 decimals for 75th percentile
                formatted_summary.loc['max'] = summary.loc['max'].map('{:.2f}'.format)  # 2 decimals for max

                # Display the formatted summary table
                # st.write("Formatted Summary Statistics (ignoring missing values)")
                st.dataframe(formatted_summary)
            else:
                st.write("Please select variables to summarize")  
