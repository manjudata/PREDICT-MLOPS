import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

class DataProcessing:
    def __init__(self,input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None
        self.features = None

        os.makedirs(self.output_path,exist_ok=True)
        logger.info("Data Processing initalized...")

    def load_data(self):
        try:
            self.df = pd.read_csv(self.input_path)
            logger.info("Data loaded sucesfully...")
        except Exception as e:
            logger.error(f"Error while loading data {e}")
            raise CustomException("Failed to load data",e)
        
    def preprocess(self):
        try:
            categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
            for col in categorical_cols:
                self.df[col] =self.df[col].astype('category')
            self.df['Last_Maintenance_Date'] = pd.to_datetime(self.df['Last_Maintenance_Date'])

            self.df['Maintenance_Year'] = self.df['Last_Maintenance_Date'].dt.year
            self.df['Maintenance_Month'] = self.df['Last_Maintenance_Date'].dt.month
            self.df['Maintenance_Day'] = self.df['Last_Maintenance_Date'].dt.day
            self.df['Maintenance_Weekday'] = self.df['Last_Maintenance_Date'].dt.weekday
            self.df.drop('Last_Maintenance_Date', axis=1, inplace=True)
            self.df = self.df.drop(['Vehicle_ID','Make_and_Model','Route_Info'], axis = 1)
            le = LabelEncoder()
            self.df['Vehicle_Type'] = le.fit_transform(self.df['Vehicle_Type'])
            brake_map = {'Good': 2, 'Fair': 1, 'Poor': 0}
            self.df['Brake_Condition'] = self.df['Brake_Condition'].map(brake_map)
            self.df.columns = self.df.columns.str.strip()
            non_numeric_cols = self.df.select_dtypes(exclude=['number']).columns

            logger.info("All basic data preprocessing done..")
        
        except Exception as e:
            logger.error(f"Error while preprocessing data {e}")
            raise CustomException("Failed to preprocess data",e)
              
    def split_and_scale_and_save(self):
        try:

    
            X = self.df.drop('Maintenance_Required', axis=1)
            y = self.df['Maintenance_Required']
      
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            joblib.dump(X_train, os.path.join(self.output_path, "X_train.pkl")) 
            joblib.dump(X_test, os.path.join(self.output_path, "X_test.pkl")) 
            joblib.dump(y_train, os.path.join(self.output_path, "y_train.pkl")) 
            joblib.dump(y_test, os.path.join(self.output_path, "y_test.pkl"))    

            logger.info("All things saved sucesfully for Data processing..")

        except Exception as e:
            logger.error(f"Error while split scale and save data {e}")
            raise CustomException("Failed to split sacle and save data",e)


    def run(self):
        self.load_data()
        self.preprocess()
        self.split_and_scale_and_save()

if __name__=="__main__":
    processor = DataProcessing("artifacts/raw/vehicledata.csv" , "artifacts/processed")
    processor.run()

