from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions
from time import sleep
import pandas as pd
import os

targetUser = 'HamadaE03645116'

# Define your login credentials
email = "ahmadmedoan2@gmail.com"
user = "HamadaE03645116"
password = "********"

# Define the URL of the login page and followers page
login_url = "https://twitter.com/login"
followers_url = "https://twitter.com/{}/followers".format(targetUser)
Message_url = "https://twitter.com/messages/compose"

# Set the logging level to WARNING or higher
#logging.basicConfig(level=logging.WARNING)

# Create a new instance of the Chrome driver with the "maxSize" option set to 2097152
options = webdriver.ChromeOptions()
#options.add_argument('headless')
options.add_argument('window-size=1200,1000')  # Set a fixed window size

driver = webdriver.Chrome(options=options)
print('Chromedriver opened successfully')


# Navigate to the login page
driver.get(login_url)

# Find the email input field and enter the email
wait = WebDriverWait(driver, 20)
email_field = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@type="text"]')))
email_field.send_keys(email)

# Click on the "next" button
next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Next")]')))
next_button.click()
print("Email entered")

try:
# Find the user input field and enter the user
    user_field = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@type="text"]')))
    user_field.send_keys(user)

# Click on the "next" button
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Next")]')))
    next_button.click()
    print("Username entered")    
except Exception as e:
    print("Username skip")

# Find the password input field and enter the password
password_field = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@type="password"]')))
password_field.send_keys(password)
print("Password entered")

# Find the login button and click it
login_button = driver.find_element(By.XPATH, '//div[@data-testid="LoginForm_Login_Button"]')
login_button.click()
print('Login done succesfully')

# Sleep for 5 seconds to give the login process time to complete
sleep(2)

# Navigate to the followers page
driver.get(followers_url)
print('Going to',targetUser,'followers list')

# Sleep for 5 seconds to give the followers page time to load
sleep(3)

follower_count = driver.find_elements(By.XPATH, './/div[@dir="ltr"]/span[starts-with(text(), "@")]')
print("Number of followers found:", len(follower_count)-1)

# Scroll down to load all the followers
for i in range(1):
    try:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        sleep(1)
        print('Scrolling...')
    except Exception as e:
        print(f"Error scrolling down: {e}")
        exit()

# Find all the follower names on the page
try:
    display_names = driver.find_elements(By.XPATH, '//span[@class="css-901oao css-16my406 css-1hf3ou5 r-poiln3 r-bcqeeo r-qvutc0"]/span[1]')
except Exception as e:
    print(f"Error finding follower names: {e}")
    exit()

try:
    usernames = driver.find_elements(By.XPATH, './/div[@dir="ltr"]/span[starts-with(text(), "@")]')
except Exception as e:
    print(f"Error finding follower names: {e}")
    exit()



# Print the follower names
follower_data = []
for username, display_name in zip(usernames[1:], display_names):


    follower_data.append({
        'Username': username.text[1:],
        'Display Name': display_name.text,
    })
print("Number of users that collected succesfully:", len(follower_data))

# Create a dataframe from the follower data list
df = pd.DataFrame(follower_data)

# Reset the index and add 1 to start counting from 1 instead of 0
df.index = df.reset_index().index + 1

# Define the message to send
message = "Enter_Your_Message_Here"
driver.get(Message_url)

search_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="searchPeople"]')))
print('Search field Located')

user_list = df["Username"]

message_count = 0  # Initialize message count
for i in user_list:
    user = "@" + i
    print("Searching for {}".format(user))

    # Search for the user
    search_field.send_keys(user)
    try:
        select_follower = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//span[@class='css-901oao css-16my406 r-poiln3 r-bcqeeo r-qvutc0' and contains(text(), '{}')]".format(user))))
        print(user, "found")
        #sleep(2)

    except selenium.common.exceptions.TimeoutException:
        print(user, "not found")
        search_field.send_keys(Keys.CONTROL + "a")
        search_field.send_keys(Keys.DELETE)
        print("Search field cleared")
        continue

    try:
        select_follower.click()
    except (selenium.common.exceptions.TimeoutException, selenium.common.exceptions.ElementClickInterceptedException):
        print("Can't send messages to this user")
        search_field.send_keys(Keys.CONTROL + "a")
        search_field.send_keys(Keys.DELETE)
        print("Search field cleared")
        continue

    # Send message to the user
    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Next")]')))
    if next_button is None:
        print("Not able to send a message to", user)
        search_field.send_keys(Keys.CONTROL + "a")
        search_field.send_keys(Keys.DELETE)
        print("Search field cleared")
        continue
    next_button.click()

    message_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='notranslate public-DraftEditor-content' and @data-testid='dmComposerTextInput']")))
    message_button.send_keys(message)

    send_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@data-testid='dmComposerSendButton']")))
    send_button.click()

    print('Message sent to @' + i)

    # Update message count and wait for 10 minutes after every 10 messages
    message_count += 1
    if message_count % 10 == 0:
        print(f"Waiting for 10 minutes after sending {message_count} messages...")
        sleep(600)

    new_message = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-testid='NewDM_Button']")))
    new_message.click()
    search_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="searchPeople"]')))

# Write the dataframe to a CSV file
filename = 'follower_data_({}).csv'.format(targetUser)
print('Exporting data to',filename)
df.to_csv(filename, index_label='f.num', encoding='utf-16', sep='\t')

# Open the CSV file in Excel
print('Opening',filename)
os.system('start excel.exe {}'.format(filename))

# Close the driver and the service
driver.quit()
