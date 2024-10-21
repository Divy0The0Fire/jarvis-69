import os
import shutil
import streamlit as st
import subprocess
import json

# Function to check Python version
def check_python_version():
    try:
        result = subprocess.run(["py", "-3.10", "--version"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error checking Python version: {e}"

# Function to copy the example.env to .env
def configure_env():
    old_file = 'example.env'
    new_file = '.env'

    if os.path.exists(new_file):
        choice = st.radio(f'The file "{new_file}" already exists. Do you want to reset it?', ['Yes', 'No'])
        
        if choice == 'Yes':
            os.remove(new_file)
            st.success(f'The file "{new_file}" has been deleted.')
        else:
            st.warning('Aborting the operation.')
            return

    if os.path.exists(old_file):
        shutil.copy(old_file, new_file)
        st.success(f'Successfully copied "{old_file}" to "{new_file}".')
    else:
        st.error(f'The file "{old_file}" does not exist.')

# Function to load API setup instructions
def load_api_setup():
    return [
        {
            "name": "GROQ_API_KEY",
            "description": "groq api key for llm its mandatory.",
            "url": "https://console.groq.com/keys",
            "required": True
        },
        {
            "name": "OPENAI_API_KEY",
            "description": "openai api key for llm its optional.",
            "url": "https://platform.openai.com/account/api-keys",
            "required": False
        },
        {
            "name": "TOGETHER_API_KEY",
            "description": "its not mandatory. but if you have it then you can use it.",
            "url": 'https://api.together.xyz/',
            "required": False
        },
        {
            "name": "DEEPGRAM_API_KEY",
            "description": "Deepgram API key for speech recognition $200 free credits.",
            "url": "https://deepgram.com/",
            "required": False
        }
    ]

# Function to read .env file values
def read_env():
    env_values = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_values[key] = value
    return env_values

# Function to write updated values back to .env file
def update_env(updates):
    if os.path.exists('.env'):
        with open('.env', 'w') as f:
            for key, value in updates.items():
                f.write(f"{key}={value}\n")
        st.success("Updated .env file successfully.")
    else:
        st.error("The .env file does not exist.")

# Function to run tests from test.py
def run_tests():
    try:
        result = subprocess.run([*"py -3.10".split(), "test.py"], capture_output=True, text=True)
        return json.loads(result.stdout)
    except Exception as e:
        return [{"error": str(e)}]

# Function to run the batch file to install Python
def run_install_python():
    try:
        # Run the install_python.bat in a new window
        subprocess.Popen(r"win/install_python.bat", creationflags=subprocess.CREATE_NEW_CONSOLE)
        return True
    except Exception as e:
        st.error(f"Failed to run installer: {e}")
        return False

# Function to install packages from requirements.txt
def install_requirements():
    subprocess.Popen([*"py -3.10 -m pip".split(), "install", "-r", "requirements.txt"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    st.success("Requirements are installing")


# Streamlit layout
st.set_page_config(page_title="Project Setup", layout="wide")

# Navigation Bar
st.sidebar.title("Setup Navigation")
options = st.sidebar.radio("Select an option:", ["Check Python Version", "Configure .env", "API Setup", "Run Tests", "Install Requirements"])

if options == "Check Python Version":
    st.title("Check Python Version")
    python_version = check_python_version()
    st.write(f"Python Version: `{python_version}`")

    # If Python 3.10.10 is not installed, show the option to install
    if "3.10.10" not in python_version:
        st.warning("Python 3.10.10 is not installed. Click the button below to install it.")
        if st.button("Install Python 3.10.10"):
            if run_install_python():
                st.success("The Python installer is running. Follow the instructions in the installation window.")

elif options == "Configure .env":
    st.title("Configure .env")
    if st.button("Copy example.env to .env"):
        configure_env()
    
    st.subheader("Update .env Values")
    env_values = read_env()
    if env_values:
        updates = {}
        for key in env_values.keys():
            updates[key] = st.text_input(key, value=env_values[key])
        
        if st.button("Update .env"):
            update_env(updates)

elif options == "API Setup":
    st.title("API Setup Instructions")
    api_setup = load_api_setup()
    for api in api_setup:
        st.subheader(api["name"])
        st.write(api["description"])
        if api["url"]:
            st.write(f"[Documentation]({api['url']})")
        st.write("Required:", "Yes" if api["required"] else "No")
        st.write("---")

elif options == "Run Tests":
    st.title("Run Test Code")
    if st.button("Run Tests"):
        results = run_tests()
        st.write(results)

elif options == "Install Requirements":
    st.title("Install Requirements")
    if st.button("Install from requirements.txt"):
        install_requirements()
