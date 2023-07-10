# Import packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager 
import pandas as pd

# Define the url to be searched from
url = 'http://www.cefconnect.com/api/v3/DailyPricing?props=LastUpdated,Name,CategoryName,Ticker,Price,NAV,Discount'

# Reference the locaiton of the 'DailyPricing.txt' file
file_path = r'Raw_JSON\DailyPricing.txt'

def CEF_Webscrape(url):

    # Initalize the chrome web driver and reach out to the url
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    # Get the page's raw source content, write to to the 'DailyPricing.txt' file, and close the webdriver
    pagesource = driver.page_source
    f1 = open(r'Raw_JSON\DailyPricing.txt', 'w')
    f1.write(pagesource)
    f1.close()
    driver.quit()

    # Print helpful note
    print('[25%] Webpage extracted successfully...')

# Gather and save CEF Daily Pricing data
CEF_Webscrape(url)

def CEF_Dataset(file_path):

    # Read the content of the DailyPricing.txt file
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Find the starting and ending positions of the dataset
    start_index = file_content.find('[')
    end_index = file_content.rfind(']')

    if start_index == -1 or end_index == -1:
        # Dataset brackets not found
        return

    # Extract the dataset
    dataset = file_content[start_index:end_index+1]

    # Write the dataset to a new 'DailyPricing_dataset.json' file
    new_file_path = file_path.replace('.txt', '_dataset.json')
    with open(new_file_path, 'w') as new_file:
        new_file.write(dataset)

    # Print helpful note
    print('[50%] Dataset extracted successfully...')

# Extract the dataset
CEF_Dataset(file_path)

def CEF_Cleaning():

    # Initalize an empty CEFData DataFrame    
    global CEFData
    CEFData = pd.DataFrame()

    # Read the previously saved .json file into a pandas DataFrame
    CEFData = pd.read_json(r'Raw_JSON\DailyPricing_dataset.json', encoding='latin1')

    # Clean up the 'Date' Column
    CEFData['LastUpdated'] = CEFData['LastUpdated'].str.split('T').str[0]

    # Clean up the 'Premium / Discount' column
    CEFData['Discount'] = CEFData['Discount']/100

    # Clean up the column names
    CEFData = CEFData.rename(columns={'LastUpdated': 'Date',
                                                'Name': 'Fund Name',
                                                'CategoryName': 'Category',
                                                'Price': 'Share Price',
                                                'Discount': 'Premium / Discount'})

    # Reorder the columns, print the first five rows of data for visual assurance
    CEFData = CEFData[['Date', 'Ticker', 'Fund Name', 'Category', 'Share Price', 'NAV', 'Premium / Discount']]
    # print(CEFData.head())
    
    # Export to individual CSV file
    CEFData.to_csv(r'Daily_Pricing\DailyPricing-'+str(CEFData['Date'].iloc[0])+'.csv')
    
    # Print a helpful note, return the CEFData DataFrame to be accessed later
    print('[75%] Dataset saved successfully...')
    return CEFData

# Clean and organize the dataset
CEF_Cleaning()

def CEF_Consolidating():

    # Append newly-compiled data to exising DailyPricing.csv consolidated worksheet
    with open(r'Daily_Pricing\DailyPricing.csv', 'r') as DailyPricing:
        
        # If newly-compiled data already exists (based on the last updated date), don't append to DailyPricing.csv consolidated worksheet, and print helpful note
        if pd.read_csv(DailyPricing)['Date'].iloc[-1] == CEFData['Date'].iloc[0]:
            print('[100%] Dataset previously consolidated to DailyPricing.csv')
            exit()
        
        # If newly-compiled data does not exist (based on the last updated date), append to DailyPricing.csv consolidated worksheet, and print helpful note
        else:
            CEFData.to_csv(r'Daily_Pricing\DailyPricing.csv', mode='a', index=True, header=False)
            print('[100%] Dataset consolidated to DailyPricing.csv')

# Append to Consolidated CEF CSV file
CEF_Consolidating()