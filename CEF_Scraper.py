# Import packages and define global CEFData dataframe
from datetime import date
from selenium import webdriver
import pandas as pd

global CEFData
CEFData = pd.DataFrame()

def CEF_Webscrape():
    # Define the url to be searched from
    url = 'http://www.cefconnect.com/api/v3/DailyPricing?props=LastUpdated,Name,CategoryName,Ticker,Price,NAV,Discount'

    # Initalize the chrome web driver
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(executable_path=r'C:\Users\delor\OneDrive\Desktop\Desktop\Applications\Browsers\chromedriver_win32\chromedriver.exe',options=options)
    driver.get(url)

    # Get the page's raw source content
    pagesource = driver.page_source
    f1 = open(r'C:\Users\delor\OneDrive\Desktop\Desktop\Programming\CEF Connect\CEF-Connect\Raw JSON\DailyPricing'+'.txt', 'w')
    f1.write(pagesource)
    f1.close()
    driver.quit()

    print('Webpage extracted successfully.')

# Gather and save CEF daily pricing data
CEF_Webscrape()

def CEF_Dataset(file_path):
    # Read the content of DailyPricing.txt file
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

    # Write the dataset to a new DailyPricing_dataset.json file
    new_file_path = file_path.replace('.txt', '_dataset.json')
    with open(new_file_path, 'w') as new_file:
        new_file.write(dataset)

    print('Dataset extracted successfully.')

# Reference the saved locaiton of the .txt file
# e.g. r'C:\Users\delor\OneDrive\Desktop\Desktop\Programming\CEF Connect\Raw JSON\DailyPricing.txt'
file_path = r'C:\Users\delor\OneDrive\Desktop\Desktop\Programming\CEF Connect\CEF-Connect\Raw JSON\DailyPricing.txt'

# Extract the dataset
CEF_Dataset(file_path)

def CEF_Cleaning():
    
    global CEFData
    # Read the previously saved .json file into a pandas dataframe
    # V:\Resources\Research\CEF Database\v2 Archive\Raw JSON\DailyPricing_2023-06-29.json
    CEFData = pd.read_json(r'C:\Users\delor\OneDrive\Desktop\Desktop\Programming\CEF Connect\CEF-Connect\Raw JSON\DailyPricing_dataset.json', encoding='latin1')

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

    # Reorder the columns
    CEFData = CEFData[['Date', 'Ticker', 'Fund Name', 'Category', 'Share Price', 'NAV', 'Premium / Discount']]
    return CEFData

    # Export to individual CSV file
    # V:\Resources\Research\CEF Database\v2 Archive\CEF-Daily-Pricing-'
    CEFData.to_csv(r'C:\Users\delor\OneDrive\Desktop\Desktop\Programming\CEF Connect\CEF-Connect\DailyPricing-'+str(CEFData['Date'].iloc[0])+'.csv')
    
    print('Dataset saved successfully.')

CEF_Cleaning()

# Append to Consolidated CEF CSV file

def CEF_Consolidating():

    # Append newly-compiled data to exising DailyPricing.csv consolidated worksheet
    with open(r'C:\Users\delor\OneDrive\Desktop\Desktop\Programming\CEF Connect\CEF-Connect\DailyPricing.csv', 'r') as DailyPricing:
        while True:
            
            # If newly-compiled data already exists (based on the last updated date), don't append to DailyPricing.csv consolidated worksheet 
            if pd.read_csv(DailyPricing)['Date'].iloc[0] == CEFData['Date'].iloc[0]:
                print('Dataset previously consolidated to DailyPricing.csv')
                break
        
        # If newly-compiled data does not exist (based on the last updated date), append to DailyPricing.csv consolidated worksheet 
        else:
            CEFData.to_csv(r'C:\Users\delor\OneDrive\Desktop\Desktop\Programming\CEF Connect\CEF-Connect\DailyPricing.csv', mode='a', index=True, header=False)
            print('Dataset consolidated to DailyPricing.csv')

CEF_Consolidating()