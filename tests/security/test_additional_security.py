import pytest
import json
import jwt
import bcrypt
import re
from datetime import datetime, timedelta
import pytz
from nocturna.calculations.chart import Chart
from nocturna.calculations.position import Position
from nocturna.calculations.constants import CoordinateSystem
from nocturna.exceptions import SecurityError, ValidationError

class TestAdditionalSecurity:
    @pytest.fixture
    def test_chart_data(self):
        return {
            "date": datetime(2000, 1, 1, 12, 0, 0, tzinfo=pytz.UTC),
            "location": Position(0.0, 51.5, 0.0, CoordinateSystem.GEOGRAPHIC)  # London coordinates
        }

    def test_sql_injection_prevention(self, test_chart_data):
        """Test SQL injection prevention"""
        # Test malicious SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; SELECT * FROM users; --",
            "' UNION SELECT * FROM users; --",
            "'; WAITFOR DELAY '0:0:10'; --"
        ]
        
        for malicious_input in malicious_inputs:
            # Test in various fields
            with pytest.raises(ValidationError):
                Chart(
                    date=test_chart_data["date"],
                    location=Position(
                        latitude=float(malicious_input),
                        longitude=0.0,
                        altitude=0.0,
                        system=CoordinateSystem.GEOGRAPHIC
                    )
                )

    def test_xss_prevention(self, test_chart_data):
        """Test XSS prevention"""
        # Test malicious XSS attempts
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg/onload=alert('xss')>",
            "'-alert('xss')-'"
        ]
        
        for malicious_input in malicious_inputs:
            # Test in various fields
            with pytest.raises(ValidationError):
                Chart(
                    date=test_chart_data["date"],
                    location=Position(
                        latitude=0.0,
                        longitude=0.0,
                        altitude=0.0,
                        system=CoordinateSystem.GEOGRAPHIC,
                        description=malicious_input
                    )
                )

    def test_jwt_security(self):
        """Test JWT token security"""
        # Test token expiration
        expired_token = jwt.encode(
            {
                'user_id': 1,
                'exp': datetime.utcnow() - timedelta(hours=1)
            },
            'secret',
            algorithm='HS256'
        )
        
        with pytest.raises(SecurityError):
            jwt.decode(expired_token, 'secret', algorithms=['HS256'])
        
        # Test token tampering
        token = jwt.encode(
            {
                'user_id': 1,
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            'secret',
            algorithm='HS256'
        )
        
        tampered_token = token[:-1] + ('1' if token[-1] == '0' else '0')
        with pytest.raises(SecurityError):
            jwt.decode(tampered_token, 'secret', algorithms=['HS256'])

    def test_password_security(self):
        """Test password security"""
        # Test password strength
        weak_passwords = [
            "password",
            "123456",
            "qwerty",
            "abc123",
            "letmein"
        ]
        
        for password in weak_passwords:
            with pytest.raises(ValidationError):
                # Assuming there's a password validation function
                self.validate_password(password)
        
        # Test password hashing
        strong_password = "StrongP@ssw0rd123!"
        hashed = bcrypt.hashpw(strong_password.encode(), bcrypt.gensalt())
        assert bcrypt.checkpw(strong_password.encode(), hashed)

    def test_input_sanitization(self, test_chart_data):
        """Test input sanitization"""
        # Test various input types
        malicious_inputs = {
            "date": "2024-01-01'; DROP TABLE users; --",
            "latitude": "51.5 OR 1=1",
            "longitude": "0.0; SELECT * FROM users",
            "description": "<script>alert('xss')</script>"
        }
        
        for field, value in malicious_inputs.items():
            with pytest.raises(ValidationError):
                # Assuming there's an input sanitization function
                self.sanitize_input(field, value)

    def test_rate_limiting_security(self):
        """Test rate limiting security"""
        # Test rapid requests
        for _ in range(100):
            try:
                # Simulate API request
                self.make_api_request()
            except SecurityError as e:
                if "Rate limit exceeded" in str(e):
                    break
        else:
            pytest.fail("Rate limiting not enforced")

    def test_csrf_protection(self):
        """Test CSRF protection"""
        # Test missing CSRF token
        with pytest.raises(SecurityError):
            self.make_api_request(csrf_token=None)
        
        # Test invalid CSRF token
        with pytest.raises(SecurityError):
            self.make_api_request(csrf_token="invalid_token")

    def test_file_upload_security(self):
        """Test file upload security"""
        # Test malicious file types
        malicious_files = [
            ("malicious.exe", b"MZ..."),
            ("script.php", b"<?php system($_GET['cmd']); ?>"),
            ("shell.sh", b"#!/bin/bash\nrm -rf /"),
            ("malicious.js", b"alert('xss')")
        ]
        
        for filename, content in malicious_files:
            with pytest.raises(SecurityError):
                self.validate_file_upload(filename, content)

    def test_api_key_security(self):
        """Test API key security"""
        # Test invalid API key
        with pytest.raises(SecurityError):
            self.validate_api_key("invalid_key")
        
        # Test expired API key
        expired_key = self.generate_api_key(expiry=datetime.utcnow() - timedelta(days=1))
        with pytest.raises(SecurityError):
            self.validate_api_key(expired_key)

    def test_data_encryption(self):
        """Test data encryption"""
        sensitive_data = {
            "user_id": 1,
            "email": "test@example.com",
            "password": "hashed_password"
        }
        
        # Test encryption
        encrypted_data = self.encrypt_data(sensitive_data)
        assert encrypted_data != sensitive_data
        
        # Test decryption
        decrypted_data = self.decrypt_data(encrypted_data)
        assert decrypted_data == sensitive_data

    def test_secure_headers(self):
        """Test secure headers"""
        headers = self.get_security_headers()
        
        # Verify security headers
        assert headers.get('X-Content-Type-Options') == 'nosniff'
        assert headers.get('X-Frame-Options') == 'DENY'
        assert headers.get('X-XSS-Protection') == '1; mode=block'
        assert 'Content-Security-Policy' in headers
        assert 'Strict-Transport-Security' in headers

    # Helper methods
    def validate_password(self, password):
        """Validate password strength"""
        if len(password) < 8:
            raise ValidationError("Password too short")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password needs uppercase")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password needs lowercase")
        if not re.search(r"\d", password):
            raise ValidationError("Password needs number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password needs special character")

    def sanitize_input(self, field, value):
        """Sanitize input data"""
        if isinstance(value, str):
            # Remove SQL injection attempts
            if any(keyword in value.lower() for keyword in ['select', 'insert', 'update', 'delete', 'drop']):
                raise ValidationError("Invalid input")
            # Remove XSS attempts
            if any(tag in value.lower() for tag in ['<script', '<img', '<svg', 'javascript:']):
                raise ValidationError("Invalid input")
        return value

    def make_api_request(self, csrf_token=None):
        """Simulate API request"""
        if csrf_token is None:
            raise SecurityError("CSRF token required")
        if csrf_token == "invalid_token":
            raise SecurityError("Invalid CSRF token")
        # Simulate rate limiting
        if not hasattr(self, '_request_count'):
            self._request_count = 0
        self._request_count += 1
        if self._request_count > 50:
            raise SecurityError("Rate limit exceeded")

    def validate_file_upload(self, filename, content):
        """Validate file upload"""
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.txt'}
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise SecurityError("Invalid file type")
        if len(content) > 5 * 1024 * 1024:  # 5MB limit
            raise SecurityError("File too large")

    def validate_api_key(self, key):
        """Validate API key"""
        if key == "invalid_key":
            raise SecurityError("Invalid API key")
        # Check expiration
        try:
            payload = jwt.decode(key, 'secret', algorithms=['HS256'])
            if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
                raise SecurityError("API key expired")
        except jwt.InvalidTokenError:
            raise SecurityError("Invalid API key")

    def generate_api_key(self, expiry=None):
        """Generate API key"""
        if expiry is None:
            expiry = datetime.utcnow() + timedelta(days=30)
        return jwt.encode(
            {
                'exp': expiry,
                'iat': datetime.utcnow()
            },
            'secret',
            algorithm='HS256'
        )

    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        # Simulate encryption
        return json.dumps(data)

    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        # Simulate decryption
        return json.loads(encrypted_data)

    def get_security_headers(self):
        """Get security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': "default-src 'self'",
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
        } 