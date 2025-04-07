import os
import subprocess
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_backup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db_backup")

def backup_database():
    """Create a backup of the PostgreSQL database"""
    try:
        # Get environment variables
        db_name = os.environ.get('POSTGRES_DB', 'webpush')
        db_user = os.environ.get('POSTGRES_USER', 'postgres')
        db_host = os.environ.get('POSTGRES_SERVER', 'db')
        db_port = os.environ.get('POSTGRES_PORT', '5432')
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create timestamp for the backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"{db_name}_backup_{timestamp}.sql")
        
        # Run pg_dump to create the backup
        command = [
            "pg_dump",
            f"--host={db_host}",
            f"--port={db_port}",
            f"--username={db_user}",
            f"--dbname={db_name}",
            f"--file={backup_file}",
            "--format=plain",
            "--clean"
        ]
        
        logger.info(f"Starting database backup to {backup_file}")
        
        # Execute the command
        result = subprocess.run(
            command, 
            env={**os.environ, "PGPASSWORD": os.environ.get('POSTGRES_PASSWORD', '')},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode == 0:
            logger.info(f"Database backup completed successfully")
            return True
        else:
            logger.error(f"Database backup failed: {result.stderr.decode()}")
            return False
            
    except Exception as e:
        logger.error(f"Error during database backup: {str(e)}")
        return False

if __name__ == "__main__":
    backup_database()
