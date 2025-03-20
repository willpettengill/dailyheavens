import pytest
from app.services.interpretation import InterpretationService
from app.services.birth_chart import BirthChartService
from app.models.interpretation import InterpretationArea, InterpretationLevel
from tests.test_data_generator import TestDataGenerator

@pytest.mark.comprehensive
class TestComprehensiveInterpretations:
    """Test comprehensive interpretation scenarios."""
    
    @pytest.fixture(scope="class")
    def interpretation_service(self):
        return InterpretationService()
    
    @pytest.fixture(scope="class")
    def birth_chart_service(self):
        return BirthChartService()
    
    def test_sign_combinations(self, interpretation_service, sample_birth_chart):
        """Test interpretation of various sign combinations."""
        interpretation = interpretation_service.generate_interpretation(sample_birth_chart)
        
        assert interpretation["status"] == "success"
        data = interpretation["data"]
        
        # Check planet interpretations
        planets = data["interpretations"]["planets"]
        assert "Sun" in planets
        assert "Moon" in planets
        assert "sign" in planets["Sun"]
        assert "house" in planets["Sun"]
        assert "dignity" in planets["Sun"]
        
        # Check aspect interpretations
        aspects = data["interpretations"]["aspects"]
        assert len(aspects) > 0
        assert "planets" in aspects[0]
        assert "type" in aspects[0]
        assert "interpretation" in aspects[0]

    def test_house_placements(self, interpretation_service, sample_birth_chart):
        """Test interpretation of various house placements."""
        interpretation = interpretation_service.generate_interpretation(sample_birth_chart)
        
        assert interpretation["status"] == "success"
        data = interpretation["data"]
        
        # Check house interpretations
        houses = data["interpretations"]["houses"]
        assert "1" in houses
        assert "7" in houses
        assert "10" in houses
        
        # Check house emphasis
        house_emphasis = data["house_emphasis"]
        assert "counts" in house_emphasis
        assert "dominant" in house_emphasis
        assert "interpretation" in house_emphasis

    def test_aspect_patterns(self, interpretation_service, sample_birth_chart):
        """Test interpretation of various aspect patterns."""
        interpretation = interpretation_service.generate_interpretation(sample_birth_chart)
        
        assert interpretation["status"] == "success"
        data = interpretation["data"]
        
        # Check aspect interpretations
        aspects = data["interpretations"]["aspects"]
        assert len(aspects) > 0
        for aspect in aspects:
            assert "planets" in aspect
            assert "type" in aspect
            assert "interpretation" in aspect

    def test_dignity_combinations(self, interpretation_service, sample_birth_chart):
        """Test interpretation of various dignity combinations."""
        interpretation = interpretation_service.generate_interpretation(sample_birth_chart)
        
        assert interpretation["status"] == "success"
        data = interpretation["data"]
        
        # Check planet dignities
        planets = data["interpretations"]["planets"]
        for planet_data in planets.values():
            assert "dignity" in planet_data

    def test_interpretation_combinations(self, interpretation_service, sample_birth_chart):
        """Test combinations of different interpretation factors."""
        interpretation = interpretation_service.generate_interpretation(sample_birth_chart)
        
        assert interpretation["status"] == "success"
        data = interpretation["data"]
        
        # Check patterns
        patterns = data["patterns"]
        assert "element_distribution" in patterns
        assert "modality_distribution" in patterns
        assert "dominant" in patterns
        assert "interpretation" in patterns
        
        # Check combinations
        combinations = data["combinations"]
        assert any(key in combinations for key in ["sun_moon", "sun_rising", "moon_rising"])
        for combo in combinations.values():
            assert "interpretation" in combo
            assert "strength" in combo

    def test_edge_cases(self, interpretation_service):
        """Test edge cases and error handling."""
        # Test with empty birth chart
        empty_chart = {"planets": {}, "houses": {}, "aspects": [], "angles": {}}
        interpretation = interpretation_service.generate_interpretation(empty_chart)
        assert interpretation["status"] == "error"
        assert "message" in interpretation
        
        # Test with missing required data
        incomplete_chart = {
            "planets": {"Sun": {"sign": "Aries"}},
            "houses": {},
            "aspects": [],
            "angles": {}
        }
        interpretation = interpretation_service.generate_interpretation(incomplete_chart)
        assert interpretation["status"] == "error"
        assert "message" in interpretation

    def test_special_configurations(self, interpretation_service, sample_birth_chart):
        """Test interpretation of special configurations."""
        interpretation = interpretation_service.generate_interpretation(sample_birth_chart)
        assert interpretation["status"] == "success"
        assert "data" in interpretation
        data = interpretation["data"]
        assert "special_configurations" in data

    def test_interpretation_combinations(self, interpretation_service):
        """Test all possible combinations of interpretation areas and levels."""
        requests = TestDataGenerator.generate_interpretation_requests()
        
        for request in requests:
            interpretation = interpretation_service.generate_interpretation(
                birth_chart=request["birth_chart"],
                area=InterpretationArea(request["area"]),
                level=InterpretationLevel(request["level"])
            )
            
            assert interpretation.status == "success"
            assert "interpretations" in interpretation.data
            
            # Verify area-specific interpretations
            for interpretation in interpretation.data["interpretations"]:
                assert interpretation["area"] == request["area"]
                assert interpretation["level"] == request["level"]
    
    def test_edge_cases(self, interpretation_service):
        """Test edge cases and special configurations."""
        edge_cases = TestDataGenerator.generate_edge_cases()
        
        for chart in edge_cases:
            interpretation = interpretation_service.generate_interpretation(
                birth_chart=chart,
                area=InterpretationArea.GENERAL,
                level=InterpretationLevel.BASIC
            )
            
            assert interpretation.status == "success"
            assert "interpretations" in interpretation.data
            
            # Verify special case handling
            for interpretation in interpretation.data["interpretations"]:
                assert "content" in interpretation
                content = interpretation["content"]
                
                # Check for retrograde planet mentions
                for planet, data in chart["planets"].items():
                    if data.get("retrograde"):
                        assert f"retrograde {planet}" in content.lower()
                
                # Check for cusp mentions
                for planet, data in chart["planets"].items():
                    if data.get("degree", 0) >= 29.0:
                        assert "cusp" in content.lower()
                
                # Check for intercepted sign mentions
                if "intercepted_signs" in chart["houses"]["1"]:
                    assert "intercepted" in content.lower()
    
    def test_dignity_combinations(self, interpretation_service):
        """Test all possible combinations of planetary dignities."""
        # Generate test cases for different dignity combinations
        for planet in TestDataGenerator.PLANETS:
            for sign in TestDataGenerator.SIGNS:
                chart = TestDataGenerator.generate_birth_chart()
                chart["planets"][planet]["sign"] = sign
                
                interpretation = interpretation_service.generate_interpretation(
                    birth_chart=chart,
                    area=InterpretationArea.GENERAL,
                    level=InterpretationLevel.BASIC
                )
                
                assert interpretation.status == "success"
                assert "interpretations" in interpretation.data
                
                # Verify dignity-specific interpretations
                for interpretation in interpretation.data["interpretations"]:
                    assert "content" in interpretation
                    content = interpretation["content"]
                    assert any(dignity in content.lower() 
                             for dignity in ["rulership", "exaltation", "fall", "detriment"])
    
    def test_special_configurations(self, interpretation_service):
        """Test special astrological configurations."""
        # Test grand trine
        chart = TestDataGenerator.generate_birth_chart()
        chart["aspects"] = {
            "Sun-Moon": {"type": "trine", "degree": 0.0},
            "Moon-Mars": {"type": "trine", "degree": 0.0},
            "Mars-Sun": {"type": "trine", "degree": 0.0}
        }
        
        interpretation = interpretation_service.generate_interpretation(
            birth_chart=chart,
            area=InterpretationArea.GENERAL,
            level=InterpretationLevel.BASIC
        )
        
        assert interpretation.status == "success"
        assert "interpretations" in interpretation.data
        assert any("grand trine" in interp["content"].lower() 
                  for interp in interpretation.data["interpretations"])
        
        # Test t-square
        chart = TestDataGenerator.generate_birth_chart()
        chart["aspects"] = {
            "Sun-Moon": {"type": "opposition", "degree": 0.0},
            "Mars-Sun": {"type": "square", "degree": 0.0},
            "Mars-Moon": {"type": "square", "degree": 0.0}
        }
        
        interpretation = interpretation_service.generate_interpretation(
            birth_chart=chart,
            area=InterpretationArea.GENERAL,
            level=InterpretationLevel.BASIC
        )
        
        assert interpretation.status == "success"
        assert "interpretations" in interpretation.data
        assert any("t-square" in interp["content"].lower() 
                  for interp in interpretation.data["interpretations"]) 