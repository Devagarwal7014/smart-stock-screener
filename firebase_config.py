import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyBycC4lifxms_PC_4mTdzkn8i0NuDIpvtQ",
    "authDomain": "smart-stock-screener-e4317.firebaseapp.com",
    "databaseURL": "https://smart-stock-screener-e4317-default-rtdb.firebaseio.com",
    "projectId": "smart-stock-screener-e4317",
    "storageBucket": "smart-stock-screener-e4317.appspot.com",
    "messagingSenderId": "1044375015853",
    "appId": "1:1044375015853:web:1deff30092548e32171124"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()


