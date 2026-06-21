import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("superstore.csv")

# Convert date
df['Order Date'] = pd.to_datetime(df['Order Date'])

# Title
st.title("📊 E-Commerce Sales Dashboard")

# Sidebar filters
region = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())
category = st.sidebar.multiselect("Select Category", df['Category'].unique(), default=df['Category'].unique())

filtered_df = df[(df['Region'].isin(region)) & (df['Category'].isin(category))]

# KPI Cards
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
col2.metric("Total Profit", f"${filtered_df['Profit'].sum():,.0f}")
col3.metric("Total Orders", filtered_df.shape[0])

# Line Chart
sales_trend = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
fig1 = px.line(sales_trend, x='Order Date', y='Sales', title="Sales Over Time")
st.plotly_chart(fig1)

# Bar Chart
fig2 = px.bar(filtered_df, x='Category', y='Sales', color='Category', title="Sales by Category")
st.plotly_chart(fig2)

# Pie Chart
fig3 = px.pie(filtered_df, names='Segment', values='Profit', title="Profit by Segment")
st.plotly_chart(fig3)

# Heatmap
corr = filtered_df[['Sales', 'Profit', 'Quantity']].corr()
fig4 = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
st.plotly_chart(fig4)