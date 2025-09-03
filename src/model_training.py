import os, sys, joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

class ModelTraining:
    def __init__(self, processed_data_path, model_output_path):
        self.processed_path = processed_data_path
        self.model_path = model_output_path
        self.clf = None
        self.X_train = self.X_test = self.y_train = self.y_test = None
        os.makedirs(self.model_path, exist_ok=True)
        logger.info("Model Training initialized...")

    def load_data(self):
        try:
            self.X_train = joblib.load(os.path.join(self.processed_path, "X_train.pkl"))
            self.X_test  = joblib.load(os.path.join(self.processed_path, "X_test.pkl"))
            self.y_train = joblib.load(os.path.join(self.processed_path, "y_train.pkl"))
            self.y_test  = joblib.load(os.path.join(self.processed_path, "y_test.pkl"))

            logger.info("Data loaded sucesfuly...")

        except Exception as e:
            raise CustomException("Failed to load data", sys)

    def train_model(self):
        try:
            # Figure out column types (assumes DataFrame)
            cat_cols = self.X_train.select_dtypes(include=['object','string','category']).columns
            num_cols = self.X_train.select_dtypes(include=[np.number]).columns

            # Preprocess
            numeric_pipe = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                # No scaler needed for RandomForest; keep numeric as-is
            ])
            categorical_pipe = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ])

            preprocessor = ColumnTransformer(
                transformers=[
                    ("num", numeric_pipe, list(num_cols)),
                    ("cat", categorical_pipe, list(cat_cols)),
                ],
                remainder="drop",
            )

            model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)

            self.clf = Pipeline(steps=[
                ("prep", preprocessor),
                ("rf", model),
            ])

            self.clf.fit(self.X_train, self.y_train)

            joblib.dump(self.clf, os.path.join(self.model_path, "model.pkl"))

            logger.info("Model trained and saved sucesfuly...")

        except Exception as e:
            logger.error(f"Error while training model {e}")
            raise CustomException("Failed to train model", sys)

    def evaluate_model(self):
        try:
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            y_pred = self.clf.predict(self.X_test)
            return {
                "accuracy":  accuracy_score(self.y_test, y_pred),
                "precision": precision_score(self.y_test, y_pred, average="weighted", zero_division=0),
                "recall":    recall_score(self.y_test, y_pred, average="weighted", zero_division=0),
                "f1":        f1_score(self.y_test, y_pred, average="weighted", zero_division=0),
                
            }
        
        
        except Exception as e:
            logger.error(f"Error while evaluating model {e}")
            raise CustomException("Failed to evaluate model", sys)

    def run(self):
        self.load_data()
        self.train_model()
        metrics = self.evaluate_model()
        logger.info(metrics)
        return metrics
if __name__=="__main__":
    trainer = ModelTraining("artifacts/processed/" , "artifacts/models/")
    trainer.run()