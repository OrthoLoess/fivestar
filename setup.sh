mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = milestommo87@gmail.com\n\
" > ~/.streamlit/credentials.toml

echo "[server]
headless = true
enableCORS = false
enableXsrfProtection = false
port = $PORT
" > ~/.streamlit/config.toml


