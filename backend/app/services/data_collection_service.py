"""Data collection service using Version Zero collectors"""
import os
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any

from ..models.analysis import Analysis
from ..services.file_service import file_service
from ..config import settings

# Import Version Zero classes (we'll need to adjust import paths)
from ..data_collection.fred_collector import FREDCollector  
from ..data_collection.financial_collector import FinancialDataCollection
from .collector_loader_service import collector_loader_service

class DataCollectionService:
    def __init__(self):
        self.fmp_api_key = settings.FMP_API_KEY
        self.fred_api_key = settings.FRED_API_KEY
    
    def collect_data_for_analysis(self, db: Session, analysis: Analysis) -> None:
        """Run Phase A data collection for an analysis"""
        
        print(f"Starting data collection for analysis {analysis.analysis_id}")
        
        # Update analysis status
        analysis.status = "collection"
        analysis.phase = "A"
        analysis.started_at = datetime.utcnow()
        db.commit()
        
        try:
            # Create directories
            file_service.create_analysis_dirs(analysis.analysis_id)
            
            # Convert companies list back to dictionary for FinancialDataCollection
            companies_dict = {
                company['name']: company['ticker'] 
                for company in analysis.companies
            }
            
            # Extract just the tickers list
            tickers = [company['ticker'] for company in analysis.companies]
            
            print(f"Collecting data for companies: {companies_dict}")
            print(f"Years back: {analysis.years_back}")
            
            # Step 1: Collect economic indicators (FREDCollector)
            # This needs to be adapted from Version Zero
            print("✓ Collecting economic indicators...")
            # fred_collector = FREDCollector(self.fred_api_key)
            # fred_data = fred_collector.collect_indicators()
            
            # Step 2: Collect financial data (FinancialDataCollection) 
            
            financial_collector = FinancialDataCollection(
                 api_key=self.fmp_api_key,
                 companies=companies_dict,
                 years=analysis.years_back,
                 export_dir=file_service.get_analysis_dir(analysis.analysis_id),
                 econ_dir = file_service.get_shared_economic_indicators_path()
             )
            financial_data = financial_collector.get_all_financial_data(force_collect=True)
            raw_data_path = financial_collector.export_excel()
            # Step 3: Save to Excel file
            # raw_data_path = file_service.get_raw_data_path(analysis.analysis_id)
            # Save collected data to raw_data_path
            print(f"✓ Saving data to {raw_data_path}")
            
            print("✓ Raw collection complete")

            collector_path = collector_loader_service.save_financial_collector(
            collector=financial_collector,
            analysis_id=analysis.analysis_id
            )
            
            collector_info = collector_loader_service.get_collector_info(analysis.analysis_id)
            if collector_info:
                print(f"Collector file size: {collector_info['size_mb']} MB")
            
            # Update analysis status
            analysis.status = "collection_complete"
            analysis.progress = 100  # Phase A complete
            db.commit()
            
            print(f"Data collection completed for analysis {analysis.analysis_id}")
            
        except Exception as e:
            print(f"Data collection failed: {str(e)}")
            analysis.status = "failed"
            analysis.error_log = str(e)
            db.commit()
            raise

data_collection_service = DataCollectionService()