import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Base directory path using relative path
base_dir = 'E-commerce-public-dataset/'

# List of dataset filenames with relative paths
dataset_filenames = {
    'orders': 'orders_dataset.csv',
    'items': 'order_items_dataset.csv',
    'products': 'products_dataset.csv',
    'payments': 'order_payments_dataset.csv',
    'reviews': 'order_reviews_dataset.csv',
    'customers': 'customers_dataset.csv',
    'sellers': 'sellers_dataset.csv',
    'geolocation': 'geolocation_dataset.csv',
    'category': 'product_category_name_translation.csv'
}

# Opening datasets and storing them in a dictionary
data = {name: pd.read_csv(os.path.join(base_dir, filename)) for name, filename in dataset_filenames.items()}

# Load datasets
orders_df = data['orders']
items_df = data['items']
products_df = data['products']
reviews_df = data['reviews']
customers_df = data['customers']
geolocation_df = data['geolocation']

# Analysis 1: Produk dengan ulasan paling positif
# Merge datasets to get product information in reviews
merged_df = pd.merge(reviews_df, items_df, on='order_id')
merged_df = pd.merge(merged_df, products_df, on='product_id')

# Calculate average review score for each product
product_reviews = merged_df.groupby('product_id').agg({
    'review_score': 'mean',
    'price': 'mean'
}).reset_index()

# Identify the product with the highest average review score
most_positive_product = product_reviews.loc[product_reviews['review_score'].idxmax()]

# Determine if the product is cheap or expensive
median_price = product_reviews['price'].median()
most_positive_product['category'] = 'Murah' if most_positive_product['price'] < median_price else 'Mahal'

# Analysis 2: Rata-rata waktu pengiriman untuk setiap pesanan
# Merge datasets to get customer location in orders
orders_customers_df = pd.merge(orders_df, customers_df, on='customer_id')

# Calculate delivery time for each order
orders_customers_df['order_purchase_timestamp'] = pd.to_datetime(orders_customers_df['order_purchase_timestamp'])
orders_customers_df['order_delivered_customer_date'] = pd.to_datetime(orders_customers_df['order_delivered_customer_date'])
orders_customers_df['delivery_time'] = (orders_customers_df['order_delivered_customer_date'] - orders_customers_df['order_purchase_timestamp']).dt.days

# Merge with geolocation data
orders_geo_df = pd.merge(orders_customers_df, geolocation_df, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix')

# Calculate average delivery time for each location
avg_delivery_time_by_location = orders_geo_df.groupby('geolocation_city')['delivery_time'].mean().reset_index()

# Streamlit app
st.title('E-Commerce Data Analysis')

# Dropdown for analysis type
analysis_type = st.selectbox('Select Analysis Type', ['Produk dengan Ulasan Paling Positif', 'Rata-rata Waktu Pengiriman untuk Setiap Lokasi Geografis'])

if analysis_type == 'Produk dengan Ulasan Paling Positif':
    st.subheader('Produk dengan Ulasan Paling Positif')
    
    # Plotting
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=product_reviews, x='price', y='review_score', hue='review_score', palette='viridis', size='review_score', sizes=(20, 200))
    plt.axvline(median_price, color='red', linestyle='--', label='Median Price')
    plt.title('Produk dengan Ulasan Paling Positif')
    plt.xlabel('Harga Produk')
    plt.ylabel('Skor Ulasan Rata-rata')
    plt.legend()
    
    # Display plot in Streamlit
    st.pyplot(plt)

    # Display the most positive product
    st.write(f"Produk dengan ulasan paling positif: {most_positive_product['product_id']}")
    st.write(f"Kategori produk: {most_positive_product['category']}")
    st.write(f"Skor ulasan rata-rata: {most_positive_product['review_score']:.2f}")
    st.write(f"Harga produk: R$ {most_positive_product['price']:.2f}")

elif analysis_type == 'Rata-rata Waktu Pengiriman untuk Setiap Lokasi Geografis':
    st.subheader('Rata-rata Waktu Pengiriman untuk Setiap Lokasi Geografis')
    
    # Plotting
    plt.figure(figsize=(12, 8))
    sns.barplot(data=avg_delivery_time_by_location, x='delivery_time', y='geolocation_city', palette='viridis')
    plt.title('Rata-rata Waktu Pengiriman untuk Setiap Lokasi Geografis')
    plt.xlabel('Rata-rata Waktu Pengiriman (hari)')
    plt.ylabel('Lokasi Geografis')
    
    # Display plot in Streamlit
    st.pyplot(plt)

    # Display the average delivery time by location
    st.write(avg_delivery_time_by_location)