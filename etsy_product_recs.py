import streamlit as st
import pandas as pd

# Create a file uploader widget
file_uploader = st.file_uploader("Upload a CSV file", type="csv")

# Function to return recommendations for SKU provided
def get_recommendations(df, item):
    """Generate a set of product recommendations using item-based collaborative filtering.
    
    Args:
        df (dataframe): Pandas dataframe containing matrix of items purchased.
        item (string): Column name for target item. 
        
    Returns: 
        recommendations (dataframe): Pandas dataframe containing product recommendations. 
    """
    
    recommendations = df.corrwith(df[item])
    recommendations.dropna(inplace=True)
    recommendations = pd.DataFrame(recommendations, columns=['correlation']).reset_index()
    recommendations = recommendations.sort_values(by='correlation', ascending=False)
    
    return recommendations

# Check if a file has been uploaded
if file_uploader is not None:
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_uploader)

    # extract username from Buyer column
    df['Buyer'] = df['Buyer'].str.extract(r'(\(.*?\))')
    df['Buyer'] = df['Buyer'].str.replace(r'(\(|\))', '', regex=True)
        
    # convert usernames to IDs
    df["Buyer"], name_index = df["Buyer"].factorize()
    
    # Count the occurrences of each value in the 'Buyer' column
    counts = df["Buyer"].value_counts()
    
    # Filter the DataFrame to include only rows where the value in the 'Buyer' column occurs more than once
    etsy_multi = df[df["Buyer"].isin(counts[counts > 1].index)]
    
    # select required columns & remove duplicates
    etsy_df = etsy_multi[['Buyer', 'SKU', 'Quantity']].drop_duplicates()
    
    top_50_items = etsy_df.groupby('SKU').agg(
        orders=('Buyer', 'nunique'),
        quantity=('Quantity', 'sum')
        ).sort_values(by='orders', ascending=False).head(50)
    
    etsy_df_items = etsy_df[etsy_df["SKU"].isin(top_50_items.index)].pivot_table(index='Buyer', columns=['SKU'], values='Quantity').fillna(0)
    
    # Get the unique values in the 'SKU' column
    skus = etsy_df["SKU"].unique()
    
    # Create a dropdown widget with the unique SKUs
    selected_sku = st.selectbox("Select a SKU", skus)
    
    recommendations = get_recommendations(etsy_df_items, selected_sku).head(10)

    # Display the filtered DataFrame
    st.dataframe(recommendations)