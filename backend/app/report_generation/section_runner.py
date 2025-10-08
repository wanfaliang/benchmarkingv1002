"""Orchestrates the generation of all 20 sections."""

import logging
from pathlib import Path
from typing import Dict
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.analysis import Analysis
from ..models.section import Section
from ..services.collector_loader_service import collector_loader_service
from ..services.file_service import FileService

import importlib

logger = logging.getLogger(__name__)
file_service = FileService()

SECTIONS_METADATA = [
    {"number": 0, "name": "Cover & Metadata"},
    {"number": 1, "name": "Executive Summary"},
    {"number": 2, "name": "Company Classification & Factor Tags"},
    {"number": 3, "name": "Financial Overview & Historical Analysis"},
    {"number": 4, "name": "Profitability & Returns Analysis"},
    {"number": 5, "name": "Liquidity, Solvency & Capital Structure"},
    {"number": 6, "name": "Workforce & Productivity Analysis"},
    {"number": 7, "name": "Valuation Analysis"},
    {"number": 8, "name": "Macroeconomic Environment Analysis"},
    {"number": 9, "name": "Signal Discovery & Macro-Financial Analysis"},
    {"number": 10, "name": "Regimes & Scenario Analysis"},
    {"number": 11, "name": "Risk & Alert Panel"},
    {"number": 12, "name": "Peer Context & Comparative Analysis"},
    {"number": 13, "name": "Institutional Ownership Dynamics"},
    {"number": 14, "name": "Insider Activity & Corporate Sentiment"},
    {"number": 15, "name": "Market Microstructure Analysis"},
    {"number": 16, "name": "Benchmark Relative Analysis"},
    {"number": 17, "name": "Cross-Asset Signal Discovery"},
    {"number": 18, "name": "Equity Analysis & Investment Risk Assessment"},
    {"number": 19, "name": "Appendix"},
]


class SectionRunner:
    """Manages the generation of all analysis sections."""
    
    def __init__(self, analysis_id: str, db: Session):
        self.analysis_id = analysis_id
        self.db = db
        self.collector = None
    
    def initialize(self):
        """Load the financial collector and prepare for section generation."""
        logger.info(f"Loading financial collector for analysis {self.analysis_id}")
        self.collector = collector_loader_service.load_financial_collector(self.analysis_id)
        logger.info("Collector loaded successfully")
    
    def create_section_records(self):
        """Create section records in the database for tracking."""
        for section_meta in SECTIONS_METADATA:
            section = Section(
                analysis_id=self.analysis_id,
                section_number=section_meta["number"],
                section_name=section_meta["name"],
                status="pending"
            )
            self.db.add(section)
        
        self.db.commit()
        logger.info(f"Created {len(SECTIONS_METADATA)} section records")
    
    def generate_section(self, section_number: int) -> bool:
        """Generate a single section."""
        section = self.db.query(Section).filter(
            Section.analysis_id == self.analysis_id,
            Section.section_number == section_number
        ).first()
        
        if not section:
            logger.error(f"Section {section_number} not found in database")
            return False
        
        try:
            section.status = "processing"
            section.started_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Generating section {section_number}: {section.section_name}")
            
            # Import and call the section generator
            try:
                # Get the sections directory
                sections_dir = Path(__file__).parent / "sections"
                module_file = sections_dir / f"section_{section_number:02d}.py"
                
                logger.info(f"Looking for module at: {module_file}")
                
                if not module_file.exists():
                    raise ModuleNotFoundError(f"Section file not found: {module_file}")
                
                # Import using spec
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    f"section_{section_number:02d}", 
                    module_file
                )
                section_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(section_module)
                
                html_content = section_module.generate(
                    collector=self.collector,
                    analysis_id=self.analysis_id
                )
            except (ModuleNotFoundError, FileNotFoundError) as e:
                logger.warning(f"Section {section_number} not implemented yet: {str(e)}")
                html_content = self._generate_placeholder(section_number, section.section_name)
            
            # Save HTML file
            section_path = file_service.get_section_path(
                self.analysis_id, 
                section_number, 
                section.section_name
            )
            
            with open(section_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Update section record
            section.status = "complete"
            section.completed_at = datetime.utcnow()
            section.html_path = str(section_path)
            
            if section.started_at:
                processing_time = (section.completed_at - section.started_at).total_seconds()
                section.processing_time = processing_time
            
            self.db.commit()
            logger.info(f"Section {section_number} completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate section {section_number}: {str(e)}", exc_info=True)
            section.status = "failed"
            section.error_message = str(e)
            section.completed_at = datetime.utcnow()
            self.db.commit()
            return False
    
    def _generate_placeholder(self, section_number: int, section_name: str) -> str:
        """Generate placeholder HTML for unimplemented sections."""
        from .html_utils import generate_section_wrapper
        
        content = f"""
        <div class="placeholder-section">
            <h2>Section {section_number}: {section_name}</h2>
            <p class="placeholder-message">This section is not yet implemented.</p>
            <p>Create the section generator at:</p>
            <code>backend/app/report_generation/sections/section_{section_number:02d}.py</code>
        </div>
        """
        return generate_section_wrapper(section_number, section_name, content)
    
    def generate_all_sections(self) -> Dict:
        """Generate all 20 sections sequentially."""
        results = {
            "total": len(SECTIONS_METADATA),
            "successful": 0,
            "failed": 0,
            "failures": []
        }
        
        for section_meta in SECTIONS_METADATA:
            section_number = section_meta["number"]
            success = self.generate_section(section_number)
            
            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["failures"].append(section_number)
        
        return results


def run_section_generation(analysis: Analysis, db: Session):
    """Main entry point for Phase B - called by BackgroundTasks."""
    try:
        analysis.status = "generating"
        analysis.phase = "B"
        analysis.progress = 0
        db.commit()
        
        runner = SectionRunner(analysis.analysis_id, db)
        runner.initialize()
        runner.create_section_records()
        
        logger.info(f"Starting generation of all sections for analysis {analysis.analysis_id}")
        results = runner.generate_all_sections()
        
        if results["failed"] == 0:
            analysis.status = "complete"
        else:
            analysis.status = "partial_complete"
            analysis.error_log = f"Failed sections: {results['failures']}"
        
        analysis.progress = 100
        db.commit()
        
        logger.info(f"Section generation completed: {results}")
        
    except Exception as e:
        logger.error(f"Section generation failed: {str(e)}", exc_info=True)
        analysis.status = "generation_failed"
        analysis.error_log = str(e)
        db.commit()
        raise