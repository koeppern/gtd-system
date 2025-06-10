#!/usr/bin/env python3
"""
GTD Tasks ETL Pipeline
Extracts, transforms and loads GTD tasks from Notion CSV export into Supabase.
"""

import os
import sys
import csv
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from supabase import create_client, Client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GTDTasksETL:
    """ETL Pipeline for GTD Tasks from Notion export"""
    
    def __init__(self, user_id: Optional[str] = None):
        """Initialize ETL pipeline with Supabase connection"""
        load_dotenv()
        
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.user_id = user_id or os.getenv("DEFAULT_USER_ID")
        
        if not all([self.supabase_url, self.supabase_key, self.user_id]):
            raise ValueError(
                "Missing required environment variables: "
                "SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, DEFAULT_USER_ID"
            )
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.tasks_table = "gtd_tasks"
        self.projects_table = "gtd_projects"
        self.fields_table = "gtd_fields"
        
        # Caches for performance
        self._field_id_cache = None
        self._project_mapping_cache = None
    
    def get_field_id_mapping(self) -> Dict[str, int]:
        """Get field name to ID mapping from database"""
        if self._field_id_cache is None:
            try:
                result = self.supabase.table(self.fields_table).select("id, name").execute()
                self._field_id_cache = {field['name']: field['id'] for field in result.data}
                logger.info(f"Loaded field mapping: {self._field_id_cache}")
            except Exception as e:
                logger.error(f"Error loading field mapping: {e}")
                self._field_id_cache = {'Private': 1, 'Work': 2}
                logger.warning(f"Using fallback field mapping: {self._field_id_cache}")
        
        return self._field_id_cache
    
    def get_project_mapping(self) -> Dict[str, int]:
        """Get project name to ID mapping from database"""
        if self._project_mapping_cache is None:
            try:
                result = self.supabase.table(self.projects_table).select("id, project_name, readings").eq("user_id", self.user_id).execute()
                self._project_mapping_cache = {}
                
                for project in result.data:
                    # Use project_name as primary key
                    if project.get('project_name'):
                        self._project_mapping_cache[project['project_name'].strip().lower()] = project['id']
                    
                    # Also use readings as alternative key
                    if project.get('readings'):
                        self._project_mapping_cache[project['readings'].strip().lower()] = project['id']
                
                logger.info(f"Loaded {len(self._project_mapping_cache)} project mappings")
                
            except Exception as e:
                logger.error(f"Error loading project mapping: {e}")
                self._project_mapping_cache = {}
        
        return self._project_mapping_cache
    
    def normalize_boolean(self, value: Any) -> bool:
        """Convert string boolean values to Python boolean"""
        if value is None or pd.isna(value):
            return False
        
        value_str = str(value).strip().lower()
        return value_str in ['yes', 'true', '1']
    
    def normalize_field_id(self, value: Any) -> Optional[int]:
        """Convert field value to field ID"""
        if value is None or pd.isna(value) or str(value).strip() == '':
            return None
        
        value_str = str(value).strip()
        field_mapping = self.get_field_id_mapping()
        
        # Normalize field names
        if value_str.lower() in ['private']:
            return field_mapping.get('Private')
        elif value_str.lower() in ['work']:
            return field_mapping.get('Work')
        else:
            return field_mapping.get(value_str)
    
    def parse_project_reference(self, project_ref: str) -> tuple[Optional[str], Optional[int]]:
        """
        Parse project reference to extract project name and find project ID
        Format: "Project Name (https://www.notion.so/...)"
        Returns: (project_name, project_id)
        """
        if not project_ref or pd.isna(project_ref):
            return None, None
        
        project_ref = str(project_ref).strip()
        
        # Extract project name (text before first parenthesis)
        match = re.match(r'^([^(]+)(?:\s*\([^)]*\))?', project_ref)
        if match:
            project_name = match.group(1).strip()
        else:
            project_name = project_ref
        
        # Find project ID from mapping
        project_mapping = self.get_project_mapping()
        project_id = project_mapping.get(project_name.lower())
        
        if not project_id:
            # Try fuzzy matching
            for mapped_name, mapped_id in project_mapping.items():
                if project_name.lower() in mapped_name or mapped_name in project_name.lower():
                    project_id = mapped_id
                    break
        
        return project_name, project_id
    
    def parse_date(self, date_str: Any) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str or pd.isna(date_str):
            return None
        
        date_str = str(date_str).strip()
        if not date_str:
            return None
        
        # Common date formats in Notion exports
        date_formats = [
            "%B %d, %Y %I:%M %p",  # "March 6, 2022 1:46 PM"
            "%B %d, %Y",           # "February 28, 2022"
            "%Y-%m-%d %H:%M:%S",   # ISO format
            "%Y-%m-%d",            # ISO date only
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def clean_value(self, value: Any) -> Any:
        """Clean value to be JSON-compatible"""
        if value is None or pd.isna(value):
            return None
        
        # Handle datetime and date objects
        if isinstance(value, datetime):
            return value.isoformat()
        elif hasattr(value, 'isoformat'):  # date objects
            return value.isoformat()
        
        str_value = str(value).strip()
        if str_value in ['nan', 'NaN', '']:
            return None
        
        return str_value if str_value else None
    
    def transform_task_row(self, row: Dict[str, Any], row_num: int, source_file: str) -> Dict[str, Any]:
        """Transform a single CSV row into database format"""
        
        # Parse project reference
        project_name, project_id = self.parse_project_reference(row.get('🚀Project'))
        
        # Parse dates
        last_edited = self.parse_date(row.get('Last editted'))
        date_of_creation = self.parse_date(row.get('Date of creation'))
        do_on_date_parsed = self.parse_date(row.get('📆Do on date'))
        do_on_date = do_on_date_parsed.date() if do_on_date_parsed else None
        
        # Parse done_at timestamp
        done_at = None
        if self.normalize_boolean(row.get('🟩Done')):
            # Use last_edited as completion time, fallback to creation time
            done_at = last_edited or date_of_creation
        
        return {
            'user_id': self.user_id,
            'notion_export_row': row_num,
            'task_name': self.clean_value(row.get('Task name')) or f"Task_{row_num}",
            'project_id': project_id,
            'project_reference': self.clean_value(project_name),
            
            # Status flags
            'done_at': self.clean_value(done_at),
            'do_today': self.normalize_boolean(row.get('✨Do today')),
            'do_this_week': self.normalize_boolean(row.get('🌙Do this week')),
            'is_reading': self.normalize_boolean(row.get('📙Reading')),
            'wait_for': self.normalize_boolean(row.get('⌛Wait for')),
            'postponed': self.normalize_boolean(row.get('Postponed')),
            'reviewed': self.normalize_boolean(row.get('👌Reviewed')),
            
            # Dates and timing
            'do_on_date': self.clean_value(do_on_date),
            'last_edited': self.clean_value(last_edited),
            'date_of_creation': self.clean_value(date_of_creation),
            
            # Additional fields
            'field_id': self.normalize_field_id(row.get('👔Field')),
            'priority': self.clean_value(row.get("Project's priority")),
            'time_expenditure': self.clean_value(row.get('Time expenditure')),
            'url': self.clean_value(row.get('🕸URL')),
            'knowledge_db_entry': self.clean_value(row.get('🎓Related Knowledge DB entry')),
            
            # Metadata
            'source_file': source_file
        }
    
    def extract_and_transform_tasks(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """Extract data from CSV and transform it"""
        csv_path = Path(csv_file_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        
        logger.info(f"Reading tasks CSV file: {csv_file_path}")
        
        transformed_data = []
        errors = []
        
        try:
            # Read CSV with pandas to handle multiline fields properly
            df = pd.read_csv(csv_file_path, encoding='utf-8')
            
            logger.info(f"Found {len(df)} tasks in CSV")
            
            # Pre-load mappings for performance
            self.get_field_id_mapping()
            self.get_project_mapping()
            
            for idx, row in df.iterrows():
                try:
                    # Skip empty rows
                    if pd.isna(row.get('Task name')) and pd.isna(row.get('🚀Project')):
                        logger.debug(f"Skipping empty row {idx + 2}")
                        continue
                    
                    transformed_row = self.transform_task_row(
                        row.to_dict(), 
                        idx + 2,  # CSV row number (accounting for header)
                        csv_path.name
                    )
                    transformed_data.append(transformed_row)
                    
                except Exception as e:
                    error_msg = f"Error transforming row {idx + 2}: {e}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    continue
            
            logger.info(f"Successfully transformed {len(transformed_data)} tasks")
            
            # Log project mapping statistics
            mapped_count = sum(1 for task in transformed_data if task['project_id'] is not None)
            unmapped_count = len(transformed_data) - mapped_count
            logger.info(f"Project mapping: {mapped_count} mapped, {unmapped_count} unmapped")
            
            if errors:
                logger.warning(f"Encountered {len(errors)} errors during transformation")
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def truncate_tasks_table(self, force: bool = False) -> bool:
        """Truncate the gtd_tasks table with user confirmation"""
        if not force:
            try:
                response = input(f"This will delete all existing tasks for user {self.user_id}. Continue? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Operation cancelled by user")
                    return False
            except EOFError:
                logger.warning("No input available, assuming 'no' for safety")
                return False
        
        try:
            result = self.supabase.table(self.tasks_table).delete().eq('user_id', self.user_id).execute()
            logger.info(f"Deleted existing tasks for user {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error truncating tasks table: {e}")
            return False
    
    def load_tasks_data(self, data: List[Dict[str, Any]]) -> None:
        """Load transformed tasks data into Supabase"""
        if not data:
            logger.warning("No tasks data to load")
            return
        
        logger.info(f"Loading {len(data)} tasks into {self.tasks_table}")
        
        # Insert data in batches
        batch_size = 100
        success_count = 0
        error_count = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            try:
                result = self.supabase.table(self.tasks_table).insert(batch).execute()
                success_count += len(batch)
                logger.info(f"Inserted tasks batch {i//batch_size + 1}: {len(batch)} records")
                
            except Exception as e:
                error_count += len(batch)
                logger.error(f"Error inserting tasks batch {i//batch_size + 1}: {e}")
                
                # Try inserting records individually in this batch
                for record in batch:
                    try:
                        self.supabase.table(self.tasks_table).insert(record).execute()
                        success_count += 1
                        error_count -= 1
                    except Exception as individual_error:
                        logger.warning(f"Error inserting individual task: {individual_error}")
        
        logger.info(f"Tasks load complete: {success_count} successful, {error_count} failed")
    
    def run_tasks_etl(self, csv_file_path: str, truncate: bool = True, force: bool = False) -> None:
        """Run the complete ETL process for tasks"""
        logger.info("Starting GTD Tasks ETL process")
        
        try:
            # Truncate existing data if requested
            if truncate:
                if not self.truncate_tasks_table(force=force):
                    return
            
            # Extract and transform
            data = self.extract_and_transform_tasks(csv_file_path)
            
            # Load
            self.load_tasks_data(data)
            
            logger.info("Tasks ETL process completed successfully")
            
        except Exception as e:
            logger.error(f"Tasks ETL process failed: {e}")
            raise


def find_gtd_tasks_csv() -> str:
    """Find the GTD Tasks CSV file in the data directory"""
    data_dir = Path("data/from_notion")
    
    if not data_dir.exists():
        raise FileNotFoundError("Data directory not found: data/from_notion")
    
    # Search for the GTD_Tasks CSV file
    csv_files = list(data_dir.rglob("GTD_Tasks*_all.csv"))
    
    if not csv_files:
        raise FileNotFoundError("GTD_Tasks CSV file not found in data directory")
    
    if len(csv_files) > 1:
        logger.warning(f"Multiple GTD_Tasks CSV files found, using: {csv_files[0]}")
    
    return str(csv_files[0])


def main():
    """Main entry point for the ETL script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL Pipeline for GTD Tasks')
    parser.add_argument('--force', action='store_true', 
                       help='Force truncate without confirmation')
    parser.add_argument('--no-truncate', action='store_true',
                       help='Skip truncation of existing data')
    
    args = parser.parse_args()
    
    try:
        # Find CSV file
        csv_file = find_gtd_tasks_csv()
        logger.info(f"Found GTD Tasks CSV: {csv_file}")
        
        # Initialize and run ETL
        etl = GTDTasksETL()
        etl.run_tasks_etl(csv_file, truncate=not args.no_truncate, force=args.force)
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()