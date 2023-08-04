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
backgroundColor='#AAEECC'
secondaryBackgroundColor='#F4F6FA'
textColor='#262730'
font='sans serif'
" > ~/.streamlit/config.toml


