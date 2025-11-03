import random
# %pip install faker
from faker import Faker
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from data_pipeline.core.util import get_dbutils

# Initialize Spark session
spark = SparkSession.builder.getOrCreate()

# List of special characters 
special_chars = ['@', '#', '$', '!', '&', '*']
dbutils = get_dbutils(spark)

def inject_special_chars(value, num_chars=1):
    """
    Introduce special characters into the input string.
    """
    # To handle None 
    if not value:
        return value
    
    # Separate the value into individual characters of a list
    value_chars = list(value)
    
    # Injecting special characters into random locations
    for x in range(num_chars):
        rand_index_loc = random.randint(0, len(value_chars))
        rand_special_char = random.choice(special_chars)
        value_chars.insert(rand_index_loc, rand_special_char)
    return ''.join(value_chars)

def batch_ids_processing(path) -> str:
    """
    Process batch IDs for data generation task.

    :param path: path string
    :return: Processed batch ID
    """
    folder_paths = [f.path for f in dbutils.fs.ls(path) if f.isDir()]

    # Filter folders that start with '2025'
    matching_folders = [f for f in folder_paths if '2025' in f]

    if matching_folders:
        print("Found batches of folders - processing the batch_ids")
        batch_ids = []
        for folder in matching_folders:
            folder = folder.split("/")
            batch_id = next( (p for p in folder if p.startswith('2025')), None )

            if batch_id is not None:
                batch_ids.append( int(batch_id) )

        latest_batch = max(batch_ids)
        new_batch = latest_batch + 100
        print(f"Latest batch id: {latest_batch}")
    else:
        print("No batches of folders found - introducing batch_id: 20250101")
        new_batch = 20250101
        print(f"New batch id: {new_batch}")
    return str(new_batch)


def etl_process(**options):
    """
    To generate profiles containing details of Real Estate & Contact Info
    - by using Faker library
    """

    fake = Faker()
    Faker.seed(42)

    num_rows = 5 # To create 100 rows of profiles
    data = []

    # Randomly converts a string to lowercase, uppercase, or capitalized.
    def random_cases(text):
        random_text = random.choice([text.lower(), text.upper(), text.capitalize()])
        return random_text

    # Handle properly for email generation
    def email_cases(first_name, last_name):
        domains = ["gmail.com", "yahoo.com", "outlook.com", "realtorhub.com", "hotmail.com", "aol.com", "comcast.net", "verizon.net", "mail.com"]
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"
        return email

    property_types = ["Apartment", "Condo", "FarmHouse", "Townhouse", "Duplex", "Bungalow", "Cottage"]
    agencies = ["Dream Homes Realty", "Reliable Realtors", "Urban Estates", "Coast Realty", "HomeFinder UK"]
    sources = ["Website", "Referral", "Ad", "Social Media"]
    methods = ["Email", "Phone", "WhatsApp", "LinkedIn"]

    for i in range(num_rows):
        # Handle first_name
        if random.random() < 0.2:
            first_name = None
        else:
            if random.random() < 0.3:  # inject random special char 
                first_name = inject_special_chars(random_cases(fake.first_name()), random.randint(1, 2))
            else:
                first_name = random_cases(fake.first_name())  # Introduce random cases

        # Handle middle_name
        middle_name = random_cases(fake.first_name()) if random.random() > 0.2 else None
        
        # Handle last_name
        if random.random() < 0.2:
            last_name = None
        else:
            if random.random() < 0.3:
                last_name = inject_special_chars(random_cases(fake.last_name()), random.randint(1, 2))
            else:
                last_name = random_cases(fake.last_name())

        data.append(
            {
                # Contact Info information
                "profile_id": fake.uuid4(),
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "personal_address": fake.address(),
                "phone_personal": fake.phone_number(),
                "phone_office": fake.phone_number() if random.random() > 0.7 else None,
                "email": email_cases(first_name if first_name else "", last_name if last_name else ""),
                "age": random.randint(18, 65),
                "birth_country": fake.country(),
                "preferred_contact_method": random.choice(methods),
                "linkedin_url": f"https://linkedin.com/in/{first_name.lower() if first_name else ''}-{last_name.lower() if last_name else ''}",

                # Real Estate information
                "property_id": f"RE-{1000+i}",
                "property_type": random.choice(property_types),
                "property_address": fake.street_address(),
                "property_city": fake.city(),
                "property_state": fake.state_abbr(),
                "property_country": fake.country(),
                "property_postal_code": fake.postcode(),
                "bedrooms": random.randint(0, 5),
                "bathrooms": round(random.uniform(1, 4), 1),
                "area_sqft": round(random.uniform(800, 5000), 2),
                "property_pricing": round(random.uniform(500000, 5000000), 0),
                "listed_date": fake.date_between(start_date="-3y", end_date="today"),
                "realtor_name": fake.name(),
                "realtor_email": email_cases(first_name if first_name else "", last_name if last_name else ""),
                "realtor_phone": fake.phone_number(),
                "agency_name": random.choice(agencies),
                "contact_source": random.choice(sources)
                }
            )
    data_df = spark.createDataFrame(data)

    # Filter for Contact Info data ----------
    ci_exclude_cols = ["property_country", "property_postal_code", "bedrooms", "bathrooms", "area_sqft", "property_pricing", "listed_date", "realtor_name", "realtor_email", "realtor_phone", "agency_name", "contact_source"]
    contact_info_df = data_df.select([col for col in data_df.columns if col not in ci_exclude_cols])

    # Contact Info data conversion to parquet file
    print("Loading Contact Info data to parquet file...")
    contact_info_df = contact_info_df\
        .select("profile_id", "first_name", "middle_name", "last_name", "personal_address", "phone_personal", "phone_office", "email", "age", "birth_country", "preferred_contact_method", "linkedin_url")
    # Generate batch ID
    batch_id = batch_ids_processing("dbfs:/Volumes/data_lake_dev/feature_raw_data/contact_info_parquet/")   
    contact_info_df.write.mode("overwrite").parquet(f"dbfs:/Volumes/data_lake_dev/feature_raw_data/contact_info_parquet/{batch_id}")

    # Filter for Real Estate data ----------
    re_exclude_cols = ["personal_address", "phone_personal", "phone_office", "email", "age", "birth_country", "preferred_contact_method", "linkedin_url"]
    real_estate_df = data_df.select([col for col in data_df.columns if col not in re_exclude_cols])

    # Real Estate data conversion to parquet file
    print("\nLoading Real Estate data to parquet file...")
    real_estate_df = real_estate_df \
        .select("profile_id", "first_name", "middle_name", "last_name", "property_id", "property_type", "property_address", "property_city", "property_state", "property_country", "property_postal_code", "bedrooms", "bathrooms", "area_sqft", "property_pricing", "listed_date", "realtor_name", "realtor_email", "realtor_phone", "agency_name", "contact_source")
    # Generate batch ID
    batch_id = batch_ids_processing("dbfs:/Volumes/data_lake_dev/feature_raw_data/real_estate_parquet/")
    real_estate_df.write.mode("overwrite").parquet(f"dbfs:/Volumes/data_lake_dev/feature_raw_data/real_estate_parquet/{batch_id}")

    print("\nData loading complete.")