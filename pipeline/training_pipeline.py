
from src.data_processing import DataProcessing
from src.model_training import ModelTraining

if __name__=="__main__":
    processor = DataProcessing("artifacts/raw/vehicledata.csv" , "artifacts/processed")
    processor.run()

    trainer = ModelTraining("artifacts/processed/" , "artifacts/models/")
    trainer.run()

