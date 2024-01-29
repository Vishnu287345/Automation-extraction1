# from linkedin_api import Linkedin
# import json
# import pandas as pd
# from urllib.parse import urlparse


# def extract_company_name(linkedin_url):
#     parsed_url = urlparse(linkedin_url)
#     path_segments = parsed_url.path.split('/')
#     # Filter out empty path segments
#     path_segments = [segment for segment in path_segments if segment]

#     if path_segments:
#         # Check if the last segment is 'about', if yes, take the one before it
#         if path_segments[-1] == 'about' and len(path_segments) >= 2:
#             company_name = path_segments[-2]
#         else:
#             # Assuming the company name is the last segment in the path
#             company_name = path_segments[-1]
#         return company_name
#     else:
#         return None


# 

# # Read LinkedIn URLs from an Excel sheet
# linkedin_urls_df = pd.read_excel('urls.xlsx')
# linkedin_urls = linkedin_urls_df['LinkedIn URL'].tolist()

# # Initialize an empty list to store company details
# all_company_details = []

# # Iterate over each LinkedIn URL
# for linkedin_url in linkedin_urls:
#     # Extract company name from the LinkedIn URL
#     company_name = extract_company_name(linkedin_url)

#     if company_name:
#         try:
#             z = api.get_company(company_name)
#             company = json.dumps(z, indent=2)

#             # Check if the response is in valid JSON format
#             try:
#                 data = json.loads(company)
#             except json.JSONDecodeError as json_error:
#                 print(
#                     f"Error decoding JSON response for {company_name} from {linkedin_url}: {str(json_error)}")
#                 continue  # Skip to the next iteration

#             # Extracting details with error handling
#             try:
#                 employee_range_start = data['staffCountRange']['start']
#             except KeyError:
#                 employee_range_start = None

#             if employee_range_start is not None and employee_range_start < 10000:
#                 try:
#                     employee_range_end = data['staffCountRange']['end']
#                 except KeyError:
#                     employee_range_end = None
#             else:
#                 employee_range_end = 0

#             try:
#                 funds = data['fundingData']['lastFundingRound']['moneyRaised']['amount']
#             except (KeyError, TypeError):
#                 funds = 0

#             company_name = data['name']
#             company_url = data["companyPageUrl"]

#             try:
#                 industry = data['companyIndustries'][0]["localizedName"]
#             except (KeyError, IndexError):
#                 industry = None

#             try:
#                 hq = data["headquarter"]['country']
#             except KeyError:
#                 hq = None

#             try:
#                 specialities = data['specialities']
#             except KeyError:
#                 specialities = None

#             try:
#                 mem = data['staffCount']
#             except KeyError:
#                 mem = None

#             try:
#                 des = data['description']
#             except KeyError:
#                 des = None

#             try:
#                 founded = data['foundedOn']['year']
#             except KeyError:
#                 founded = None

#             # Store company details in a dictionary
#             company_details = {
#                 'Company name': company_name,
#                 'Company Domain': company_url,
#                 'Founded': founded,
#                 'ECR_start': employee_range_start,
#                 'ECR_End': employee_range_end,
#                 'Associated_members': mem,
#                 'Industry': industry,
#                 'HQ': hq,
#                 'Funds': funds,
#                 'Description': des,
#                 'Specialities': specialities
#             }

#             # Append the details to the list
#             all_company_details.append(company_details)
#         except Exception as e:
#             print(
#                 f"Error fetching details for {company_name} from {linkedin_url}: {str(e)}")

# # Convert the list of dictionaries to a DataFrame
# df = pd.DataFrame(all_company_details)

# # Save DataFrame to Excel
# df.to_excel('companies_data_with_details.xlsx', index=False)

# print("Excel sheet 'companies_data_with_details.xlsx' created successfully.")


# -----------------------------------------------------------------------------------------------------------------

import json
import logging
import pandas as pd
from urllib.parse import urlparse
from linkedin_api import Linkedin
import streamlit as st
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_company_name(linkedin_url):
    parsed_url = urlparse(linkedin_url)
    path_segments = [
        segment for segment in parsed_url.path.split('/') if segment]

    if 'company' in path_segments:
        # Find the index of 'company' in the path and get the next segment
        company_index = path_segments.index('company')
        if company_index < len(path_segments) - 1:
            return path_segments[company_index + 1]

    return None


def fetch_company_details(api, company_name, linkedin_url):
    try:
        company_data = api.get_company(company_name)
        return json.loads(json.dumps(company_data, indent=2))
    except Exception as e:
        logger.error(
            f"Error fetching details for {company_name} from {linkedin_url}: {str(e)}")
        return None


def convert_to_billion_million(value):
    if value is None:
        return None

    # Ensure that the value is a numeric type
    try:
        value = float(value)
    except (ValueError, TypeError):
        return f"{value}"

    # Define the thresholds for conversion
    billion_threshold = 1_000_000_000
    million_threshold = 1_000_000

    if value >= billion_threshold:
        return f"{value / billion_threshold:.2f}B"
    elif value >= million_threshold:
        return f"{value / million_threshold:.2f}M"
    else:
        return f"{value:.2f}"


def check(df1):
    api = Linkedin('245vishnuteja@gmail.com','Vishnu@245')
    linkedin_urls_df=df1
    if 'LinkedIn URL' not in linkedin_urls_df.columns:
        logger.error("Input file must contain a column named 'LinkedIn URL'.")
        return

    # Initialize an empty list to store company details
    all_company_details = []

    # Iterate over each LinkedIn URL
    for _, row in linkedin_urls_df.iterrows():
        linkedin_url = row['LinkedIn URL']
        company_name = extract_company_name(linkedin_url)

        if company_name:
            company_data = fetch_company_details(
                api, company_name, linkedin_url)

            if company_data:
                try:
                    # Extracting details with error handling
                    employee_range_start = company_data.get(
                        'staffCountRange', {}).get('start')
                    employee_range_end = company_data.get(
                        'staffCountRange', {}).get('end')
                    funds = company_data.get('fundingData', {}).get(
                        'lastFundingRound', {}).get('moneyRaised', {}).get('amount', " ")
                    converted_funds = convert_to_billion_million(funds)
                    industry = company_data.get('companyIndustries', [{}])[
                        0].get('localizedName')
                    hq = company_data.get('headquarter', {}).get('country')
                    specialities = company_data.get('specialities')
                    mem = company_data.get('staffCount')
                    des = company_data.get('description')
                    founded = company_data.get('foundedOn', {}).get('year')

                    # Store company details in a dictionary
                    company_details = {
                        'Company name': company_name,
                        'Company Domain': company_data.get("companyPageUrl"),
                        'Founded': founded,
                        'ECR_start': employee_range_start,
                        'ECR_End': employee_range_end,
                        'Associated_members': mem,
                        'Industry': industry,
                        'HQ': hq,
                        'Funds': converted_funds,
                        'Description': des,
                        'Specialities': specialities
                    }

                    # Append the details to the list
                    all_company_details.append(company_details)
                except Exception as e:
                    logger.error(
                        f"Error extracting details for {company_name} from {linkedin_url}: {str(e)}")
            else:
                logger.warning(
                    f"No data fetched for {company_name} from {linkedin_url}.")

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_company_details)

    # Save DataFrame to Excel
    #df.to_excel('companies_data_with_details.xlsx', index=False)
    
   # print(df)
    st.download_button(
        label="Download File",
        data=df.to_csv(index=False),
        file_name="data.csv",
        mime="text/csv"
    )

    #return None
