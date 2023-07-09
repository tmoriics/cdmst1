#####
##### about.py
##### 
##### 2022-07-15T06:00 sttest1
##### 2022-07-19T00:27 sttest2
##### 2022-07-29T21:30 sttest2
##### 2022-08-04T00:05 sttest2
##### 2022-08-05T00:57 sttest2 
##### 2022-08-05T00:57 sttest2
##### 2022-08-05T16:20 cdmst1
##### 2022-08-05T19:20 cdmst1
##### 2022-08-05T22:30 cdmst1
##### 2023-07-08T11:41 cdmst1
##### 2023-07-09T12:08 cdmst1
#####

### 
# Imports
###
import time
from PIL import Image
import streamlit as st


#####
#####
# Functions
#####
#####
#
# None 


#####
#####
# Main Script
#####
#####

###
### Main
### 
def main():
    
    ###
    # Preload
    ###
    # img = Image.open('images/aicenter.jpg')
    img = Image.open('images/tus.jpg')

    ###
    # Title section
    ###
    
    st.set_page_config(page_title='About this site')
    hide_menu_style = """
      <style>
      #MainMenu {visibility: hidden;}
      </style>
      """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    
    st.title('このサイトについて')
    st.write('About this site @tmoriics')
    # st.image(img, caption='AI Center of the University of Tokyo', use_column_width=False)
    st.image(img, caption='tmorilab of Tokyo University of Science', use_column_width=False)
    
    st.markdown('Copyright: ')
    st.text('(c) 2022-2023 tmoriics')
    
    st.header('About: ')
    st.subheader('アプリの機能')
    st.text('排尿日誌の認識とそれに基づく指標演算を行います。')
    
    
    ###
    # Progress bar
    ###
    bar = st.progress(0)
    frame_text = st.empty()
    for i in range(100):
        bar.progress(i)
        frame_text.text("%i/100" % (i + 1))
        time.sleep(0.05)
    frame_text.text("Now you can proceed.")
    time.sleep(0.5)
    frame_text.empty()
    bar.empty()


###
###
###
if __name__ == '__main__':
    main()

