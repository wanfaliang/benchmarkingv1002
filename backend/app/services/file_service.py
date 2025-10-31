"""File management service"""
import os
from pathlib import Path
from typing import Optional
from ..config import settings

class FileService:
    def __init__(self):
        self.data_dir = Path(settings.DATA_DIR)
    
    def get_analysis_dir(self, analysis_id: str) -> Path:
        """Get analysis directory path"""
        return self.data_dir / "analyses" / analysis_id
    
    def get_raw_data_path(self, analysis_id: str) -> Path:
        """Get raw data Excel file path"""
        return self.get_analysis_dir(analysis_id) / "raw_data.xlsx"
    
    
    def get_sections_dir(self, analysis_id: str) -> Path:
        """Get sections directory path"""
        return self.get_analysis_dir(analysis_id) / "sections"
    
    def get_section_path(self, analysis_id: str, section_number: int, section_name: str) -> Path:
        """Get the path for a specific section HTML file."""
        sections_dir = self.get_sections_dir(analysis_id)
        clean_name = section_name.lower().replace(" ", "_").replace("&", "and")
        filename = f"section_{section_number:02d}_{clean_name}.html"
        return sections_dir / filename
    
    def create_analysis_dirs(self, analysis_id: str) -> None:
        """Create directory structure for analysis"""
        analysis_dir = self.get_analysis_dir(analysis_id)
        sections_dir = self.get_sections_dir(analysis_id)
        
        analysis_dir.mkdir(parents=True, exist_ok=True)
        sections_dir.mkdir(parents=True, exist_ok=True)
    
    def raw_data_exists(self, analysis_id: str) -> bool:
        """Check if raw data file exists"""
        return self.get_raw_data_path(analysis_id).exists()
    
    def get_shared_economic_indicators_path(self) -> Path:
        """Get shared economic indicators file path"""
        return self.data_dir / "shared"
    
    def get_collector_pickle_path(self, analysis_id: str) -> Path:
        """Get path to the pickled FinancialDataCollection object."""
        return self.get_analysis_dir(analysis_id) / "financial_collector.pkl"

    def collector_pickle_exists(self, analysis_id: str) -> bool:
        """Check if collector pickle file exists."""
        return self.get_collector_pickle_path(analysis_id).exists()
    
    # --------------------------------------------------------------------------
    # dataset methods
    
    def get_dataset_directory(self,dataset_id: str) -> Path:
        """Get directory path for a dataset"""
        base_dir = self.data_dir / "datasets" / dataset_id
        return base_dir
    
    def get_raw_dataset_path(self, dataset_id: str) -> Path:
        """Get raw data Excel file path"""
        return self.get_dataset_directory(dataset_id) / "raw_data.xlsx"
    
    def get_dataset_sections_directory(self, dataset_id: str) -> Path:
        """Get sections directory path"""
        return self.get_dataset_directory(dataset_id) / "sections" 

    def create_dataset_directory(self, dataset_id: str) -> None:
        """Create directory structure for analysis"""
        dataset_dir = self.get_dataset_directory(dataset_id)
        sections_dir = self.get_dataset_sections_directory(dataset_id)
        
        dataset_dir.mkdir(parents=True, exist_ok=True)
        sections_dir.mkdir(parents=True, exist_ok=True)

    def raw_dataset_exists(self, dataset_id: str) -> bool:
        """Check if raw data file exists"""
        return self.get_raw_dataset_path(dataset_id).exists()   

    def get_dataset_collector_pickle_path(self, dataset_id: str) -> Path:
        """Get path to the pickled FinancialDataCollection object."""
        return self.get_dataset_directory(dataset_id) / "dataset_collector.pkl"
    
    def dataset_collector_pickle_exists(self, dataset_id: str) -> bool:
        """Check if dataset collector pickle file exists."""
        return self.get_dataset_collector_pickle_path(dataset_id).exists()

    def ensure_directory_exists(self, directory: Path):
        """Create directory if it doesn't exist"""
        directory.mkdir(parents=True, exist_ok=True)


file_service = FileService()
