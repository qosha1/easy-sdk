"""
AI Analysis Engine for enhanced Django code understanding
"""

import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import openai
except ImportError:
    openai = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from ..core.config import DjangoDocsConfig
from .prompts import PromptTemplates

logger = logging.getLogger(__name__)


class AIAnalysisResult:
    """Result of AI analysis operation"""
    
    def __init__(self):
        self.success = True
        self.enhanced_data: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.analysis_time = 0.0
        self.tokens_used = 0
        self.model_used = ""
    
    def add_error(self, error: str) -> None:
        """Add error to result"""
        self.errors.append(error)
        self.success = False
        logger.error(f"AI Analysis error: {error}")
    
    def add_warning(self, warning: str) -> None:
        """Add warning to result"""
        self.warnings.append(warning)
        logger.warning(f"AI Analysis warning: {warning}")


class AIAnalysisEngine:
    """
    AI-powered analysis engine that enhances structural Django analysis
    with intelligent code understanding, type inference, and documentation generation
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        self.ai_config = config.ai
        self.prompt_templates = PromptTemplates()
        
        # Load environment variables from .env file
        self._load_environment()
        
        # Initialize AI clients
        self.openai_client = None
        self.langchain_client = None
        self.anthropic_client = None
        
        if self.ai_config.provider == "openai":
            self._initialize_openai()
        elif self.ai_config.provider == "anthropic":
            self._initialize_anthropic()
        
        # Rate limiting
        self._request_times = []
        self._max_requests_per_minute = 50
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file"""
        if load_dotenv is None:
            logger.debug("dotenv not available, skipping .env file loading")
            return
            
        # Try to find .env file in common locations
        env_paths = [
            Path.cwd() / ".env",  # Current working directory
            Path(__file__).parent.parent.parent.parent / ".env",  # Project root
            self.config.project_path / ".env",  # Django project directory
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                logger.debug(f"Loading environment from: {env_path}")
                load_dotenv(env_path)
                return
        
        logger.debug("No .env file found in common locations")
        
    def _initialize_openai(self) -> None:
        """Initialize OpenAI clients (both direct and LangChain)"""
        if openai is None or ChatOpenAI is None:
            logger.warning("OpenAI or LangChain not installed. Install with: pip install 'easy-sdk[ai]'")
            return
            
        try:
            api_key = self.ai_config.api_key or self._get_api_key_from_env("OPENAI_API_KEY")
            if api_key:
                # Initialize direct OpenAI client for Responses API
                self.openai_client = openai.OpenAI(api_key=api_key)
                
                # Initialize LangChain OpenAI client for structured interactions
                self.langchain_client = ChatOpenAI(
                    api_key=api_key,
                    model=self.ai_config.model,
                    temperature=self.ai_config.temperature,
                    max_tokens=self.ai_config.max_tokens,
                    timeout=self.ai_config.timeout
                )
                logger.info("OpenAI clients initialized (direct + LangChain)")
            else:
                logger.warning("OpenAI API key not found")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI clients: {str(e)}")
    
    def _initialize_anthropic(self) -> None:
        """Initialize Anthropic client"""
        if Anthropic is None:
            logger.warning("Anthropic not installed. Install with: pip install 'easy-sdk[ai]'")
            return
            
        try:
            api_key = self.ai_config.api_key or self._get_api_key_from_env("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = Anthropic(api_key=api_key)
                logger.info("Anthropic client initialized")
            else:
                logger.warning("Anthropic API key not found")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {str(e)}")
    
    def _get_api_key_from_env(self, env_var: str) -> Optional[str]:
        """Get API key from environment variable"""
        return os.getenv(env_var)
    
    def enhance_analysis(self, analysis_data: Dict[str, Any], progress=None, main_task=None) -> Dict[str, Any]:
        """
        Enhance structural analysis with AI insights
        
        Args:
            analysis_data: Results from Django structural analysis
            progress: Rich progress instance for updates (optional)
            main_task: Main task ID for progress updates (optional)
            
        Returns:
            Enhanced analysis data with AI insights
        """
        start_time = time.time()
        
        try:
            enhanced_data = analysis_data.copy()
            
            # Get list of apps for progress calculation
            apps_to_process = [(name, data) for name, data in analysis_data.items() if isinstance(data, dict)]
            total_apps = len(apps_to_process)
            
            # Process each app
            for i, (app_name, app_data) in enumerate(apps_to_process):
                logger.info(f"Running AI analysis for app: {app_name}")
                
                # Update progress description with current app
                if progress and main_task:
                    progress.update(
                        main_task, 
                        description=f"🧠 AI analysis: {app_name} ({i+1}/{total_apps})"
                    )
                
                enhanced_app_data = self._enhance_app_analysis(app_name, app_data)
                enhanced_data[app_name] = enhanced_app_data
            
            processing_time = time.time() - start_time
            logger.info(f"AI analysis completed in {processing_time:.2f} seconds")
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Return original data if AI analysis fails
            return analysis_data
    
    def _enhance_app_analysis(self, app_name: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance analysis for a single Django app"""
        enhanced_data = app_data.copy()
        
        try:
            # Enhance serializer analysis
            if 'serializers' in app_data:
                enhanced_serializers = []
                for serializer in app_data['serializers']:
                    enhanced_serializer = self._enhance_serializer_analysis(
                        app_name, serializer
                    )
                    enhanced_serializers.append(enhanced_serializer)
                enhanced_data['serializers'] = enhanced_serializers
            
            # Enhance view analysis  
            if 'views' in app_data:
                enhanced_views = []
                for view in app_data['views']:
                    enhanced_view = self._enhance_view_analysis(app_name, view)
                    enhanced_views.append(enhanced_view)
                enhanced_data['views'] = enhanced_views
            
            # Generate relationship mappings
            enhanced_data['relationships'] = self._analyze_relationships(
                app_name, enhanced_data
            )
            
        except Exception as e:
            logger.error(f"Failed to enhance analysis for app {app_name}: {str(e)}")
            # Return original data if enhancement fails
            return app_data
        
        return enhanced_data
    
    def _enhance_serializer_analysis(self, app_name: str, serializer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance serializer analysis with AI insights"""
        try:
            # Prepare context for AI analysis
            context = {
                'app_name': app_name,
                'file_path': serializer_data.get('file_path', ''),
                'serializer_code': self._extract_serializer_code(serializer_data),
                'related_models': serializer_data.get('related_models', [])
            }
            
            # Run AI analysis
            ai_result = self._call_ai_api(
                'SERIALIZER_ANALYSIS',
                context
            )
            
            if ai_result.success:
                # Enhance field information
                enhanced_fields = self._enhance_field_types(
                    serializer_data.get('fields', {}),
                    ai_result.enhanced_data
                )
                
                serializer_data['fields'] = enhanced_fields
                serializer_data['ai_insights'] = ai_result.enhanced_data
                serializer_data['documentation'] = ai_result.enhanced_data.get('documentation', {})
        
        except Exception as e:
            logger.warning(f"Failed to enhance serializer {serializer_data.get('name', 'unknown')}: {str(e)}")
        
        return serializer_data
    
    def _enhance_view_analysis(self, app_name: str, view_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance view analysis with AI insights"""
        try:
            # Prepare context for AI analysis
            context = {
                'app_name': app_name,
                'file_path': view_data.get('file_path', ''),
                'view_code': self._extract_view_code(view_data),
                'url_patterns': view_data.get('url_patterns', []),
                'serializers': view_data.get('serializer_class', [])
            }
            
            # Run AI analysis
            ai_result = self._call_ai_api(
                'VIEW_ANALYSIS',
                context
            )
            
            if ai_result.success:
                # Enhance endpoint information
                enhanced_endpoints = self._enhance_endpoints(
                    view_data.get('endpoints', []),
                    ai_result.enhanced_data
                )
                
                view_data['endpoints'] = enhanced_endpoints
                view_data['ai_insights'] = ai_result.enhanced_data
                view_data['documentation'] = ai_result.enhanced_data.get('documentation', {})
        
        except Exception as e:
            logger.warning(f"Failed to enhance view {view_data.get('name', 'unknown')}: {str(e)}")
        
        return view_data
    
    def _enhance_field_types(self, fields: Dict[str, Any], ai_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance field type information with AI analysis"""
        enhanced_fields = fields.copy()
        
        try:
            ai_field_analysis = ai_insights.get('field_analysis', {})
            
            for field_name, field_data in enhanced_fields.items():
                if field_name in ai_field_analysis:
                    ai_field_info = ai_field_analysis[field_name]
                    
                    # Enhance field properties
                    field_data.update({
                        'ai_inferred_type': ai_field_info.get('data_type'),
                        'ai_description': ai_field_info.get('description'),
                        'ai_validation_rules': ai_field_info.get('validation_rules', []),
                        'ai_examples': ai_field_info.get('examples', []),
                        'business_purpose': ai_field_info.get('business_purpose', ''),
                    })
                    
                    # Generate TypeScript type
                    ts_type = self._generate_typescript_type(field_data, ai_field_info)
                    field_data['typescript_type'] = ts_type
        
        except Exception as e:
            logger.warning(f"Failed to enhance field types: {str(e)}")
        
        return enhanced_fields
    
    def _enhance_endpoints(self, endpoints: List[Dict[str, Any]], ai_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance endpoint information with AI analysis"""
        enhanced_endpoints = []
        
        try:
            ai_endpoint_analysis = ai_insights.get('endpoint_mapping', {})
            
            for endpoint in endpoints:
                enhanced_endpoint = endpoint.copy()
                endpoint_key = f"{endpoint['method']} {endpoint['path']}"
                
                if endpoint_key in ai_endpoint_analysis:
                    ai_endpoint_info = ai_endpoint_analysis[endpoint_key]
                    
                    enhanced_endpoint.update({
                        'ai_description': ai_endpoint_info.get('description'),
                        'ai_examples': ai_endpoint_info.get('examples', {}),
                        'ai_parameters': ai_endpoint_info.get('parameters', []),
                        'ai_responses': ai_endpoint_info.get('responses', {}),
                        'business_logic': ai_endpoint_info.get('business_logic', ''),
                    })
                
                enhanced_endpoints.append(enhanced_endpoint)
        
        except Exception as e:
            logger.warning(f"Failed to enhance endpoints: {str(e)}")
            return endpoints
        
        return enhanced_endpoints
    
    def _generate_typescript_type(self, field_data: Dict[str, Any], ai_field_info: Dict[str, Any]) -> str:
        """Generate TypeScript type for a field"""
        try:
            context = {
                'field_name': field_data.get('name', ''),
                'field_type': field_data.get('type', ''),
                'field_options': field_data,
                'context': ai_field_info
            }
            
            ai_result = self._call_ai_api(
                'TYPE_INFERENCE',
                context
            )
            
            if ai_result.success and 'typescript_type' in ai_result.enhanced_data:
                return ai_result.enhanced_data['typescript_type']
        
        except Exception as e:
            logger.warning(f"Failed to generate TypeScript type: {str(e)}")
        
        # Fallback to basic type mapping
        return self._basic_typescript_mapping(field_data.get('type', 'any'))
    
    def _basic_typescript_mapping(self, django_type: str) -> str:
        """Basic Django to TypeScript type mapping"""
        mapping = {
            'string': 'string',
            'integer': 'number',
            'float': 'number',
            'decimal': 'number',
            'boolean': 'boolean',
            'date': 'string',
            'datetime': 'string',
            'time': 'string',
            'email': 'string',
            'url': 'string',
            'uuid': 'string',
            'json': 'object',
            'list': 'any[]',
            'object': 'object',
        }
        
        return mapping.get(django_type, 'any')
    
    def _analyze_relationships(self, app_name: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationships between components"""
        try:
            context = {
                'components': json.dumps(app_data, indent=2)
            }
            
            ai_result = self._call_ai_api(
                'RELATIONSHIP_MAPPING',
                context
            )
            
            if ai_result.success:
                return ai_result.enhanced_data
        
        except Exception as e:
            logger.warning(f"Failed to analyze relationships for app {app_name}: {str(e)}")
        
        return {}
    
    def _call_ai_api(self, template_name: str, context: Dict[str, Any]) -> AIAnalysisResult:
        """Call AI API with rate limiting and error handling"""
        result = AIAnalysisResult()
        
        try:
            # Apply rate limiting
            self._apply_rate_limiting()
            
            # Prepare prompt
            prompt = self.prompt_templates.get_prompt(template_name, **context)
            
            # Enhanced logging for AI calls
            app_name = context.get('app_name', 'unknown')
            context_info = f"app={app_name}"
            if 'serializer_name' in context:
                context_info += f", serializer={context['serializer_name']}"
            elif 'view_name' in context:
                context_info += f", view={context['view_name']}"
            
            logger.info(f"🤖 AI Call: {template_name} ({context_info}) -> {self.ai_config.provider}:{self.ai_config.model}")
            if self.config.verbose:
                logger.debug(f"AI Prompt length: {len(prompt)} chars")
                logger.debug(f"AI Context keys: {list(context.keys())}")
            
            # Call appropriate AI service
            start_time = time.time()
            if self.ai_config.provider == "openai" and self.openai_client:
                response = self._call_openai(prompt)
            elif self.ai_config.provider == "anthropic" and self.anthropic_client:
                response = self._call_anthropic(prompt)
            else:
                result.add_error("No AI provider configured or available")
                logger.warning(f"❌ AI Call failed: No provider configured (requested: {self.ai_config.provider})")
                return result
            
            call_duration = time.time() - start_time
            
            # Parse response
            result.enhanced_data = self._parse_ai_response(response)
            result.model_used = self.ai_config.model
            
            # Log success with timing
            response_length = len(response) if response else 0
            logger.info(f"✅ AI Response: {template_name} completed in {call_duration:.2f}s ({response_length} chars)")
            
        except Exception as e:
            logger.error(f"❌ AI Call failed: {template_name} - {str(e)}")
            result.add_error(f"AI API call failed: {str(e)}")
        
        return result
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI Responses API"""
        try:
            # Try using the new Responses API first
            response = self.openai_client.responses.create(
                model=self.ai_config.model,
                instructions="You are an expert Django developer and technical writer. Analyze the provided code and generate comprehensive, accurate documentation.",
                input=prompt,
                max_output_tokens=self.ai_config.max_tokens,
                temperature=self.ai_config.temperature,
                text={"format": {"type": "text"}},
                store=True  # Store for better caching and optimization
            )
            
            # Extract text from the new response format
            if response.output and len(response.output) > 0:
                first_output = response.output[0]
                if hasattr(first_output, 'content') and len(first_output.content) > 0:
                    first_content = first_output.content[0]
                    if hasattr(first_content, 'text'):
                        return first_content.text
            
            # Fallback to empty string if parsing fails
            logger.warning("Could not extract text from Responses API response")
            return ""
            
        except Exception as e:
            # Fallback to LangChain client if Responses API fails
            logger.debug(f"Responses API failed, falling back to LangChain: {str(e)}")
            if self.langchain_client:
                from langchain_core.messages import HumanMessage, SystemMessage
                
                messages = [
                    SystemMessage(content="You are an expert Django developer and technical writer. Analyze the provided code and generate comprehensive, accurate documentation."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.langchain_client.invoke(messages)
                return response.content
            else:
                raise Exception(f"Both Responses API and LangChain failed: {str(e)}")
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        response = self.anthropic_client.messages.create(
            model=self.ai_config.model,
            max_tokens=self.ai_config.max_tokens,
            temperature=self.ai_config.temperature,
            system="You are an expert Django developer and technical writer. Analyze the provided code and generate comprehensive, accurate documentation.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            # Try to extract JSON from response if present
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Otherwise, return response as structured text analysis
            return {
                'raw_response': response,
                'analysis_sections': self._extract_sections(response)
            }
        
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {str(e)}")
            return {'raw_response': response}
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract sections from markdown-like text"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in text.split('\n'):
            if line.startswith('##'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.replace('##', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _apply_rate_limiting(self) -> None:
        """Apply rate limiting to AI API calls"""
        now = time.time()
        
        # Remove requests older than 1 minute
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        # Check if we're at the limit
        if len(self._request_times) >= self._max_requests_per_minute:
            sleep_time = 60 - (now - self._request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limiting: sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
        
        self._request_times.append(now)
    
    def _extract_serializer_code(self, serializer_data: Dict[str, Any]) -> str:
        """Extract serializer code from file for AI analysis"""
        try:
            file_path = serializer_data.get('file_path')
            if not file_path:
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract just the serializer class (simplified)
            class_name = serializer_data.get('name', '')
            if class_name:
                # Simple extraction - could be enhanced with AST parsing
                class_start = content.find(f"class {class_name}")
                if class_start != -1:
                    # Find the end of the class (next class or end of file)
                    next_class = content.find("\nclass ", class_start + 1)
                    if next_class != -1:
                        return content[class_start:next_class]
                    else:
                        return content[class_start:]
            
            return content[:2000]  # Limit to avoid token limits
            
        except Exception as e:
            logger.warning(f"Failed to extract serializer code: {str(e)}")
            return ""
    
    def _extract_view_code(self, view_data: Dict[str, Any]) -> str:
        """Extract view code from file for AI analysis"""
        try:
            file_path = view_data.get('file_path')
            if not file_path:
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract just the view class (simplified)
            class_name = view_data.get('name', '')
            if class_name:
                class_start = content.find(f"class {class_name}")
                if class_start != -1:
                    next_class = content.find("\nclass ", class_start + 1)
                    if next_class != -1:
                        return content[class_start:next_class]
                    else:
                        return content[class_start:]
            
            return content[:2000]  # Limit to avoid token limits
            
        except Exception as e:
            logger.warning(f"Failed to extract view code: {str(e)}")
            return ""