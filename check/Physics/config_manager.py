"""
Unified Configuration Manager for Streamlit and OCR Integration
Supports both .env files and Streamlit secrets management
Based on: https://docs.streamlit.io/develop/concepts/connections/secrets-management
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigManager:
    """
    Unified configuration manager that works with:
    1. Streamlit secrets (st.secrets) - for deployed apps
    2. .env files - for local development  
    3. Environment variables - fallback
    
    Based on Streamlit's official secrets management documentation.
    """
    
    def __init__(self):
        # Load .env file for local development
        load_dotenv()
        
        # Try to import streamlit for deployed apps
        self._streamlit_available = False
        self._st_secrets = None
        
        try:
            import streamlit as st
            self._streamlit_available = True
            self._st_secrets = st.secrets
        except ImportError:
            # Not running in Streamlit environment
            pass
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret value with the following priority:
        1. Streamlit secrets (if available)
        2. Environment variables
        3. Default value
        
        Args:
            key: The secret key to retrieve
            default: Default value if key not found
            
        Returns:
            Secret value or default
        """
        # Try Streamlit secrets first (for deployed apps)
        if self._streamlit_available and self._st_secrets:
            try:
                return str(self._st_secrets[key])
            except KeyError:
                pass
        
        # Fallback to environment variables (for local development)
        return os.getenv(key, default)
    
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """
        Get a configuration section (only works with Streamlit secrets).
        
        Args:
            section_name: Name of the configuration section
            
        Returns:
            Dictionary of section values
        """
        if self._streamlit_available and self._st_secrets:
            try:
                return dict(self._st_secrets[section_name])
            except KeyError:
                return {}
        
        # For .env files, we can't have sections, so return empty dict
        return {}
    
    def get_api_key(self, service: str = "GOOGLE_GEMINI_API") -> str:
        """
        Get API key with proper error handling.
        
        Args:
            service: The service API key to retrieve
            
        Returns:
            API key value
            
        Raises:
            ValueError: If API key is not found or is placeholder
        """
        api_key = self.get_secret(service)
        
        if not api_key:
            raise ValueError(
                f"❌ {service} not found. Please set it in:\n"
                f"   • Streamlit secrets: .streamlit/secrets.toml\n"
                f"   • Environment: .env file or export {service}=your_key\n"
                f"   • See docs/env_setup.md for detailed instructions"
            )
        
        # Check for placeholder values
        placeholder_values = [
            "your_actual_gemini_api_key_here",
            "your_actual_api_key_here", 
            "your_api_key_here",
            "placeholder"
        ]
        
        if api_key.lower() in [p.lower() for p in placeholder_values]:
            raise ValueError(
                f"❌ Please replace the placeholder value for {service} with your actual API key"
            )
        
        return api_key
    
    def get_ocr_config(self) -> Dict[str, Any]:
        """Get OCR configuration with defaults."""
        # Try to get from main config file first
        try:
            import config
            if hasattr(config, 'OCR_CONFIG'):
                return config.OCR_CONFIG
        except ImportError:
            pass
        
        # Try to get from Streamlit secrets section
        ocr_config = self.get_section("ocr_config")
        if ocr_config:
            return ocr_config
        
        # Fallback to individual environment variables
        return {
            "default_cache_dir": self.get_secret("DEFAULT_CACHE_DIR", "./data/ocr_cache"),
            "default_prompt_version": self.get_secret("DEFAULT_PROMPT_VERSION", "v10"),
            "max_pdf_pages": int(self.get_secret("MAX_PDF_PAGES", "50")),
            "confidence_threshold": float(self.get_secret("OCR_CONFIDENCE_THRESHOLD", "0.8")),
            "image_resize_dim": int(self.get_secret("IMAGE_RESIZE_DIM", "1536")),
            "cache_enabled": True,
            "max_concurrent_requests": 4
        }
    
    def get_data_config(self) -> Dict[str, Any]:
        """Get data configuration with defaults."""
        # Try to get from Streamlit secrets section first
        data_config = self.get_section("data_config")
        
        if data_config:
            return data_config
        
        # Fallback to individual environment variables
        return {
            "data_path": self.get_secret("DATA_PATH", "./data/hw_df_with_solutions_and_questions.csv"),
            "output_dir": self.get_secret("OUTPUT_DIR", "./results")
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the current configuration.
        
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        # Check if we're in Streamlit environment
        if self._streamlit_available:
            warnings.append("✅ Running in Streamlit environment - using st.secrets")
        else:
            warnings.append("ℹ️  Running outside Streamlit - using .env files")
        
        # Try to get API key
        try:
            api_key = self.get_api_key("GOOGLE_GEMINI_API")
            # Don't log the actual key for security
            warnings.append(f"✅ GOOGLE_GEMINI_API is configured (***{api_key[-4:]})")
        except ValueError as e:
            issues.append(str(e))
        
        # Check OCR config
        try:
            ocr_config = self.get_ocr_config()
            warnings.append(f"✅ OCR config loaded: {list(ocr_config.keys())}")
        except Exception as e:
            issues.append(f"OCR config error: {e}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "environment": "streamlit" if self._streamlit_available else "local"
        }
    
    def get_streamlit_connection_info(self) -> Dict[str, Any]:
        """
        Get database connection info for Streamlit connections.
        Useful for st.connection() calls.
        """
        db_config = self.get_section("database")
        
        if db_config:
            return db_config
        
        # Fallback to individual variables
        return {
            "username": self.get_secret("DB_USERNAME"),
            "password": self.get_secret("DB_PASSWORD"), 
            "host": self.get_secret("DB_HOST"),
            "port": self.get_secret("DB_PORT", "5432")
        }

# Global instance
config = ConfigManager()

# Convenience functions
def get_api_key(service: str = "GOOGLE_GEMINI_API") -> str:
    """Get API key - convenience function."""
    return config.get_api_key(service)

def get_ocr_config() -> Dict[str, Any]:
    """Get OCR configuration - convenience function."""
    return config.get_ocr_config()

def get_data_config() -> Dict[str, Any]:
    """Get data configuration - convenience function."""
    return config.get_data_config()

def validate_config() -> Dict[str, Any]:
    """Validate configuration - convenience function."""
    return config.validate_config()

if __name__ == "__main__":
    # CLI validation
    print("🔍 Configuration Validation")
    print("=" * 40)
    
    validation = validate_config()
    
    for warning in validation["warnings"]:
        print(warning)
    
    for issue in validation["issues"]:
        print(issue)
    
    print("\n" + "=" * 40)
    if validation["valid"]:
        print("🎉 Configuration is valid!")
    else:
        print("❌ Configuration needs attention.")
        exit(1) 