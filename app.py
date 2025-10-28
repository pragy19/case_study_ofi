import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NexGen Cost Intelligence Dashboard",
    page_icon="🚛",
    layout="wide"
)

# --- 2. DATA LOADING & CACHING ---
@st.cache_data
def load_data():
    """Loads, merges, and processes all data. Cached for performance."""
    
    # Define file names
    orders_file = "orders.csv"
    delivery_file = "delivery_performance.csv"
    routes_file = "routes_distance.csv"
    costs_file = "cost_breakdown.csv"
    feedback_file = "customer_feedback.csv"
    
    try:
        # Load datasets
        orders_df = pd.read_csv(orders_file)
        delivery_df = pd.read_csv(delivery_file)
        routes_df = pd.read_csv(routes_file)
        costs_df = pd.read_csv(costs_file)
        feedback_df = pd.read_csv(feedback_file)
    except FileNotFoundError as e:
        st.error(f"Error: File not found - {e.filename}. Please make sure all CSVs are in the same folder.")
        return pd.DataFrame() # Return empty dataframe

    # --- Pre-processing & Merging ---
    
    # Create Total_Cost
    cost_components = ['Fuel_Cost', 'Labor_Cost', 'Vehicle_Maintenance', 
                       'Insurance', 'Packaging_Cost', 'Technology_Platform_Fee', 
                       'Other_Overhead']
    costs_df['Total_Cost'] = costs_df[cost_components].sum(axis=1)

    # Start with costs and merge others
    master_df = costs_df.copy()
    master_df = pd.merge(master_df, routes_df[['Order_ID', 'Route', 'Distance_KM']], on='Order_ID', how='left')
    master_df = pd.merge(master_df, orders_df[['Order_ID', 'Order_Date', 'Customer_Segment', 'Product_Category', 'Order_Value_INR']], on='Order_ID', how='left')
    master_df = pd.merge(master_df, delivery_df[['Order_ID', 'Carrier', 'Customer_Rating']], on='Order_ID', how='left')
    master_df = pd.merge(master_df, feedback_df[['Order_ID', 'Rating']], on='Order_ID', how='left')

    # Create final rating column
    master_df['Final_Rating'] = master_df['Rating'].fillna(master_df['Customer_Rating'])
    
    # --- Engineer Key Metrics ---
    master_df['Distance_KM'] = master_df['Distance_KM'].replace(0, pd.NA)
    master_df['Cost_Per_KM'] = (master_df['Total_Cost'] / master_df['Distance_KM']).round(2)
    master_df['Cost_Per_Order'] = master_df['Total_Cost']
    master_df['Cost_Efficiency_Ratio'] = (master_df['Order_Value_INR'] / master_df['Total_Cost']).round(2)
    
    # Convert Order_Date to datetime
    master_df['Order_Date'] = pd.to_datetime(master_df['Order_Date'])

    # --- Split Domestic/International ---
    international_cities = ['Singapore', 'Dubai', 'Hong Kong', 'Bangkok']
    pattern = '|'.join(international_cities)
    is_international = master_df['Route'].str.contains(pattern, case=False, na=False)
    master_df['Route_Type'] = 'Domestic'
    master_df.loc[is_international, 'Route_Type'] = 'International'

    master_df = master_df.dropna(subset=['Cost_Per_KM', 'Cost_Efficiency_Ratio', 'Final_Rating', 'Route', 'Order_Date'])
    
    return master_df

# Load the data
df = load_data()

