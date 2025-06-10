#!/usr/bin/env python3
"""
GTD Projects ETL Pipeline
Extracts, transforms and loads GTD projects from Notion CSV export into Supabase.
"""

import os
import sys
import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import pandas as pd
from supabase import create_client, Client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GTDProjectsETL:
    """ETL Pipeline for GTD Projects from Notion export"""
    
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
        self.table_name = "gtd_projects"
        self.fields_table_name = "gtd_fields"
        self._field_id_cache = None
        
    def create_table_if_not_exists(self) -> None:
        """Check if required tables exist"""
        logger.info("Checking if required tables exist - tables must be created manually in Supabase")
        logger.info("Please run the SQL from sql/create_normalized_schema.sql in your Supabase SQL editor")
        
        # Check if both tables exist
        try:
            # Test gtd_fields table
            result = self.supabase.table(self.fields_table_name).select("id").limit(1).execute()
            logger.info(f"Table {self.fields_table_name} exists and is accessible")
            
            # Test gtd_projects table
            result = self.supabase.table(self.table_name).select("id").limit(1).execute()
            logger.info(f"Table {self.table_name} exists and is accessible")
            
        except Exception as e:
            logger.error(f"Required tables do not exist or are not accessible: {e}")
            logger.error("Please create the tables using sql/create_normalized_schema.sql")
            raise
    
    def normalize_boolean(self, value: str) -> Optional[bool]:
        """Convert string boolean values to Python boolean"""
        if value is None or pd.isna(value) or str(value).strip() == '':
            return None
        
        value_str = str(value).strip().lower()
        if value_str in ['yes', 'true', '1']:
            return True
        elif value_str in ['no', 'false', '0']:
            return False
        else:
            return None
    
    def get_field_id_mapping(self) -> Dict[str, int]:
        """Get field name to ID mapping from database"""
        if self._field_id_cache is None:
            try:
                result = self.supabase.table(self.fields_table_name).select("id, name").execute()
                self._field_id_cache = {field['name']: field['id'] for field in result.data}
                logger.info(f"Loaded field mapping: {self._field_id_cache}")
            except Exception as e:
                logger.error(f"Error loading field mapping: {e}")
                # Fallback to default mapping if table doesn't exist yet
                self._field_id_cache = {'Private': 1, 'Work': 2}
                logger.warning(f"Using fallback field mapping: {self._field_id_cache}")
        
        return self._field_id_cache
    
    def normalize_field(self, value: str) -> Optional[int]:
        """Normalize field values to field IDs"""
        if value is None or pd.isna(value) or str(value).strip() == '':
            return None
        
        value_str = str(value).strip()
        field_mapping = self.get_field_id_mapping()
        
        # Normalize to expected field names
        if value_str.lower() in ['private']:
            normalized_name = 'Private'
        elif value_str.lower() in ['work']:
            normalized_name = 'Work'
        else:
            normalized_name = value_str
        
        # Return field ID if found in mapping
        return field_mapping.get(normalized_name)
    
    def extract_project_name(self, readings: str, row_num: int) -> str:
        """Extract project name from readings field or generate from row number"""
        if readings is not None and not pd.isna(readings) and str(readings).strip():
            return str(readings).strip()
        else:
            return f"Project_{row_num}"
    
    def clean_value(self, value: Any) -> Any:
        """Clean value to be JSON-compatible"""
        if value is None or pd.isna(value):
            return None
        
        # Convert to string and check if empty
        str_value = str(value).strip()
        if str_value in ['nan', 'NaN', '']:
            return None
        
        return str_value if str_value else None
    
    def transform_row(self, row: Dict[str, Any], row_num: int, source_file: str) -> Dict[str, Any]:
        """Transform a single CSV row into database format"""
        return {
            'user_id': self.user_id,
            'notion_export_row': row_num,
            'done_status': self.normalize_boolean(row.get('❇Done')),
            'readings': self.clean_value(row.get('Readings')),
            'field_id': self.normalize_field(row.get('Field')),
            'keywords': self.clean_value(row.get('Keywords')),
            'done_duplicate': self.normalize_boolean(row.get('Done')),
            'mother_project': self.clean_value(row.get('Mother project')),
            'related_projects': self.clean_value(row.get('Related GTD_Projects')),
            'related_mother_projects': self.clean_value(row.get('Related to GTD_Projects (Mother project)')),
            'related_knowledge_vault': self.clean_value(row.get('Related to Knowledge volt (Project)')),
            'related_tasks': self.clean_value(row.get('Related to Tasks (Project)')),
            'do_this_week': self.normalize_boolean(row.get('🌙Do this week')),
            'gtd_processes': self.clean_value(row.get('🏃‍♂️ GTD_Processes')),
            'add_checkboxes': self.clean_value(row.get('Add checkboxes as option for answers')),
            'project_name': self.extract_project_name(row.get('Readings'), row_num),
            'source_file': source_file
        }
    
    def extract_and_transform(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """Extract data from CSV and transform it"""
        csv_path = Path(csv_file_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        
        logger.info(f"Reading CSV file: {csv_file_path}")
        
        transformed_data = []
        errors = []
        
        try:
            # Read CSV with pandas to handle multiline fields properly
            df = pd.read_csv(csv_file_path, encoding='utf-8')
            
            logger.info(f"Found {len(df)} rows in CSV")
            
            for idx, row in df.iterrows():
                try:
                    # Skip empty rows
                    if pd.isna(row.get('Readings')) and pd.isna(row.get('❇Done')):
                        logger.debug(f"Skipping empty row {idx + 2}")
                        continue
                    
                    transformed_row = self.transform_row(
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
            
            logger.info(f"Successfully transformed {len(transformed_data)} rows")
            if errors:
                logger.warning(f"Encountered {len(errors)} errors during transformation")
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def truncate_table(self, force: bool = False) -> bool:
        """Truncate the gtd_projects table with user confirmation"""
        if not force:
            try:
                response = input(f"This will delete all existing data in {self.table_name}. Continue? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Operation cancelled by user")
                    return False
            except EOFError:
                logger.warning("No input available, assuming 'no' for safety")
                return False
        
        try:
            # Delete all records for this user
            result = self.supabase.table(self.table_name).delete().eq('user_id', self.user_id).execute()
            logger.info(f"Deleted existing records for user {self.user_id}")
            # Clear field cache to reload after potential schema changes
            self._field_id_cache = None
            return True
        except Exception as e:
            logger.error(f"Error truncating table: {e}")
            return False
    
    def load_data(self, data: List[Dict[str, Any]]) -> None:
        """Load transformed data into Supabase"""
        if not data:
            logger.warning("No data to load")
            return
        
        logger.info(f"Loading {len(data)} records into {self.table_name}")
        
        # Insert data in batches to avoid timeouts
        batch_size = 100
        success_count = 0
        error_count = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            try:
                result = self.supabase.table(self.table_name).insert(batch).execute()
                success_count += len(batch)
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")
                
            except Exception as e:
                error_count += len(batch)
                logger.error(f"Error inserting batch {i//batch_size + 1}: {e}")
                
                # Try inserting records individually in this batch
                for record in batch:
                    try:
                        self.supabase.table(self.table_name).insert(record).execute()
                        success_count += 1
                        error_count -= 1
                    except Exception as individual_error:
                        logger.warning(f"Error inserting individual record: {individual_error}")
        
        logger.info(f"Load complete: {success_count} successful, {error_count} failed")
    
    def run_etl(self, csv_file_path: str, truncate: bool = True, force: bool = False) -> None:
        """Run the complete ETL process"""
        logger.info("Starting GTD Projects ETL process")
        
        try:
            # Create table if needed
            self.create_table_if_not_exists()
            
            # Truncate existing data if requested
            if truncate:
                if not self.truncate_table(force=force):
                    return
            
            # Extract and transform
            data = self.extract_and_transform(csv_file_path)
            
            # Load
            self.load_data(data)
            
            logger.info("ETL process completed successfully")
            
        except Exception as e:
            logger.error(f"ETL process failed: {e}")
            raise


def find_gtd_projects_csv() -> str:
    """Find the GTD Projects CSV file in the data directory"""
    data_dir = Path("data/from_notion")
    
    if not data_dir.exists():
        raise FileNotFoundError("Data directory not found: data/from_notion")
    
    # Search for the GTD_Projects CSV file
    csv_files = list(data_dir.rglob("GTD_Projects*_all.csv"))
    
    if not csv_files:
        raise FileNotFoundError("GTD_Projects CSV file not found in data directory")
    
    if len(csv_files) > 1:
        logger.warning(f"Multiple GTD_Projects CSV files found, using: {csv_files[0]}")
    
    return str(csv_files[0])


def main():
    """Main entry point for the ETL script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL Pipeline for GTD Projects')
    parser.add_argument('--force', action='store_true', 
                       help='Force truncate without confirmation')
    parser.add_argument('--no-truncate', action='store_true',
                       help='Skip truncation of existing data')
    
    args = parser.parse_args()
    
    try:
        # Find CSV file
        csv_file = find_gtd_projects_csv()
        logger.info(f"Found GTD Projects CSV: {csv_file}")
        
        # Initialize and run ETL
        etl = GTDProjectsETL()
        etl.run_etl(csv_file, truncate=not args.no_truncate, force=args.force)
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()