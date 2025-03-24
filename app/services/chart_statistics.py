from pathlib import Path
import json
import logging
from typing import Dict, Any, List, Optional, Union
import os

class ChartStatisticsService:
    """Service for managing and providing statistical data about astrological configurations."""
    
    def __init__(self):
        """Initialize the chart statistics service."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing ChartStatisticsService")
        
        # Set up data directory
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "statistics"
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
        self.frequencies_file = self.data_dir / "baseline_frequencies.json"
        self.frequencies = self._load_frequencies()
        self.sample_size = self.frequencies.get("meta", {}).get("sample_size", 0)
        
        self.logger.info(f"Loaded statistics based on {self.sample_size} charts")
    
    def _load_frequencies(self) -> Dict[str, Any]:
        """Load frequency statistics from file or generate defaults if not found."""
        if self.frequencies_file.exists():
            try:
                with open(self.frequencies_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading frequencies file: {str(e)}")
                return self._generate_default_frequencies()
        else:
            self.logger.info("No frequencies file found, generating defaults")
            frequencies = self._generate_default_frequencies()
            self._save_frequencies(frequencies)
            return frequencies
    
    def _generate_default_frequencies(self) -> Dict[str, Any]:
        """Generate default frequency statistics based on astrological literature."""
        # These values are approximations based on theoretical distributions
        # They will be replaced with actual analysis when charts are processed
        return {
            "meta": {
                "sample_size": 0,
                "last_updated": "",
                "version": "1.0"
            },
            "aspects": {
                "conjunction": 15.0,
                "sextile": 12.5,
                "square": 11.0,
                "trine": 14.0,
                "opposition": 9.5
            },
            "patterns": {
                "grand_trine": 3.0,
                "t_square": 5.5,
                "grand_cross": 0.8,
                "yod": 2.0,
                "stellium": 8.0
            },
            "element_balance": {
                "dominant": {
                    "fire": 25.0,
                    "earth": 25.0,
                    "air": 25.0,
                    "water": 25.0
                },
                "lacking": {
                    "fire": 12.0,
                    "earth": 12.0,
                    "air": 12.0,
                    "water": 12.0
                }
            },
            "modality_balance": {
                "dominant": {
                    "cardinal": 33.3,
                    "fixed": 33.3,
                    "mutable": 33.3
                },
                "lacking": {
                    "cardinal": 12.0,
                    "fixed": 12.0,
                    "mutable": 12.0
                }
            }
        }
    
    def _save_frequencies(self, frequencies: Dict[str, Any]) -> None:
        """Save frequency statistics to file."""
        try:
            with open(self.frequencies_file, 'w') as f:
                json.dump(frequencies, f, indent=2)
            self.logger.info(f"Frequencies saved to {self.frequencies_file}")
        except Exception as e:
            self.logger.error(f"Error saving frequencies file: {str(e)}")
    
    def get_aspect_frequency(self, aspect_type: str) -> Optional[float]:
        """Get the frequency percentage for a specific aspect type."""
        return self.frequencies.get("aspects", {}).get(aspect_type.lower())
    
    def get_pattern_frequency(self, pattern_type: str) -> Optional[float]:
        """Get the frequency percentage for a specific pattern type."""
        return self.frequencies.get("patterns", {}).get(pattern_type.lower())
    
    def get_element_dominance_frequency(self, element: str) -> Optional[float]:
        """Get the frequency percentage for element dominance."""
        return self.frequencies.get("element_balance", {}).get("dominant", {}).get(element.lower())
    
    def get_element_lacking_frequency(self, element: str) -> Optional[float]:
        """Get the frequency percentage for lacking an element."""
        return self.frequencies.get("element_balance", {}).get("lacking", {}).get(element.lower())
    
    def get_modality_dominance_frequency(self, modality: str) -> Optional[float]:
        """Get the frequency percentage for modality dominance."""
        return self.frequencies.get("modality_balance", {}).get("dominant", {}).get(modality.lower())
    
    def analyze_charts(self, charts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a batch of charts and update frequency statistics.
        
        Args:
            charts: List of birth chart dictionaries
            
        Returns:
            Updated frequency statistics
        """
        if not charts:
            return self.frequencies
            
        self.logger.info(f"Analyzing {len(charts)} charts for statistical frequencies")
        
        # Initialize counters
        aspect_counts = {aspect_type: 0 for aspect_type in self.frequencies.get("aspects", {})}
        pattern_counts = {pattern_type: 0 for pattern_type in self.frequencies.get("patterns", {})}
        element_dominant = {element: 0 for element in self.frequencies.get("element_balance", {}).get("dominant", {})}
        element_lacking = {element: 0 for element in self.frequencies.get("element_balance", {}).get("lacking", {})}
        modality_dominant = {modality: 0 for modality in self.frequencies.get("modality_balance", {}).get("dominant", {})}
        
        # Count occurrences in each chart
        for chart in charts:
            # Count aspects
            for aspect in chart.get("aspects", []):
                aspect_type = aspect.get("type")
                if isinstance(aspect_type, int):
                    # Convert numeric aspect types to names
                    aspect_name = {
                        0: "conjunction",
                        60: "sextile",
                        90: "square",
                        120: "trine",
                        180: "opposition"
                    }.get(aspect_type, str(aspect_type).lower())
                else:
                    aspect_name = str(aspect_type).lower()
                
                if aspect_name in aspect_counts:
                    aspect_counts[aspect_name] += 1
            
            # Analyze elements and modalities (simplified)
            # This would be more complex in a full implementation
            
        # Update frequencies with new data
        new_sample_size = self.sample_size + len(charts)
        
        # Calculate new frequencies
        if new_sample_size > 0:
            for aspect_type, count in aspect_counts.items():
                old_count = self.frequencies["aspects"][aspect_type] * self.sample_size / 100
                new_count = old_count + count
                self.frequencies["aspects"][aspect_type] = (new_count / new_sample_size) * 100
        
        # Update meta information
        self.frequencies["meta"]["sample_size"] = new_sample_size
        from datetime import datetime
        self.frequencies["meta"]["last_updated"] = datetime.now().isoformat()
        
        # Save updated frequencies
        self._save_frequencies(self.frequencies)
        self.sample_size = new_sample_size
        
        return self.frequencies
    
    def enhance_aspect_interpretation(self, aspect_type: str, interpretation: str) -> str:
        """Add frequency information to an aspect interpretation.
        
        Args:
            aspect_type: The type of aspect
            interpretation: The existing interpretation text
            
        Returns:
            Enhanced interpretation with frequency information
        """
        frequency = self.get_aspect_frequency(aspect_type)
        if frequency:
            return f"{interpretation} This aspect occurs in approximately {frequency:.1f}% of birth charts."
        return interpretation
    
    def enhance_pattern_interpretation(self, pattern_type: str, interpretation: str) -> str:
        """Add frequency information to a pattern interpretation.
        
        Args:
            pattern_type: The type of pattern
            interpretation: The existing interpretation text
            
        Returns:
            Enhanced interpretation with frequency information
        """
        frequency = self.get_pattern_frequency(pattern_type)
        if frequency:
            return f"{interpretation} This pattern occurs in approximately {frequency:.1f}% of birth charts."
        return interpretation 