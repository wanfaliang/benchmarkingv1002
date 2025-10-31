import pickle
from pathlib import Path
from typing import Optional
from .file_service import FileService
from ..data_collection.financial_collector import FinancialDataCollection
from ..data_collection.dataset_collector import DatasetCollection

file_service = FileService()

class CollectorLoaderService:
    """Service for loading and managing pickled FinancialDataCollection objects."""
    
    @staticmethod
    def load_financial_collector(analysis_id: str) -> FinancialDataCollection:
        """
        Load the pickled FinancialDataCollection object for an analysis.
        
        Args:
            analysis_id: The unique identifier for the analysis
            
        Returns:
            FinancialDataCollection object with all collected data
            
        Raises:
            FileNotFoundError: If the pickle file doesn't exist
            pickle.UnpicklingError: If the file is corrupted
        """
        collector_path = file_service.get_collector_pickle_path(analysis_id)
        
        if not collector_path.exists():
            raise FileNotFoundError(
                f"Financial collector not found for analysis {analysis_id}. "
                "Data collection (Phase A) must be completed first."
            )
        
        try:
            with open(collector_path, 'rb') as f:
                collector = pickle.load(f)
            
            # Validate it's the right type
            if not isinstance(collector, FinancialDataCollection):
                raise TypeError(
                    f"Loaded object is not a FinancialDataCollection instance. "
                    f"Got {type(collector)} instead."
                )
            
            return collector
            
        except pickle.UnpicklingError as e:
            raise pickle.UnpicklingError(
                f"Failed to load collector for analysis {analysis_id}. "
                f"The pickle file may be corrupted: {str(e)}"
            )
    
    @staticmethod
    def save_financial_collector(
        collector: FinancialDataCollection, 
        analysis_id: str
    ) -> Path:
        """
        Save a FinancialDataCollection object to disk.
        
        Args:
            collector: The FinancialDataCollection object to save
            analysis_id: The unique identifier for the analysis
            
        Returns:
            Path to the saved pickle file
        """
        collector_path = file_service.get_collector_pickle_path(analysis_id)
        
        try:
            with open(collector_path, 'wb') as f:
                pickle.dump(collector, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            return collector_path
            
        except Exception as e:
            raise IOError(
                f"Failed to save collector for analysis {analysis_id}: {str(e)}"
            )
    
    @staticmethod
    def delete_financial_collector(analysis_id: str) -> bool:
        """
        Delete the pickled collector file for an analysis.
        
        Args:
            analysis_id: The unique identifier for the analysis
            
        Returns:
            True if deleted, False if file didn't exist
        """
        collector_path = file_service.get_collector_pickle_path(analysis_id)
        
        if collector_path.exists():
            collector_path.unlink()
            return True
        return False
    
    @staticmethod
    def get_collector_info(analysis_id: str) -> Optional[dict]:
        """
        Get information about the pickled collector without loading it.
        
        Args:
            analysis_id: The unique identifier for the analysis
            
        Returns:
            Dict with file info, or None if file doesn't exist
        """
        collector_path = file_service.get_collector_pickle_path(analysis_id)
        
        if not collector_path.exists():
            return None
        
        stat_info = collector_path.stat()
        return {
            "path": str(collector_path),
            "size_bytes": stat_info.st_size,
            "size_mb": round(stat_info.st_size / (1024 * 1024), 2),
            "modified_at": stat_info.st_mtime
        }
    
    # --------------------------------------------------------------------------
    # dataset loader, saver, deleter, info methods
    # --------------------------------------------------------------------------
    @staticmethod
    def load_dataset_collector(dataset_id: str) -> DatasetCollection:

        collector_path = file_service.get_dataset_collector_pickle_path(dataset_id)
        
        if not collector_path.exists():
            raise FileNotFoundError(
                f"Dataset collector not found for analysis {dataset_id}. "
                "Data collection (Phase A) must be completed first."
            )
        
        try:
            with open(collector_path, 'rb') as f:
                collector = pickle.load(f)
            
            # Validate it's the right type
            if not isinstance(collector, DatasetCollection):
                raise TypeError(
                    f"Loaded object is not a DatasetCollection instance. "
                    f"Got {type(collector)} instead."
                )
            
            return collector
            
        except pickle.UnpicklingError as e:
            raise pickle.UnpicklingError(
                f"Failed to load collector for dataset {dataset_id}. "
                f"The pickle file may be corrupted: {str(e)}"
            )
    
    @staticmethod
    def save_dataset_collector(
        collector: DatasetCollection, 
        dataset_id: str
    ) -> Path:

        collector_path = file_service.get_dataset_collector_pickle_path(dataset_id)
        
        try:
            with open(collector_path, 'wb') as f:
                pickle.dump(collector, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            return collector_path
            
        except Exception as e:
            raise IOError(
                f"Failed to save dataset collector for dataset {dataset_id}: {str(e)}"
            )
    
    @staticmethod
    def delete_dataset_collector(analysis_id: str) -> bool:

        collector_path = file_service.get_dataset_collector_pickle_path(analysis_id)
        
        if collector_path.exists():
            collector_path.unlink()
            return True
        return False
    
    @staticmethod
    def get_dataset_collector_info(dataset_id: str) -> Optional[dict]:

        collector_path = file_service.get_dataset_collector_pickle_path(dataset_id)
        
        if not collector_path.exists():
            return None
        
        stat_info = collector_path.stat()
        return {
            "path": str(collector_path),
            "size_bytes": stat_info.st_size,
            "size_mb": round(stat_info.st_size / (1024 * 1024), 2),
            "modified_at": stat_info.st_mtime
        }


# Create a singleton instance
collector_loader_service = CollectorLoaderService()