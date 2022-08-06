mkdir -p ~/.streamlit

echo "[general] 
email = 'tmoriics-tky@umin.ac.jp'
" > ~/.streamlit/credentials.toml

echo "[server]
headless = true
port = $PORT
enableCORS = false

[theme]
primaryColor='#F63366'
backgroundColor='#88EE55'
secondaryBackgroundColor='#E0F2C6'
textColor='#262730'
font='sans serif'
" > ~/.streamlit/config.toml