if not df.empty:
    # --- 3. SIDEBAR FILTERS ---
    st.sidebar.title("🚛 NexGen Dashboard Filters")
    
    # Date Range Filter
    min_date = df['Order_Date'].min().date()
    max_date = df['Order_Date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        (min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Handle date range selection
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
    
    # Other Filters
    segment = st.sidebar.multiselect(
        "Select Customer Segment",
        options=df['Customer_Segment'].unique(),
        default=df['Customer_Segment'].unique()
    )
    
    route_type = st.sidebar.multiselect(
        "Select Route Type",
        options=df['Route_Type'].unique(),
        default=df['Route_Type'].unique()
    )

    product = st.sidebar.multiselect(
        "Select Product Category",
        options=df['Product_Category'].unique(),
        default=df['Product_Category'].unique()
    )

    # --- 4. FILTER DATAFRAME ---
    df_filtered = df[
        (df['Order_Date'] >= start_date) &
        (df['Order_Date'] <= end_date) &
        (df['Customer_Segment'].isin(segment)) &
        (df['Route_Type'].isin(route_type)) &
        (df['Product_Category'].isin(product))
    ]

    # --- 5. MAIN PAGE ---
    st.title("NexGen Cost Intelligence Dashboard")
    st.markdown("Dynamic analysis of logistics costs and performance.")

    # --- 6. KPIs ---
    total_cost = df_filtered['Total_Cost'].sum()
    avg_cost_order = df_filtered['Cost_Per_Order'].mean()
    avg_cost_km = df_filtered['Cost_Per_KM'].mean()
    avg_efficiency = df_filtered['Cost_Efficiency_Ratio'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cost", f"{total_cost:,.0f} INR")
    col2.metric("Avg. Cost / Order", f"{avg_cost_order:,.2f} INR")
    col3.metric("Avg. Cost / KM", f"{avg_cost_km:,.2f} INR")
    col4.metric("Avg. Efficiency Ratio", f"{avg_efficiency:,.2f}x")
    
    st.markdown("---")

    # --- 7. CHARTS ---
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        # Chart 1: Cost Breakdown
        cost_components = ['Fuel_Cost', 'Labor_Cost', 'Vehicle_Maintenance', 
                           'Insurance', 'Packaging_Cost', 'Technology_Platform_Fee', 
                           'Other_Overhead']
        cost_totals = df_filtered[cost_components].sum()
        fig1 = px.pie(cost_totals, 
                      values=cost_totals.values, 
                      names=cost_totals.index, 
                      title='<b>Chart 1: Overall Cost Breakdown</b>',
                      hole=0.4)
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Chart 3: Cost by Product
        product_cost = df_filtered.groupby('Product_Category')['Cost_Per_Order'].mean().reset_index().sort_values(by='Cost_Per_Order')
        fig3 = px.bar(product_cost,
                      x='Cost_Per_Order',
                      y='Product_Category',
                      orientation='h',
                      title='<b>Chart 3: Avg. Cost-per-Order by Product</b>')
        st.plotly_chart(fig3, use_container_width=True)

    with col_c2:
        # Chart 4: Segment Efficiency
        segment_efficiency = df_filtered.groupby('Customer_Segment')['Cost_Efficiency_Ratio'].mean().reset_index().sort_values(by='Cost_Efficiency_Ratio')
        fig4 = px.bar(segment_efficiency,
                      x='Customer_Segment',
                      y='Cost_Efficiency_Ratio',
                      title='<b>Chart 4: Cost Efficiency by Customer Segment</b>')
        st.plotly_chart(fig4, use_container_width=True)
        
        # Chart 5: Cost vs. Rating
        fig5 = px.scatter(df_filtered,
                          x='Total_Cost',
                          y='Final_Rating',
                          color='Customer_Segment',
                          title='<b>Chart 5: Cost vs. Customer Satisfaction</b>',
                          labels={'Total_Cost': 'Total Cost (INR)', 'Final_Rating': 'Rating (1-5)'})
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")
    
    # Chart 2 (Domestic & International)
    st.header("Route Efficiency Analysis (Cost per KM)")
    
    # Filter for Domestic
    df_domestic = df_filtered[df_filtered['Route_Type'] == 'Domestic']
    if not df_domestic.empty:
        domestic_route_cost_km = df_domestic.groupby('Route')['Cost_Per_KM'].mean().reset_index().sort_values(by='Cost_Per_KM')
        fig2a = px.bar(domestic_route_cost_km.tail(15), # Show top 15 most expensive
                      x='Cost_Per_KM',
                      y='Route',
                      orientation='h',
                      title='<b>Chart 2a: Most Expensive Domestic Routes</b>')
        st.plotly_chart(fig2a, use_container_width=True)
    
    # Filter for International
    df_international = df_filtered[df_filtered['Route_Type'] == 'International']
    if not df_international.empty:
        international_route_cost_km = df_international.groupby('Route')['Cost_Per_KM'].mean().reset_index().sort_values(by='Cost_Per_KM')
        fig2b = px.bar(international_route_cost_km.tail(15), # Show top 15 most expensive
                      x='Cost_Per_KM',
                      y='Route',
                      orientation='h',
                      title='<b>Chart 2b: Most Expensive International Routes</b>')
        st.plotly_chart(fig2b, use_container_width=True)

    # --- 8. RAW DATA ---
    st.markdown("---")
    st.header("Raw Data Explorer")
    st.dataframe(df_filtered)

else:
    st.warning("Data loading failed. Please check your CSV files and refresh.")