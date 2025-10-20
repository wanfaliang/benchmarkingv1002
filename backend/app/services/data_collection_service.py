"""Data collection service using Version Zero collectors"""
import os
import asyncio
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
from ..core.websocket_manager import manager
from ..database import SessionLocal

class DataCollectionService:
    def __init__(self):
        self.fmp_api_key = settings.FMP_API_KEY
        self.fred_api_key = settings.FRED_API_KEY
    
    async def collect_data_for_analysis(self, analysis_id: str) -> None:
        """Run Phase A data collection for an analysis"""
        db = SessionLocal()
        try:
            analysis: Analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
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
        
            
                financial_collector = FinancialDataCollection(
                    api_key=self.fmp_api_key,
                    companies=companies_dict,
                    years=analysis.years_back,
                    export_dir=file_service.get_analysis_dir(analysis.analysis_id),
                    econ_dir = file_service.get_shared_economic_indicators_path(),
                    websocket_manager=manager,
                    analysis_id=analysis.analysis_id
                )
                await financial_collector.get_all_financial_data_async(force_collect=True)
                await financial_collector.export_excel()

                # Save pickled collector for later use
                collector_loader_service.save_financial_collector(
                collector=financial_collector,
                analysis_id=analysis.analysis_id
                )
                
                # Update analysis status
                analysis.status = "collection_complete"
                analysis.progress = 100  # Phase A complete
                db.commit()
                
                await manager.broadcast_completion(
                analysis_id=analysis.analysis_id,
                status="collection_complete"
                )
                print(f"Data collection completed successfully")
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Data collection failed: {error_msg}")
                
                analysis.status = "failed"
                analysis.error_log = f"Collection failed: {error_msg}"
                db.commit()
                
                await manager.broadcast_error(
                    analysis_id=analysis.analysis_id,
                    error=error_msg
                )
                
                raise
            
           
        finally:
            db.close()
        
        

data_collection_service = DataCollectionService()